local folder = child(ReplicatedStorage, "Folder", "AetherixAdmin")
local remote = child(folder, "RemoteEvent", "Inventory")
ItemManager:Refresh()
local message = remote.LastArgs[1]
check(message.Action == "Catalog", "Client requests authorized catalog")
remote.OnClientEvent:Fire({ RequestId = message.RequestId, Ok = true, Message = "Ready", Items = {
    { Id = "Sword", Type = "Weapon", Name = "Test Sword", MaxQuantity = 10 },
} })
check(#ItemManager.Catalog == 1 and ItemManager.Catalog[1].Grantable, "Server catalog becomes grantable")
local entry = ItemManager.Catalog[1]
local calls = remote.Calls
ItemManager:Grant(entry, 11)
ItemManager:Grant(entry, 0 / 0)
ItemManager:Grant(entry, 1.5)
check(remote.Calls == calls, "Invalid quantities do not leave client")
ItemManager:Grant(entry, 2)
local grant = remote.LastArgs[1]
check(grant.Key == "Weapon:Sword" and grant.Quantity == 2, "Grant uses canonical server key and quantity")
ItemManager:Grant(entry, 3)
check(remote.Calls == calls + 1, "Rapid clicks cannot duplicate pending grant")
now += 13
ItemManager:Grant(entry, 3)
check(remote.LastArgs[1].RequestId == grant.RequestId and remote.LastArgs[1].Quantity == 2, "Timeout retries same ID and original quantity")
remote.OnClientEvent:Fire({ RequestId = "unknown", Ok = true })
check(ItemManager.PendingGrant ~= nil, "Uncorrelated responses ignored")
remote.OnClientEvent:Fire({ RequestId = grant.RequestId, Ok = true, Message = "Synchronized" })
check(ItemManager.PendingGrant == nil and ItemManager.Status == "Synchronized", "Only server confirmation completes grant")
folder:Destroy()
ItemManager:Grant(entry, 1)
check(ItemManager.PendingGrant == nil and string.find(ItemManager.Status, "not installed", 1, true), "Missing endpoint is actionable and clears unsent grant")
print("Inventory client:", checks, "checks passed")
