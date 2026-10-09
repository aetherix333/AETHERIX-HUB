-- Minimal engine boundary mock; actual production functions are embedded by verify.py.
local now = 0
local os = { clock = function() return now end }
local function signal()
    local listeners = {}
    return {
        Connect = function(_, fn)
            local connection = { Connected = true }
            function connection:Disconnect() self.Connected = false end
            table.insert(listeners, { connection, fn })
            return connection
        end,
        Fire = function(_, ...)
            for _, pair in ipairs(listeners) do if pair[1].Connected then pair[2](...) end end
        end,
    }
end
local Methods = {}
local Instance = {}
function Instance.new(class)
    local props = { ClassName = class, Name = class, Children = {}, Attributes = {}, Archivable = true }
    if class == "RemoteEvent" then props.OnServerEvent = signal(); props.OnClientEvent = signal(); props.Replies = {} end
    return setmetatable({}, {
        __index = function(_, key) return Methods[key] or props[key] end,
        __newindex = function(self, key, value)
            if key == "Parent" then
                if props.Parent then
                    local index = table.find(props.Parent.Children, self)
                    if index then table.remove(props.Parent.Children, index) end
                end
                if value then table.insert(value.Children, self) end
            end
            props[key] = value
        end,
    })
end
function Methods:IsA(class) return self.ClassName == class end
function Methods:GetChildren() return table.clone(self.Children) end
function Methods:GetDescendants()
    local result = {}
    for _, child in ipairs(self.Children) do
        table.insert(result, child)
        for _, descendant in ipairs(child:GetDescendants()) do table.insert(result, descendant) end
    end
    return result
end
function Methods:FindFirstChild(name)
    for _, child in ipairs(self.Children) do if child.Name == name then return child end end
end
function Methods:FindFirstChildOfClass(class)
    for _, child in ipairs(self.Children) do if child:IsA(class) then return child end end
end
function Methods:GetAttribute(name) return self.Attributes[name] end
function Methods:SetAttribute(name, value) self.Attributes[name] = value end
function Methods:Clone()
    if not self.Archivable then return nil end
    local copy = Instance.new(self.ClassName)
    copy.Name = self.Name
    return copy
end
function Methods:Destroy() self.Parent = nil; self.Destroyed = true end
function Methods:FireClient(player, result) table.insert(self.Replies, { Player = player, Result = result }) end
function Methods:FireServer(...) self.LastArgs = table.pack(...); self.Calls = (self.Calls or 0) + 1 end
function Methods:InvokeServer(...) self:FireServer(...); return self.Result end
local typeof = function(value) return type(value) == "table" and value.ClassName and "Instance" or type(value) end
local Enum = { CreatorType = { User = "User", Group = "Group" } }
local Players = Instance.new("Players")
Players.PlayerRemoving = signal()
local ReplicatedStorage = Instance.new("ReplicatedStorage")
local RunService = { IsServer = function() return true end }
local game = { CreatorType = Enum.CreatorType.User, CreatorId = 1 }
function game:GetService(name) return ({ Players = Players, ReplicatedStorage = ReplicatedStorage, RunService = RunService })[name] end
local warn = function() end
local function child(parent, class, name)
    local value = Instance.new(class)
    value.Name, value.Parent = name, parent
    return value
end
local function player(id)
    local result = child(Players, "Player", tostring(id))
    result.UserId = id
    child(result, "Backpack", "Backpack")
    return result
end
local checks = 0
local function check(condition, message)
    assert(condition, message)
    checks += 1
end
