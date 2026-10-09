#!/usr/bin/env python3
"""Run the actual edited Luau functions with a mocked Roblox boundary.
Usage: LUAU_BIN=/path/to/luau python3 tests/verify.py
Does not substitute for Roblox Studio or live multiplayer tests.
"""
import os
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LUAU = os.environ.get("LUAU_BIN", "luau")
parser = argparse.ArgumentParser()
parser.add_argument("--only", choices=["inventory", "network", "item_client"])
args = parser.parse_args()

def run(name, source):
    if args.only and args.only != name:
        return
    with tempfile.TemporaryDirectory(prefix="aetherix-tests-") as directory:
        path = Path(directory) / f"{name}.luau"
        path.write_text(source)
        subprocess.run([LUAU, str(path)], check=True, cwd=ROOT)

mock = (ROOT / "tests/roblox_mock.luau").read_text()
server = (ROOT / "AetherixInventoryServer.luau").read_text()
run("inventory", mock + "\nlocal InventoryServer = (function()\n" + server + "\nend)()\n" + (ROOT / "tests/inventory_cases.luau").read_text())
hub = (ROOT / "AETHERIX_HUB").read_text()
network = hub[hub.index("local function getRemote("):hub.index("local function char()")]
run("network", mock + '''
local Session = { Alive = true }
local State = { Debug = true }
local RemoteRoot
''' + network + '''
check(getRemote("Backpack", "TryEquipItemRE") == nil, "Missing root is safe")
local root = child(ReplicatedStorage, "Folder", "Remote")
local legacy = child(root, "Folder", "Backpack")
child(legacy, "BindableEvent", "TryEquipItemRE")
check(getRemote("Backpack", "TryEquipItemRE") == nil, "Never treat bindables as network remotes")
local current = child(root, "Folder", "Backpack_Server")
local equip = child(current, "RemoteEvent", "TryEquipItemRE")
check(getRemote("Backpack", "TryEquipItemRE") == equip, "Late replication and server suffix resolve")
local result, sent = call("Backpack", "TryEquipItemRE", "id", nil, "Weapon", nil)
check(sent and result and equip.LastArgs.n == 4 and equip.LastArgs[3] == "Weapon", "Nil arguments preserved")
local rf = child(current, "RemoteFunction", "GetDataRF")
rf.Result = false
result, sent = call("Backpack", "GetDataRF")
check(result == false and sent, "Server false is preserved")
rf.Result = { have = {} }
check(call("Backpack", "GetDataRF") == rf.Result, "Server result preserved")
current:Destroy()
local oldRemote = child(legacy, "RemoteEvent", "OldRE")
check(getRemote("Backpack", "OldRE") == oldRemote, "Legacy folder remains supported")
Session.Alive = false
result, sent = call("Backpack", "OldRE")
check(not sent and oldRemote.Calls == nil, "Shutdown stops network work")
print("Remote dispatch:", checks, "checks passed")
''')
items = hub[hub.index("local ItemManager = (function()"):hub.index("local UIRebuilding = false")]
run("item_client", mock + '''
local Session = { Alive = true }
function Session:Connect(event, callback) return event:Connect(callback) end
local State = { Language = "EN" }
local guid = 0
local HttpService = { GenerateGUID = function() guid += 1; return tostring(guid) end }
local task = { delay = function() end }
local notify = function() end
''' + items + (ROOT / "tests/client_cases.luau").read_text())
