-- Install as a ModuleScript in ServerScriptService and call Start once from a Script.
-- This bridge never trusts client catalog data, target players, or permission claims.
local InventoryServer = {}
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local function integer(value, minimum, maximum)
    return type(value) == "number" and value == value and value % 1 == 0 and value >= minimum and value <= maximum
end

function InventoryServer.ToolAdapter(folder)
    assert(typeof(folder) == "Instance", "ToolAdapter requires a server-owned folder")
    local templates, catalog = {}, {}
    for _, tool in ipairs(folder:GetDescendants()) do
        if tool:IsA("Tool") then
            local id = tostring(tool:GetAttribute("ItemId") or tool.Name)
            local key = "Tool:" .. id
            assert(not templates[key], "Duplicate tool item ID: " .. id)
            templates[key] = tool
            table.insert(catalog, { Type = "Tool", Id = id, Name = tool:GetAttribute("DisplayName") or tool.Name, MaxQuantity = 100 })
        end
    end
    return {
        Catalog = catalog,
        Grant = function(player, item, quantity)
            local backpack = player:FindFirstChildOfClass("Backpack")
            local template = templates[item.Key]
            if not backpack or not template or not template.Parent then
                return { Ok = false, Message = "Backpack or tool template unavailable" }
            end
            local clones = {}
            local ok, err = pcall(function()
                -- Prepare all instances before exposing any to the player.
                for _ = 1, quantity do
                    local clone = template:Clone()
                    assert(clone, "Tool must be Archivable")
                    table.insert(clones, clone)
                end
                for _, clone in ipairs(clones) do clone.Parent = backpack end
            end)
            if not ok then
                for _, clone in ipairs(clones) do clone:Destroy() end
                warn("[AETHERIX Inventory] Tool grant failed:", err)
                return { Ok = false, Message = "Tool grant failed; changes rolled back" }
            end
            -- Server-parented Tools replicate through Roblox's native Backpack.
            return { Ok = true, Quantity = quantity, Message = "Added " .. quantity .. " × " .. item.Name .. " to Backpack" }
        end,
    }
end

function InventoryServer.Start(options)
    assert(RunService:IsServer(), "Inventory bridge must run on the server")
    options = options or {}
    local adapter = options.Adapter
    assert(type(adapter) == "table" and type(adapter.Catalog) == "table" and type(adapter.Grant) == "function",
        "Provide an inventory adapter with Catalog and an atomic Grant function")
    assert(not ReplicatedStorage:FindFirstChild("AetherixAdmin"), "AetherixAdmin already exists; start the bridge only once")
    local catalog, byKey = {}, {}
    for _, row in ipairs(adapter.Catalog) do
        assert(type(row) == "table" and type(row.Type) == "string" and #row.Type > 0 and #row.Type <= 64 and not row.Type:find(":", 1, true), "Invalid item type")
        assert(type(row.Id) == "string" and #row.Id > 0 and #row.Id <= 128, "Invalid item ID")
        assert(type(row.Name) == "string" and #row.Name > 0 and #row.Name <= 256, "Invalid display name")
        local item = { Key = row.Type .. ":" .. row.Id, Type = row.Type, Id = row.Id, Name = row.Name, MaxQuantity = row.MaxQuantity or 100 }
        assert(integer(item.MaxQuantity, 1, 1000), "Invalid item quantity limit")
        assert(not byKey[item.Key], "Duplicate item key: " .. item.Key)
        table.freeze(item)
        byKey[item.Key] = item
        table.insert(catalog, item)
    end
    table.sort(catalog, function(a, b) return a.Key < b.Key end)
    local allowed = {}
    for _, userId in ipairs(options.AllowedUserIds or {}) do
        assert(integer(userId, 1, 9007199254740991), "Invalid administrator UserId")
        allowed[userId] = true
    end
    local function authorized(player)
        return allowed[player.UserId] == true
            or (game.CreatorType == Enum.CreatorType.User and player.UserId == game.CreatorId)
    end
    local folder = Instance.new("Folder")
    folder.Name = "AetherixAdmin"
    local remote = Instance.new("RemoteEvent")
    remote.Name = "Inventory"
    remote.Parent = folder
    local states = {}
    local alive = true
    local function reply(player, requestId, result)
        if not alive or player.Parent ~= Players then return end
        local response = table.clone(result)
        response.RequestId = requestId
        remote:FireClient(player, response)
    end
    local connection = remote.OnServerEvent:Connect(function(player, request)
        if not alive or type(request) ~= "table" or type(request.RequestId) ~= "string" or #request.RequestId < 1 or #request.RequestId > 64 then return end
        local id = request.RequestId
        local state = states[player]
        if not state then state = { Results = {}, Count = 0, LastRequest = -math.huge }; states[player] = state end
        local now = os.clock()
        if now - state.LastRequest < 0.25 then return end
        state.LastRequest = now
        if not authorized(player) then
            reply(player, id, { Ok = false, Message = "Permission denied: this server has not authorized your UserId" })
            return
        end
        local cached = state.Results[id]
        if cached then reply(player, id, cached); return end
        if request.Action == "Catalog" then
            reply(player, id, { Ok = true, Items = catalog, Message = "Server catalog ready • " .. #catalog .. " items" })
            return
        end
        if request.Action ~= "Grant" then reply(player, id, { Ok = false, Message = "Unknown action" }); return end
        if state.Busy then
            -- The original in-flight request receives its eventual result.
            if state.Busy ~= id then reply(player, id, { Ok = false, Message = "Another grant is still in progress" }) end
            return
        end
        if state.Count >= 256 then reply(player, id, { Ok = false, Message = "Session grant limit reached; rejoin to continue" }); return end
        local item = type(request.Key) == "string" and byKey[request.Key] or nil
        if not item or not integer(request.Quantity, 1, item.MaxQuantity) then
            reply(player, id, { Ok = false, Message = "Unknown item or invalid quantity" })
            return
        end
        state.Busy = id
        state.Count += 1
        -- The adapter owns capacity checks, persistence and game-specific replication.
        -- Grant must be atomic and finish synchronization before returning Ok=true.
        local ok, result = pcall(adapter.Grant, player, item, request.Quantity, id)
        if not ok or type(result) ~= "table" or type(result.Ok) ~= "boolean" then
            warn("[AETHERIX Inventory] Adapter failed for request", id)
            result = { Ok = false, Message = "Inventory adapter failed; administrator must check server logs" }
        elseif result.Ok and result.Quantity ~= request.Quantity then
            result = { Ok = false, Message = "Adapter returned an invalid quantity; administrator must check inventory" }
        else
            result = { Ok = result.Ok, Quantity = result.Quantity, Message = tostring(result.Message or (result.Ok and "Inventory synchronized" or "Grant rejected")) }
        end
        state.Results[id] = result -- Retain for the full session; retries cannot grant twice.
        state.Busy = nil
        reply(player, id, result)
    end)
    local leaving = Players.PlayerRemoving:Connect(function(player) states[player] = nil end)
    folder.Parent = ReplicatedStorage -- Publish only once the handler is ready.
    return {
        Stop = function()
            alive = false
            connection:Disconnect()
            leaving:Disconnect()
            folder:Destroy()
            table.clear(states)
        end,
    }
end

return InventoryServer
