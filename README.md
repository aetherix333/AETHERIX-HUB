# AETHERIX HUB

ปรับปรุง **ไฟล์ `AETHERIX_HUB` เดิม** สำหรับ `[BOSS]+1 Loot To Forge` โดยคงแท็บและฟังก์ชันเดิมไว้ เพิ่มตัวเชื่อมเซิร์ฟเวอร์สำหรับเกมที่คุณควบคุม ไม่ใช่โปรเจกต์ทดแทน

## สิ่งที่แก้ไข

- ค้นหา Remote ใน `<หมวด>_Server` ก่อน แล้วรองรับชื่อโฟลเดอร์เดิม; ไม่เรียก BindableEvent เป็น RemoteEvent และรองรับ Remote ที่ replicate มาช้า
- ส่ง argument ที่มี `nil` ได้ครบ และรักษาผล `false` จาก RemoteFunction
- จำกัด Auto Max ตามจำนวนด่านที่ค้นพบ; ไม่เลื่อนด่านเพียงเพราะโฟลเดอร์ศัตรูว่างโดยไม่ได้รับผลตอบกลับจาก StageFinishedRF
- เมื่อยังอยู่ในดันเจี้ยน ให้ทำรอบปัจจุบันต่อแม้ตั๋วใบสุดท้ายถูกใช้แล้ว
- ลดการทำงานซ้ำของ Master กับ Auto Forge / Upgrade / Equip / Enchant; ตรวจจำนวนแร่ขั้นต่ำก่อนหลอม
- โหลด config ที่เปิด toggle ไว้แล้วเริ่ม loop จริง; บันทึกการเปลี่ยนผ่าน UI; แจ้งความผิดพลาดเมื่อเขียนไฟล์ไม่ได้ และไม่รับตัวเลข NaN/Infinity/ติดลบ
- เปิดสคริปต์ซ้ำแล้วปิด session เก่า; ยกเลิก listeners/loops และคืนค่า collision เมื่อหยุด Noclip หรือปิดเมนู
- แก้การ rebuild UI เมื่อเปลี่ยนภาษา: WindUI เดิมทำลาย ScreenGui แบบหน่วงเวลา จึงต้องรอและสร้าง library instance ใหม่
- ธีม Obsidian สีเข้ม, Inter SemiBold และ Syne Bold, คงธีมเดิมทั้งหมด, search ใน dropdown, หน้าต่างพอดี viewport/ปรับตามการหมุนจอ, ปุ่มเปิดเมนูบนมือถือ และใช้ tween ของ WindUI
- เพิ่ม Item Manager: ค้นหาชื่อ/ID แบบข้อความ, กรองประเภท, แบ่งหน้าละ 80 รายการ, เลือกจำนวน และแสดงผลตอบกลับจากเซิร์ฟเวอร์

## Dependencies และการรัน

- Runtime: Roblox Luau ฝั่ง client; `AETHERIX_HUB` เป็นสคริปต์ client ไม่ใช่ Lua ทั่วไปหรือเว็บแอป
- UI: [WindUI 1.6.66](https://github.com/Footagesus/WindUI/releases/tag/1.6.66) ถูกตรึงเวอร์ชันแทน `latest` เพื่อไม่ให้ API เปลี่ยนโดยไม่ตั้งใจ สคริปต์เดิมใช้ `loadstring` และ `game:HttpGet` ซึ่ง **LocalScript ปกติไม่มี**
- ใน Studio ให้นำ WindUI เวอร์ชันดังกล่าวที่จัดเตรียมให้รันในสภาพแวดล้อมของคุณใส่ ModuleScript ชื่อ `ReplicatedStorage.AetherixWindUI` แล้วใส่เนื้อหา `AETHERIX_HUB` ใน LocalScript เดิม ต้องตรวจข้อกำหนด runtime ของ WindUI ด้วย; ไม่ได้รับรองว่า release สำหรับ executor จะทำงานใน Studio โดยไม่ปรับ dependency
- โมดูลเกมเดิมใน `ReplicatedStorage.Config`, `LocalData`, `CTRL`, `Utils`, `GuiUtils`, `ProfileData` ยังคงใช้ตามเดิม
- `getsenv`, `debug.getupvalues`, `fireproximityprompt`, file APIs, HTTP request, clipboard, `setfpscap` เป็นความสามารถเสริมของ runtime เดิม ไม่ใช่ Roblox APIs มาตรฐาน ฟังก์ชันที่พึ่งความสามารถเหล่านี้ต้องทดสอบใน runtime เป้าหมาย
- การตรวจไฟล์แนบยืนยันเฉพาะ **ชื่อและชนิดของ 41 Remote และ 18 ModuleScript** ไม่ยืนยัน argument หรือ method ภายในโมดูล เพราะไฟล์แนบมีเพียง hierarchy

### ฟอนต์

ลำดับการโหลดฟอนต์:

1. กำหนด string attributes ของ `ReplicatedStorage`: `AetherixInterFont` และ `AetherixSyneFont` เป็น `rbxassetid://...` ของ **font-family assets** ที่เกมมีสิทธิ์ใช้
2. Runtime ที่รองรับ `writefile` และ `getcustomasset` จะใช้ TTF จาก Google Fonts Inter v20 / Syne v24 และสร้าง font-family JSON ในเครื่อง
3. ถ้าไม่รองรับ จะใช้ฟอนต์ Roblox สำรองและเตือนใน Console ฟอนต์จริง/การแสดงภาษาไทยยังต้องตรวจใน Roblox

ไม่สามารถนำ URL Google Fonts ไปตั้ง `FontFace` ใน LocalScript ปกติโดยตรงได้

## เพิ่มไอเท็มจริง: ต้องติดตั้งฝั่งเซิร์ฟเวอร์

ไฟล์ ReplicatedStorage ที่แนบมาไม่มีซอร์สระบบ Inventory หรือโค้ดเซิร์ฟเวอร์ จึง **ไม่สามารถยืนยันรายชื่อไอเท็มครบทุกชนิด หรือเชื่อมกระเป๋าเฉพาะของเกมได้จากไฟล์นี้เพียงอย่างเดียว** รายการจาก Config/Assets เป็นรายการสำหรับค้นดูและไม่อนุญาตให้เพิ่มจนกว่าเซิร์ฟเวอร์จะส่ง catalog ที่อนุญาต

`AetherixInventoryServer.luau` เป็นโมดูลเสริมของ HUB เดิม ใช้กับเกมที่คุณควบคุม โดย:

- อนุญาตเจ้าของเกมประเภท User และ UserId ใน allowlist ฝั่งเซิร์ฟเวอร์เท่านั้น สำหรับเกมที่เป็นของ Group ให้ระบุ UserId ผู้ดูแลชัดเจน
- เพิ่มให้ผู้เล่นที่ส่งคำขอเท่านั้น ไม่รับ target player หรือสิทธิ์จากไคลเอนต์
- ใช้ catalog ฝั่งเซิร์ฟเวอร์ ตรวจจำนวนเต็ม/ขีดจำกัด และจำผล request ID กันการเพิ่มซ้ำ
- จำกัดคำขอทุก 0.25 วินาที ล็อก grant ระหว่างทำงาน และเก็บผลสูงสุด 256 grants ต่อ session; ออกจากเกมจึงล้าง state
- ไคลเอนต์ที่รอเกิน 12 วินาทีจะลอง **request ID/จำนวนเดิม** และไม่อ้างว่าสำเร็จจนได้รับผลยืนยัน

### โหมดกระเป๋า Roblox Tool (มี implementation พร้อม)

1. ใส่ `AetherixInventoryServer.luau` เป็น ModuleScript ชื่อ `AetherixInventoryServer` ใน ServerScriptService
2. สร้าง `ServerStorage.AetherixItems` ใส่ Tool templates ที่อนุญาตให้แจก (รวม subfolders ได้) ใช้ชื่อไม่ซ้ำ หรือกำหนด string attribute `ItemId` และ optional `DisplayName`
3. เพิ่ม Script ใน ServerScriptService:

```luau
local ServerStorage = game:GetService("ServerStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local InventoryServer = require(ServerScriptService:WaitForChild("AetherixInventoryServer"))

InventoryServer.Start({
    AllowedUserIds = {}, -- ใส่ UserId ผู้ดูแล โดยเฉพาะเกมของ Group
    Adapter = InventoryServer.ToolAdapter(ServerStorage:WaitForChild("AetherixItems")),
})
```

ToolAdapter clone Tool จากเซิร์ฟเวอร์และใส่ใน `Player.Backpack` จึงใช้การ replicate มาตรฐานของ Roblox ไม่ใช่การเพิ่มตัวเลขปลอมใน UI รายการ catalog คือ Tool ทุกชิ้นใน folder นี้ ต้องใช้ Tool ที่ตั้งค่าใช้งานถูกต้องเอง

**ขอบเขต:** Tool ใน Backpack เป็นของ session ปัจจุบัน ไม่ได้บันทึก DataStore/StarterGear และไม่ได้เชื่อมกับกระเป๋า custom ของ +1 Loot To Forge ผู้เล่นอื่นเห็น Tool ที่ equip ผ่าน replication ปกติ แต่ไม่ได้เห็นหน้า inventory ส่วนตัวของกันและกันโดยอัตโนมัติ

### กระเป๋าเฉพาะของเกม

แทนที่ ToolAdapter ด้วย table ที่มี:

- `Catalog`: array ของ `{Type = "Ore", Id = "<ID จริง>", Name = "<ชื่อจริง>", MaxQuantity = 100}` ต้องสร้างจาก **รายการไอเท็มทั้งหมดฝั่งเซิร์ฟเวอร์**; คีย์คือ `Type:Id` และต้องไม่ซ้ำ
- `Grant(player, item, quantity, requestId)`: ตรวจ capacity/สถานะ profile, เพิ่มไอเท็มผ่าน Inventory service ตัวจริง, บันทึกตามนโยบายเกม และส่ง snapshot/delta ผ่านช่อง sync ของเกม จากนั้นคืน `{Ok = true, Quantity = quantity, Message = "..."}`
- ถ้าปฏิเสธให้คืน `{Ok = false, Message = "..."}` โดยไม่ทิ้งการแก้ไขค้างไว้ การ mutate ต้อง atomic; หากต้องรองรับ retry ข้ามเซิร์ฟเวอร์/reconnect ให้ deduplicate `requestId` ใน transaction ของระบบเกมด้วย

อย่าให้ adapter เพิ่มของก่อนแล้วโยน error โดยไม่ rollback ตัว bridge ไม่สามารถย้อน transaction ของ Inventory service ที่ไม่รู้จักได้ และจะไม่ลอง grant ที่ error ซ้ำให้อัตโนมัติ

ไม่เดารูปแบบ payload ของ `Dev_Server.Get*RE` และไม่แก้ `BackpackData.have` ฝั่ง client เพื่อแสดงว่าสำเร็จ

## การตรวจสอบ

ใช้ Luau CLI 0.741 และ Python 3 (ไม่มี pip/npm dependencies):

```bash
luau-compile AETHERIX_HUB > /tmp/aetherix-hub.bytecode.txt
luau-compile AetherixInventoryServer.luau > /tmp/aetherix-server.bytecode.txt
LUAU_BIN=/path/to/luau python3 tests/verify.py
python3 tests/audit_dump.py /path/to/ReplicatedStorage-dump.txt
git diff --check
```

Tests ใช้ฟังก์ชันจริงจากไฟล์ที่แก้และ mock ขอบเขต Roblox เพื่อตรวจ authorization, quantity, replay, in-flight lock, server Backpack parenting, client retry และ remote dispatch ไม่ใช่การรัน engine จริง

### ข้อจำกัดที่ยังต้องทดสอบในเกม

- Roblox Studio/engine ไม่มีใน sandbox Linux นี้: ยังไม่ได้ทดสอบภาพ UI, animation, touch/keyboard, font loading หรือ multiplayer replication จริง
- API payload, game rules, module methods และข้อมูล save/profile ยืนยันไม่ได้จาก instance dump ต้องมีซอร์สฝั่งเซิร์ฟเวอร์หรือทดสอบในเกมที่คุณควบคุม
- Instant Kill/God Mode, การเข้า stage, forge/enchant/gacha/rewards, zone coordinates และตัวนับผลลัพธ์บางรายการเป็นตรรกะเดิม ไม่สามารถรับรองว่าเซิร์ฟเวอร์เกมเวอร์ชันใหม่ยอมรับ คงฟังก์ชันไว้และไม่ได้อ้างว่า client-side damage/attributes เป็นผลสำเร็จฝั่งเซิร์ฟเวอร์
- สถิติเดิมหลายตัวนับครั้งที่เรียกทำงาน ไม่ใช่ผลยืนยัน; ให้ใช้ข้อมูลจริงของเกมในการตรวจยอด
- รายชื่อจาก Config แบบ nested ที่ยังไม่ทราบ schema อาจไม่ครบหรือใช้ ID แทน display name; authoritative catalog จาก adapter เป็นทางที่จะให้ครบจริง

### Studio acceptance checks

1. ทดสอบสองผู้เล่น: ผู้ดูแลเห็น catalog/เพิ่มได้ และผู้ไม่มีสิทธิ์ถูกปฏิเสธโดยจำนวนของไม่เปลี่ยน
2. เพิ่มจำนวน 1 และหลายชิ้น, ตรวจ inventory จริง/ผู้เล่นอื่นเห็น Tool ที่ equip, ทดสอบ quantity ผิดและ Backpack เต็มตาม adapter
3. หน่วง reply แล้ว retry ตรวจว่าเพิ่มครั้งเดียว; ทดสอบ respawn/rejoin และนโยบาย persistence ของเกม
4. เปลี่ยนภาษา/โหลด config/เปิด HUB ซ้ำ ตรวจว่าไม่มีหน้าต่างหายจาก delayed destroy หรือ loop ซ้ำ
5. ตรวจจอ portrait/landscape, ค้นหาไทย/อังกฤษ, slider, toggles, font fallback และปุ่มเปิด/ปิดเมนู
