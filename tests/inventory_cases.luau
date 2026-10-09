local templates = Instance.new("Folder")
child(templates, "Tool", "Sword")
child(templates, "Tool", "Potion")
local owner, admin, stranger = player(1), player(2), player(3)
local adapter = InventoryServer.ToolAdapter(templates)
local bridge = InventoryServer.Start({ Adapter = adapter, AllowedUserIds = { 2 } })
local remote = ReplicatedStorage:FindFirstChild("AetherixAdmin"):FindFirstChild("Inventory")
local function send(who, id, action, key, quantity)
    now += 1
    local before = #remote.Replies
    remote.OnServerEvent:Fire(who, { RequestId = id, Action = action, Key = key, Quantity = quantity })
    return #remote.Replies > before and remote.Replies[#remote.Replies].Result or nil
end
local function count(who) return #who:FindFirstChildOfClass("Backpack"):GetChildren() end
check(send(stranger, "deny", "Grant", "Tool:Sword", 1).Ok == false and count(stranger) == 0, "Reject unauthorized grant")
check(send(stranger, "deny-cat", "Catalog").Ok == false, "Catalog requires authorization")
check(#send(owner, "catalog", "Catalog").Items == 2, "Full server catalog returned")
check(send(admin, "admin", "Grant", "Tool:Sword", 3).Ok and count(admin) == 3, "Allowlisted admin gets actual server-parented tools")
check(send(admin, "admin", "Grant", "Tool:Potion", 50).Ok and count(admin) == 3, "Replay cannot change or duplicate committed grant")
check(count(owner) == 0, "Cannot mutate another player's inventory")
check(send(owner, "unknown", "Grant", "Tool:Fake", 1).Ok == false, "Reject unknown item")
for index, quantity in ipairs({ 0, -1, 1.5, 101, math.huge, 0 / 0, "3" }) do
    check(send(owner, "bad-" .. index, "Grant", "Tool:Sword", quantity).Ok == false, "Reject invalid quantity " .. index)
end
check(count(owner) == 0, "Invalid grants have no side effects")
check(send(owner, "wrong-action", "Delete", "Tool:Sword", 1).Ok == false, "Reject unknown action")
game.CreatorType = Enum.CreatorType.Group
check(send(owner, "group", "Grant", "Tool:Sword", 1).Ok == false, "Group ID never authorizes a matching user ID")
game.CreatorType = Enum.CreatorType.User
remote.OnServerEvent:Fire(owner, nil)
remote.OnServerEvent:Fire(owner, { RequestId = string.rep("x", 65) })
check(count(owner) == 0, "Malformed requests do not grant")
local tool = templates:FindFirstChild("Sword")
tool.Archivable = false
check(send(owner, "clone-fail", "Grant", "Tool:Sword", 2).Ok == false and count(owner) == 0, "Clone failure rolls back")
tool.Archivable = true
check(send(owner, "clone-fail", "Grant", "Tool:Sword", 2).Ok == false and count(owner) == 0, "Failed request remains idempotent")
check(send(owner, "valid", "Grant", "Tool:Sword", 2).Ok and count(owner) == 2, "Creator grants work")
local before = #remote.Replies
remote.OnServerEvent:Fire(owner, { RequestId = "fast", Action = "Grant", Key = "Tool:Sword", Quantity = 1 })
check(#remote.Replies == before and count(owner) == 2, "Rate limiting prevents immediate repeated work")
bridge.Stop()
check(not ReplicatedStorage:FindFirstChild("AetherixAdmin"), "Stop removes endpoint")
local calls = 0
bridge = InventoryServer.Start({ Adapter = { Catalog = adapter.Catalog, Grant = function(_, item, quantity, id)
    calls += 1
    if id == "throw" then error("test") end
    if id == "yielding" then coroutine.yield() end
    return { Ok = true, Quantity = quantity, Message = item.Name }
end } })
remote = ReplicatedStorage:FindFirstChild("AetherixAdmin"):FindFirstChild("Inventory")
check(send(owner, "throw", "Grant", "Tool:Sword", 1).Ok == false, "Adapter errors are reported")
check(send(owner, "throw", "Grant", "Tool:Sword", 1).Ok == false and calls == 1, "Adapter exception is not retried")
local pending = coroutine.create(function() send(owner, "yielding", "Grant", "Tool:Sword", 1) end)
check(coroutine.resume(pending), "Yielding adapter starts")
check(send(owner, "yielding", "Grant", "Tool:Sword", 1) == nil and calls == 2, "Retry during yield cannot duplicate grant")
check(send(owner, "overlap", "Grant", "Tool:Sword", 1).Ok == false and calls == 2, "Other grants are locked while yielding")
check(coroutine.resume(pending), "Yielding adapter completes")
check(send(owner, "yielding", "Grant", "Tool:Sword", 1).Ok and calls == 2, "Completed yield result is cached")
bridge.Stop()
print("Inventory bridge:", checks, "checks passed")
