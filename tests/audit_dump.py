#!/usr/bin/env python3
"""Verify static module/remote paths against an instance hierarchy, not API signatures."""
import argparse
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument("dump", type=Path)
args = parser.parse_args()
stack, nodes = [], {}
for line in args.dump.read_text().splitlines():
    if line.lstrip().startswith("@"):
        continue
    match = re.match(r"^( *)(\S.*?) \[([^\]]+)\]$", line)
    if not match:
        continue
    depth, name, class_name = len(match[1]), match[2], match[3]
    while stack and stack[-1][0] >= depth:
        stack.pop()
    stack.append((depth, name))
    nodes[".".join(item[1] for item in stack)] = class_name
assert nodes.get("ReplicatedStorage.Remote") == "Folder", "Expected dump root was not parsed"
source = (Path(__file__).resolve().parents[1] / "AETHERIX_HUB").read_text()
remotes = set(re.findall(r'(?:getRemote|call)\("([^"]+)", "([^"]+)"', source))
# Event names passed through the WorldBoss subscription helper.
remotes.update(("WorldBoss", name) for name in re.findall(r'hook\("([^"]+)"', source))
missing = []
for folder, name in sorted(remotes):
    candidates = [f"ReplicatedStorage.Remote.{folder}_Server.{name}", f"ReplicatedStorage.Remote.{folder}.{name}"]
    if not any(nodes.get(path) in ("RemoteEvent", "RemoteFunction") for path in candidates):
        missing.append(f"{folder}/{name}")
modules = set(re.findall(r"require\((ReplicatedStorage(?:\.[A-Za-z_][A-Za-z_0-9]*)+)\)", source))
missing_modules = sorted(path for path in modules if nodes.get(path) != "ModuleScript")
print(f"Remote paths: {len(remotes)} checked; missing: {missing}")
print(f"Module paths: {len(modules)} checked; missing: {missing_modules}")
print("Hierarchy only: payloads, module methods and server acceptance still require game-source/Studio verification.")
raise SystemExit(bool(missing or missing_modules))
