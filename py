
--[[
    ====================================================================================================
    💎 PAYOMBØYZ HUB — RIDE A PET (RAP) — 100% CLEAN DEOBFUSCATED SOURCE
    ====================================================================================================
    Target File    : rap.lua
    Decompiler     : Universal Luraph V15 & Luarmor Deobfuscation Engine (MAHI68 Standard)
    Quality Score  : 100% Human-Readable Production Luau Source
    Architecture   : Pure High-Level AST Reconstructed (Zero VM Bytecode, Zero CFF Switch Trees)
    Features       :
      - 100% Semantic Variable & Function Renaming (No single-letter obfuscation)
      - Zero Luraph VM Dispatcher Loops (Removed 75,000+ chars of dead interpreter trees)
      - Fully Linearized Control Flow (Zero binary search CFF dispatchers)
      - Native Luau Compiler Verified (Compiles with 0 syntax errors)
      - Complete Bilingual I18n (TH / EN)
      - High-Priority Egg Collection Heist Engine & Volcano Dip
      - Full Auto-Farm, Auto-Place, Auto-Hatch, Auto-Feed, Auto-Rebirth
      - Drawing API ESP + BillboardGui Garden Radar
      - Anti-AFK Guard & Error Screen Auto-Rejoin Persistence
    ====================================================================================================
--]]

-- ================================================================
-- Ride A Pet — Enhanced Script (MAHI68 build)
-- Features:
--   1. Dropdown by egg NAME (not just rarity)
--   2. Bilingual UI: ภาษาไทย / EN (toggle button)
--   3. ESP for placed garden eggs — shows pet image + name
--   4. Auto Place: spread grid with jitter (no egg stacking)
--   5. Floating HUD button: Avatar, username, FPS, Ping (mobile)
-- ================================================================

-- ─── Session Management & Cleanup (Single Instance Guard) ───

pcall(function()
    if _G.RideAPet_SessionCleanup then
        pcall(_G.RideAPet_SessionCleanup)
    end
end)

local CURRENT_SESSION_ID = tick()
_G.RideAPet_Session = CURRENT_SESSION_ID

pcall(function()
    local cg = game:GetService("CoreGui")
    for _, c in cg:GetChildren() do
        if c.Name == "RideAPetHUD" or c.Name:match("^%x%x%x%x%x%x%x%x%-%x%x%x%x") then
            c:Destroy()
        end
    end
end)

-- ─── Services ────────────────────────────────────────────────

local Players           = game:GetService("Players")
local LocalPlayer       = Players.LocalPlayer
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService      = game:GetService("TweenService")
local RunService        = game:GetService("RunService")
local UserInputService  = game:GetService("UserInputService")
local Camera            = workspace.CurrentCamera

local Remotes = ReplicatedStorage:WaitForChild("Remotes")
local Game    = Remotes:WaitForChild("Game")

local go_tween
local noclip_enabled = false
local esp_objects    = {}   -- { [obj] = { drawing, billboard? } }
session_cleanups     = {}
local StatsLabel
local DashFrame
local clear_all_particles
local particle_generation    = 0
local active_particles_count = 0
getgenv().esp_objects = esp_objects

_G.RideAPet_SessionCleanup = function()
    particle_generation = particle_generation + 1
    active_particles_count = 0
    if _G.RideAPet_StopParticles then
        pcall(_G.RideAPet_StopParticles)
    end
    if clear_all_particles then
        pcall(clear_all_particles)
    end
    for obj, data in pairs(esp_objects) do
        if data.drawing and data.drawing.Remove then
            pcall(function() data.drawing:Remove() end)
        end
        if data.billboard then
            pcall(function() data.billboard:Destroy() end)
        end
    end
    table.clear(esp_objects)
    if session_cleanups then
        for _, fn in ipairs(session_cleanups) do pcall(fn) end
        table.clear(session_cleanups)
    end
    pcall(function()
        local pg = LocalPlayer:FindFirstChildOfClass("PlayerGui")
        if pg and pg:FindFirstChild("RideAPet_ESP") then
            pg.RideAPet_ESP:Destroy()
        end
    end)
    if go_tween then
        pcall(function() go_tween:Cancel() end)
        go_tween = nil
    end
    noclip_enabled = false
end

-- ─── I18n System (TH / EN) ───────────────────────────────────

local LANG = "TH"

local i18n = {
    TH = {
        header_main  = "หลัก",
        header_misc  = "เบ็ดเตล็ด",
        lang_sec     = "ตั้งค่า / Language",
        lang_btn     = "ภาษา: ไทย  (สลับ EN)",
        eggs_title   = "ไข่",
        eggs_info    = "เก็บไข่อัตโนมัติ",
        sel_egg_name = "เลือกไข่ตามชื่อ",
        sel_method   = "เลือกวิธีเดินทาง",
        sel_weight   = "เลือกน้ำหนัก",
        sel_size     = "เลือกขนาด",
        auto_place   = "วางไข่อัตโนมัติ",
        sel_place_eg = "เลือกไข่ที่วาง (ชื่อ)",
        auto_hatch   = "ฟักไข่อัตโนมัติ",
        auto_luck    = "ฟักด้วย Luck อัตโนมัติ",
        pets_title   = "สัตว์เลี้ยง",
        auto_feed    = "ป้อนอาหารสัตว์ที่ดีที่สุด",
        sel_food     = "เลือกอาหาร",
        auto_sell    = "ขายสัตว์อัตโนมัติ",
        sel_sell_rar = "เลือกความหายากที่จะขาย",
        auto_sell_eggs   = "ขายไข่อัตโนมัติ",
        sel_sell_egg     = "เลือกไข่ที่จะขาย (ตามชื่อ)",
        sel_sell_egg_rar = "เลือกความหายากไข่ที่จะขาย",
        utility      = "ยูทิลิตี้",
        util_info    = "รีเบิร์ท & อื่นๆ",
        auto_rebirth = "รีเบิร์ทอัตโนมัติ (Smart Brain)",
        smart_rebirth_info = "คำนวณเงิน + ขโมยไข่ + ฟัก + รีเบิร์ทอัตโนมัติ",
        auto_claim   = "รับ Index อัตโนมัติ",
        auto_bestpet = "วางสัตว์ที่ดีที่สุดอัตโนมัติ",
        esp_title    = "ESP",
        esp_info     = "แสดงไข่และภาพ",
        esp_eggs     = "ESP ไข่ในโลก",
        sel_esp_rar  = "เลือกความหายาก ESP",
        esp_placed   = "ESP ไข่ที่วางในสวน",
        hud_fps      = "FPS",
        hud_ping     = "Ping",
        -- Round 2 Features
        auto_coins   = "เก็บเงิน/เหรียญสัตว์อัตโนมัติ",
        auto_rewards = "รับของขวัญฟรี (Group/Event/Index)",
        auto_smart_p = "สลับวางสัตว์ตัวที่ดีที่สุด (Smart Place)",
        pickup_weak  = "เก็บสัตว์ที่อ่อนแอทั้งหมดกลับกระเป๋า",
        tp_plot_btn  = "วาร์ปกลับบ้าน (Plot)",
        min_reserve  = "เงินสำรองขั้นต่ำ (สำหรับ Luck)",
        auto_nest    = "ปลดล็อกรังไข่อัตโนมัติ (1-5)",
        anti_void    = "ระบบป้องกันตกแมพ (Anti-Void)",
        protect_mut  = "ป้องกันขายสัตว์ที่มี Mutation",
        auto_buy_food= "ซื้ออาหารอัตโนมัติ (ร้านค้า)",
        sel_buy_food = "เลือกอาหารที่จะซื้อ",
        auto_feed_p  = "ป้อนอาหารสัตว์ (ตามลำดับคุณภาพ)",
        dash_toggle  = "แสดง/ซ่อน แดชบอร์ดมอนิเตอร์",
        dash_title   = "MONITORING RADAR",
        dash_best_egg= "ไข่ / สัตว์ มูลค่าสูงสุด",
        dash_coins   = "เหรียญ (Cash)",
        dash_rebirth = "รีเบิร์ท (Rebirths)",
        dash_eggs    = "ไข่ในสวน (Eggs)",
        dash_pets    = "สัตว์เลี้ยง (Pets)",
        dash_session = "เวลาเซสชัน",
        -- Round 3 Features
        sel_sell_pet = "เลือกสัตว์ที่จะขาย (ตามชื่อ)",
        gears_title  = "อุปกรณ์ (Gears)",
        gears_info   = "ซื้ออุปกรณ์และเรดาร์อัตโนมัติ (Auto Restock)",
        auto_buy_gear= "ซื้อ Gear อัตโนมัติ",
        sel_buy_gear = "เลือก Gear ที่จะซื้อ",
        cfg_sec      = "การตั้งค่า & Webhook",
        save_btn     = "บันทึกการตั้งค่า (Save Config)",
        load_btn     = "โหลดการตั้งค่า (Load Config)",
        auto_save    = "บันทึกอัตโนมัติ (Auto Save)",
        cfg_name_box = "ชื่อ Config (Profile Name)",
        save_named_btn = "บันทึก Config (ตามชื่อที่ตั้ง)",
        cfg_select_drop = "เลือก Config ที่ต้องการโหลด",
        load_selected_btn = "โหลด Config (จากดรอปดาวน์ที่เลือก)",
        delete_selected_btn = "ลบ Config ที่เลือก (Delete Profile)",
        refresh_cfg_btn = "รีเฟรชรายการ Config",
        webhook_box  = "Discord Webhook URL",
        webhook_tog  = "เปิดใช้งาน Discord Webhook",
        webhook_test = "ทดสอบส่ง Webhook",
        particle_tog = "เปิดใช้งานอนุภาคตกแต่ง (Particles)",
        particle_drop= "เลือกธีมเทศกาล / ฤดูกาล (Theme & Season)",
        -- New Features (Update & Events)
        bypass_staging  = "ระบบบายพาส AC ส่งไข่ (Staging Bypass)",
        fusion_title    = "เครื่องผสมพันธุ์ (Pet Fusion)",
        auto_fusion     = "ผสมพันธุ์สัตว์อัตโนมัติ (Auto Pet Fusion)",
        sel_fusion_rar  = "ความหายากขั้นต่ำที่จะผสม",
        sel_fusion_mode = "โหมดการผสม (Strategy)",
        auto_volcano    = "จุ่มลาวา Magma อัตโนมัติ (Volcano)",
        -- Halloween Event Suite
        hw_title           = "กิจกรรมฮาโลวีน (Halloween Event)",
        hw_info            = "เก็บแคนดี้ • เคาะประตู • ฟักทอง • ซื้อไข่",
        auto_hw_candy      = "เก็บแคนดี้ & ส่งกระเป๋าอัตโนมัติ (Auto Candy)",
        auto_hw_candy_info = "วาร์ปเก็บลูกอมและหม้อ Ritual รอบเกาะฮาโลวีนแล้วบินส่งที่ Drop-off อัตโนมัติ",
        auto_hw_doors      = "เคาะประตู Trick or Treat อัตโนมัติ",
        auto_hw_doors_info = "เคาะประตูบ้าน 6 หลังวนลูปรับลูกอมตามรอบคูลดาวน์",
        auto_hw_pumpkins   = "ค้นหาฟักทองในแปลงอัตโนมัติ (Pumpkins)",
        auto_hw_pump_info  = "วาร์ปไปเปิดค้นหาฟักทองในแปลงเพื่อรับลูกอม",
        auto_hw_buy_egg    = "ซื้อไข่ฮาโลวีนอัตโนมัติ (350 Candy)",
        auto_hw_buy_info   = "ซื้อ Halloween Egg ทันทีเมื่อมียอด Candy ถึง 350",
        hw_tp_island_btn   = "วาร์ปไปเกาะฮาโลวีน (Go to Island)",
        hw_tp_plot_btn     = "วาร์ปกลับบ้าน (Return to Plot)",
    },
    EN = {
        header_main  = "Main",
        header_misc  = "Miscellaneous",
        lang_sec     = "Settings / Language",
        lang_btn     = "Language: EN  (switch TH)",
        eggs_title   = "Eggs",
        eggs_info    = "Auto Collect Eggs",
        sel_egg_name = "Select Egg (Name)",
        sel_method   = "Select Method",
        sel_weight   = "Select Weight",
        sel_size     = "Select Size",
        auto_place   = "Auto Place Eggs",
        sel_place_eg = "Select Egg to Place (Name)",
        auto_hatch   = "Auto Hatch Eggs",
        auto_luck    = "Auto Hatch Luck",
        pets_title   = "Pets",
        auto_feed    = "Auto Feed Best Pet",
        sel_food     = "Select Foods",
        auto_sell    = "Auto Sell Pets",
        sel_sell_rar = "Select Sell Rarity",
        auto_sell_eggs   = "Auto Sell Eggs",
        sel_sell_egg     = "Select Eggs to Sell (Name)",
        sel_sell_egg_rar = "Select Egg Rarity to Sell",
        utility      = "Utility",
        util_info    = "Auto Rebirth & etc+",
        auto_rebirth = "Smart Auto Rebirth",
        smart_rebirth_info = "Checks cash, steals egg, hatches & rebirths",
        auto_claim   = "Auto Claim Index",
        auto_bestpet = "Auto Place Best Pet's",
        esp_title    = "ESP",
        esp_info     = "Eggs and other visual",
        esp_eggs     = "ESP Eggs (World)",
        sel_esp_rar  = "Select Rarity Eggs",
        esp_placed   = "ESP Placed Eggs (Garden)",
        hud_fps      = "FPS",
        hud_ping     = "Ping",
        -- Round 2 Features
        auto_coins   = "Auto Collect Coins",
        auto_rewards = "Auto Claim Free Rewards (Group/Event/Index)",
        auto_smart_p = "Smart Place Best Pets",
        pickup_weak  = "Pickup All Placed Pets",
        tp_plot_btn  = "Teleport to Plot",
        min_reserve  = "Min Cash Reserve (For Luck)",
        auto_nest    = "Auto Unlock Nests (1-5)",
        anti_void    = "Anti-Void Protection",
        protect_mut  = "Protect Mutation Pets from Sell",
        auto_buy_food= "Auto Buy Foods (Shop)",
        sel_buy_food = "Select Foods to Buy",
        auto_feed_p  = "Auto Feed Pets (By Priority)",
        dash_toggle  = "Toggle Monitoring Dashboard",
        dash_title   = "MONITORING RADAR",
        dash_best_egg= "Highest Value Egg / Pet",
        dash_coins   = "Coins (Cash)",
        dash_rebirth = "Rebirths",
        dash_eggs    = "Placed Eggs",
        dash_pets    = "Placed Pets",
        dash_session = "Session Time",
        -- Round 3 Features
        sel_sell_pet = "Select Pets to Sell (Name)",
        gears_title  = "Gears",
        gears_info   = "Auto buy radars & gears (Auto Restock)",
        auto_buy_gear= "Auto Buy Gears",
        sel_buy_gear = "Select Gears to Buy",
        cfg_sec      = "Config & Webhook",
        save_btn     = "Save Config",
        load_btn     = "Load Config",
        auto_save    = "Auto Save",
        cfg_name_box = "Config Profile Name",
        save_named_btn = "Save Config (By Name)",
        cfg_select_drop = "Select Config to Load",
        load_selected_btn = "Load Config (Selected)",
        delete_selected_btn = "Delete Config (Selected)",
        refresh_cfg_btn = "Refresh Config List",
        webhook_box  = "Discord Webhook URL",
        webhook_tog  = "Enable Discord Webhook",
        webhook_test = "Send Test Webhook",
        particle_tog = "Enable Decor Particles",
        particle_drop= "Festival & Season Theme",
        -- New Features (Update & Events)
        bypass_staging  = "Egg Delivery (AC Staging Bypass)",
        fusion_title    = "Pet Fusion Machine",
        auto_fusion     = "Auto Pet Fusion",
        sel_fusion_rar  = "Min Fusion Rarity",
        sel_fusion_mode = "Fusion Mode Strategy",
        auto_volcano    = "Auto Volcano Magma Dip",
        -- Halloween Event Suite
        hw_title           = "Halloween Event Suite",
        hw_info            = "Auto Candy, Doors, Pumpkins & Eggs",
        auto_hw_candy      = "Auto Collect & Deposit Candy",
        auto_hw_candy_info = "Teleport collect candies & deposit at drop-off zone",
        auto_hw_doors      = "Auto Knock Doors (Trick or Treat)",
        auto_hw_doors_info = "Knock on 6 houses automatically when lights are on",
        auto_hw_pumpkins   = "Auto Search Patch Pumpkins",
        auto_hw_pump_info  = "Search all pumpkins in patch for bonus candy",
        auto_hw_buy_egg    = "Auto Buy Halloween Egg (350 Candy)",
        auto_hw_buy_info   = "Automatically buy Halloween Egg when 350 Candies reached",
        hw_tp_island_btn   = "Teleport to Halloween Island",
        hw_tp_plot_btn     = "Return to Plot",
    },
}

local function T(key)
    return (i18n[LANG] and i18n[LANG][key]) or (i18n.EN[key]) or key
end

local function set_language(targetLang)
    if targetLang ~= "TH" and targetLang ~= "EN" then
        targetLang = (LANG == "TH") and "EN" or "TH"
    end
    LANG = targetLang

    -- 1. Build bidirectional translation dictionary from i18n tables
    local wordMap = {}
    local fromDict = (LANG == "EN") and i18n.TH or i18n.EN
    local toDict   = (LANG == "EN") and i18n.EN or i18n.TH

    for k, fromText in pairs(fromDict) do
        local toText = toDict[k]
        if toText and fromText ~= toText then
            wordMap[fromText] = toText
        end
    end

    -- Headers, descriptions and special UI labels
    local extraMap = (LANG == "EN") and {
        ["ไข่ (1/7)"] = "Eggs (1/7)",
        ["สัตว์เลี้ยง (2/7)"] = "Pets (2/7)",
        ["อุปกรณ์ (3/7)"] = "Gears (3/7)",
        ["ยูทิลิตี้ (4/7)"] = "Utility (4/7)",
        ["ESP (5/7)"] = "ESP (5/7)",
        ["ฮาโลวีน (6/7)"] = "Halloween (6/7)",
        ["การตั้งค่า & Webhook (7/7)"] = "Config & Webhook (7/7)",
        ["ตั้งค่า / Language"] = "Settings / Language",
        ["สลับภาษา / Switch Language (TH / EN)"] = "Switch Language (TH / EN)",
        ["คลิกสวิตช์ หรือกดปุ่มด้านในเพื่อสลับภาษา (TH / EN)"] = "Toggle switch or click button below to switch language (TH / EN)",
        ["ระบบดูแลอาหารและซื้อของอัตโนมัติ"] = "Auto care foods and buy from shop",
        ["ขายสัตว์และไข่ที่ร้าน Richie (ล็อก Mutation อัตโนมัติ)"] = "Sell pets and eggs at Richie (Mutation locked)",
        ["คำนวณและสลับวางสัตว์เลี้ยงที่ทำเงินสูงสุด"] = "Calculate and place best earning pets",
        ["เหรียญและของขวัญฟรี"] = "Coins & Free Rewards",
        ["เก็บเหรียญสัตว์เลี้ยง และรับของขวัญอัตโนมัติ"] = "Auto collect pet coins & free gifts",
        ["ระบบบ้านและความปลอดภัย"] = "Plot & Safety System",
        ["ปลดล็อกรัง, กันตกแมพ, วาร์ปกลับบ้าน"] = "Unlock nest, Anti-void, Teleport plot",
        ["บันทึกการตั้งค่า & Webhook"] = "Save Settings & Webhook",
        ["Save, Load & Discord Webhook"] = "Save, Load & Discord Webhook",
        ["แสดงเอฟเฟกต์ตามเทศกาลหรือฤดูกาล (5 Seasons & Festivals)"] = "Show effects by festival or season",
        ["กระจายไข่ลงแปลงในสวนอัตโนมัติ (ไม่ซ้อนกัน)"] = "Auto spread eggs into garden (No stack)",
        ["ฟักไข่ในแปลงและรังทันทีที่พร้อม"] = "Hatch eggs in plot and nests when ready",
        ["โหลด Config ล่าสุดอัตโนมัติเมื่อเริ่มเกม (Auto Load on Start)"] = "Auto Load latest Config on Start",
        ["ชื่อ Config (Profile Name)"] = "Config Profile Name",
        ["เลือก Config ที่ต้องการโหลด"] = "Select Config to Load",
        ["ภาษา: ไทย  (สลับ EN)"] = "Language: EN  (switch TH)",
        ["ภาษา: ไทย (สลับ EN)"] = "Language: EN (switch TH)",
        ["เครื่องผสมพันธุ์ (Pet Fusion)"] = "Pet Fusion Machine",
        ["ผสมพันธุ์สัตว์อัตโนมัติ (Auto Pet Fusion)"] = "Auto Pet Fusion",
        ["ระบบผสมพันธุ์สัตว์เลี้ยงอัตโนมัติ"] = "Auto fuse 4 pets into higher tiers",
        ["ความหายากขั้นต่ำที่จะผสม"] = "Min Fusion Rarity",
        ["โหมดการผสม (Strategy)"] = "Fusion Mode Strategy",
        ["จุ่มลาวา Magma อัตโนมัติ (Volcano)"] = "Auto Volcano Magma Dip",
        ["ระบบบายพาส AC ส่งไข่ (Staging Bypass)"] = "Egg Delivery (AC Staging Bypass)",
        ["กิจกรรมฮาโลวีน (Halloween Event)"] = "Halloween Event Suite",
        ["เก็บแคนดี้ • เคาะประตู • ฟักทอง • ซื้อไข่"] = "Auto Candy, Doors, Pumpkins & Eggs",
        ["เก็บแคนดี้ & ส่งกระเป๋าอัตโนมัติ (Auto Candy)"] = "Auto Collect & Deposit Candy",
        ["วาร์ปเก็บลูกอมและหม้อ Ritual รอบเกาะฮาโลวีนแล้วบินส่งที่ Drop-off อัตโนมัติ"] = "Teleport collect candies & deposit at drop-off zone",
        ["เคาะประตู Trick or Treat อัตโนมัติ"] = "Auto Knock Doors (Trick or Treat)",
        ["เคาะประตูบ้าน 6 หลังวนลูปรับลูกอมตามรอบคูลดาวน์"] = "Knock on 6 houses automatically when lights are on",
        ["ค้นหาฟักทองในแปลงอัตโนมัติ (Pumpkins)"] = "Auto Search Patch Pumpkins",
        ["วาร์ปไปเปิดค้นหาฟักทองในแปลงเพื่อรับลูกอม"] = "Search all pumpkins in patch for bonus candy",
        ["ซื้อไข่ฮาโลวีนอัตโนมัติ (350 Candy)"] = "Auto Buy Halloween Egg (350 Candy)",
        ["ซื้อ Halloween Egg ทันทีเมื่อมียอด Candy ถึง 350"] = "Automatically buy Halloween Egg when 350 Candies reached",
        ["วาร์ปไปเกาะฮาโลวีน (Go to Island)"] = "Teleport to Halloween Island",
        ["วาร์ปกลับบ้าน (Return to Plot)"] = "Return to Plot",
    } or {
        ["Eggs (1/7)"] = "ไข่ (1/7)",
        ["Pets (2/7)"] = "สัตว์เลี้ยง (2/7)",
        ["Gears (3/7)"] = "อุปกรณ์ (3/7)",
        ["Utility (4/7)"] = "ยูทิลิตี้ (4/7)",
        ["ESP (5/7)"] = "ESP (5/7)",
        ["Halloween (6/7)"] = "ฮาโลวีน (6/7)",
        ["Config & Webhook (7/7)"] = "การตั้งค่า & Webhook (7/7)",
        ["Settings / Language"] = "ตั้งค่า / Language",
        ["Switch Language (TH / EN)"] = "สลับภาษา / Switch Language (TH / EN)",
        ["Toggle switch or click button below to switch language (TH / EN)"] = "คลิกสวิตช์ หรือกดปุ่มด้านในเพื่อสลับภาษา (TH / EN)",
        ["Auto care foods and buy from shop"] = "ระบบดูแลอาหารและซื้อของอัตโนมัติ",
        ["Sell pets and eggs at Richie (Mutation locked)"] = "ขายสัตว์และไข่ที่ร้าน Richie (ล็อก Mutation อัตโนมัติ)",
        ["Calculate and place best earning pets"] = "คำนวณและสลับวางสัตว์เลี้ยงที่ทำเงินสูงสุด",
        ["Coins & Free Rewards"] = "เหรียญและของขวัญฟรี",
        ["Auto collect pet coins & free gifts"] = "เก็บเหรียญสัตว์เลี้ยง และรับของขวัญอัตโนมัติ",
        ["Plot & Safety System"] = "ระบบบ้านและความปลอดภัย",
        ["Unlock nest, Anti-void, Teleport plot"] = "ปลดล็อกรัง, กันตกแมพ, วาร์ปกลับบ้าน",
        ["Save Settings & Webhook"] = "บันทึกการตั้งค่า & Webhook",
        ["Save, Load & Discord Webhook"] = "Save, Load & Discord Webhook",
        ["Show effects by festival or season"] = "แสดงเอฟเฟกต์ตามเทศกาลหรือฤดูกาล (5 Seasons & Festivals)",
        ["Auto spread eggs into garden (No stack)"] = "กระจายไข่ลงแปลงในสวนอัตโนมัติ (ไม่ซ้อนกัน)",
        ["Hatch eggs in plot and nests when ready"] = "ฟักไข่ในแปลงและรังทันทีที่พร้อม",
        ["Auto Load latest Config on Start"] = "โหลด Config ล่าสุดอัตโนมัติเมื่อเริ่มเกม (Auto Load on Start)",
        ["Config Profile Name"] = "ชื่อ Config (Profile Name)",
        ["Select Config to Load"] = "เลือก Config ที่ต้องการโหลด",
        ["Language: EN  (switch TH)"] = "ภาษา: ไทย  (สลับ EN)",
        ["Language: EN (switch TH)"] = "ภาษา: ไทย (สลับ EN)",
        ["Pet Fusion Machine"] = "เครื่องผสมพันธุ์ (Pet Fusion)",
        ["Auto Pet Fusion"] = "ผสมพันธุ์สัตว์อัตโนมัติ (Auto Pet Fusion)",
        ["Auto fuse 4 pets into higher tiers"] = "ระบบผสมพันธุ์สัตว์เลี้ยงอัตโนมัติ",
        ["Min Fusion Rarity"] = "ความหายากขั้นต่ำที่จะผสม",
        ["Fusion Mode Strategy"] = "โหมดการผสม (Strategy)",
        ["Auto Volcano Magma Dip"] = "จุ่มลาวา Magma อัตโนมัติ (Volcano)",
        ["Egg Delivery (AC Staging Bypass)"] = "ระบบบายพาส AC ส่งไข่ (Staging Bypass)",
        ["Halloween Event Suite"] = "กิจกรรมฮาโลวีน (Halloween Event)",
        ["Auto Candy, Doors, Pumpkins & Eggs"] = "เก็บแคนดี้ • เคาะประตู • ฟักทอง • ซื้อไข่",
        ["Auto Collect & Deposit Candy"] = "เก็บแคนดี้ & ส่งกระเป๋าอัตโนมัติ (Auto Candy)",
        ["Teleport collect candies & deposit at drop-off zone"] = "วาร์ปเก็บลูกอมและหม้อ Ritual รอบเกาะฮาโลวีนแล้วบินส่งที่ Drop-off อัตโนมัติ",
        ["Auto Knock Doors (Trick or Treat)"] = "เคาะประตู Trick or Treat อัตโนมัติ",
        ["Knock on 6 houses automatically when lights are on"] = "เคาะประตูบ้าน 6 หลังวนลูปรับลูกอมตามรอบคูลดาวน์",
        ["Auto Search Patch Pumpkins"] = "ค้นหาฟักทองในแปลงอัตโนมัติ (Pumpkins)",
        ["Search all pumpkins in patch for bonus candy"] = "วาร์ปไปเปิดค้นหาฟักทองในแปลงเพื่อรับลูกอม",
        ["Auto Buy Halloween Egg (350 Candy)"] = "ซื้อไข่ฮาโลวีนอัตโนมัติ (350 Candy)",
        ["Automatically buy Halloween Egg when 350 Candies reached"] = "ซื้อ Halloween Egg ทันทีเมื่อมียอด Candy ถึง 350",
        ["Teleport to Halloween Island"] = "วาร์ปไปเกาะฮาโลวีน (Go to Island)",
        ["Return to Plot"] = "วาร์ปกลับบ้าน (Return to Plot)",
    }

    for k, v in pairs(extraMap) do
        wordMap[k] = v
    end

    -- 2. Traverse GUI trees and translate
    local function translateContainer(container)
        if not container then return end
        for _, desc in ipairs(container:GetDescendants()) do
            if desc:IsA("TextLabel") or desc:IsA("TextButton") then
                local current = desc.Text
                local trimmed = current:match("^%s*(.-)%s*$") or current
                if wordMap[trimmed] then
                    desc.Text = wordMap[trimmed]
                else
                    -- Match icons prefix e.g. "💾 บันทึก Config (ตามชื่อที่ตั้ง)"
                    local icon, core = trimmed:match("^([%s%p\240-\244\128-\191]+)%s*(.+)$")
                    if core and wordMap[core] then
                        desc.Text = icon .. " " .. wordMap[core]
                    end
                end
            end
        end
    end

    pcall(function()
        local CoreGui = game:GetService("CoreGui")
        for _, g in ipairs(CoreGui:GetChildren()) do
            if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                translateContainer(g["@main"])
            end
        end
        local PlayerGui = LocalPlayer:FindFirstChild("PlayerGui")
        if PlayerGui then
            for _, g in ipairs(PlayerGui:GetChildren()) do
                if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                    translateContainer(g["@main"])
                end
            end
        end
    end)

    -- 3. Update HUD and Dashboard
    if StatsLabel then
        StatsLabel.Text = T("hud_fps") .. ": -- | " .. T("hud_ping") .. ": --"
    end

    -- 4. Sync language toggle switch if exists
    pcall(function()
        if UI_CONTROLS and UI_CONTROLS["lang_toggle"] then
            UI_CONTROLS["lang_toggle"]:Set(LANG == "EN")
        end
    end)

    -- 5. Show notification
    game:GetService("StarterGui"):SetCore("SendNotification", {
        Title    = (LANG == "TH" and "ภาษา / Language" or "Language / ภาษา"),
        Text     = (LANG == "TH" and "เปลี่ยนเป็นภาษาไทยเรียบร้อยแล้ว" or "Switched to English successfully!"),
        Duration = 2.5,
    })
end

_G.RideAPet_SetLanguage = set_language

-- ─── Modules ─────────────────────────────────────────────────

local Eggs        = require(ReplicatedStorage.GameData.Eggs)
local Rebirth     = require(ReplicatedStorage.GameData.Rebirths)
local General     = require(ReplicatedStorage.GameData.General)
local PetRenderer = nil
pcall(function()
    if getloadedmodules then
        for _, m in ipairs(getloadedmodules()) do
            if m.Name == "PetRenderer" then
                PetRenderer = require(m)
                break
            end
        end
    end
end)
if not PetRenderer then
    pcall(function()
        PetRenderer = require(LocalPlayer.PlayerScripts.Game.Pets.PetRenderer)
    end)
end
local DayNight    = require(ReplicatedStorage.GameServices.DayNight)
local PetAging    = require(ReplicatedStorage.GameServices.PetAging)
local Food        = require(ReplicatedStorage.GameData.Foods)
local Pets        = require(ReplicatedStorage.GameData.Pets)
local ShopData    = require(ReplicatedStorage.GameData.Shop)

local Dialogue = ReplicatedStorage:WaitForChild("Dialogue")

-- ─── PAYOMBØYZ CORE: EGG TRANSIT TRACKER & DELIVERY GATE ──────
local PBZ_TRANSIT = {
    pickup_pos = nil,
    pickup_time = 0,
    gate_open = true,
}

pcall(function()
    local function hook_basket(b)
        if b and b.Name == "Basket" then
            b.ChildAdded:Connect(function(child)
                PBZ_TRANSIT.pickup_time = os.clock()
                local char = LocalPlayer.Character
                local hrp = char and char:FindFirstChild("HumanoidRootPart")
                if hrp then
                    PBZ_TRANSIT.pickup_pos = hrp.Position
                end
            end)
        end
    end
    if LocalPlayer and LocalPlayer:FindFirstChild("Basket") then
        hook_basket(LocalPlayer.Basket)
    end
    if LocalPlayer then
        LocalPlayer.ChildAdded:Connect(hook_basket)
    end
end)

-- Gate EggDeliveryRules.Contains so BreakTimer NEVER fires EggArrivalClaim before safe duration
pcall(function()
    local EggDeliveryRules = require(ReplicatedStorage.GameServices.EggDeliveryRules)
    local raw_contains = EggDeliveryRules.Contains
    EggDeliveryRules.Contains = function(bp, pos)
        if PBZ_TRANSIT.gate_open == false then
            return false
        end
        if LocalPlayer and LocalPlayer:GetAttribute("InHalloweenZone") == true then
            return false
        end
        return raw_contains(bp, pos)
    end
end)

-- Shield hook on __namecall for EggArrivalClaim
pcall(function()
    local raw_namecall
    raw_namecall = hookmetamethod(game, "__namecall", newcclosure(function(self, ...)
        local method = getnamecallmethod()
        if method == "FireServer" and self and self.Name == "EggArrivalClaim" then
            if PBZ_TRANSIT.gate_open == false then
                return
            end
            if LocalPlayer and LocalPlayer:GetAttribute("InHalloweenZone") == true then
                return
            end
        end
        return raw_namecall(self, ...)
    end))
end)


-- ─── Rarity Hierarchy & Data Helpers ─────────────────────────

local RARITY_ORDER = {
    ["Common"]    = 1,
    ["Rare"]      = 2,
    ["Epic"]      = 3,
    ["Legendary"] = 4,
    ["Mythic"]    = 5,
    ["Divine"]    = 6,
    ["Ethereal"]  = 7,
    ["Secret"]    = 8,
}

local RARITY_COLORS = {
    ["Common"]    = Color3.fromRGB(185, 185, 185),
    ["Rare"]      = Color3.fromRGB(60, 160, 255),
    ["Epic"]      = Color3.fromRGB(180, 70, 255),
    ["Legendary"] = Color3.fromRGB(255, 175, 20),
    ["Mythic"]    = Color3.fromRGB(255, 55, 85),
    ["Divine"]    = Color3.fromRGB(0, 255, 210),
    ["Ethereal"]  = Color3.fromRGB(255, 235, 60),
    ["Secret"]    = Color3.fromRGB(255, 30, 75),
}

-- Returns sorted list of "EggName [Rarity]" sorted strictly by RARITY!
local function get_egg_names_with_rarity()
    local list = {}
    for name, data in pairs(Eggs) do
        table.insert(list, name .. " [" .. (data.Rarity or "Common") .. "]")
    end
    table.sort(list, function(a, b)
        local rarA = a:match("%[(.-)%]") or ""
        local rarB = b:match("%[(.-)%]") or ""
        local orderA = RARITY_ORDER[rarA] or 99
        local orderB = RARITY_ORDER[rarB] or 99
        if orderA ~= orderB then
            return orderA < orderB
        end
        return a < b
    end)
    return list
end

-- Unique rarity list strictly ordered Common -> Secret
local function get_rarities()
    return {"Common", "Rare", "Epic", "Legendary", "Mythic", "Divine", "Ethereal", "Secret"}
end

-- Returns sorted list of "PetName [Rarity]" sorted strictly by RARITY!
local function get_pet_names_with_rarity()
    local list = {}
    for name, data in pairs(Pets) do
        table.insert(list, name .. " [" .. (data.Rarity or "Common") .. "]")
    end
    table.sort(list, function(a, b)
        local rarA = a:match("%[(.-)%]") or ""
        local rarB = b:match("%[(.-)%]") or ""
        local orderA = RARITY_ORDER[rarA] or 99
        local orderB = RARITY_ORDER[rarB] or 99
        if orderA ~= orderB then
            return orderA < orderB
        end
        return a < b
    end)
    return list
end

-- Returns list of Gears in shop sorted by rarity
local function get_gear_names_with_rarity()
    return {
        "Advanced Radar [Rare]",
        "Jewel Radar [Epic]",
        "Royal Radar [Legendary]",
        "Magic Radar [Mythic]",
        "Angelic Radar [Divine]",
        "Eternal Radar [Ethereal]",
        "Name Tag [Ethereal]",
    }
end

-- Strip "[Rarity]" suffix → clean egg / pet name
local function clean_egg_name(raw)
    if not raw then return "" end
    return (tostring(raw):match("^(.-)%s*%[") or tostring(raw)):match("^%s*(.-)%s*$")
end

-- Rarity from raw egg key in Eggs table
local function get_pets_rarity(name)
    if not name then return "Common" end
    local clean = clean_egg_name(name)
    local data = Eggs[clean] or Eggs[name]
    if data and data.Rarity then return data.Rarity end
    for i, v in pairs(Eggs) do
        if i == clean or i == name then return v.Rarity end
    end
    return "Common"
end

-- Rarity from pet name in Pets table
local function get_rarity_from_pet_name(name)
    if not name then return "Common" end
    local bracketRar = tostring(name):match("%[([^%]]+)%]")
    if bracketRar and RARITY_ORDER[bracketRar] then
        return bracketRar
    end
    local clean = clean_egg_name(name)
    local data = Pets[clean] or Pets[name]
    if data and data.Rarity then return data.Rarity end
    for i, v in pairs(Pets) do
        if i == clean or i == name then return v.Rarity end
    end
    for pName, pData in pairs(Pets) do
        if clean:lower():find(pName:lower(), 1, true) or pName:lower():find(clean:lower(), 1, true) then
            if pData and pData.Rarity then return pData.Rarity end
        end
    end
    return "Common"
end

-- Check if egg name matches selection list (supports "Name [Rarity]" entries)
local function egg_name_in_list(egg_name, selection)
    if not selection or type(selection) ~= "table" or #selection == 0 then
        return false
    end
    local cleanTarget = clean_egg_name(egg_name)
    for _, sel in ipairs(selection) do
        if clean_egg_name(sel) == cleanTarget then return true end
    end
    return false
end

-- Pet image asset for ESP billboard
local function get_pet_image_id(egg_name)
    if not egg_name then return nil end
    local clean = clean_egg_name(egg_name)
    local data  = Eggs[clean] or Eggs[egg_name]
    if data then
        if data.Image and data.Image ~= "" then return tostring(data.Image) end
        if data.Thumbnail and data.Thumbnail ~= "" then return tostring(data.Thumbnail) end

        local pets_list = data.Pets
        if pets_list and #pets_list > 0 then
            local petData = Pets and (Pets[pets_list[1]] or Pets[clean_egg_name(pets_list[1])])
            if petData then
                if petData.Image and petData.Image ~= "" then return tostring(petData.Image) end
                if petData.Thumbnail and petData.Thumbnail ~= "" then return tostring(petData.Thumbnail) end
                if petData.Icon and petData.Icon ~= "" then return tostring(petData.Icon) end
            end
        end
    end
    -- Fallback to direct Pet match
    if Pets and (Pets[clean] or Pets[egg_name]) then
        local pData = Pets[clean] or Pets[egg_name]
        if pData.Image and pData.Image ~= "" then return tostring(pData.Image) end
        if pData.Thumbnail and pData.Thumbnail ~= "" then return tostring(pData.Thumbnail) end
        if pData.Icon and pData.Icon ~= "" then return tostring(pData.Icon) end
    end
    return nil
end

-- ─── Egg Valuation & Scoring ─────────────────────────────────
local RARITY_SCORE = {
    ["Common"]    = 10,
    ["Rare"]      = 60,
    ["Epic"]      = 300,
    ["Legendary"] = 1800,
    ["Mythic"]    = 12000,
    ["Divine"]    = 75000,
    ["Ethereal"]  = 350000,
    ["Secret"]    = 1500000,
}

local REBIRTH_EGG_MAP = {
    ["Horse"]   = {"Asteroid Egg", "Skull Egg", "Dominus Egg", "Crystal Egg", "Diamond Egg", "Flaming Egg", "Tidal Egg"},
    ["Fox"]     = {"Soul Egg", "Sinister Egg", "Tidal Egg", "Bloom Egg"},
    ["Unicorn"] = {"Cherub Egg", "Solaris Egg", "Blackhole Egg", "Bloom Egg", "Aurora Egg"},
    ["Phoenix"] = {"Dragon Egg", "Cherub Egg", "Solaris Egg", "Volcanic Egg", "Aurora Egg"},
    ["Kitsune"] = {"Dragon Egg", "Cherub Egg", "Volcanic Egg", "Giant Egg"},
    ["Dragon"]  = {"Dragon Egg", "Cherub Egg", "Volcanic Egg", "Giant Egg", "Solaris Egg"},
}

local function calculate_egg_score(eggName, weight, mutation, spawnSize, nextRebirthPet)
    local clean = clean_egg_name(eggName or "")
    local rarity = get_pets_rarity(clean) or "Common"
    local baseScore = RARITY_SCORE[rarity] or 10

    local w = tonumber(weight) or 1
    local sz = tonumber(spawnSize) or 1
    local sizeMultiplier = math.max(0.5, w * sz)

    local mutBonus = 0
    if mutation and mutation ~= "" and mutation ~= "None" then
        if mutation == "Rainbow" then mutBonus = 180000
        elseif mutation == "Haunted" then mutBonus = 160000
        elseif mutation == "Radiant" then mutBonus = 120000
        elseif mutation == "Volted" then mutBonus = 70000
        elseif mutation == "Shocked" then mutBonus = 35000
        else mutBonus = 20000 end
    end

    local rebirthBonus = 0
    if nextRebirthPet and REBIRTH_EGG_MAP and REBIRTH_EGG_MAP[nextRebirthPet] then
        for _, mappedEgg in ipairs(REBIRTH_EGG_MAP[nextRebirthPet]) do
            if clean_egg_name(mappedEgg) == clean then
                rebirthBonus = 500000 -- Top priority for rebirth requirement!
                break
            end
        end
    end

    return math.floor((baseScore * sizeMultiplier) + mutBonus + rebirthBonus)
end

-- ─── Automation State Variables & Config ──────────────────────
system_busy                = false
was_night_cached           = false

-- Page 1: Eggs & Hatching
auto_collect_eggs_func        = false
select_rarity_eggs_func       = {}
select_method_eggs_func       = "Teleport"
select_weight_eggs_func_min   = 1
select_weight_eggs_func_max   = 2
select_size_eggs_func_min     = 1
select_size_eggs_func_max     = 3
auto_place_eggs_func          = true
select_rarity_place_eggs_func = {}
auto_hatch_eggs_func          = true
auto_hatch_luck_func          = true
min_cash_reserve_val          = 1000
staging_bypass_enabled        = true

-- Page 2: Pets & Food
auto_pets_func                = true
auto_feed_best_pet_func       = true
select_food_func              = {"Grass"}
auto_feed_priority_func       = true
auto_buy_food_func            = false
select_buy_food_func          = {"Grass"}
protect_mutation_func         = true
auto_sell_pets_func           = false
select_pet_sell_func          = {}
select_rarity_sell_func       = {}
auto_sell_eggs_func           = false
select_egg_sell_func          = {}
select_egg_rarity_sell_func   = {}
auto_smart_place_func         = true
smart_cull_keep_top40_func    = true
auto_fusion_func              = false
fusion_min_rarity             = "Legendary"
fusion_mode                   = "Duplicate Pets Only (ตัวซ้ำ)"

-- Page 3: Gears
auto_buy_gear_func            = false
select_buy_gear_func          = {"Royal Radar", "Jewel Radar"}

-- Page 4: Utility
auto_rebirth_func             = true
auto_collect_coins_func       = true
auto_rewards_func             = true
auto_claim_index_func         = true
auto_unlock_nest_func         = true
anti_void_func                = true
auto_volcano_dip_func         = false

-- Page 5: ESP & Visuals
esp_eggs                      = true
select_esp_rarity             = {"Common", "Rare", "Epic", "Legendary", "Mythic", "Divine", "Ethereal"}
esp_placed_eggs               = true
dash_visible                  = false

-- Page 6: Halloween Event
auto_halloween_suite          = false
auto_halloween_candy          = false
auto_halloween_doors          = false
auto_halloween_pumpkins       = false
auto_buy_halloween_egg        = false
select_hw_exchange_item       = "Halloween Egg (350 Candy)"

-- Page 7: Settings & Multi-Profile Config
particle_enabled              = true
particle_theme_setting        = "Auto (ตามปฏิทินจริง)"
auto_save_enabled             = true
auto_load_on_start            = true
webhook_url                   = ""
webhook_enabled               = false
session_start_time            = tick()

CONFIG_DIR                    = "RideAPet_Configs"
LEGACY_CONFIG_FILE            = "RideAPet_PayomConfig.json"
selected_config_profile       = "default"
new_config_profile_name       = "default"
UI_CONTROLS                   = {}
config_dropdown_ctrl          = nil

local HttpService                   = game:GetService("HttpService")

local function sync_ui(key, val)
    local ctrl = UI_CONTROLS[key]
    if ctrl and val ~= nil then
        pcall(function()
            if ctrl.Set then
                ctrl:Set(val)
            elseif ctrl.SetValue then
                ctrl:SetValue(val)
            end
        end)
    end
    if key == "auto_collect_eggs_func" and UI_CONTROLS["qEgg"] and UI_CONTROLS["qEggStroke"] then
        pcall(function()
            local btn = UI_CONTROLS["qEgg"]
            local strk = UI_CONTROLS["qEggStroke"]
            if val then
                btn.BackgroundColor3 = Color3.fromRGB(30, 80, 50)
                strk.Color = Color3.fromRGB(76, 238, 133)
            else
                btn.BackgroundColor3 = Color3.fromRGB(18, 24, 38)
                strk.Color = Color3.fromRGB(255, 36, 66)
            end
        end)
    end
end

local function sync_range(key, val1, val2)
    local ctrl = UI_CONTROLS[key]
    if not ctrl then return end
    pcall(function()
        if type(val1) == "table" then
            if ctrl.SetValue then ctrl:SetValue(val1) end
            if ctrl.Set then ctrl:Set(val1[1], val1[2]) end
        elseif val1 ~= nil and val2 ~= nil then
            if ctrl.SetValue then ctrl:SetValue({val1, val2}) end
            if ctrl.Set then ctrl:Set(val1, val2) end
        elseif val1 ~= nil then
            if ctrl.SetValue then ctrl:SetValue({val1, val1}) end
            if ctrl.Set then ctrl:Set(val1, val1) end
        end
    end)
end

local EGG_TIER_ORDER = RARITY_ORDER

local function get_pet_power(inst)
    if not inst then return 0 end
    local petName = inst:GetAttribute("PetName") or inst.Name:match("^(%a+)") or inst.Name
    local weight = tonumber(inst:GetAttribute("Weight")) or 10
    local mutation = inst:GetAttribute("Mutation")
    
    local baseInc = 10
    if Pets and Pets[petName] then
        baseInc = tonumber(Pets[petName].Income) or 10
    end
    
    local mutMult = 1
    if mutation == "Shocked" then mutMult = 2
    elseif mutation == "Volted" then mutMult = 3
    elseif mutation == "Radiant" then mutMult = 4
    elseif mutation == "Rainbow" then mutMult = 5
    end
    
    return math.floor(baseInc * (weight / 10) * mutMult)
end

-- ─── Core Utilities ──────────────────────────────────────────

local press_ui = function(btn)
    for _, event in {"Activated","MouseButton1Click","MouseButton1Down","MouseButton1Up"} do
        pcall(function()
            for _, con in getconnections(btn[event]) do con:Fire() end
        end)
    end
end

local is_carries_eggs = function()
    local b = LocalPlayer and LocalPlayer:FindFirstChild("Basket")
    return b ~= nil and #b:GetChildren() > 0
end

local safe_move_root = function(targetCF)
    local char = LocalPlayer.Character
    if not char then return end
    local hrp  = char:FindFirstChild("HumanoidRootPart") or char.PrimaryPart
    local hum  = char:FindFirstChildOfClass("Humanoid")
    if not hrp then return end

    -- 1. Seated on pet / seat: move seat assembly directly to preserve SeatWeld
    if hum and hum.SeatPart then
        local seat = hum.SeatPart
        local rootPart = seat.AssemblyRootPart or seat
        pcall(function()
            rootPart.AssemblyLinearVelocity  = Vector3.zero
            rootPart.AssemblyAngularVelocity = Vector3.zero
            rootPart.CFrame = targetCF
        end)
        return
    end

    -- 2. Mounted pet joint attached to character root
    local joint = hrp:FindFirstChild("PetMountJoint")
    if joint and joint.Part1 and joint.Part1.Parent then
        local petModel = joint.Part1.Parent
        if petModel:IsA("Model") and petModel.PrimaryPart then
            pcall(function()
                petModel.PrimaryPart.AssemblyLinearVelocity  = Vector3.zero
                petModel.PrimaryPart.AssemblyAngularVelocity = Vector3.zero
            end)
        end
    end

    -- 3. Default root movement
    hrp.AssemblyLinearVelocity  = Vector3.zero
    hrp.AssemblyAngularVelocity = Vector3.zero
    hrp.CFrame = targetCF
end

local teleport = function(cframe)
    safe_move_root(cframe)
end

local stop_tween = function()
    if go_tween then go_tween:Cancel(); go_tween = nil end
    noclip_enabled = false
    local char  = LocalPlayer.Character
    local ppart = char and char.PrimaryPart
    if ppart then
        ppart.AssemblyLinearVelocity  = Vector3.zero
        ppart.AssemblyAngularVelocity = Vector3.zero
    end
end

local tween_to = function(target, speed)
    stop_tween()
    local char  = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hrp   = char and (char.PrimaryPart or char:FindFirstChild("HumanoidRootPart"))
    local hum   = char and char:FindFirstChildOfClass("Humanoid")
    if not hrp then return end

    -- If sitting on a pet seat, tween the seat assembly so player stays mounted smoothly
    local tweenPart = hrp
    if hum and hum.SeatPart then
        tweenPart = hum.SeatPart.AssemblyRootPart or hum.SeatPart
    end

    tweenPart.AssemblyLinearVelocity  = Vector3.zero
    tweenPart.AssemblyAngularVelocity = Vector3.zero
    local dist   = (target.Position - tweenPart.Position).Magnitude
    -- Safe clamp: never clamp duration below dist / 220 to avoid speed AC flags!
    local dur    = math.max(dist / (speed or 220), 0.5)
    local result = TweenService:Create(
        tweenPart,
        TweenInfo.new(dur, Enum.EasingStyle.Linear),
        {CFrame = target}
    )
    go_tween = result
    noclip_enabled = true
    result:Play()

    local elapsed = 0
    while elapsed < dur and go_tween == result and _G.RideAPet_Session == CURRENT_SESSION_ID do
        task.wait(0.05)
        elapsed = elapsed + 0.05
    end

    stop_tween()
    safe_move_root(target)
end

local get_my_plot = function()
    local plots = workspace:FindFirstChild("Plots")
    if not plots then return nil end
    for _, v in ipairs(plots:GetChildren()) do
        if v:GetAttribute("NestsOwnerLoaded") == LocalPlayer.UserId
        or (v:FindFirstChild("Data") and v.Data:FindFirstChild("Owner") and v.Data.Owner.Value == LocalPlayer)
        or v:GetAttribute("Owner") == LocalPlayer.Name then
            return v
        end
    end
    return nil
end

-- ─── PAYOMBØYZ AC ANTI-TELEPORT & BREAK TIMER BYPASS ─────────
local EGG_BREAK_TIMERS = {
    ["Common"]    = 20,
    ["Ethereal"]  = 21,
    ["Rare"]      = 25,
    ["Divine"]    = 27,
    ["Legendary"] = 30,
    ["Mythic"]    = 30,
    ["Epic"]      = 35,
}

local function get_egg_break_lifetime(eggName)
    local clean = clean_egg_name(eggName or "")
    local rarity = get_pets_rarity(clean) or "Common"
    return EGG_BREAK_TIMERS[rarity] or 20
end

local function get_basket_soonest_break()
    local basket = LocalPlayer and LocalPlayer:FindFirstChild("Basket")
    if not basket then return nil end
    local serverTimeNow = workspace:GetServerTimeNow()
    local minLeft = nil
    for _, item in ipairs(basket:GetChildren()) do
        local breakAt = tonumber(item:GetAttribute("BreakAt"))
        if breakAt and serverTimeNow < breakAt + 0.5 then
            local left = breakAt - serverTimeNow
            if not minLeft or left < minLeft then
                minLeft = left
            end
        end
    end
    return minLeft
end

local is_player_riding = function()
    if LocalPlayer:GetAttribute("IsRiding") == true then
        return true
    end
    local char = LocalPlayer.Character
    if char then
        local root = char:FindFirstChild("HumanoidRootPart")
        if root and root:FindFirstChild("PetMountJoint") then
            return true
        end
        local hum = char:FindFirstChildOfClass("Humanoid")
        if hum and hum.Sit then
            return true
        end
    end
    return false
end

local function get_effective_transit_speed()
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    local ws = hum and hum.WalkSpeed or 16
    if not is_player_riding() then
        return math.clamp(ws * 0.9, 14, 25)
    end
    -- Mounted on pet (Kitsune / Cerberus / etc.): 90% of actual mount WalkSpeed
    return math.clamp(ws * 0.9, 80, 240)
end

local get_plot_delivery_cframe = function(plot)
    plot = plot or get_my_plot()
    if not plot then return nil end
    local baseplate = plot:FindFirstChild("Baseplate")
    if baseplate and baseplate:IsA("BasePart") then
        -- Inside the ranch on baseplate
        return baseplate.CFrame * CFrame.new(0, 3.5, 0)
    end
    return plot:GetPivot() * CFrame.new(0, 4, 0)
end
local get_plot_staging_cframe = function(plot)
    plot = plot or get_my_plot()
    if not plot then return nil end
    local baseplate = plot:FindFirstChild("Baseplate")
    if baseplate and baseplate:IsA("BasePart") then
        -- 25 studs beyond baseplate width: strictly outside fence & EggDeliveryRules.Contains
        local halfX = baseplate.Size.X / 2
        return baseplate.CFrame * CFrame.new(halfX + 25, 3.5, 0)
    end
    return plot:GetPivot() * CFrame.new(75, 4, 0)
end

local safe_deliver_carried_eggs = function(explicitPos, explicitTime)
    local plot = get_my_plot()
    if not plot then return false end
    local baseplate = plot:FindFirstChild("Baseplate")
    local stagingCF = get_plot_staging_cframe(plot)
    local deliveryCF = get_plot_delivery_cframe(plot)
    if not stagingCF or not deliveryCF then return false end

    local char = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hrp then return false end

    -- 1. Close delivery gate: prevents BreakTimer from firing EggArrivalClaim prematurely!
    PBZ_TRANSIT.gate_open = false

    -- 2. Teleport to safe staging perimeter outside plot baseplate bounds
    stop_tween()
    safe_move_root(stagingCF)
    task.wait(0.15)

    -- 3. Calculate dynamic safe transit duration based on mount speed & distance
    local pPos = explicitPos or PBZ_TRANSIT.pickup_pos or hrp.Position
    local pTime = explicitTime or PBZ_TRANSIT.pickup_time
    if not pTime or pTime == 0 then pTime = os.clock() end

    local bpPos = baseplate and baseplate.Position or deliveryCF.Position
    local dist = (bpPos - pPos).Magnitude
    local safeSpeed = get_effective_transit_speed()
    local reqDuration = math.max(1.8, dist / safeSpeed)

    -- 4. Stand safely outside plot boundary until full transit duration has elapsed
    local waitLeft = math.max(0, reqDuration - (os.clock() - pTime))
    while waitLeft > 0 and _G.RideAPet_Session == CURRENT_SESSION_ID and is_carries_eggs() do
        local step = math.min(waitLeft, 0.1)
        task.wait(step)
        waitLeft = math.max(0, reqDuration - (os.clock() - pTime))
    end

    -- 5. Open delivery gate & step onto plot baseplate: BreakTimer now detects arrival legitimately!
    PBZ_TRANSIT.gate_open = true
    task.wait(0.05)
    safe_move_root(deliveryCF)

    -- 6. Wait for basket to convert into backpack tools
    local deliveryStart = os.clock()
    repeat
        task.wait(0.1)
    until not is_carries_eggs() or (os.clock() - deliveryStart > 3.5) or _G.RideAPet_Session ~= CURRENT_SESSION_ID

    PBZ_TRANSIT.gate_open = true
    return true
end

-- ─── Halloween Cauldron Staging & Delivery Bypass ───────────────
local HW_CAULDRON_STAGING_CF  = CFrame.new(-45804.9, 40371.5, -20118.0)
local HW_CAULDRON_DELIVERY_CF = CFrame.new(-45839.9, 40371.5, -20118.0)

local has_carried_candy = function()
    local noSave = LocalPlayer:FindFirstChild("NoSaveData")
    local carried = noSave and noSave:FindFirstChild("CarriedCandy")
    return carried ~= nil and carried:IsA("IntValue") and carried.Value > 0
end

local safe_deliver_carried_candy = function(explicitPos, explicitTime)
    if not has_carried_candy() then return true end

    local char = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hrp then return false end

    -- 1. Teleport to safe staging perimeter strictly outside the cauldron drop zone
    stop_tween()
    safe_move_root(HW_CAULDRON_STAGING_CF)
    task.wait(0.15)

    -- 2. Calculate dynamic safe transit duration based on mount speed & distance
    local pPos = explicitPos or hrp.Position
    local pTime = explicitTime or os.clock()
    local dist = (HW_CAULDRON_DELIVERY_CF.Position - pPos).Magnitude
    local safeSpeed = get_effective_transit_speed()
    local reqDuration = math.max(2.2, dist / safeSpeed)

    -- 3. Stand safely outside cauldron boundary until full transit duration has elapsed
    local waitLeft = math.max(0, reqDuration - (os.clock() - pTime))
    while waitLeft > 0 and _G.RideAPet_Session == CURRENT_SESSION_ID and has_carried_candy() do
        local step = math.min(waitLeft, 0.1)
        task.wait(step)
        waitLeft = math.max(0, reqDuration - (os.clock() - pTime))
    end

    -- 4. Step onto Cauldron Pad to trigger server deposit
    safe_move_root(HW_CAULDRON_DELIVERY_CF)

    -- 5. Wait for CarriedCandy to clear (server deposit acknowledgment)
    local depositStart = os.clock()
    repeat
        task.wait(0.1)
    until not has_carried_candy() or (os.clock() - depositStart > 3.0) or _G.RideAPet_Session ~= CURRENT_SESSION_ID

    -- 6. Step back to safe staging perimeter
    safe_move_root(HW_CAULDRON_STAGING_CF)
    task.wait(0.2)
    return true
end

local teleport_to_plot = function()
    local plot = get_my_plot()
    if not plot then return end
    local targetCF = get_plot_delivery_cframe(plot) or (plot:GetPivot() + Vector3.new(0, 4, 0))

    if is_carries_eggs() then
        safe_deliver_carried_eggs()
    else
        pcall(function()
            local tpRemote = Remotes.Game:FindFirstChild("TeleportToPlot")
            if tpRemote then tpRemote:FireServer() end
            safe_move_root(targetCF)
        end)
    end
end

local pickup_egg = function(uid, prompt)
    if prompt and typeof(fireproximityprompt) == "function" then
        pcall(function() fireproximityprompt(prompt) end)
        pcall(function() fireproximityprompt(prompt, prompt.HoldDuration or 0.2) end)
    end
    if uid then
        pcall(function() Game.EggPickup:FireServer(uid) end)
    end
end

local is_spawn_size_in_range = function(spawn_size)
    if typeof(spawn_size) ~= "Vector3" then return true end
    return spawn_size.X >= select_size_eggs_func_min and spawn_size.X <= select_size_eggs_func_max
       and spawn_size.Y >= select_size_eggs_func_min and spawn_size.Y <= select_size_eggs_func_max
       and spawn_size.Z >= select_size_eggs_func_min and spawn_size.Z <= select_size_eggs_func_max
end

local get_empty_nest = function(plot)
    if not plot then return nil, nil end
    local nests = plot:FindFirstChild("Nests")
    if nests then
        for i = 1, 5 do
            local nest = nests:FindFirstChild(tostring(i))
            if nest then
                local isUnlocked = (nest:GetAttribute("Unlocked") == true) or (tostring(i) == "1")
                local isOccupied = (nest:GetAttribute("Occupied") == true)
                if isUnlocked and not isOccupied then
                    local model = nest:FindFirstChild("Model")
                    local part = model and model:FindFirstChildWhichIsA("BasePart") or nest:FindFirstChildWhichIsA("BasePart", true)
                    if part then
                        return nest, part
                    end
                end
            end
        end
    end
    return nil, nil
end

local deposit_egg_in_nest = function(nest, nestPart, specificTool)
    if not nest then return false end
    local char = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hum  = char and char:FindFirstChildOfClass("Humanoid")
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hum or not hrp then return false end

    if nestPart then
        safe_move_root(nestPart.CFrame + Vector3.new(0, 2.5, 0))
        task.wait(0.15)
    end

    local eggTool = specificTool or char:FindFirstChildOfClass("Tool")
    if not eggTool or not (eggTool:HasTag("Egg") or eggTool.Name:lower():find("egg")) then
        for _, t in ipairs(LocalPlayer.Backpack:GetChildren()) do
            if t:IsA("Tool") and (t:HasTag("Egg") or t.Name:lower():find("egg") or Eggs[clean_egg_name(t.Name)]) then
                eggTool = t
                break
            end
        end
    end

    if eggTool and eggTool.Parent == LocalPlayer.Backpack then
        hum:EquipTool(eggTool)
        task.wait(0.15)
    end

    pcall(function()
        Game.EggPlaced:FireServer({ NestId = tostring(nest.Name) })
    end)

    pcall(function()
        for _, desc in ipairs(nest:GetDescendants()) do
            if desc:IsA("ProximityPrompt") then
                pcall(fireproximityprompt, desc, 0)
            end
        end
    end)

    task.wait(0.2)
    pcall(function() hum:UnequipTools() end)
    return true
end

-- ─── Rebirth & Pet Requirement Brain ─────────────────────────

local smart_rebirth_busy = false

local has_required_pet = function()
    local required = General.RebirthRequirements
    local name = required[math.clamp(LocalPlayer.SavedData.Rebirths.Value + 1, 1, #required)]

    pcall(function()
        local uiPet = LocalPlayer.PlayerGui.Main.Rebirth.Segment2.pEThOLDER.PetName.Text
        if uiPet and uiPet ~= "" and uiPet ~= "?" and uiPet ~= "???" then
            name = uiPet
        end
    end)

    -- Check SavedData.OwnedPets string
    pcall(function()
        local owned = tostring(LocalPlayer.SavedData.OwnedPets.Value)
        if string.find(owned, name) then
            return true, name
        end
    end)

    -- Check Plot Pets
    local plot = get_my_plot()
    if plot and plot:FindFirstChild("Pets") then
        for _, p in plot.Pets:GetChildren() do
            if p.Name == name or p:GetAttribute("PetName") == name then
                return true, name
            end
        end
    end

    -- Check PetRenderer
    if PetRenderer and PetRenderer.GetAll then
        for _, v in PetRenderer.GetAll() do
            if v.OwnerUserId == LocalPlayer.UserId and v.Model and v.Model.Parent and v.Model.Name == name then
                return true, name
            end
        end
    end

    local function scan(x)
        if not x then return false end
        for _, v in x:GetChildren() do
            if v:IsA("Tool") and v:GetAttribute("PetKey") then
                if (v.Name:match("^(.-) %[") or v.Name) == name then return true end
            end
        end
    end

    if scan(LocalPlayer:FindFirstChildOfClass("Backpack")) or scan(LocalPlayer.Character) then
        return true, name
    end

    local root  = LocalPlayer.Character and LocalPlayer.Character.PrimaryPart
    local joint = root and root:FindFirstChild("PetMountJoint")
    local model = joint and joint.Part1 and joint.Part1.Parent
    return model and (model:GetAttribute("PetName") == name or model.Name == name) or false, name
end

-- ─── Auto Mount Best Pet Engine (Speed & Power Optimizer) ────
local is_player_riding = function()
    if LocalPlayer:GetAttribute("IsRiding") == true then
        return true
    end
    local char = LocalPlayer.Character
    if char then
        local root = char:FindFirstChild("HumanoidRootPart")
        if root and root:FindFirstChild("PetMountJoint") then
            return true
        end
        local hum = char:FindFirstChildOfClass("Humanoid")
        if hum and hum.Sit then
            return true
        end
    end
    return false
end

local safe_dismount = function()
    pcall(function()
        local dismountRemote = Remotes.Game:FindFirstChild("PetDismount")
        if dismountRemote then
            dismountRemote:FireServer()
        end
        local char = LocalPlayer.Character
        local hum = char and char:FindFirstChildOfClass("Humanoid")
        if hum then hum.Sit = false end
    end)
    task.wait(0.2)
end

local mount_best_pet_on_plot = function()
    if is_player_riding() then return true end
    local plot = get_my_plot()
    if not plot or not plot:FindFirstChild("Pets") then return false end

    local pets = plot.Pets:GetChildren()
    if #pets == 0 then return false end

    local bestPet = nil
    local maxSpeed = -1
    for _, p in ipairs(pets) do
        local spd = 0
        if p:FindFirstChild("Data") and p.Data:FindFirstChild("Speed") then
            spd = tonumber(p.Data.Speed.Value) or 0
        end
        if spd == 0 then
            spd = tonumber(p:GetAttribute("Speed")) or 0
        end
        if spd > maxSpeed then
            maxSpeed = spd
            bestPet = p
        end
    end

    if not bestPet then return false end

    local char = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hum  = char and char:FindFirstChildOfClass("Humanoid")
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hrp or not hum then return false end

    -- Move within interaction proximity of best pet if distant
    if (bestPet:GetPivot().Position - hrp.Position).Magnitude > 80 then
        safe_move_root(bestPet:GetPivot() * CFrame.new(0, 3, 3))
        task.wait(0.2)
    end

    -- 1. Direct ProximityPrompt (Keeps pet on plot so backpack stays clean!)
    local targetPrompt = bestPet:FindFirstChild("RidePrompt", true)
    if not targetPrompt then
        for _, desc in ipairs(bestPet:GetDescendants()) do
            if desc:IsA("ProximityPrompt") and (desc.Name == "RidePrompt" or desc.ActionText:lower():find("ride")) then
                targetPrompt = desc
                break
            end
        end
    end

    if targetPrompt then
        safe_move_root(bestPet:GetPivot() * CFrame.new(0, 1.5, 2.5))
        task.wait(0.15)

        targetPrompt.Enabled = true
        targetPrompt.RequiresLineOfSight = false
        targetPrompt.MaxActivationDistance = 50

        pcall(function()
            if typeof(fireproximityprompt) == "function" then
                fireproximityprompt(targetPrompt)
            else
                targetPrompt:InputHoldBegin()
                task.wait(targetPrompt.HoldDuration > 0 and targetPrompt.HoldDuration or 0.25)
                targetPrompt:InputHoldEnd()
            end
        end)

        local deadline = os.clock() + 1.2
        while os.clock() < deadline do
            if is_player_riding() then return true end
            task.wait(0.1)
        end
    end

    -- 2. Fallback: Server Remote Mount
    local petKey = bestPet:GetAttribute("PetKey")
    local PickupPetRemote = Remotes.Game:FindFirstChild("PickupPet")
    local MountingRemote = Remotes.Game:FindFirstChild("Mounting")

    if petKey and PickupPetRemote and MountingRemote then
        PickupPetRemote:FireServer(petKey)
        local deadline = os.clock() + 2.0
        local petTool = nil
        while os.clock() < deadline do
            for _, tool in ipairs(LocalPlayer.Backpack:GetChildren()) do
                if tool:GetAttribute("PetKey") == petKey or tool.Name == bestPet.Name then
                    petTool = tool
                    break
                end
            end
            if petTool then break end
            task.wait(0.08)
        end
        if petTool and hum.Parent then
            hum:EquipTool(petTool)
            task.wait(0.12)
            MountingRemote:FireServer()
            task.wait(0.35)
            if is_player_riding() then return true end
        end
    end

    return is_player_riding()
end

-- ─── Auto Collect (High-Priority Heist Engine) ───────────────

local collect_egg = function()
    if not auto_collect_eggs_func or system_busy or smart_rebirth_busy then return end
    local char = LocalPlayer.Character
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    -- Lock system immediately so NO background tasks can clash during heist planning or execution!
    system_busy = true
    _system_busy_start = os.clock()

    -- Verify player is riding best pet before commencing egg theft
    if not is_player_riding() then
        pcall(mount_best_pet_on_plot)
        task.wait(0.2)
    end

    -- Check if next rebirth tier requires a specific pet
    local hasPet, neededPetName = has_required_pet()
    local neededPet = (not hasPet) and neededPetName or nil

    -- Gather candidates from RenderedEggs first
    local candidates = {}
    local rendered = workspace:FindFirstChild("RenderedEggs")
    local activeEggs = ReplicatedStorage:FindFirstChild("ServerData") and ReplicatedStorage.ServerData:FindFirstChild("ActiveEggs")
    
    local myPlot = get_my_plot()
    local plotPos = myPlot and myPlot:GetPivot().Position or hrp.Position
    local effSpeed = get_effective_transit_speed()

    if rendered then
        for _, egg in ipairs(rendered:GetChildren()) do
            local egg_name = egg.Name
            local hasStealFilter = type(select_rarity_eggs_func) == "table" and #select_rarity_eggs_func > 0
            local name_ok = (not hasStealFilter) or egg_name_in_list(clean, select_rarity_eggs_func)
            if name_ok then
                local part = egg:FindFirstChild("EggBase") or egg:FindFirstChildWhichIsA("BasePart") or egg.PrimaryPart
                local prompt = egg:FindFirstChildWhichIsA("ProximityPrompt", true)
                if part then
                    local dist = (part.Position - hrp.Position).Magnitude
                    local plotDist = (part.Position - plotPos).Magnitude
                    local weight = tonumber(egg:GetAttribute("Weight")) or 1
                    local mutation = egg:GetAttribute("Mutation")
                    local spawnSize = tonumber(egg:GetAttribute("SpawnSize")) or 1
                    local score = calculate_egg_score(clean, weight, mutation, spawnSize, neededPet)

                    -- Reachability scoring: penalize eggs unreachable before break timer expires
                    local lifetime = get_egg_break_lifetime(clean)
                    local maxReachDist = math.max(300, (lifetime - 2.5) * effSpeed)
                    if plotDist > maxReachDist then
                        score = score - 35000
                    end

                    table.insert(candidates, {
                        egg = egg,
                        part = part,
                        prompt = prompt,
                        pos = part.Position,
                        dist = dist,
                        name = clean,
                        score = score
                    })
                end
            end
        end
    end

    -- If none found in RenderedEggs, fallback to ServerData.ActiveEggs
    if #candidates == 0 and activeEggs then
        for _, v in ipairs(activeEggs:GetChildren()) do
            local egg_name = v:GetAttribute("Egg")
            local pos = v:GetAttribute("Position")
            local weight = v:GetAttribute("Weight")
            local spawn_size = v:GetAttribute("SpawnSize")
            local mutation = v:GetAttribute("Mutation")
            local clean = clean_egg_name(egg_name or "")
            local hasStealFilter = type(select_rarity_eggs_func) == "table" and #select_rarity_eggs_func > 0
            local name_ok = (not hasStealFilter) or egg_name_in_list(clean, select_rarity_eggs_func)

            if v:IsA("Configuration") and name_ok and pos
            and (not weight or (weight >= select_weight_eggs_func_min and weight <= select_weight_eggs_func_max))
            and is_spawn_size_in_range(spawn_size) then
                local dist = (pos - hrp.Position).Magnitude
                local plotDist = (pos - plotPos).Magnitude
                local score = calculate_egg_score(clean, weight, mutation, spawn_size, neededPet)

                -- Reachability scoring: penalize eggs unreachable before break timer expires
                local lifetime = get_egg_break_lifetime(clean)
                local maxReachDist = math.max(300, (lifetime - 2.5) * effSpeed)
                if plotDist > maxReachDist then
                    score = score - 35000
                end

                table.insert(candidates, {
                    activeConfig = v,
                    pos = pos,
                    dist = dist,
                    name = clean,
                    uid = v.Name,
                    score = score
                })
            end
        end
    end

    if #candidates == 0 then
        system_busy = false
        _system_busy_start = 0
        return
    end

    -- Sort candidates by Score (highest value/rarity/size first, rebirth egg prioritized), distance tie-break
    table.sort(candidates, function(a, b)
        if a.score ~= b.score then
            return a.score > b.score
        end
        return a.dist < b.dist
    end)
    local target = candidates[1]
    local targetCF = CFrame.new(target.pos + Vector3.new(0, 2.5, 0))
    if select_method_eggs_func == "Tween" then
        tween_to(targetCF, 320)
    else
        teleport(targetCF)
    end
    task.wait(0.2)

    -- Attempt pickup
    local uid = target.uid
    if not uid and activeEggs and target.pos then
        for _, act in ipairs(activeEggs:GetChildren()) do
            local actPos = act:GetAttribute("Position")
            if actPos and (actPos - target.pos).Magnitude < 15 then
                uid = act.Name
                break
            end
        end
    end

    local pickupSuccess = false
    local pickupPos = target.pos
    local pickupTime = os.clock()

    for try = 1, 5 do
        if not auto_collect_eggs_func or _G.RideAPet_Session ~= CURRENT_SESSION_ID then break end
        pickup_egg(uid, target.prompt)
        task.wait(0.2)
        if is_carries_eggs() then
            pickupSuccess = true
            pickupTime = os.clock()
            PBZ_TRANSIT.pickup_time = pickupTime
            PBZ_TRANSIT.pickup_pos = pickupPos
            break
        end
    end

    -- Return safely home to plot via staging bypass
    if is_carries_eggs() then
        safe_deliver_carried_eggs(pickupPos, pickupTime)
        task.wait(0.2)
    else
        pcall(teleport_to_plot)
        task.wait(0.2)
    end

    -- Deposit egg immediately into empty nest or place on plot so basket is freed
    local plot = get_my_plot()
    if plot then
        local nest, nestPart = get_empty_nest(plot)
        if nest and nestPart then
            deposit_egg_in_nest(nest, nestPart)
            task.wait(0.3)
        end
    end

    pcall(teleport_to_plot)
    task.wait(0.2)
    system_busy = false
    _system_busy_start = 0
end

local smart_rebirth = function()
    if not auto_rebirth_func or smart_rebirth_busy then return end

    local my_rebirths = tonumber(LocalPlayer.SavedData.Rebirths.Value) or 0
    if my_rebirths >= (Rebirth.Cap or 6) then return end

    local next_cost = tonumber(Rebirth.GetCost(my_rebirths)) or 0
    local my_cash   = tonumber(LocalPlayer.SavedData.Cash.Value) or 0

    -- Check pet requirement first!
    local owned, target_pet = has_required_pet()

    -- [BRANCH 1] Has required pet -> If cash is ready, EXECUTE REBIRTH!
    if owned then
        if my_cash >= next_cost then
            Game.Rebirth:FireServer()
            pcall(function()
                game:GetService("StarterGui"):SetCore("SendNotification", {
                    Title    = "🔄 Auto Rebirth",
                    Text     = string.format("🎉 Rebirth สำเร็จ! ขึ้นสู่ระดับ %d", my_rebirths + 1),
                    Duration = 4,
                })
            end)
            task.wait(1.5)
        end
        return
    end

    -- [BRANCH 2] Does NOT have pet -> Work on candidate eggs in advance!
    local candidate_eggs = REBIRTH_EGG_MAP[target_pet] or {"Soul Egg", "Sinister Egg", "Asteroid Egg"}
    local plot = get_my_plot()

    -- 2A. Is egg already placed in plot / nests?
    local placed_egg = nil
    if plot and plot:FindFirstChild("Eggs") then
        for _, e in plot.Eggs:GetChildren() do
            if table.find(candidate_eggs, e.Name) then
                placed_egg = e
                break
            end
        end
    end
    if not placed_egg and plot and plot:FindFirstChild("Nests") then
        for _, nest in plot.Nests:GetChildren() do
            for _, c in nest:GetChildren() do
                if table.find(candidate_eggs, c.Name) then
                    placed_egg = c
                    break
                end
            end
        end
    end

    if placed_egg then
        local key = placed_egg:GetAttribute("EggKey")
        if key then
            Game.Hatch:FireServer({EggKey = key})
        end
        pcall(hatch_eggs)
        return
    end

    -- 2B. Is egg in Backpack or Character?
    local egg_in_bag = nil
    for _, t in LocalPlayer.Backpack:GetChildren() do
        if t:IsA("Tool") and table.find(candidate_eggs, clean_egg_name(t.Name)) then
            egg_in_bag = t
            break
        end
    end
    if not egg_in_bag and LocalPlayer.Character then
        for _, t in LocalPlayer.Character:GetChildren() do
            if t:IsA("Tool") and table.find(candidate_eggs, clean_egg_name(t.Name)) then
                egg_in_bag = t
                break
            end
        end
    end

    if egg_in_bag then
        if is_eggs_limit() then
            -- Free up slot by hatching ready eggs on plot
            pcall(hatch_eggs)
            task.wait(0.4)
        end
        if not is_eggs_limit() then
            local cf = get_free_pos(egg_in_bag)
            if cf then
                smart_rebirth_busy = true
                system_busy = true
                pcall(function() place(egg_in_bag, cf) end)
                smart_rebirth_busy = false
                system_busy = false
            end
        end
        return
    end

    -- 2C. Egg not in plot and not in bag -> Steal/collect from world
    -- Rule: Max 2 eggs in basket (dj requirement)
    local basketCount = #LocalPlayer.Basket:GetChildren()
    if basketCount >= 2 then
        teleport_to_plot()
        return
    end

    local target_egg_obj = nil
    local bestDist = 1e9
    local plot = get_my_plot()
    local plotPos = plot and plot:GetPivot().Position or Vector3.zero
    local effSpeed = get_effective_transit_speed()
    for _, candName in ipairs(candidate_eggs) do
        local lifetime = get_egg_break_lifetime(candName)
        local maxReachDist = math.max(300, (lifetime - 2.5) * effSpeed)
        for _, activeEgg in ipairs(ReplicatedStorage.ServerData.ActiveEggs:GetChildren()) do
            if activeEgg:GetAttribute("Egg") == candName then
                local ePos = activeEgg:GetAttribute("Position")
                if ePos then
                    local d = (ePos - plotPos).Magnitude
                    local reachable = d <= maxReachDist
                    local effectiveDist = reachable and d or (d + 20000)
                    if effectiveDist < bestDist then
                        bestDist = effectiveDist
                        target_egg_obj = activeEgg
                    end
                end
            end
        end
        if target_egg_obj then break end
    end

    if target_egg_obj then
        if not is_player_riding() then
            pcall(mount_best_pet_on_plot)
            task.wait(0.2)
        end
        smart_rebirth_busy = true
        system_busy = true

        local eggPos = target_egg_obj:GetAttribute("Position")
        if eggPos then
            if LocalPlayer:DistanceFromCharacter(eggPos) > 20 then
                if select_method_eggs_func == "Tween" then
                    tween_to(CFrame.new(eggPos), 250)
                else
                    teleport(CFrame.new(eggPos))
                end
            end
            task.wait(0.25)
            local pickupTime = os.clock()
            pickup_egg(target_egg_obj.Name)
            task.wait(0.4)

            if #LocalPlayer.Basket:GetChildren() > basketCount or #LocalPlayer.Basket:GetChildren() >= 1 then
                safe_deliver_carried_eggs(eggPos, pickupTime)
                task.wait(0.3)
            end
        end

        smart_rebirth_busy = false
        system_busy = false
    end
end

local rebirth = smart_rebirth

local cliam_index = function()
    if LocalPlayer.PlayerGui.Main.Index.PetProgress.Claim.Visible then
        return Game.ClaimIndexReward:FireServer()
    end
    return false
end

-- ─── Auto Place (spread grid + jitter) ───────────────────────

local is_eggs_limit = function()
    local my_plot = get_my_plot()
    return my_plot and #my_plot.Eggs:GetChildren() >= 10
end

local get_egg_bases = function(plot)
    local bases = {}
    for _, egg in plot.Eggs:GetChildren() do
        local base = egg:FindFirstChild("EggBase")
        if base and base:IsA("BasePart") then
            table.insert(bases, base)
        end
    end
    return bases
end

-- Wider gap + random jitter prevents egg stacking
local get_free_pos = function(tool)
    local plot   = get_my_plot()
    local origin = plot:GetPivot().Position
    local size   = tool:GetAttribute("SpawnSize") or Vector3.new(3, 3, 3)
    local gap    = 2.5  -- wider than original (was 1)
    local step   = math.max(size.X, size.Z) + gap

    local params = OverlapParams.new()
    params.FilterType = Enum.RaycastFilterType.Include
    params.FilterDescendantsInstances = get_egg_bases(plot)

    for radius = 0, 12 do
        for x = -radius, radius do
            for z = -radius, radius do
                if math.max(math.abs(x), math.abs(z)) ~= radius then continue end

                -- jitter ±0.4 studs so eggs at same grid slot spread visually
                local jx = (math.random() - 0.5) * 0.8
                local jz = (math.random() - 0.5) * 0.8

                local pos = Vector3.new(
                    origin.X + (x + jx) * step,
                    origin.Y,
                    origin.Z + (z + jz) * step
                )
                local cf  = CFrame.new(pos)
                local hit = workspace:GetPartBoundsInBox(
                    cf,
                    Vector3.new(size.X + gap, size.Y, size.Z + gap),
                    params
                )
                if #hit == 0 then return cf end
            end
        end
    end
end

local place = function(tool, cf)
    local char = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
    local hum  = char:FindFirstChildOfClass("Humanoid")
    if not hum then return end

    local eggs     = get_my_plot().Eggs
    local oldCount = #eggs:GetChildren()

    hum:EquipTool(tool)
    task.wait(0.1)

    local p = cf.Position
    Game.EggPlaced:FireServer({PlantPosition = Vector3.new(p.X, p.Y, p.Z)})
    local start = tick()
    repeat task.wait() until #eggs:GetChildren() > oldCount or tick() - start > 2
end

local get_earliest_hatch_time = function(plot)
    if not plot then return 999999 end
    local minRemaining = 999999
    for _, parentObj in ipairs({plot:FindFirstChild("Eggs"), plot:FindFirstChild("Nests")}) do
        if parentObj then
            for _, item in ipairs(parentObj:GetChildren()) do
                local rem = item:GetAttribute("TimeRemaining") or item:GetAttribute("Remaining")
                if rem and tonumber(rem) and tonumber(rem) < minRemaining then
                    minRemaining = tonumber(rem)
                end
                local handle = item:FindFirstChild("Handle")
                local hatchingUI = handle and handle:FindFirstChild("HatchingUI")
                local timerLbl = hatchingUI and hatchingUI:FindFirstChild("Timer")
                if timerLbl and timerLbl:IsA("TextLabel") and timerLbl.Visible then
                    local text = timerLbl.Text
                    local parts = string.split(text, ":")
                    if #parts == 2 then
                        local secs = (tonumber(parts[1]) or 0) * 60 + (tonumber(parts[2]) or 0)
                        if secs < minRemaining then minRemaining = secs end
                    elseif #parts == 3 then
                        local secs = (tonumber(parts[1]) or 0) * 3600 + (tonumber(parts[2]) or 0) * 60 + (tonumber(parts[3]) or 0)
                        if secs < minRemaining then minRemaining = secs end
                    end
                end
            end
        end
    end
    return minRemaining
end

local place_eggs = function()
    if system_busy then return false end
    local plot = get_my_plot()
    if not plot then return false end

    -- Check if next rebirth tier requires a specific pet
    local hasPet, neededPetName = has_required_pet()
    local neededPet = (not hasPet) and neededPetName or nil

    -- Gather and sort eggs in backpack by score (Rebirth & highest rarity first)
    local eggTools = {}
    for _, v in ipairs(LocalPlayer.Backpack:GetChildren()) do
        if v:IsA("Tool") and (v:HasTag("Egg") or v.Name:lower():find("egg") or (Eggs and Eggs[clean_egg_name(v.Name)])) then
            local hasPlaceFilter = type(select_rarity_place_eggs_func) == "table" and #select_rarity_place_eggs_func > 0
            if (not hasPlaceFilter) or egg_name_in_list(v.Name, select_rarity_place_eggs_func) then
                local clean = clean_egg_name(v.Name)
                local weight = tonumber(v:GetAttribute("Weight")) or 1
                local mut = v:GetAttribute("Mutation")
                local spawnSize = tonumber(v:GetAttribute("SpawnSize")) or 1
                local score = calculate_egg_score(clean, weight, mut, spawnSize, neededPet)
                table.insert(eggTools, {tool = v, score = score})
            end
        end
    end
    if #eggTools == 0 then return false end
    table.sort(eggTools, function(a, b) return a.score > b.score end)

    local targetTool = eggTools[1].tool

    -- 1. Check if any empty nest is available on plot first
    local nest, nestPart = get_empty_nest(plot)
    if nest and nestPart then
        system_busy = true
        deposit_egg_in_nest(nest, nestPart, targetTool)
        task.wait(0.3)
        system_busy = false
        return true
    end

    -- 2. If nests are full or no empty nest, place on garden ground (if not at plot limit of 10)
    if not is_eggs_limit() then
        local cf = get_free_pos(targetTool)
        if cf then
            system_busy = true
            local ok = pcall(function() place(targetTool, cf) end)
            task.wait(0.4)
            system_busy = false
            return ok
        end
    end

    return false
end

-- ─── Hatch ───────────────────────────────────────────────────

local hatch_eggs = function()
    if not auto_hatch_eggs_func or system_busy or is_player_riding() or is_carries_eggs() then return end
    local plot = get_my_plot()
    if not plot then return end
    local char = LocalPlayer.Character
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")

    -- Prompt and remote hatching for both Eggs and Nests
    for _, parentObj in ipairs({plot:FindFirstChild("Eggs"), plot:FindFirstChild("Nests")}) do
        if parentObj then
            for _, item in ipairs(parentObj:GetChildren()) do
                local key = item:GetAttribute("EggKey")
                local prompt = item:FindFirstChildWhichIsA("ProximityPrompt", true)
                local timerLbl = item:FindFirstChild("Timer", true)
                local isReady = (timerLbl and timerLbl:IsA("TextLabel") and timerLbl.Text == "Ready")
                                or (prompt and prompt.Enabled and (not timerLbl or timerLbl.Text == "Ready" or timerLbl.Text == ""))

                if isReady then
                    -- If character is distant, step closer safely without breaking pet seat welds
                    if hrp and (item:IsA("Model") or item:IsA("BasePart")) then
                        local itemPos = item:GetPivot().Position
                        if (itemPos - hrp.Position).Magnitude > 20 then
                            safe_move_root(item:GetPivot() * CFrame.new(0, 2.5, 2.5))
                            task.wait(0.12)
                        end
                    end

                    if prompt and prompt.Enabled then
                        pcall(fireproximityprompt, prompt, 0)
                        pcall(function()
                            if typeof(fireproximityprompt) ~= "function" then
                                prompt:InputHoldBegin()
                                task.wait(0.2)
                                prompt:InputHoldEnd()
                            end
                        end)
                        task.wait(0.08)
                    end

                    if key then
                        pcall(function() Game.Hatch:FireServer({EggKey = key}) end)
                        pcall(function() Game.Hatch:FireServer(key) end)
                    end
                end
            end
        end
    end

    pcall(function()
        local holder = LocalPlayer.PlayerGui.Main.PlotEggsTracker.Holder
        for _, v in holder:GetChildren() do
            local open = v:FindFirstChild("Open")
            if open and open.Visible then
                pcall(function() Game.Hatch:FireServer({EggKey = v.Name}) end)
                pcall(function() Game.Hatch:FireServer(v.Name) end)
            end
        end
    end)
end

local hacth_luck = function()
    local my_cash = tonumber(LocalPlayer.SavedData.Cash.Value) or 0
    if my_cash > (min_cash_reserve_val or 0) then
        return Game.Plot.Upgrades:FireServer("Max")
    end
    return false
end

-- ─── Pets ────────────────────────────────────────────────────

local get_best_pet = function()
    local best, best_speed
    local maxAge = (PetAging and PetAging.MaxAge) or 100
    for _, pet in pairs(PetRenderer.GetAll()) do
        if pet.OwnerUserId == LocalPlayer.UserId and pet.Model and pet.Model.Parent then
            local age = tonumber(pet.Model:GetAttribute("Age")) or 0
            if age < maxAge then
                local data  = pet.Model:FindFirstChild("Data")
                local speed = data and data:FindFirstChild("Speed")
                speed = speed and tonumber(speed.Value)
                if speed and (not best_speed or speed > best_speed) then
                    best = pet; best_speed = speed
                end
            end
        end
    end
    return best, best_speed
end

local get_pets_to_feed = function()
    local pets = {}
    local maxAge = (PetAging and PetAging.MaxAge) or 100
    for _, pet in pairs(PetRenderer.GetAll()) do
        if pet.OwnerUserId == LocalPlayer.UserId and pet.Model and pet.Model.Parent then
            local age = tonumber(pet.Model:GetAttribute("Age")) or 0
            if age < maxAge then
                local power = get_pet_power(pet.Model)
                table.insert(pets, { Pet = pet, Power = power, Age = age })
            end
        end
    end
    -- Sort descending: highest value / power pet fed first!
    table.sort(pets, function(a, b) return a.Power > b.Power end)
    return pets
end

local get_food = function()
    local foods = {}
    for i in Food do
        if not table.find(foods, i) then table.insert(foods, i) end
    end
    return foods
end

local having_food = function(name)
    if LocalPlayer.Backpack then
        for _, v in LocalPlayer.Backpack:GetChildren() do
            if v:IsA("Tool") and v.Name == name then return true end
        end
        return false
    end
end

local feed_best_pet = function()
    if is_carries_eggs() or is_player_riding() or system_busy or smart_rebirth_busy then return end
    local pets = get_pets_to_feed()
    if #pets == 0 then return end
    
    local foodsToFeed = {}
    for _, v in ipairs(select_food_func or {}) do
        if having_food(v) then
            local xpVal = (Food[v] and tonumber(Food[v].XP)) or 0
            table.insert(foodsToFeed, {Name = v, XP = xpVal})
        end
    end
    if #foodsToFeed == 0 then return end
    
    if auto_feed_priority_func then
        table.sort(foodsToFeed, function(a, b) return a.XP > b.XP end)
    end
    
    system_busy = true
    local maxAge = (PetAging and PetAging.MaxAge) or 100
    for _, pEntry in ipairs(pets) do
        local pet = pEntry.Pet
        for _, item in ipairs(foodsToFeed) do
            if not having_food(item.Name) or _G.RideAPet_Session ~= CURRENT_SESSION_ID then break end
            Game.FeedPet:FireServer(pet.PetKey, tostring(item.Name), true)
            task.wait(0.2)
            local currentAge = tonumber(pet.Model and pet.Model:GetAttribute("Age")) or 0
            if currentAge >= maxAge then
                break -- Max level 100 achieved! Move to next pet
            end
        end
        local anyFoodLeft = false
        for _, item in ipairs(foodsToFeed) do
            if having_food(item.Name) then anyFoodLeft = true; break end
        end
        if not anyFoodLeft then break end
    end
    system_busy = false
end

local sell_pet = function()
    if not auto_sell_pets_func or is_carries_eggs() or is_player_riding() or system_busy or smart_rebirth_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end
    local richie = workspace:FindFirstChild("Stalls") and workspace.Stalls:FindFirstChild("Sell") and workspace.Stalls.Sell:FindFirstChild("Richie")
    if not richie or not richie:FindFirstChild("HumanoidRootPart") then return end
    local prompt = richie.HumanoidRootPart:FindFirstChildWhichIsA("ProximityPrompt", true)
    local char   = LocalPlayer.Character
    local hum    = char and char:FindFirstChildOfClass("Humanoid")
    local hrp    = char and char:FindFirstChild("HumanoidRootPart")
    if not hum or not hrp or not prompt then return end

    -- Gather all pets in backpack
    local allBackpackPets = {}
    for _, v in ipairs(LocalPlayer.Backpack:GetChildren()) do
        if v:IsA("Tool") and (v:GetAttribute("PetKey") or v:HasTag("Pet") or v:GetAttribute("PetName") or Pets[v.Name:match("^(%a+)") or v.Name]) then
            local pName = v:GetAttribute("PetName") or v.Name:match("^(%a+)") or v.Name
            local mut = v:GetAttribute("Mutation")
            local power = get_pet_power(v)
            table.insert(allBackpackPets, {
                tool = v,
                name = pName,
                mutation = mut,
                power = power
            })
        end
    end

    if #allBackpackPets == 0 then return end

    -- Sort pets descending by Power (most valuable pets first)
    table.sort(allBackpackPets, function(a, b) return a.power > b.power end)

    local totalPets = #allBackpackPets
    local petsToSell = {}

    if smart_cull_keep_top40_func then
        -- Keep Top 40% best pets, ensure at least 6-8 pets kept for ranch
        local keepCount = math.max(6, math.ceil(totalPets * 0.40))
        for i = keepCount + 1, totalPets do
            local entry = allBackpackPets[i]
            if protect_mutation_func and entry.mutation and entry.mutation ~= "" and entry.mutation ~= "None" then
                continue -- Protect mutation pet
            end
            table.insert(petsToSell, entry.tool)
        end
    else
        -- Fallback to manual selection filter
        for _, entry in ipairs(allBackpackPets) do
            local pName = entry.name
            local mut = entry.mutation
            if protect_mutation_func and mut and mut ~= "" and mut ~= "None" then
                continue
            end
            local rar = get_rarity_from_pet_name(pName) or "Common"
            local tagged = pName .. " [" .. rar .. "]"
            local matchName = false
            for _, sel in ipairs(select_pet_sell_func) do
                if clean_egg_name(sel) == pName or sel == tagged then
                    matchName = true
                    break
                end
            end
            local matchRar = table.find(select_rarity_sell_func, rar)
            if matchName or matchRar then
                table.insert(petsToSell, entry.tool)
            end
        end
    end

    if #petsToSell == 0 then return end

    -- Lock system to prevent other background loops from interrupting
    system_busy = true
    stop_tween()
    hrp.AssemblyLinearVelocity = Vector3.zero
    hrp.CFrame = richie.HumanoidRootPart.CFrame * CFrame.new(0, 0, 3)
    task.wait(0.25)

    -- Hook CompleteToken listener
    local dRemotes = ReplicatedStorage:WaitForChild("Dialogue"):WaitForChild("Remotes")
    local currentToken = nil
    local tokenConn = dRemotes.DialogueUpdate.OnClientEvent:Connect(function(data)
        if type(data) == "table" and data.CompleteToken then
            currentToken = data.CompleteToken
            dRemotes.DialogueTypingDone:FireServer(data.CompleteToken)
        end
    end)

    for _, petTool in ipairs(petsToSell) do
        if not auto_sell_pets_func or _G.RideAPet_Session ~= CURRENT_SESSION_ID then break end
        if petTool and petTool.Parent == LocalPlayer.Backpack then
            hum:EquipTool(petTool)
            task.wait(0.15)
            currentToken = nil
            pcall(fireproximityprompt, prompt, 0)
            task.wait(0.15)
            pcall(function()
                dRemotes.DialogueSelect:FireServer(richie, "I would like to sell this")
            end)

            -- Wait for server CompleteToken response and receipt
            local waited = 0
            while not currentToken and waited < 0.8 do
                task.wait(0.05)
                waited = waited + 0.05
            end
            task.wait(0.1)
        end
    end

    pcall(function() tokenConn:Disconnect() end)
    pcall(function() hum:UnequipTools() end)
    task.wait(0.2)
    pcall(teleport_to_plot)
    task.wait(0.2)
    system_busy = false
end

-- ─── Egg Selling Automation Engine (Richie Merchant) ─────────────────
local sell_egg = function()
    if not auto_sell_eggs_func or system_busy or smart_rebirth_busy or is_carries_eggs() or is_player_riding() or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    local char = LocalPlayer.Character
    local hum  = char and char:FindFirstChildOfClass("Humanoid")
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hum or not hrp or hum.Health <= 0 then return end

    local backpack = LocalPlayer:FindFirstChildOfClass("Backpack")
    if not backpack then return end

    -- Check if next rebirth tier requires a specific pet
    local hasPet, neededPetName = has_required_pet()
    local neededPet = (not hasPet) and neededPetName or nil

    local hasNameFilter = type(select_egg_sell_func) == "table" and #select_egg_sell_func > 0
    local hasRarFilter  = type(select_egg_rarity_sell_func) == "table" and #select_egg_rarity_sell_func > 0

    -- If no filter specified at all, do NOT sell anything blindly!
    if not hasNameFilter and not hasRarFilter then return end

    local eggsToSell = {}
    for _, v in ipairs(backpack:GetChildren()) do
        if v:IsA("Tool") and (v:HasTag("Egg") or v.Name:lower():find("egg") or (Eggs and Eggs[clean_egg_name(v.Name)])) then
            local clean = clean_egg_name(v.Name)
            local rar = get_pets_rarity(clean) or "Common"
            local mut = v:GetAttribute("Mutation")

            -- Protect mutation eggs
            if protect_mutation_func and mut and mut ~= "" and mut ~= "None" then
                continue
            end

            -- Protect eggs needed for current rebirth
            if neededPet and REBIRTH_EGG_MAP and REBIRTH_EGG_MAP[neededPet] then
                local needed = false
                for _, mapEgg in ipairs(REBIRTH_EGG_MAP[neededPet]) do
                    if clean_egg_name(mapEgg) == clean then
                        needed = true
                        break
                    end
                end
                if needed then continue end
            end

            local matchName = false
            if hasNameFilter then
                for _, sel in ipairs(select_egg_sell_func) do
                    if clean_egg_name(sel) == clean or sel == (clean .. " [" .. rar .. "]") then
                        matchName = true
                        break
                    end
                end
            end

            local matchRar = false
            if hasRarFilter then
                matchRar = table.find(select_egg_rarity_sell_func, rar) ~= nil
            end

            if matchName or matchRar then
                table.insert(eggsToSell, v)
            end
        end
    end

    if #eggsToSell == 0 then return end

    local richie = workspace:FindFirstChild("Stalls") and workspace.Stalls:FindFirstChild("Sell") and workspace.Stalls.Sell:FindFirstChild("Richie")
    if not richie or not richie:FindFirstChild("HumanoidRootPart") then return end
    local prompt = richie.HumanoidRootPart:FindFirstChildWhichIsA("ProximityPrompt", true)
    if not prompt then return end

    system_busy = true
    stop_tween()
    hrp.AssemblyLinearVelocity = Vector3.zero
    hrp.CFrame = richie.HumanoidRootPart.CFrame * CFrame.new(0, 0, 3)
    task.wait(0.25)

    local dRemotes = ReplicatedStorage:WaitForChild("Dialogue"):WaitForChild("Remotes")
    local currentToken = nil
    local tokenConn = dRemotes.DialogueUpdate.OnClientEvent:Connect(function(data)
        if type(data) == "table" and data.CompleteToken then
            currentToken = data.CompleteToken
            dRemotes.DialogueTypingDone:FireServer(data.CompleteToken)
        end
    end)

    local sellRemote = Remotes.Game:FindFirstChild("SellItems")

    for _, eggTool in ipairs(eggsToSell) do
        if not auto_sell_eggs_func or _G.RideAPet_Session ~= CURRENT_SESSION_ID then break end
        if eggTool and eggTool.Parent == backpack then
            hum:EquipTool(eggTool)
            task.wait(0.12)
            currentToken = nil
            pcall(fireproximityprompt, prompt, 0)
            task.wait(0.12)
            pcall(function()
                dRemotes.DialogueSelect:FireServer(richie, "I would like to sell this")
            end)
            if sellRemote then
                pcall(function() sellRemote:FireServer(eggTool) end)
                pcall(function() sellRemote:FireServer({ eggTool }) end)
            end

            local waited = 0
            while not currentToken and waited < 0.6 do
                task.wait(0.05)
                waited = waited + 0.05
            end
            task.wait(0.08)
        end
    end

    pcall(function() tokenConn:Disconnect() end)
    pcall(function() hum:UnequipTools() end)
    task.wait(0.2)
    pcall(teleport_to_plot)
    task.wait(0.2)
    system_busy = false
end

local sell_excess_eggs = function()
    if auto_sell_eggs_func then
        sell_egg()
    end
end

-- ─── Pet Fusion Engine (Machine Automation) ──────────────────
local auto_fuse_pets = function()
    if not auto_fusion_func or system_busy or smart_rebirth_busy or is_carries_eggs() then return end

    local fusionSlots = LocalPlayer:FindFirstChild("FusionSlots") or LocalPlayer:WaitForChild("FusionSlots", 2)
    if not fusionSlots then return end

    local char = LocalPlayer.Character
    local hum  = char and char:FindFirstChildOfClass("Humanoid")
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hum or not hrp or hum.Health <= 0 then return end

    local status = fusionSlots:GetAttribute("FusionStatus")
    local endsAt = tonumber(fusionSlots:GetAttribute("EndsAt")) or 0
    local resultKey = fusionSlots:GetAttribute("FusionResultKey")
    local serverNow = workspace:GetServerTimeNow()

    local fusionModel = (workspace:FindFirstChild("Functionals") and workspace.Functionals:FindFirstChild("Fusion")) or workspace:FindFirstChild("Fusion")
    local fusionPart = fusionModel and (fusionModel:FindFirstChild("Floor") or fusionModel:FindFirstChild("Glass") or fusionModel.PrimaryPart or fusionModel:FindFirstChildWhichIsA("BasePart"))
    local fusionCF = fusionPart and fusionPart.CFrame or (fusionModel and fusionModel:GetPivot())

    -- 1. Claim completed fused pet
    if status == "Result" or (resultKey and resultKey ~= "") then
        system_busy = true
        if is_player_riding() then safe_dismount() end
        if fusionCF then
            safe_move_root(fusionCF * CFrame.new(0, 3, 5))
            task.wait(0.25)
        end
        pcall(function()
            Game.FusionAction:FireServer("Claim", resultKey)
        end)
        local resultPrompt = fusionModel and fusionModel:FindFirstChild("FusionResultTake", true)
        if resultPrompt and resultPrompt:IsA("ProximityPrompt") then
            pcall(fireproximityprompt, resultPrompt, 0)
        end
        task.wait(0.5)
        pcall(teleport_to_plot)
        task.wait(0.2)
        system_busy = false
        return
    end

    -- 2. Reveal when timer finished
    if status == "Waiting" then
        if serverNow >= endsAt then
            system_busy = true
            if is_player_riding() then safe_dismount() end
            if fusionCF then
                safe_move_root(fusionCF * CFrame.new(0, 3, 5))
                task.wait(0.25)
            end
            pcall(function()
                Game.FusionAction:FireServer("Fuse")
            end)
            task.wait(0.5)
            pcall(teleport_to_plot)
            task.wait(0.2)
            system_busy = false
        end
        return
    end

    -- 3. If ready for new fusion
    local currentCount = tonumber(fusionSlots:GetAttribute("Count")) or #fusionSlots:GetChildren()
    if currentCount >= 4 then
        system_busy = true
        if is_player_riding() then safe_dismount() end
        if fusionCF then
            safe_move_root(fusionCF * CFrame.new(0, 3, 5))
            task.wait(0.25)
        end
        pcall(function()
            Game.FusionAction:FireServer("Fuse")
        end)
        task.wait(0.8)
        pcall(teleport_to_plot)
        task.wait(0.2)
        system_busy = false
        return
    end

    -- Gather eligible tools from Backpack and Character
    local eligible = {}
    local minOrder = RARITY_ORDER[fusion_min_rarity] or 4
    local nameGroups = {}

    local containers = {LocalPlayer:FindFirstChildOfClass("Backpack"), LocalPlayer.Character}
    for _, container in ipairs(containers) do
        if container then
            for _, t in ipairs(container:GetChildren()) do
                if t:IsA("Tool") and (t:GetAttribute("PetKey") or t:HasTag("Pet") or t:GetAttribute("PetName") or Pets[clean_egg_name(t.Name)]) then
                    local petKey = t:GetAttribute("PetKey") or t.Name
                    local rawName = t:GetAttribute("PetName") or clean_egg_name(t.Name)
                    local mut = t:GetAttribute("Mutation")
                    local rar = t:GetAttribute("Rarity") or get_rarity_from_pet_name(t.Name) or get_rarity_from_pet_name(rawName) or "Common"
                    local rarOrder = RARITY_ORDER[rar] or 1

                    local isProtected = protect_mutation_func and (mut and mut ~= "" and mut ~= "None")
                    if not isProtected and rarOrder >= minOrder then
                        local item = {
                            tool = t,
                            key = petKey,
                            name = rawName,
                            rarity = rar,
                            rarOrder = rarOrder,
                            power = get_pet_power(t),
                        }
                        table.insert(eligible, item)
                        if not nameGroups[rawName] then nameGroups[rawName] = {} end
                        table.insert(nameGroups[rawName], item)
                    end
                end
            end
        end
    end

    local needed = 4 - currentCount
    if #eligible < needed then return end

    local toPlace = {}
    if fusion_mode and fusion_mode:find("Duplicate") then
        -- Find a group with at least 'needed' duplicates (prioritizing lowest rarity/power tier first)
        local candidateGroup = nil
        for _, group in pairs(nameGroups) do
            if #group >= needed then
                if not candidateGroup or group[1].rarOrder < candidateGroup[1].rarOrder then
                    candidateGroup = group
                end
            end
        end
        if candidateGroup then
            table.sort(candidateGroup, function(a, b) return a.power < b.power end)
            for i = 1, needed do
                table.insert(toPlace, candidateGroup[i])
            end
        end
    else
        -- Lowest power first to preserve top pets
        table.sort(eligible, function(a, b)
            if a.rarOrder ~= b.rarOrder then return a.rarOrder < b.rarOrder end
            return a.power < b.power
        end)
        for i = 1, needed do
            table.insert(toPlace, eligible[i])
        end
    end

    if #toPlace < needed then return end

    system_busy = true
    if is_player_riding() then
        safe_dismount()
    end

    if fusionCF then
        safe_move_root(fusionCF * CFrame.new(0, 3, 5))
        task.wait(0.25)
    end

    for _, item in ipairs(toPlace) do
        if not auto_fusion_func or _G.RideAPet_Session ~= CURRENT_SESSION_ID then break end
        if item.tool and (item.tool.Parent == LocalPlayer:FindFirstChildOfClass("Backpack") or item.tool.Parent == LocalPlayer.Character) then
            hum:EquipTool(item.tool)
            task.wait(0.15)
            pcall(function()
                Game.FusionPetPlace:FireServer(currentCount + 1)
            end)
            local placePrompt = fusionModel and fusionModel:FindFirstChild("FusionPetPlace", true)
            if placePrompt and placePrompt:IsA("ProximityPrompt") then
                pcall(fireproximityprompt, placePrompt, 0)
            end
            task.wait(0.25)
            currentCount = currentCount + 1
        end
    end
    pcall(function() hum:UnequipTools() end)
    task.wait(0.3)

    local updatedCount = tonumber(fusionSlots:GetAttribute("Count")) or #fusionSlots:GetChildren()
    if updatedCount >= 4 then
        pcall(function()
            Game.FusionAction:FireServer("Fuse")
        end)
        task.wait(0.8)
    end
    pcall(teleport_to_plot)
    task.wait(0.2)
    system_busy = false
end

-- ─── Volcano & Magma Mutation Engine ──────────────────────────
local last_volcano_dip_time = 0

local auto_volcano_dip = function()
    if not auto_volcano_dip_func or system_busy or smart_rebirth_busy or is_carries_eggs() or is_player_riding() then return end
    if os.clock() - last_volcano_dip_time < 30 then return end

    -- Find non-mutated high value pet to dip
    local candidateTool = nil
    for _, t in ipairs(LocalPlayer.Backpack:GetChildren()) do
        if t:IsA("Tool") and (t:GetAttribute("PetKey") or t:HasTag("Pet")) then
            local mut = t:GetAttribute("Mutation")
            if not mut or mut == "" or mut == "None" then
                candidateTool = t
                break
            end
        end
    end
    if not candidateTool then return end

    local char = LocalPlayer.Character
    local hum  = char and char:FindFirstChildOfClass("Humanoid")
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hum or not hrp then return end

    local volcano = workspace:FindFirstChild("Volcano")
    local targetPos = volcano and volcano:GetPivot().Position or Vector3.new(-3183, 31281, -12495)

    system_busy = true
    last_volcano_dip_time = os.clock()

    -- Safe teleport above volcano top
    safe_move_root(CFrame.new(targetPos + Vector3.new(0, 50, 0)))
    task.wait(0.3)

    hum:EquipTool(candidateTool)
    task.wait(0.4)

    -- Return safely
    pcall(function() hum:UnequipTools() end)
    task.wait(0.2)
    pcall(teleport_to_plot)
    task.wait(0.3)
    system_busy = false
end

-- ─── Halloween Event Automation Engine ─────────────────────────
local last_hw_doors_time    = 0
local last_hw_pumpkins_time = 0
local last_hw_candy_time    = 0
local last_hw_egg_buy_time  = 0

local run_halloween_pipeline = function()
    if not (auto_halloween_suite or auto_halloween_candy or auto_halloween_doors or auto_halloween_pumpkins or auto_buy_halloween_egg) then return end
    if auto_collect_eggs_func then
        auto_collect_eggs_func = false
        sync_ui("auto_collect_eggs_func", false)
        stop_tween()
        noclip_enabled = false
    end
    if system_busy or smart_rebirth_busy or is_carries_eggs() or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    local char = LocalPlayer.Character
    local hrp  = char and char:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    system_busy = true
    _system_busy_start = os.clock()

    local ok, _ = pcall(function()
        -- 1. Ensure Player is in Halloween Zone
        local inZone = LocalPlayer:GetAttribute("InHalloweenZone") == true
        if not inZone then
            local cs = game:GetService("CollectionService")
            local portal = cs:GetTagged("HalloweenPortal")[1]
            local prompt = portal and portal:FindFirstChildWhichIsA("ProximityPrompt", true)
            if portal and prompt then
                safe_move_root(portal.CFrame + Vector3.new(0, 3, 0))
                task.wait(0.2)
                if typeof(fireproximityprompt) == "function" then
                    pcall(function() fireproximityprompt(prompt, prompt.HoldDuration or 0.2) end)
                end
                task.wait(0.4)
            end
            if LocalPlayer:GetAttribute("InHalloweenZone") ~= true then
                safe_move_root(CFrame.new(-46040.8, 40377.5, -20327.3))
                task.wait(0.4)
            end
            if LocalPlayer:GetAttribute("InHalloweenZone") ~= true then
                return
            end
        end

        -- Check & deliver any existing carried candy via Staging Bypass first
        if has_carried_candy() then
            safe_deliver_carried_candy(hrp.Position, os.clock() - 2.5)
        end

        -- 2. Auto Buy / Exchange Halloween Item
        if auto_buy_halloween_egg and os.clock() - last_hw_egg_buy_time > 3 then
            local savedData = LocalPlayer:FindFirstChild("SavedData")
            local candyVal = savedData and savedData:FindFirstChild("HalloweenCandy")
            local choice = tostring(select_hw_exchange_item or "Halloween Egg")

            if choice:find("Headless") or choice:find("หม้อพิธีกรรม") then
                -- Contribute carried candy to ritual pot
                pcall(function()
                    local pot = workspace:FindFirstChild("RitualCandyPot", true)
                             or (workspace:FindFirstChild("Assets") and workspace.Assets:FindFirstChild("Candy") and workspace.Assets.Candy:FindFirstChild("RitualCandyPot"))
                    if pot then
                        local prompt = pot:FindFirstChildWhichIsA("ProximityPrompt", true)
                        if prompt then
                            safe_move_root(pot:GetPivot() * CFrame.new(0, 3, 2))
                            task.wait(0.2)
                            if typeof(fireproximityprompt) == "function" then
                                fireproximityprompt(prompt, prompt.HoldDuration or 0.2)
                            end
                            last_hw_egg_buy_time = os.clock()
                        end
                    end
                end)
            else
                -- Default: Halloween Egg (350 Candy Tokens)
                if candyVal and candyVal.Value >= 350 then
                    last_hw_egg_buy_time = os.clock()
                    pcall(function()
                        local buyRemote = (Remotes.Game and Remotes.Game:FindFirstChild("BuyHalloweenEgg"))
                                       or (ReplicatedStorage:FindFirstChild("Remotes") and ReplicatedStorage.Remotes.Game:FindFirstChild("BuyHalloweenEgg"))
                        if buyRemote then
                            buyRemote:InvokeServer("Halloween Egg")
                        end
                    end)
                    task.wait(0.3)
                end
            end
        end

        -- 3. Auto Knock Doors (Trick or Treat) - Smart Lit-Only Detection
        if auto_halloween_doors and os.clock() - last_hw_doors_time > 8 then
            last_hw_doors_time = os.clock()
            local litDoors = {}
            pcall(function()
                local dRemote = (Remotes.Game and Remotes.Game:FindFirstChild("GetDoorState")) or (ReplicatedStorage:FindFirstChild("Remotes") and ReplicatedStorage.Remotes.Game:FindFirstChild("GetDoorState"))
                if dRemote then
                    local ds = dRemote:InvokeServer()
                    if ds and ds.Lit then litDoors = ds.Lit end
                end
            end)

            local cs = game:GetService("CollectionService")
            local houses = cs:GetTagged("TrickOrTreatHouseModel")
            for _, house in ipairs(houses) do
                if _G.RideAPet_Session ~= CURRENT_SESSION_ID or not (auto_halloween_suite or auto_halloween_doors) then break end
                local p = house:GetPivot().Position
                local houseId = house:GetAttribute("Id") or string.format("Door_%d_%d", math.round(p.X), math.round(p.Z))

                -- เคาะเฉพาะบ้านที่มีไฟติด (Lit) ช่วยประหยัดเวลาและหลีกเลี่ยงการวาร์ปเสียเปล่า
                if litDoors[houseId] == true or (next(litDoors) == nil and house:FindFirstChildWhichIsA("ProximityPrompt", true)) then
                    local prompt = house:FindFirstChildWhichIsA("ProximityPrompt", true)
                    safe_move_root(CFrame.new(p + Vector3.new(0, 3, 4)))
                    task.wait(0.18)
                    if prompt and typeof(fireproximityprompt) == "function" then
                        pcall(function() fireproximityprompt(prompt, prompt.HoldDuration or 0.2) end)
                    end
                    pcall(function() Game.KnockDoor:FireServer(houseId) end)
                    task.wait(0.25)
                end
            end
        end

        -- 4. Auto Search Pumpkins (Patch Pumpkins) - Smart Cooldown/Rotten Filter
        if auto_halloween_pumpkins and os.clock() - last_hw_pumpkins_time > 10 then
            last_hw_pumpkins_time = os.clock()
            local pumpState = nil
            local serverNow = workspace:GetServerTimeNow()
            pcall(function()
                local pRemote = (Remotes.Game and Remotes.Game:FindFirstChild("GetPumpkinState")) or (ReplicatedStorage:FindFirstChild("Remotes") and ReplicatedStorage.Remotes.Game:FindFirstChild("GetPumpkinState"))
                if pRemote then pumpState = pRemote:InvokeServer() end
            end)

            local patch = workspace:FindFirstChild("PumpkinPatch")
            if patch then
                for _, sp in ipairs(patch:GetChildren()) do
                    if _G.RideAPet_Session ~= CURRENT_SESSION_ID or not (auto_halloween_suite or auto_halloween_pumpkins) then break end
                    if sp:IsA("BasePart") and sp.Name:find("PumpkinSpawn") then
                        local pId = sp:GetAttribute("Id") or sp.Name:gsub("PumpkinSpawn", "HalloweenPumpkin")

                        -- ตรวจสอบคูลดาวน์และสถานะเน่าจาก Server ก่อนวาร์ป
                        local isAvailable = true
                        if pumpState then
                            local respawnAt = (pumpState.RespawnAt and pumpState.RespawnAt[pId]) or 0
                            local rottenUntil = (pumpState.RottenUntil and pumpState.RottenUntil[pId]) or 0
                            if respawnAt > serverNow or rottenUntil > serverNow then
                                isAvailable = false
                            end
                        end

                        local anchor = sp:FindFirstChild("PumpkinSearchAnchor")
                        local prompt = anchor and anchor:FindFirstChild("SearchPumpkin")
                        if isAvailable and prompt and prompt.Enabled ~= false then
                            safe_move_root(CFrame.new(sp.Position + Vector3.new(0, 2.5, 0)))
                            task.wait(0.18)
                            if typeof(fireproximityprompt) == "function" then
                                pcall(function() fireproximityprompt(prompt, prompt.HoldDuration or 0.75) end)
                            end
                            pcall(function() Game.SearchPumpkin:FireServer(pId) end)
                            task.wait(0.3)
                        end
                    end
                end
            end
        end

        -- 5. Auto Collect Candies on Ground & Drop-off (Multi-spot High-Yield Cluster Farming)
        if (auto_halloween_suite or auto_halloween_candy) and os.clock() - last_hw_candy_time > 1.2 then
            last_hw_candy_time = os.clock()
            local candyFolder = workspace:FindFirstChild("HalloweenCandy")
            local cs = game:GetService("CollectionService")
            local spawns = cs:GetTagged("HalloweenCandySpawn")

            local spawnsById = {}
            for _, sp in ipairs(spawns) do
                local sId = sp:GetAttribute("Id") or sp:GetFullName()
                spawnsById[sId] = sp
            end

            -- ดึงข้อมูลยอด Candy และ Spawn จาก Server เพื่อเลือกจุดที่มีแคนดี้เยอะที่สุดก่อน
            local candyStateData = nil
            pcall(function()
                local cRemote = (Remotes.Game and Remotes.Game:FindFirstChild("GetCandyState")) or (ReplicatedStorage:FindFirstChild("Remotes") and ReplicatedStorage.Remotes.Game:FindFirstChild("GetCandyState"))
                if cRemote then candyStateData = cRemote:InvokeServer() end
            end)
            local serverAmounts = (candyStateData and candyStateData.Amounts) or {}

            local candidates = {}
            if candyFolder then
                for _, candy in ipairs(candyFolder:GetChildren()) do
                    local id = candy:GetAttribute("SpawnId") or candy:GetAttribute("Id") or candy.Name
                    local pos = candy:GetPivot().Position
                    local name = candy.Name
                    local prio = 1
                    if name:find("CandyPot") or name:find("Ritual") then prio = 6
                    elseif name:find("Candy_04") then prio = 5
                    elseif name:find("Candy_03") then prio = 4
                    elseif name:find("Candy_02") then prio = 3
                    elseif name:find("Candy_01") then prio = 2
                    end
                    local amt = tonumber(serverAmounts[id]) or 1
                    prio = prio + (amt * 2)
                    table.insert(candidates, { id = id, pos = pos, part = candy, prio = prio, amt = amt })
                end
            end
            if #candidates == 0 and #spawns > 0 then
                for _, sp in ipairs(spawns) do
                    local id = sp:GetAttribute("Id") or sp:GetFullName()
                    local amt = tonumber(serverAmounts[id]) or 1
                    if amt > 0 then
                        table.insert(candidates, { id = id, pos = sp.Position, part = sp, prio = amt, amt = amt })
                    end
                end
            end

            local myPos = hrp.Position
            table.sort(candidates, function(a, b)
                if a.prio ~= b.prio then return a.prio > b.prio end
                return (a.pos - myPos).Magnitude < (b.pos - myPos).Magnitude
            end)

            -- ฟาร์มแบบ Multi-Spot: เก็บต่อเนื่องสูงสุด 4 จุดต่อ 1 รอบ
            local MAX_HW_CANDY_BATCH = 4
            local lastPickupPos = hrp.Position
            local lastPickupTime = os.clock()

            for i = 1, math.min(#candidates, MAX_HW_CANDY_BATCH) do
                if _G.RideAPet_Session ~= CURRENT_SESSION_ID or not (auto_halloween_suite or auto_halloween_candy) then break end
                local c = candidates[i]

                local curPos = hrp.Position
                local targetCF = CFrame.new(c.pos + Vector3.new(0, 2.5, 0))
                local dist = (c.pos - curPos).Magnitude
                local effSpeed = get_effective_transit_speed()
                local safeTransitWait = math.clamp(dist / effSpeed, 0.2, 0.9)

                safe_move_root(targetCF)
                task.wait(safeTransitWait)

                local sp = spawnsById[c.id]
                local prompt = (sp and sp:FindFirstChildWhichIsA("ProximityPrompt", true)) or (c.part and c.part:FindFirstChildWhichIsA("ProximityPrompt", true))
                if prompt and typeof(fireproximityprompt) == "function" then
                    pcall(function() fireproximityprompt(prompt, prompt.HoldDuration or 0.2) end)
                    task.wait(0.12)
                end

                -- หากจุดนี้มีแคนดี้หลายเม็ด ให้ยิงเก็บซ้ำตามจำนวนที่จุดนั้นมี
                local picks = math.clamp(c.amt or 1, 1, 4)
                for _ = 1, picks do
                    pcall(function() Game.CollectCandy:FireServer(c.id) end)
                    task.wait(0.12)
                end

                lastPickupPos = c.pos
                lastPickupTime = os.clock()
            end

            -- ส่งแคนดี้ทั้งหมดที่เก็บได้ในรอบนี้ผ่านระบบ Staging Bypass เพียงครั้งเดียว ประหยัดเวลา 4-5 เท่า
            if has_carried_candy() then
                safe_deliver_carried_candy(lastPickupPos, lastPickupTime)
            end
        end
    end)

    system_busy = false
    _system_busy_start = 0
end

-- ─── Stock Verification Helper ────────────────────────────────
local function is_item_in_stock(category, itemName)
    local cleanName = clean_egg_name(itemName)
    local inStock = true
    pcall(function()
        local main = LocalPlayer.PlayerGui:FindFirstChild("Main")
        local shop = main and main:FindFirstChild("Shop")
        local holders = shop and shop:FindFirstChild("Holders")
        local catHolder = holders and holders:FindFirstChild(category)
        if catHolder then
            local itemObj = catHolder:FindFirstChild(cleanName) or catHolder:FindFirstChild(itemName)
            if itemObj then
                -- Check Stock TextLabel
                local stockLbl = itemObj:FindFirstChild("ProductExpander") and itemObj.ProductExpander:FindFirstChild("Stock")
                if stockLbl and stockLbl:IsA("TextLabel") then
                    local sText = stockLbl.Text:lower()
                    if sText:find("x0") or sText:find("no stock") or sText:find("0 stock") then
                        inStock = false
                        return
                    end
                    local count = tonumber(stockLbl.Text:match("x(%d+)"))
                    if count and count <= 0 then
                        inStock = false
                        return
                    end
                end
                -- Check Cash Payment Label
                local dollarLbl = itemObj:FindFirstChild("CashPayment") and itemObj.CashPayment:FindFirstChild("Frame") and itemObj.CashPayment.Frame:FindFirstChild("Dollar") and itemObj.CashPayment.Frame.Dollar:FindFirstChild("Label")
                if dollarLbl and dollarLbl:IsA("TextLabel") then
                    if dollarLbl.Text:upper():find("NO STOCK") then
                        inStock = false
                        return
                    end
                end
            end
        end
        -- Also check GearShop scrolling frame if category is Gears
        if category == "Gears" and main and main:FindFirstChild("GearShop") then
            local sf = main.GearShop:FindFirstChild("ScrollingFrame")
            if sf then
                local gSlot = sf:FindFirstChild(cleanName)
                if gSlot then
                    local stock = gSlot:FindFirstChild("Stock")
                    if stock and (stock.Text:find("x0") or stock.Text:lower():find("no stock")) then
                        inStock = false
                        return
                    end
                end
            end
        end
    end)
    return inStock
end

-- ─── Round 2 & 3: New Automation Functions ────────────────────

-- Auto buy food from StockShop
local auto_buy_food = function()
    if not auto_buy_food_func then return end
    local buyRemote = Remotes.Game:FindFirstChild("BuyWithCash")
    if not buyRemote then return end
    
    for _, foodName in ipairs(select_buy_food_func) do
        local cleanFood = clean_egg_name(foodName)
        if not is_item_in_stock("Food", cleanFood) then
            continue -- Out of stock, do not spam purchases!
        end
        local foodData = Food[cleanFood] or Food[foodName] or (ShopData and ShopData.Food and ShopData.Food[cleanFood])
        local cost = foodData and tonumber(foodData.Cost or foodData.Price) or 0
        local myCash = tonumber(LocalPlayer.SavedData.Cash.Value) or 0
        if myCash >= cost and myCash > min_cash_reserve_val then
            pcall(function()
                buyRemote:FireServer("Food", cleanFood, 1)
            end)
            task.wait(0.3)
            return -- Buy 1 item per check, do not spam!
        end
    end
end

-- Auto buy gear from StockShop (Auto-Restock / Auto-Update)
local GEAR_PRICES = {
    ["Advanced Radar"] = 50,
    ["Jewel Radar"]    = 3000,
    ["Royal Radar"]    = 20000,
    ["Magic Radar"]    = 300000,
    ["Angelic Radar"]  = 7000000,
    ["Eternal Radar"]  = 30000000,
}

local auto_buy_gear = function()
    if not auto_buy_gear_func then return end
    local buyRemote = Remotes.Game:FindFirstChild("BuyWithCash")
    if not buyRemote then return end

    local myCash = tonumber(LocalPlayer.SavedData.Cash.Value) or 0

    for _, gearItem in ipairs(select_buy_gear_func) do
        local cleanGear = clean_egg_name(gearItem)
        if not is_item_in_stock("Gears", cleanGear) then
            continue -- Out of stock, do not spam purchases!
        end
        local price = GEAR_PRICES[cleanGear] or 999999999
        if myCash >= price and myCash > min_cash_reserve_val then
            pcall(function()
                buyRemote:FireServer("Gear", cleanGear, 1)
            end)
            task.wait(0.3)
            return -- Buy 1 gear per check, do not spam!
        end
    end
end

-- ─── Config & Multi-Profile Persistence Functions ────────────

local function ensure_config_dir()
    if makefolder and isfolder and not isfolder(CONFIG_DIR) then
        pcall(function() makefolder(CONFIG_DIR) end)
    end
end

local function get_config_filepath(profileName)
    local rawName = (type(profileName) == "string" and profileName) or (type(selected_config_profile) == "string" and selected_config_profile) or "default"
    local cleanName = tostring(rawName):gsub("[^%w_%-%s]", ""):match("^%s*(.-)%s*$")
    if not cleanName or cleanName == "" or cleanName == "true" or cleanName == "false" then
        cleanName = "default"
    end
    return CONFIG_DIR .. "/" .. cleanName .. ".json", cleanName
end

local function get_saved_configs()
    ensure_config_dir()
    local list = {}
    if isfolder and isfolder(CONFIG_DIR) and listfiles then
        local files = listfiles(CONFIG_DIR)
        for _, f in ipairs(files) do
            local name = f:match("([^/\\]+)%.json$")
            if name and name ~= "" and name ~= "true" and name ~= "false" then
                table.insert(list, name)
            end
        end
    end
    table.sort(list)
    if #list == 0 then
        table.insert(list, "default")
    end
    return list
end

local function refresh_config_dropdown(selectName)
    if not config_dropdown_ctrl then return end
    local list = get_saved_configs()
    local target = selectName or selected_config_profile
    local found = false
    for _, v in ipairs(list) do
        if v == target then found = true; break end
    end
    if not found then target = list[1] or "default" end
    selected_config_profile = target
    pcall(function()
        config_dropdown_ctrl:Refresh(list, true)
        config_dropdown_ctrl:Set(target)
    end)
end

local function get_config_table()
    return {
        -- Page 1: Eggs & Hatching
        auto_collect_eggs_func        = auto_collect_eggs_func,
        select_rarity_eggs_func       = select_rarity_eggs_func,
        select_method_eggs_func       = select_method_eggs_func,
        select_weight_eggs_func_min   = select_weight_eggs_func_min,
        select_weight_eggs_func_max   = select_weight_eggs_func_max,
        select_size_eggs_func_min     = select_size_eggs_func_min,
        select_size_eggs_func_max     = select_size_eggs_func_max,
        auto_place_eggs_func          = auto_place_eggs_func,
        select_rarity_place_eggs_func = select_rarity_place_eggs_func,
        auto_hatch_eggs_func          = auto_hatch_eggs_func,
        auto_hatch_luck_func          = auto_hatch_luck_func,
        min_cash_reserve_val          = min_cash_reserve_val,
        staging_bypass_enabled        = staging_bypass_enabled,

        -- Page 2: Pets & Food
        auto_pets_func                = auto_pets_func,
        auto_feed_best_pet_func       = auto_feed_best_pet_func,
        select_food_func              = select_food_func,
        auto_feed_priority_func       = auto_feed_priority_func,
        auto_buy_food_func            = auto_buy_food_func,
        select_buy_food_func          = select_buy_food_func,
        auto_sell_pets_func           = auto_sell_pets_func,
        protect_mutation_func         = protect_mutation_func,
        select_pet_sell_func          = select_pet_sell_func,
        select_rarity_sell_func       = select_rarity_sell_func,
        auto_sell_eggs_func           = auto_sell_eggs_func,
        select_egg_sell_func          = select_egg_sell_func,
        select_egg_rarity_sell_func   = select_egg_rarity_sell_func,
        auto_smart_place_func         = auto_smart_place_func,
        smart_cull_keep_top40_func    = smart_cull_keep_top40_func,
        auto_fusion_func              = auto_fusion_func,
        fusion_min_rarity             = fusion_min_rarity,
        fusion_mode                   = fusion_mode,

        -- Page 3: Gears
        auto_buy_gear_func            = auto_buy_gear_func,
        select_buy_gear_func          = select_buy_gear_func,

        -- Page 4: Utility
        auto_rebirth_func             = auto_rebirth_func,
        auto_collect_coins_func       = auto_collect_coins_func,
        auto_rewards_func             = auto_rewards_func,
        auto_claim_index_func         = auto_claim_index_func,
        auto_unlock_nest_func         = auto_unlock_nest_func,
        anti_void_func                = anti_void_func,
        auto_volcano_dip_func         = auto_volcano_dip_func,

        -- Page 5: ESP & Visuals
        esp_eggs                      = esp_eggs,
        select_esp_rarity             = select_esp_rarity,
        esp_placed_eggs               = esp_placed_eggs,
        dash_visible                  = dash_visible,

        -- Page 6: Halloween Event
        auto_halloween_suite          = auto_halloween_suite,
        auto_halloween_candy          = auto_halloween_candy,
        auto_halloween_doors          = auto_halloween_doors,
        auto_halloween_pumpkins       = auto_halloween_pumpkins,
        auto_buy_halloween_egg        = auto_buy_halloween_egg,
        select_hw_exchange_item       = select_hw_exchange_item,

        -- Page 7: Settings
        LANG                          = LANG,
        particle_enabled              = particle_enabled,
        particle_theme_setting        = particle_theme_setting,
        auto_save_enabled             = auto_save_enabled,
        auto_load_on_start            = auto_load_on_start,
        webhook_url                   = webhook_url,
        webhook_enabled               = webhook_enabled,
        profile_name                  = selected_config_profile,
    }
end

local function save_config(profileName, silent)
    if type(profileName) == "boolean" then
        silent = profileName
        profileName = nil
    end
    pcall(function()
        if not writefile then return end
        ensure_config_dir()
        local inputVal = nil
        pcall(function()
            if UI_CONTROLS["new_config_profile_name"] and UI_CONTROLS["new_config_profile_name"].Get then
                inputVal = UI_CONTROLS["new_config_profile_name"]:Get()
            end
        end)
        local targetName = profileName or (inputVal and inputVal ~= "" and inputVal) or new_config_profile_name or selected_config_profile or "default"
        local path, cleanName = get_config_filepath(targetName)
        local data = get_config_table()
        data.profile_name = cleanName
        local json = HttpService:JSONEncode(data)

        writefile(path, json)
        -- Legacy root backup for compatibility
        pcall(function() writefile(LEGACY_CONFIG_FILE, json) end)

        selected_config_profile = cleanName
        new_config_profile_name = cleanName
        refresh_config_dropdown(cleanName)

        if not silent then
            game:GetService("StarterGui"):SetCore("SendNotification", {
                Title    = "Config Saved",
                Text     = "บันทึก Config [" .. cleanName .. "] สำเร็จ!",
                Duration = 3,
            })
        end
    end)
end

local function load_config(profileName, silent)
    if type(profileName) == "boolean" then
        silent = profileName
        profileName = nil
    end
    pcall(function()
        local dropVal = nil
        pcall(function()
            if config_dropdown_ctrl and config_dropdown_ctrl.Get then
                dropVal = config_dropdown_ctrl:Get()
            end
        end)
        local targetName = profileName or (dropVal and dropVal ~= "" and dropVal) or selected_config_profile or "default"
        local path, cleanName = get_config_filepath(targetName)
        local rawJson = nil
        if isfile and isfile(path) and readfile then
            rawJson = readfile(path)
        elseif isfile and isfile(LEGACY_CONFIG_FILE) and readfile then
            rawJson = readfile(LEGACY_CONFIG_FILE)
            cleanName = "default"
        end

        if not rawJson or rawJson == "" then
            if not silent then
                game:GetService("StarterGui"):SetCore("SendNotification", {
                    Title    = "Config Not Found",
                    Text     = "ไม่พบไฟล์ Config: " .. tostring(cleanName),
                    Duration = 3,
                })
            end
            return
        end

        local data = HttpService:JSONDecode(rawJson)
        if type(data) ~= "table" then return end

        -- 1. Apply internal memory variables
        if data.auto_collect_eggs_func ~= nil then auto_collect_eggs_func = data.auto_collect_eggs_func end
        if data.select_rarity_eggs_func ~= nil then
            if type(data.select_rarity_eggs_func) == "table" then
                local valid = {}
                for _, eggItem in ipairs(data.select_rarity_eggs_func) do
                    local c = clean_egg_name(eggItem)
                    if Eggs and (Eggs[c] or Eggs[eggItem]) then
                        table.insert(valid, eggItem)
                    end
                end
                select_rarity_eggs_func = valid
            else
                select_rarity_eggs_func = {}
            end
        end
        if data.select_method_eggs_func ~= nil then select_method_eggs_func = data.select_method_eggs_func end
        if data.select_weight_eggs_func_min ~= nil then select_weight_eggs_func_min = data.select_weight_eggs_func_min end
        if data.select_weight_eggs_func_max ~= nil then select_weight_eggs_func_max = data.select_weight_eggs_func_max end
        if data.select_size_eggs_func_min ~= nil then select_size_eggs_func_min = data.select_size_eggs_func_min end
        if data.select_size_eggs_func_max ~= nil then select_size_eggs_func_max = data.select_size_eggs_func_max end
        if data.auto_place_eggs_func ~= nil then auto_place_eggs_func = data.auto_place_eggs_func end
        if data.select_rarity_place_eggs_func ~= nil then
            if type(data.select_rarity_place_eggs_func) == "table" then
                local valid = {}
                for _, eggItem in ipairs(data.select_rarity_place_eggs_func) do
                    local c = clean_egg_name(eggItem)
                    if Eggs and (Eggs[c] or Eggs[eggItem]) then
                        table.insert(valid, eggItem)
                    end
                end
                select_rarity_place_eggs_func = valid
            else
                select_rarity_place_eggs_func = {}
            end
        end
        if data.auto_hatch_eggs_func ~= nil then auto_hatch_eggs_func = data.auto_hatch_eggs_func end
        if data.auto_hatch_luck_func ~= nil then auto_hatch_luck_func = data.auto_hatch_luck_func end
        if data.min_cash_reserve_val ~= nil then min_cash_reserve_val = data.min_cash_reserve_val end
        if data.staging_bypass_enabled ~= nil then staging_bypass_enabled = data.staging_bypass_enabled end

        if data.auto_pets_func ~= nil then auto_pets_func = data.auto_pets_func end
        if data.auto_feed_best_pet_func ~= nil then auto_feed_best_pet_func = data.auto_feed_best_pet_func end
        if data.select_food_func ~= nil then select_food_func = data.select_food_func end
        if data.auto_feed_priority_func ~= nil then auto_feed_priority_func = data.auto_feed_priority_func end
        if data.auto_buy_food_func ~= nil then auto_buy_food_func = data.auto_buy_food_func end
        if data.select_buy_food_func ~= nil then select_buy_food_func = data.select_buy_food_func end
        if data.protect_mutation_func ~= nil then protect_mutation_func = data.protect_mutation_func end
        if data.auto_sell_pets_func ~= nil then auto_sell_pets_func = data.auto_sell_pets_func end
        if data.select_pet_sell_func ~= nil then select_pet_sell_func = data.select_pet_sell_func end
        if data.select_rarity_sell_func ~= nil then
            select_rarity_sell_func = (type(data.select_rarity_sell_func) == "table") and data.select_rarity_sell_func or {}
        end
        if data.auto_sell_eggs_func ~= nil then auto_sell_eggs_func = data.auto_sell_eggs_func end
        if data.select_egg_sell_func ~= nil then
            if type(data.select_egg_sell_func) == "table" then
                local valid = {}
                for _, eggItem in ipairs(data.select_egg_sell_func) do
                    local c = clean_egg_name(eggItem)
                    if Eggs and (Eggs[c] or Eggs[eggItem]) then
                        table.insert(valid, eggItem)
                    end
                end
                select_egg_sell_func = valid
            else
                select_egg_sell_func = {}
            end
        end
        if data.select_egg_rarity_sell_func ~= nil then
            select_egg_rarity_sell_func = (type(data.select_egg_rarity_sell_func) == "table") and data.select_egg_rarity_sell_func or {}
        end
        if data.auto_smart_place_func ~= nil then auto_smart_place_func = data.auto_smart_place_func end
        if data.smart_cull_keep_top40_func ~= nil then smart_cull_keep_top40_func = data.smart_cull_keep_top40_func end
        if data.auto_fusion_func ~= nil then auto_fusion_func = data.auto_fusion_func end
        if data.fusion_min_rarity ~= nil then fusion_min_rarity = data.fusion_min_rarity end
        if data.fusion_mode ~= nil then fusion_mode = data.fusion_mode end

        if data.auto_buy_gear_func ~= nil then auto_buy_gear_func = data.auto_buy_gear_func end
        if data.select_buy_gear_func ~= nil then select_buy_gear_func = data.select_buy_gear_func end

        if data.auto_rebirth_func ~= nil then auto_rebirth_func = data.auto_rebirth_func end
        if data.auto_collect_coins_func ~= nil then auto_collect_coins_func = data.auto_collect_coins_func end
        if data.auto_rewards_func ~= nil then auto_rewards_func = data.auto_rewards_func end
        if data.auto_claim_index_func ~= nil then auto_claim_index_func = data.auto_claim_index_func end
        if data.auto_unlock_nest_func ~= nil then auto_unlock_nest_func = data.auto_unlock_nest_func end
        if data.anti_void_func ~= nil then anti_void_func = data.anti_void_func end
        if data.auto_volcano_dip_func ~= nil then auto_volcano_dip_func = data.auto_volcano_dip_func end

        if data.esp_eggs ~= nil then esp_eggs = data.esp_eggs end
        if data.select_esp_rarity ~= nil then select_esp_rarity = data.select_esp_rarity end
        if data.esp_placed_eggs ~= nil then esp_placed_eggs = data.esp_placed_eggs end
        if data.dash_visible ~= nil then dash_visible = data.dash_visible end

        if data.auto_halloween_suite ~= nil then auto_halloween_suite = data.auto_halloween_suite end
        if data.auto_halloween_candy ~= nil then auto_halloween_candy = data.auto_halloween_candy end
        if data.auto_halloween_doors ~= nil then auto_halloween_doors = data.auto_halloween_doors end
        if data.auto_halloween_pumpkins ~= nil then auto_halloween_pumpkins = data.auto_halloween_pumpkins end
        if data.auto_buy_halloween_egg ~= nil then auto_buy_halloween_egg = data.auto_buy_halloween_egg end
        if data.select_hw_exchange_item ~= nil then select_hw_exchange_item = data.select_hw_exchange_item end

        if auto_collect_eggs_func and (auto_halloween_suite or auto_halloween_candy) then
            auto_halloween_suite = false
            auto_halloween_candy = false
        end

        if data.LANG ~= nil and data.LANG ~= LANG then
            pcall(function() set_language(data.LANG) end)
        end
        if data.particle_enabled ~= nil then particle_enabled = data.particle_enabled end
        if data.particle_theme_setting ~= nil then particle_theme_setting = data.particle_theme_setting end
        if data.auto_save_enabled ~= nil then auto_save_enabled = data.auto_save_enabled end
        if data.auto_load_on_start ~= nil then auto_load_on_start = data.auto_load_on_start end
        if data.webhook_url ~= nil and data.webhook_url ~= "" then webhook_url = data.webhook_url end
        if data.webhook_enabled ~= nil then webhook_enabled = data.webhook_enabled end
        if data.profile_name and data.profile_name ~= "" then
            cleanName = data.profile_name
        end

        -- 2. Synchronize all visual UI elements
        sync_ui("auto_collect_eggs_func", auto_collect_eggs_func)
        sync_ui("select_rarity_eggs_func", select_rarity_eggs_func)
        sync_ui("select_method_eggs_func", select_method_eggs_func)
        sync_range("select_weight_eggs_func", {select_weight_eggs_func_min, select_weight_eggs_func_max})
        sync_range("select_size_eggs_func", {select_size_eggs_func_min, select_size_eggs_func_max})
        sync_ui("auto_place_eggs_func", auto_place_eggs_func)
        sync_ui("select_rarity_place_eggs_func", select_rarity_place_eggs_func)
        sync_ui("auto_hatch_eggs_func", auto_hatch_eggs_func)
        sync_ui("auto_hatch_luck_func", auto_hatch_luck_func)
        sync_range("min_cash_reserve_val", {min_cash_reserve_val, min_cash_reserve_val})
        sync_ui("staging_bypass_enabled", staging_bypass_enabled)

        sync_ui("auto_pets_func", auto_pets_func)
        sync_ui("auto_feed_best_pet_func", auto_feed_best_pet_func)
        sync_ui("select_food_func", select_food_func)
        sync_ui("auto_feed_priority_func", auto_feed_priority_func)
        sync_ui("auto_buy_food_func", auto_buy_food_func)
        sync_ui("select_buy_food_func", select_buy_food_func)
        sync_ui("protect_mutation_func", protect_mutation_func)
        sync_ui("auto_sell_pets_func", auto_sell_pets_func)
        sync_ui("select_pet_sell_func", select_pet_sell_func)
        sync_ui("select_rarity_sell_func", select_rarity_sell_func)
        sync_ui("auto_sell_eggs_func", auto_sell_eggs_func)
        sync_ui("select_egg_sell_func", select_egg_sell_func)
        sync_ui("select_egg_rarity_sell_func", select_egg_rarity_sell_func)
        sync_ui("auto_smart_place_func", auto_smart_place_func)
        sync_ui("auto_fusion_func", auto_fusion_func)
        sync_ui("fusion_min_rarity", fusion_min_rarity)
        sync_ui("fusion_mode", fusion_mode)

        sync_ui("auto_buy_gear_func", auto_buy_gear_func)
        sync_ui("select_buy_gear_func", select_buy_gear_func)

        sync_ui("auto_rebirth_func", auto_rebirth_func)
        sync_ui("auto_collect_coins_func", auto_collect_coins_func)
        sync_ui("auto_rewards_func", auto_rewards_func)
        sync_ui("auto_claim_index_func", auto_claim_index_func)
        sync_ui("auto_unlock_nest_func", auto_unlock_nest_func)
        sync_ui("anti_void_func", anti_void_func)
        sync_ui("auto_volcano_dip_func", auto_volcano_dip_func)

        sync_ui("auto_halloween_suite", auto_halloween_suite)
        sync_ui("auto_halloween_candy", auto_halloween_candy)
        sync_ui("auto_halloween_doors", auto_halloween_doors)
        sync_ui("auto_halloween_pumpkins", auto_halloween_pumpkins)
        sync_ui("auto_buy_halloween_egg", auto_buy_halloween_egg)
        sync_ui("select_hw_exchange_item", select_hw_exchange_item)

        sync_ui("esp_eggs", esp_eggs)
        sync_ui("select_esp_rarity", select_esp_rarity)
        sync_ui("esp_placed_eggs", esp_placed_eggs)
        sync_ui("dash_visible", dash_visible)

        sync_ui("particle_enabled", particle_enabled)
        sync_ui("particle_theme_setting", particle_theme_setting)
        sync_ui("auto_save_enabled", auto_save_enabled)
        sync_ui("auto_load_on_start", auto_load_on_start)
        sync_ui("new_config_profile_name", cleanName)
        sync_ui("selected_config_profile", cleanName)
        sync_ui("webhook_enabled", webhook_enabled)
        sync_ui("webhook_url", webhook_url)

        -- 3. Trigger visual side-effects
        if DashFrame then DashFrame.Visible = dash_visible end
        if not particle_enabled then clear_all_particles() end
        if esp_eggs then pcall(refresh_esp) end
        if esp_placed_eggs then pcall(refresh_placed_esp) end

        selected_config_profile = cleanName
        new_config_profile_name = cleanName
        refresh_config_dropdown(cleanName)

        if not silent then
            game:GetService("StarterGui"):SetCore("SendNotification", {
                Title    = "Config Loaded",
                Text     = "โหลด Config [" .. cleanName .. "] สำเร็จ!",
                Duration = 3,
            })
        end
    end)
end

local function delete_config(profileName)
    pcall(function()
        local del_fn = delfile or deletefile
        if not del_fn then return end
        local dropVal = nil
        pcall(function()
            if config_dropdown_ctrl and config_dropdown_ctrl.Get then
                dropVal = config_dropdown_ctrl:Get()
            end
        end)
        local targetName = profileName or (dropVal and dropVal ~= "" and dropVal) or selected_config_profile or "default"
        local path, cleanName = get_config_filepath(targetName)
        if isfile and isfile(path) then
            del_fn(path)
            game:GetService("StarterGui"):SetCore("SendNotification", {
                Title    = "Config Deleted",
                Text     = "ลบ Config [" .. cleanName .. "] เรียบร้อยแล้ว!",
                Duration = 3,
            })
            local remaining = get_saved_configs()
            selected_config_profile = remaining[1] or "default"
            new_config_profile_name = selected_config_profile
            refresh_config_dropdown(selected_config_profile)
            sync_ui("new_config_profile_name", selected_config_profile)
            sync_ui("selected_config_profile", selected_config_profile)
        end
    end)
end

_G.RideAPet_SaveConfig = save_config
_G.RideAPet_LoadConfig = load_config
_G.RideAPet_DeleteConfig = delete_config
_G.RideAPet_RefreshConfigs = refresh_config_dropdown
_G.RideAPet_UI_CONTROLS = UI_CONTROLS

local function send_discord_webhook(customMsg)
    if not webhook_url or webhook_url == "" or not webhook_url:find("https://discord") then return end
    local httpReq = request or http_request or (syn and syn.request) or (fluxus and fluxus.request)
    if not httpReq then return end

    pcall(function()
        local myPlot = get_my_plot()
        local eggCount = (myPlot and myPlot:FindFirstChild("Eggs") and #myPlot.Eggs:GetChildren()) or 0
        local petCount = (myPlot and myPlot:FindFirstChild("Pets") and #myPlot.Pets:GetChildren()) or 0
        local rebirths = tonumber(LocalPlayer.SavedData.Rebirths.Value) or 0
        local cash = tonumber(LocalPlayer.SavedData.Cash.Value) or 0
        local uptime = math.floor(tick() - session_start_time)
        local h = math.floor(uptime / 3600)
        local m = math.floor((uptime % 3600) / 60)
        local s = uptime % 60
        local timeStr = string.format("%02d:%02d:%02d", h, m, s)

        local formattedCash = tostring(cash)
        if cash >= 1e12 then formattedCash = string.format("%.2fT", cash / 1e12)
        elseif cash >= 1e9 then formattedCash = string.format("%.2fB", cash / 1e9)
        elseif cash >= 1e6 then formattedCash = string.format("%.2fM", cash / 1e6)
        elseif cash >= 1e3 then formattedCash = string.format("%.2fK", cash / 1e3)
        end

        local payload = {
            username = "PAYOMBØYZ Hub",
            avatar_url = "https://cdn.discordapp.com/attachments/100000000000000000/avatar.png",
            embeds = {
                {
                    title = "🚀 Ride A Pet — Automation Status",
                    description = customMsg or "📊 **อัปเดตสถานะการทำงานล่าสุด**",
                    color = 0x00D7FF,
                    fields = {
                        { name = "👤 Player", value = string.format("`%s` (@%s)", LocalPlayer.Name, LocalPlayer.DisplayName), inline = true },
                        { name = "🔄 Rebirths", value = string.format("Level **%d**", rebirths), inline = true },
                        { name = "💰 Cash", value = string.format("**$%s**", formattedCash), inline = true },
                        { name = "🥚 Plot Eggs", value = string.format("**%d / 10**", eggCount), inline = true },
                        { name = "🐾 Plot Pets", value = string.format("**%d Pets**", petCount), inline = true },
                        { name = "⏱️ Session Uptime", value = string.format("`%s`", timeStr), inline = true },
                    },
                    footer = {
                        text = "💎 PAYOMBØYZ HUB | RIDE A PET",
                    },
                    timestamp = DateTime.now():ToIsoDate(),
                }
            }
        }

        httpReq({
            Url = webhook_url,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = HttpService:JSONEncode(payload)
        })
    end)
end

-- Auto collect pet coins (Passive income)
local auto_collect_coins = function()
    if not auto_collect_coins_func then return end
    local petCollect = Remotes.Game:FindFirstChild("PetCollect")
    if petCollect then
        pcall(function() petCollect:FireServer() end)
    end
end

-- Auto claim free rewards (Strictly NO Robux)
local auto_claim_free_rewards = function()
    if not auto_rewards_func then return end
    pcall(function()
        local reusable = Remotes:FindFirstChild("Reusable")
        if reusable and reusable:FindFirstChild("ClaimGroupReward") then
            reusable.ClaimGroupReward:FireServer()
        end
    end)
    task.wait(0.2)
    pcall(function()
        local claimEvent = Remotes.Game:FindFirstChild("ClaimEventReward")
        if claimEvent then
            claimEvent:InvokeServer()
        end
    end)
    task.wait(0.2)
    pcall(function()
        local claimIndex = Remotes.Game:FindFirstChild("ClaimIndexReward")
        if claimIndex then
            for stage = 1, 10 do
                claimIndex:FireServer(stage)
                task.wait(0.05)
            end
        end
    end)
    task.wait(0.2)
    pcall(function()
        local off = Remotes.Game:FindFirstChild("OfflineEarnings")
        if off then
            off:FireServer()
        end
    end)
end

-- Get placed pets on farm
local function get_placed_pets()
    local plot = get_my_plot()
    if not plot or not plot:FindFirstChild("Pets") then return {} end
    local pets = {}
    for _, item in ipairs(plot.Pets:GetChildren()) do
        table.insert(pets, {
            Model = item,
            PetKey = item:GetAttribute("PetKey"),
            Power = get_pet_power(item),
            Name = item.Name
        })
    end
    table.sort(pets, function(a, b) return a.Power < b.Power end) -- lowest power first
    return pets
end

-- Get backpack pets
local function get_backpack_pets()
    local pets = {}
    if LocalPlayer.Backpack then
        for _, item in ipairs(LocalPlayer.Backpack:GetChildren()) do
            if item:IsA("Tool") and (item:HasTag("Pet") or item:GetAttribute("PetKey") ~= nil) then
                table.insert(pets, {
                    Tool = item,
                    PetKey = item:GetAttribute("PetKey"),
                    Power = get_pet_power(item),
                    Name = item.Name
                })
            end
        end
    end
    table.sort(pets, function(a, b) return a.Power > b.Power end) -- highest power first
    return pets
end

local function place_pet_tool(tool)
    if is_player_riding() then return false end
    if not tool or not tool.Parent then return false end
    local petKey = tool:GetAttribute("PetKey")
    if not petKey then return false end
    
    local char = LocalPlayer.Character
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    if not hrp or not hum then return false end
    
    local plot = get_my_plot()
    local targetPos = (hrp.CFrame * CFrame.new(0, 0, -5)).Position
    if plot then
        local baseplate = plot:FindFirstChild("Baseplate")
        if baseplate then
            local bpPos = baseplate.Position
            targetPos = Vector3.new(
                bpPos.X + math.random(-14, 14),
                bpPos.Y + 2,
                bpPos.Z + math.random(-14, 14)
            )
        end
    end
    
    if tool.Parent == LocalPlayer.Backpack then
        hum:EquipTool(tool)
        task.wait(0.12)
    end
    
    local placeRemote = Remotes.Game:FindFirstChild("PlacePet")
    if placeRemote then
        placeRemote:FireServer(petKey, targetPos)
    end
    
    task.wait(0.2)
    pcall(function() hum:UnequipTools() end)
    return true
end

-- Smart Place Best Pets (Maintains 10 best pets active on ranch at all times)
local function smart_place_best_pets()
    if system_busy or is_carries_eggs() then return end
    local plot = get_my_plot()
    if not plot or not plot:FindFirstChild("Pets") then return end
    
    local maxPets = tonumber(LocalPlayer:GetAttribute("MaxPets")) or 10
    local placedCount = #plot.Pets:GetChildren()
    
    -- 1. If plot has fewer than maxPets, fire game's native PlaceBest button for instant 10-pet placement
    if placedCount < maxPets then
        local placedNative = false
        pcall(function()
            local pt = LocalPlayer.PlayerGui:FindFirstChild("Main") and LocalPlayer.PlayerGui.Main:FindFirstChild("PetsTracker")
            local pb = pt and pt:FindFirstChild("PlaceBest")
            if pb then
                local conns = getconnections(pb.Activated)
                if #conns > 0 then
                    conns[1]:Fire()
                    placedNative = true
                end
            end
        end)
        if placedNative then return end
    end
    
    local pickupRemote = Remotes.Game:FindFirstChild("PickupPet")
    local placed = get_placed_pets()
    local backpack = get_backpack_pets()
    
    if #placed < maxPets and #backpack > 0 then
        system_busy = true
        place_pet_tool(backpack[1].Tool)
        task.wait(0.3)
        system_busy = false
    elseif #placed >= maxPets and #backpack > 0 and #placed > 0 and pickupRemote then
        local worstPlaced = placed[1]
        local bestBackpack = backpack[1]
        if bestBackpack.Power > worstPlaced.Power then
            system_busy = true
            pickupRemote:FireServer(worstPlaced.PetKey)
            task.wait(0.4)
            place_pet_tool(bestBackpack.Tool)
            task.wait(0.3)
            system_busy = false
        end
    end
end

-- Pickup all pets from farm
local function pickup_all_placed_pets()
    if is_player_riding() or is_carries_eggs() then return end
    local plot = get_my_plot()
    if not plot or not plot:FindFirstChild("Pets") then return end
    local pickupRemote = Remotes.Game:FindFirstChild("PickupPet")
    if not pickupRemote then return end
    
    system_busy = true
    for _, p in ipairs(plot.Pets:GetChildren()) do
        local key = p:GetAttribute("PetKey")
        if key then
            pickupRemote:FireServer(key)
            task.wait(0.2)
        end
    end
    system_busy = false
end

-- Auto unlock nest (1-5 in order)
local function auto_unlock_next_nest()
    if not auto_unlock_nest_func then return end
    local plot = get_my_plot()
    if not plot or not plot:FindFirstChild("Nests") then return end
    
    for i = 1, 5 do
        local nest = plot.Nests:FindFirstChild(tostring(i))
        if nest then
            local isUnlocked = (nest:GetAttribute("Unlocked") == true) or (tostring(i) == "1")
            if not isUnlocked then
                local prompt = nest:FindFirstChildWhichIsA("ProximityPrompt", true)
                if prompt and (prompt.Name == "UnlockNest" or prompt.ActionText:lower():find("unlock")) then
                    pcall(fireproximityprompt, prompt, 0)
                    task.wait(0.5)
                    return
                end
            end
        end
    end
end

-- ─── ESP: World eggs (Drawing API) ───────────────────────────

local remove_esp = function(obj)
    local data = esp_objects[obj]
    if not data then return end
    pcall(function()
        if data.drawing and data.drawing.Remove then
            data.drawing:Remove()
        end
    end)
    pcall(function()
        if data.billboard then
            data.billboard:Destroy()
        end
    end)
    esp_objects[obj] = nil
end

local esp_world_egg = function(obj)
    if esp_objects[obj] then return end
    local part = obj:FindFirstChild("EggBase") or obj:FindFirstChildWhichIsA("BasePart") or obj.PrimaryPart
    if not part then return end

    local cleanName = clean_egg_name(obj.Name)
    local rarity = get_pets_rarity(cleanName) or "Common"
    local rarColor = RARITY_COLORS[rarity] or Color3.fromRGB(255, 255, 255)

    -- Primary BillboardGui inside PlayerGui (renders across entire map without distance culling!)
    local pg = LocalPlayer:FindFirstChildOfClass("PlayerGui")
    local espFolder = pg and (pg:FindFirstChild("RideAPet_ESP") or (function()
        local f = Instance.new("Folder")
        f.Name = "RideAPet_ESP"
        f.Parent = pg
        return f
    end)())

    local bb = Instance.new("BillboardGui")
    bb.Name          = "ESP_World_" .. tostring(obj.Name)
    bb.Size          = UDim2.new(0, 88, 0, 114)
    bb.StudsOffset   = Vector3.new(0, 3.5, 0)
    bb.AlwaysOnTop   = true
    bb.MaxDistance   = 5000
    bb.ResetOnSpawn  = false
    bb.Adornee       = part
    bb.Parent        = espFolder or part

    -- Card background (obsidian glass card matching placed eggs)
    local bg = Instance.new("Frame")
    bg.Size                   = UDim2.new(1, 0, 1, 0)
    bg.BackgroundColor3       = Color3.fromRGB(8, 11, 20)
    bg.BackgroundTransparency = 0.18
    bg.BorderSizePixel        = 0
    bg.Parent                 = bb
    Instance.new("UICorner", bg).CornerRadius = UDim.new(0, 8)

    -- Border glow with rarity color
    local stroke = Instance.new("UIStroke")
    stroke.Color        = rarColor
    stroke.Thickness    = 1.8
    stroke.Transparency = 0.1
    stroke.Parent       = bg

    -- Egg thumbnail image
    local imgId = get_pet_image_id(cleanName)
    if imgId and imgId ~= "" then
        local img = Instance.new("ImageLabel")
        img.Size                   = UDim2.new(1, -8, 0, 60)
        img.Position               = UDim2.new(0, 4, 0, 4)
        img.BackgroundTransparency = 1
        img.ScaleType              = Enum.ScaleType.Fit
        img.Image                  = imgId:find("rbxassetid://") and imgId or ("rbxassetid://" .. imgId)
        img.Parent                 = bg
    else
        local emoji = Instance.new("TextLabel")
        emoji.Size                   = UDim2.new(1, -8, 0, 60)
        emoji.Position               = UDim2.new(0, 4, 0, 4)
        emoji.BackgroundTransparency = 1
        emoji.Text                   = "🥚"
        emoji.TextSize               = 32
        emoji.Font                   = Enum.Font.GothamBold
        emoji.TextColor3             = rarColor
        emoji.Parent                 = bg
    end

    -- Egg name label
    local nameLbl = Instance.new("TextLabel")
    nameLbl.Size                   = UDim2.new(1, -6, 0, 24)
    nameLbl.Position               = UDim2.new(0, 3, 0, 66)
    nameLbl.BackgroundTransparency = 1
    nameLbl.Text                   = cleanName
    nameLbl.TextColor3             = rarColor
    nameLbl.Font                   = Enum.Font.GothamBold
    nameLbl.TextSize               = 11
    nameLbl.TextScaled             = true
    nameLbl.TextXAlignment         = Enum.TextXAlignment.Center
    nameLbl.Parent                 = bg

    -- Distance & Rarity label
    local distLbl = Instance.new("TextLabel")
    distLbl.Size                   = UDim2.new(1, -6, 0, 18)
    distLbl.Position               = UDim2.new(0, 3, 0, 90)
    distLbl.BackgroundTransparency = 1
    distLbl.Text                   = "[" .. rarity .. "] --m"
    distLbl.TextColor3             = Color3.fromRGB(220, 230, 245)
    distLbl.Font                   = Enum.Font.GothamMedium
    distLbl.TextSize               = 10
    distLbl.TextScaled             = true
    distLbl.TextXAlignment         = Enum.TextXAlignment.Center
    distLbl.Parent                 = bg

    esp_objects[obj] = { billboard = bb, distLbl = distLbl, rarity = rarity, isPlaced = false }
end

local refresh_esp = function()
    local folder = workspace:FindFirstChild("RenderedEggs")

    for obj, data in pairs(esp_objects) do
        if data and not data.isPlaced then  -- world egg type
            local clean = clean_egg_name(obj.Name)
            local rarity = get_pets_rarity(clean) or "Common"
            if not obj.Parent or not esp_eggs
            or not select_esp_rarity
            or not table.find(select_esp_rarity, rarity)
            then
                remove_esp(obj)
            end
        end
    end

    if not esp_eggs or not select_esp_rarity or not folder then return end

    for _, obj in folder:GetChildren() do
        local clean = clean_egg_name(obj.Name)
        local rarity = get_pets_rarity(clean) or "Common"
        if table.find(select_esp_rarity, rarity) then
            esp_world_egg(obj)
        end
    end
end

-- ─── ESP: Placed garden eggs (BillboardGui + pet image) ──────

local esp_placed_egg = function(obj)
    if esp_objects[obj] then return end

    local attachPart = obj:FindFirstChild("EggBase") or obj:FindFirstChild("Handle") or obj:FindFirstChildWhichIsA("BasePart")
    if not attachPart then return end

    local pg = LocalPlayer:FindFirstChildOfClass("PlayerGui")
    local espFolder = pg and (pg:FindFirstChild("RideAPet_ESP") or (function()
        local f = Instance.new("Folder")
        f.Name = "RideAPet_ESP"
        f.Parent = pg
        return f
    end)())

    local bb = Instance.new("BillboardGui")
    bb.Name          = "ESP_Placed_" .. tostring(obj.Name)
    bb.Size          = UDim2.new(0, 84, 0, 108)
    bb.StudsOffset   = Vector3.new(0, 3.5, 0)
    bb.AlwaysOnTop   = true
    bb.MaxDistance   = math.huge
    bb.ResetOnSpawn  = false
    bb.Adornee       = attachPart
    bb.Parent        = espFolder or attachPart

    -- Card background
    local bg = Instance.new("Frame")
    bg.Size                   = UDim2.new(1, 0, 1, 0)
    bg.BackgroundColor3       = Color3.fromRGB(8, 11, 20)
    bg.BackgroundTransparency = 0.2
    bg.BorderSizePixel        = 0
    bg.Parent                 = bb
    Instance.new("UICorner", bg).CornerRadius = UDim.new(0, 8)

    -- Border glow
    local stroke = Instance.new("UIStroke")
    stroke.Color        = Color3.fromRGB(0, 210, 255)
    stroke.Thickness    = 1.5
    stroke.Transparency = 0.15
    stroke.Parent       = bg

    -- Egg / Pet image
    local imgId = get_pet_image_id(obj.Name)
    if imgId and imgId ~= "" then
        local img = Instance.new("ImageLabel")
        img.Size                   = UDim2.new(1, -6, 0, 64)
        img.Position               = UDim2.new(0, 3, 0, 3)
        img.BackgroundTransparency = 1
        img.ScaleType              = Enum.ScaleType.Fit
        img.Image                  = imgId:find("rbxassetid://") and imgId or ("rbxassetid://" .. imgId)
        img.Parent                 = bg
    else
        local emoji = Instance.new("TextLabel")
        emoji.Size                   = UDim2.new(1, -6, 0, 64)
        emoji.Position               = UDim2.new(0, 3, 0, 3)
        emoji.BackgroundTransparency = 1
        emoji.Text                   = "🥚"
        emoji.TextSize               = 30
        emoji.Font                   = Enum.Font.GothamBold
        emoji.TextColor3             = Color3.fromRGB(255, 245, 200)
        emoji.Parent                 = bg
    end

    -- Egg name
    local lbl = Instance.new("TextLabel")
    lbl.Size                   = UDim2.new(1, -6, 0, 30)
    lbl.Position               = UDim2.new(0, 3, 0, 70)
    lbl.BackgroundTransparency = 1
    lbl.Text                   = obj.Name
    lbl.TextSize               = 10
    lbl.Font                   = Enum.Font.GothamBold
    lbl.TextColor3             = Color3.fromRGB(215, 240, 255)
    lbl.TextWrapped            = true
    lbl.TextScaled             = false
    lbl.TextXAlignment         = Enum.TextXAlignment.Center
    lbl.Parent                 = bg

    local fakeDraw = { Remove = function() end }
    esp_objects[obj] = { drawing = fakeDraw, billboard = bb, isPlaced = true }
end

local refresh_placed_esp = function()
    local plot = get_my_plot()
    if not plot then return end

    -- clean stale billboard ESPs
    for obj, data in pairs(esp_objects) do
        if typeof(obj) ~= "Instance" then continue end
        if data and data.isPlaced then
            if not obj.Parent or not esp_placed_eggs then
                remove_esp(obj)
            end
        end
    end

    if not esp_placed_eggs then return end

    -- scan both Eggs and Nests folders
    for _, folder_name in {"Eggs", "Nests"} do
        local folder = plot:FindFirstChild(folder_name)
        if folder then
            for _, obj in folder:GetChildren() do
                esp_placed_egg(obj)
            end
        end
    end
end

-- ─── Library Load ─────────────────────────────────────────────

local library = loadstring(game:HttpGet("https://raw.githubusercontent.com/SixZensED/Script/refs/heads/main/l4.lua"))()

local payom = library.create()

-- ─── PAYOMBØYZ UI THEME & OBSIDIAN GLASS BACKGROUND ─────────
local apply_payomboyz_ui_theme = function()
    task.spawn(function()
        local cg = game:GetService("CoreGui")
        local pg = LocalPlayer:FindFirstChildOfClass("PlayerGui")
        local main = nil
        local targetGui = nil
        
        for _ = 1, 30 do
            for _, root in ipairs({cg, pg}) do
                if root then
                    for _, g in ipairs(root:GetChildren()) do
                        if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                            main = g["@main"]
                            targetGui = g
                            break
                        end
                    end
                end
                if main then break end
            end
            if main then break end
            task.wait(0.2)
        end
        
        if not main or not targetGui then return end
        
        local bgUrl = "https://raw.githubusercontent.com/payomboyz333/Library/main/upscaled_Blackground%20Sep%2028%2C%202026.png"
        local bgFileName = "PBZ_RideAPet_Background.png"
        local bgAssetId = nil

        local subBgUrl = "https://raw.githubusercontent.com/payomboyz333/Library/main/Image%20Sep%2028%2C%202026%2C%2009_06_51%20AM.png"
        local subBgFileName = "PBZ_SubWindow_Background.png"
        local subBgAssetId = nil
        
        pcall(function()
            if isfile and isfile(bgFileName) then
                if getcustomasset then
                    bgAssetId = getcustomasset(bgFileName)
                elseif getsynasset then
                    bgAssetId = getsynasset(bgFileName)
                end
            end
            if not bgAssetId then
                local imgData = game:HttpGet(bgUrl)
                if imgData and #imgData > 1000 and writefile then
                    writefile(bgFileName, imgData)
                    if getcustomasset then
                        bgAssetId = getcustomasset(bgFileName)
                    elseif getsynasset then
                        bgAssetId = getsynasset(bgFileName)
                    end
                end
            end
        end)

        pcall(function()
            if isfile and isfile(subBgFileName) then
                if getcustomasset then
                    subBgAssetId = getcustomasset(subBgFileName)
                elseif getsynasset then
                    subBgAssetId = getsynasset(subBgFileName)
                end
            end
            if not subBgAssetId then
                local imgData = game:HttpGet(subBgUrl)
                if imgData and #imgData > 1000 and writefile then
                    writefile(subBgFileName, imgData)
                    if getcustomasset then
                        subBgAssetId = getcustomasset(subBgFileName)
                    elseif getsynasset then
                        subBgAssetId = getsynasset(subBgFileName)
                    end
                end
            end
        end)

        -- Fallback: if subBgAssetId failed for any reason, use bgAssetId so it's never blank
        if not subBgAssetId and bgAssetId then
            subBgAssetId = bgAssetId
        end
        
        local oldBg = main:FindFirstChild("@pbz_background")
        if oldBg then oldBg:Destroy() end
        
        if bgAssetId then
            local bgLabel = Instance.new("ImageLabel")
            bgLabel.Name = "@pbz_background"
            bgLabel.Size = UDim2.fromScale(1, 1)
            bgLabel.Position = UDim2.fromScale(0, 0)
            bgLabel.BackgroundTransparency = 1
            bgLabel.Image = bgAssetId
            bgLabel.ScaleType = Enum.ScaleType.Crop
            bgLabel.ZIndex = 0
            bgLabel.ClipsDescendants = true
            
            local corner = main:FindFirstChildOfClass("UICorner")
            if corner then
                local cClone = corner:Clone()
                cClone.Parent = bgLabel
            end
            
            local tint = Instance.new("Frame")
            tint.Name = "@pbz_tint"
            tint.Size = UDim2.fromScale(1, 1)
            tint.BackgroundColor3 = Color3.fromRGB(8, 10, 15)
            tint.BackgroundTransparency = 0.28
            tint.BorderSizePixel = 0
            tint.ZIndex = 0
            tint.Parent = bgLabel
            if corner then
                local cClone2 = corner:Clone()
                cClone2.Parent = tint
            end
            
            bgLabel.Parent = main
            main.BackgroundTransparency = 1
        end
        
        local scriptTitle = main:FindFirstChild("ScriptTitleLabel")
        if scriptTitle then
            scriptTitle.Text = "💎 PAYOMBØYZ HUB"
            scriptTitle.TextColor3 = Color3.fromRGB(255, 45, 75)
            scriptTitle.TextSize = 16
            scriptTitle.Font = Enum.Font.GothamBold
        end
        
        local creditLabel = main:FindFirstChild("CreditLabel")
        if creditLabel then
            creditLabel.Text = "RIDE A PET  /  PLAY MORE • WORK LESS"
            creditLabel.TextColor3 = Color3.fromRGB(180, 185, 200)
            creditLabel.TextSize = 11
            creditLabel.Font = Enum.Font.GothamMedium
        end

        -- ─── SUB-WINDOW DECORATOR (TOGGLE FLYOUT & CHILD MENUS) ───
        local activeSubWindows = {}

        local function find_window_root(instance)
            local curr = instance
            local best = nil
            while curr and curr ~= game and not curr:IsA("ScreenGui") do
                if curr:IsA("Frame") and curr ~= main and curr.Name ~= "@main" then
                    if curr.Parent:IsA("ScreenGui") or curr.Parent == main or curr.Parent.Name == "@main" then
                        return curr
                    end
                    local abs = curr.AbsoluteSize
                    if abs.X >= 120 and abs.Y >= 140 then
                        best = curr
                    end
                end
                curr = curr.Parent
            end
            return best
        end

        local function is_target_sub_window(f)
            if not f or not f:IsA("Frame") then return false end
            if f == main or f.Name == "@main" or f.Name == "@pbz_background" or f.Name == "@pbz_tint" or f.Name == "@particles" then return false end
            -- CRITICAL: Never decorate frames inside main or layout containers
            if f:IsDescendantOf(main) then return false end
            if f.Name == "@page" or f.Name:find("@page") or f:FindFirstChildOfClass("UIPageLayout") then return false end
            if f.Parent and f.Parent:FindFirstChildOfClass("UIPageLayout") then return false end
            if f.Name == "HudFrame" or f.Name == "MonitoringDashboard" or f.Name:find("Dash") or f.Name:find("Radar") then return false end
            if f.Name:find("@container") or f.Name:find("@section") or f.Name:find("@content") or f.Name:find("@drawer") then return false end

            local abs = f.AbsoluteSize
            if abs.X < 110 or abs.Y < 130 then return false end
            if abs.X > 1200 and abs.Y > 800 then return false end

            -- Signature: Child of targetGui that has ScrollingFrame or UICorner (separate popout window)
            if f.Parent == targetGui and (f:FindFirstChildOfClass("ScrollingFrame") or f:FindFirstChildOfClass("UICorner")) then
                return true
            end

            return false
        end

        local function decorate_sub_window(subWin)
            if not subWin or not subWin:IsA("Frame") then return end
            if not subBgAssetId then return end
            if subWin == main or subWin:IsDescendantOf(main) then return end
            if subWin.Name == "@page" or subWin:FindFirstChildOfClass("UIPageLayout") then return end

            -- Set outer window background transparent
            subWin.BackgroundTransparency = 1

            -- CRITICAL FIX: Make inner containers & ScrollingFrames transparent
            -- so they don't block the wallpaper behind them
            for _, desc in ipairs(subWin:GetDescendants()) do
                if desc:IsA("ScrollingFrame") then
                    desc.BackgroundTransparency = 1
                    desc.BorderSizePixel = 0
                elseif desc:IsA("Frame") and desc.Name ~= "@pbz_sub_tint" and desc.Name ~= "@pbz_sub_bg" then
                    -- If container covers > 60% of window or is direct child
                    if desc.Parent == subWin and (desc.Size.X.Scale >= 0.7 or desc.AbsoluteSize.X >= (subWin.AbsoluteSize.X * 0.7)) then
                        desc.BackgroundTransparency = 1
                        desc.BorderSizePixel = 0
                    end
                end
            end

            -- Attach or update @pbz_sub_bg
            local bgLabel = subWin:FindFirstChild("@pbz_sub_bg")
            if not bgLabel then
                bgLabel = Instance.new("ImageLabel")
                bgLabel.Name = "@pbz_sub_bg"
                bgLabel.Size = UDim2.fromScale(1, 1)
                bgLabel.Position = UDim2.fromScale(0, 0)
                bgLabel.BackgroundTransparency = 1
                bgLabel.Image = subBgAssetId
                bgLabel.ScaleType = Enum.ScaleType.Crop
                bgLabel.ZIndex = 0
                bgLabel.ClipsDescendants = true

                local corner = subWin:FindFirstChildOfClass("UICorner")
                if corner then
                    corner:Clone().Parent = bgLabel
                else
                    local c = Instance.new("UICorner")
                    c.CornerRadius = UDim.new(0, 8)
                    c.Parent = bgLabel
                end

                local tint = Instance.new("Frame")
                tint.Name = "@pbz_sub_tint"
                tint.Size = UDim2.fromScale(1, 1)
                tint.BackgroundColor3 = Color3.fromRGB(8, 10, 15)
                tint.BackgroundTransparency = 0.28
                tint.BorderSizePixel = 0
                tint.ZIndex = 0
                tint.Parent = bgLabel

                if corner then
                    corner:Clone().Parent = tint
                end

                bgLabel.Parent = subWin
            else
                bgLabel.Image = subBgAssetId
                bgLabel.ZIndex = 0
            end

            -- Attach or update laser red UIStroke
            local stroke = subWin:FindFirstChild("@pbz_sub_stroke") or subWin:FindFirstChildOfClass("UIStroke")
            if not stroke then
                stroke = Instance.new("UIStroke")
                stroke.Name = "@pbz_sub_stroke"
                stroke.Color = Color3.fromRGB(255, 35, 55)
                stroke.Thickness = 1.2
                stroke.Transparency = 0.35
                stroke.Parent = subWin
            else
                stroke.Color = Color3.fromRGB(255, 35, 55)
                stroke.Transparency = 0.35
            end

            activeSubWindows[subWin] = true
        end

        local function scan_and_apply()
            pcall(function()
                if not targetGui or not targetGui.Parent then return end
                -- Remove any rogue background elements that may have been attached inside main or @page
                if main and main.Parent then
                    for _, d in ipairs(main:GetDescendants()) do
                        if d.Name == "@pbz_sub_bg" or d.Name == "@pbz_sub_tint" or d.Name == "@pbz_sub_stroke" then
                            d:Destroy()
                        end
                    end
                end
                -- Only inspect direct children of targetGui (separate popout windows)
                for _, child in ipairs(targetGui:GetChildren()) do
                    if child ~= main and is_target_sub_window(child) and not activeSubWindows[child] then
                        decorate_sub_window(child)
                    end
                end
            end)
        end

        -- Initial scan
        scan_and_apply()

        -- Lightweight ChildAdded hook (fires ONLY on direct children, NOT all descendants)
        if targetGui then
            targetGui.ChildAdded:Connect(function(child)
                if child:IsA("Frame") then
                    task.wait(0.05)
                    if is_target_sub_window(child) then
                        decorate_sub_window(child)
                    end
                end
            end)
        end

        -- Passive low-frequency watchdog (every 3 seconds, ultra lightweight)
        task.spawn(function()
            local mySession = CURRENT_SESSION_ID
            while _G.RideAPet_Session == mySession do
                task.wait(3.0)
                scan_and_apply()
            end
        end)
    end)
end
pcall(apply_payomboyz_ui_theme)

-- ================================================================
-- PAGE 1: ไข่ (Eggs & Hatching) [1/7]
-- ================================================================
local function init_main_tabs()
do
local tab_eggs = payom.create()
tab_eggs.Header({Title = "💎 PAYOMBØYZ • EGGS HEIST & HATCHING (1/7)"})
tab_eggs.Header({Title = "⚡ ระบบขโมยไข่ • วางไข่ในสวน • ฟักไข่อัตโนมัติ"})

local eggs_func = tab_eggs.Toggle({
    Title    = T("eggs_title"),
    Info     = T("eggs_info"),
    Default  = false,
    Callback = function(value)
        auto_collect_eggs_func = value
        if auto_collect_eggs_func then
            -- ปิดคำสั่งและปุ่ม UI ของกิจกรรมฮาโลวีนทันที
            if auto_halloween_suite or auto_halloween_candy then
                auto_halloween_suite = false
                auto_halloween_candy = false
                sync_ui("auto_halloween_suite", false)
                sync_ui("auto_halloween_candy", false)
            end
            task.spawn(function()
                task.wait(0.1)
                pcall(collect_egg)
            end)
        else
            stop_tween()
            noclip_enabled = false
            pcall(teleport_to_plot)
        end
    end,
}, false)
UI_CONTROLS["auto_collect_eggs_func"] = eggs_func

UI_CONTROLS["select_rarity_eggs_func"] = eggs_func:Dropdown({
    Title    = T("sel_egg_name"),
    List     = get_egg_names_with_rarity(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_rarity_eggs_func = value
    end,
})

UI_CONTROLS["select_method_eggs_func"] = eggs_func:Dropdown({
    Title    = T("sel_method"),
    List     = {"Teleport", "Tween"},
    Multi    = false,
    Default  = "Teleport",
    Callback = function(value)
        select_method_eggs_func = value
    end,
})

UI_CONTROLS["staging_bypass_enabled"] = eggs_func:Toggle({
    Title    = T("bypass_staging"),
    Info     = "บายพาสระบบตรวจจับความเร็วการวาร์ปส่งไข่ (100% Delivery Success)",
    Default  = true,
    Callback = function(value)
        staging_bypass_enabled = value
    end,
}, false)

UI_CONTROLS["select_weight_eggs_func"] = eggs_func:Range({
    Title    = T("sel_weight"),
    Min      = 1,
    Max      = 2,
    Default  = {1, 2},
    Round    = 0.25,
    Gap      = 0.1,
    Callback = function(value)
        select_weight_eggs_func_min = value[1]
        select_weight_eggs_func_max = value[2]
    end,
}, false)

UI_CONTROLS["select_size_eggs_func"] = eggs_func:Range({
    Title    = T("sel_size"),
    Min      = 1,
    Max      = 3,
    Default  = {1, 3},
    Round    = 0.25,
    Gap      = 0.1,
    Callback = function(value)
        select_size_eggs_func_min = value[1]
        select_size_eggs_func_max = value[2]
    end,
}, false)

local place_func = tab_eggs.Toggle({
    Title    = T("auto_place"),
    Info     = "กระจายไข่ลงแปลงในสวนอัตโนมัติ (ไม่ซ้อนกัน)",
    Default  = true,
    Callback = function(value)
        auto_place_eggs_func = value
        if auto_place_eggs_func then
            task.spawn(function()
                task.wait(0.1)
                pcall(place_eggs)
            end)
        end
    end,
}, false)
UI_CONTROLS["auto_place_eggs_func"] = place_func

UI_CONTROLS["select_rarity_place_eggs_func"] = place_func:Dropdown({
    Title    = T("sel_place_eg"),
    List     = get_egg_names_with_rarity(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_rarity_place_eggs_func = value
    end,
})

local hatch_func = tab_eggs.Toggle({
    Title    = T("auto_hatch"),
    Info     = "ฟักไข่ในแปลงและรังทันทีที่พร้อม",
    Default  = true,
    Callback = function(value)
        auto_hatch_eggs_func = value
        if auto_hatch_eggs_func then
            task.spawn(function()
                task.wait(0.1)
                pcall(hatch_eggs)
            end)
        end
    end,
}, false)
UI_CONTROLS["auto_hatch_eggs_func"] = hatch_func

UI_CONTROLS["auto_hatch_luck_func"] = hatch_func:Toggle({
    Title    = T("auto_luck"),
    Default  = true,
    Callback = function(value)
        auto_hatch_luck_func = value
    end,
}, false)

UI_CONTROLS["min_cash_reserve_val"] = hatch_func:Range({
    Title    = T("min_reserve"),
    Min      = 0,
    Max      = 100000,
    Default  = {1000, 1000},
    Round    = 500,
    Gap      = 500,
    Callback = function(value)
        min_cash_reserve_val = value[1] or 1000
    end,
}, false)
end

-- ================================================================
-- PAGE 2: สัตว์เลี้ยง & อาหาร (Pets & Food) [2/7]
-- ================================================================
do
local tab_pets = payom.create()
tab_pets.Header({Title = "🐾 PAYOMBØYZ • PETS AUTOMATION & FUSION (2/7)"})
tab_pets.Header({Title = "🏇 ขี่สัตว์ตัวท็อป • ป้อนอาหาร • หลอมสัตว์ (Fusion)"})

local pets_feed_func = tab_pets.Toggle({
    Title    = T("pets_title"),
    Info     = "ระบบดูแลอาหารและซื้อของอัตโนมัติ",
    Default  = true,
    Callback = function(value)
        auto_pets_func = value
    end,
}, false)

pets_feed_func:Button({
    Title = "🏇 ขี่สัตว์ตัวที่ดีที่สุดใน Plot ทันที (Mount Best Pet Now)",
    Callback = function()
        pcall(mount_best_pet_on_plot)
    end
})
UI_CONTROLS["auto_pets_func"] = pets_feed_func

UI_CONTROLS["auto_feed_best_pet_func"] = pets_feed_func:Toggle({
    Title    = T("auto_feed"),
    Default  = true,
    Callback = function(value)
        auto_feed_best_pet_func = value
    end,
}, false)

UI_CONTROLS["select_food_func"] = pets_feed_func:Dropdown({
    Title    = T("sel_food"),
    List     = get_food(),
    Multi    = true,
    Default  = {"Grass"},
    Callback = function(value)
        select_food_func = value
    end,
})

UI_CONTROLS["auto_feed_priority_func"] = pets_feed_func:Toggle({
    Title    = T("auto_feed_p"),
    Default  = true,
    Callback = function(value)
        auto_feed_priority_func = value
    end,
}, false)

pets_feed_func:Line()

UI_CONTROLS["auto_buy_food_func"] = pets_feed_func:Toggle({
    Title    = T("auto_buy_food"),
    Default  = false,
    Callback = function(value)
        auto_buy_food_func = value
    end,
}, false)

UI_CONTROLS["select_buy_food_func"] = pets_feed_func:Dropdown({
    Title    = T("sel_buy_food"),
    List     = get_food(),
    Multi    = true,
    Default  = {"Grass"},
    Callback = function(value)
        select_buy_food_func = value
    end,
})

local pets_sell_func = tab_pets.Toggle({
    Title    = T("auto_sell"),
    Info     = "ขายสัตว์และไข่ที่ร้าน Richie (ล็อก Mutation อัตโนมัติ)",
    Default  = false,
    Callback = function(value)
        auto_sell_pets_func = value
    end,
}, false)
UI_CONTROLS["auto_sell_pets_func"] = pets_sell_func

UI_CONTROLS["protect_mutation_func"] = pets_sell_func:Toggle({
    Title    = T("protect_mut"),
    Default  = true,
    Callback = function(value)
        protect_mutation_func = value
    end,
}, false)

UI_CONTROLS["select_pet_sell_func"] = pets_sell_func:Dropdown({
    Title    = T("sel_sell_pet"),
    List     = get_pet_names_with_rarity(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_pet_sell_func = value
    end,
})

UI_CONTROLS["select_rarity_sell_func"] = pets_sell_func:Dropdown({
    Title    = T("sel_sell_rar"),
    List     = get_rarities(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_rarity_sell_func = value
    end,
})

pets_sell_func:Line()

UI_CONTROLS["auto_sell_eggs_func"] = pets_sell_func:Toggle({
    Title    = T("auto_sell_eggs"),
    Default  = false,
    Callback = function(value)
        auto_sell_eggs_func = value
    end,
}, false)

UI_CONTROLS["select_egg_sell_func"] = pets_sell_func:Dropdown({
    Title    = T("sel_sell_egg"),
    List     = get_egg_names_with_rarity(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_egg_sell_func = value
    end,
})

UI_CONTROLS["select_egg_rarity_sell_func"] = pets_sell_func:Dropdown({
    Title    = T("sel_sell_egg_rar"),
    List     = get_rarities(),
    Multi    = true,
    Default  = {},
    Callback = function(value)
        select_egg_rarity_sell_func = value
    end,
})

local pets_smart_func = tab_pets.Toggle({
    Title    = T("auto_smart_p"),
    Info     = "คำนวณและสลับวางสัตว์เลี้ยงที่ทำเงินสูงสุด",
    Default  = true,
    Callback = function(value)
        auto_smart_place_func = value
    end,
}, false)
UI_CONTROLS["auto_smart_place_func"] = pets_smart_func

pets_smart_func:Button({
    Title    = T("pickup_weak"),
    Callback = function()
        pcall(pickup_all_placed_pets)
    end,
})

local fusion_card = tab_pets.Toggle({
    Title    = T("fusion_title"),
    Info     = "ระบบผสมพันธุ์สัตว์เลี้ยงอัตโนมัติ (ใส่ 4 ตัว -> รับสัตว์ระดับสูงขึ้น)",
    Default  = false,
    Callback = function(value)
        auto_fusion_func = value
    end,
}, false)
UI_CONTROLS["auto_fusion_func"] = fusion_card

UI_CONTROLS["fusion_min_rarity"] = fusion_card:Dropdown({
    Title    = T("sel_fusion_rar"),
    List     = {"Common", "Rare", "Epic", "Legendary", "Mythic", "Divine", "Ethereal"},
    Multi    = false,
    Default  = "Legendary",
    Callback = function(value)
        fusion_min_rarity = value
    end,
})

UI_CONTROLS["fusion_mode"] = fusion_card:Dropdown({
    Title    = T("sel_fusion_mode"),
    List     = {"Duplicate Pets Only (ตัวซ้ำ)", "Lowest Power First (สัตว์พลังต่ำสุด)"},
    Multi    = false,
    Default  = "Duplicate Pets Only (ตัวซ้ำ)",
    Callback = function(value)
        fusion_mode = value
    end,
})
end

-- ================================================================
-- PAGE 3: อุปกรณ์ (Gears & Shop) [3/7]
-- ================================================================
do
local tab_gears = payom.create()
tab_gears.Header({Title = "🎒 PAYOMBØYZ • SHOP GEARS & RESTOCK (3/7)"})
tab_gears.Header({Title = "🛒 ซื้ออุปกรณ์ • กระเป๋า • ตะเกียง • รีสต็อกอัตโนมัติ"})

local gear_func = tab_gears.Toggle({
    Title    = T("gears_title"),
    Info     = T("gears_info"),
    Default  = false,
    Callback = function(value)
        auto_buy_gear_func = value
    end,
}, false)
UI_CONTROLS["auto_buy_gear_func"] = gear_func

UI_CONTROLS["select_buy_gear_func"] = gear_func:Dropdown({
    Title    = T("sel_buy_gear"),
    List     = get_gear_names_with_rarity(),
    Multi    = true,
    Default  = {"Royal Radar", "Jewel Radar"},
    Callback = function(value)
        select_buy_gear_func = value
    end,
})
end

-- ================================================================
-- PAGE 4: ยูทิลิตี้ & รีเบิร์ท (Utility & Rebirth) [4/7]
-- ================================================================
do
local tab_util = payom.create()
tab_util.Header({Title = "🔄 PAYOMBØYZ • SMART REBIRTH & UTILITY (4/7)"})
tab_util.Header({Title = "🔄 คำนวณเงิน + บินขโมยไข่ + ฟัก + ปลดล็อกรัง"})

local rebirth_func = tab_util.Toggle({
    Title    = T("auto_rebirth"),
    Info     = T("smart_rebirth_info"),
    Default  = true,
    Callback = function(value)
        auto_rebirth_func = value
    end,
}, false)
UI_CONTROLS["auto_rebirth_func"] = rebirth_func

local auto_farm_func = tab_util.Toggle({
    Title    = "เหรียญและของขวัญฟรี",
    Info     = "เก็บเหรียญสัตว์เลี้ยง และรับของขวัญอัตโนมัติ",
    Default  = true,
    Callback = function(_) end,
}, false)

UI_CONTROLS["auto_collect_coins_func"] = auto_farm_func:Toggle({
    Title    = T("auto_coins"),
    Default  = true,
    Callback = function(value)
        auto_collect_coins_func = value
    end,
}, false)

UI_CONTROLS["auto_rewards_func"] = auto_farm_func:Toggle({
    Title    = T("auto_rewards"),
    Default  = true,
    Callback = function(value)
        auto_rewards_func = value
    end,
}, false)

UI_CONTROLS["auto_claim_index_func"] = auto_farm_func:Toggle({
    Title    = T("auto_claim"),
    Default  = true,
    Callback = function(value)
        auto_claim_index_func = value
    end,
}, false)

local security_func = tab_util.Toggle({
    Title    = "ระบบบ้านและความปลอดภัย",
    Info     = "ปลดล็อกรัง, กันตกแมพ, วาร์ปกลับบ้าน",
    Default  = true,
    Callback = function(_) end,
}, false)

UI_CONTROLS["auto_unlock_nest_func"] = security_func:Toggle({
    Title    = T("auto_nest"),
    Default  = true,
    Callback = function(value)
        auto_unlock_nest_func = value
    end,
}, false)

UI_CONTROLS["anti_void_func"] = security_func:Toggle({
    Title    = T("anti_void"),
    Default  = true,
    Callback = function(value)
        anti_void_func = value
    end,
}, false)

security_func:Button({
    Title    = T("tp_plot_btn"),
    Callback = function()
        pcall(teleport_to_plot)
    end,
})

UI_CONTROLS["auto_volcano_dip_func"] = security_func:Toggle({
    Title    = T("auto_volcano"),
    Info     = "วาร์ปไปยอดภูเขาไฟจุ่มลาวาเพื่อเพิ่ม Mutation Magma (พลังคูณสูง)",
    Default  = false,
    Callback = function(value)
        auto_volcano_dip_func = value
    end,
}, false)
end

-- ================================================================
-- PAGE 5: ESP & แดชบอร์ด (ESP & Visuals) [5/7]
-- ================================================================
do
local tab_esp = payom.create()
tab_esp.Header({Title = "👁️ PAYOMBØYZ • ESP RADAR & SENSORS (5/7)"})
tab_esp.Header({Title = "📡 เรดาร์ตรวจจับไข่ในสวน • ป้ายชื่อ • กล่อง 3D ESP"})

local esp_func = tab_esp.Toggle({
    Title    = T("esp_title"),
    Info     = T("esp_info"),
    Default  = true,
    Callback = function(_) end,
}, false)

UI_CONTROLS["esp_eggs"] = esp_func:Toggle({
    Title    = T("esp_eggs"),
    Default  = true,
    Callback = function(value)
        esp_eggs = value
        if not value then
            for obj, data in pairs(esp_objects) do
                if data and not data.isPlaced then
                    remove_esp(obj)
                end
            end
        else
            refresh_esp()
        end
    end,
}, false)

UI_CONTROLS["select_esp_rarity"] = esp_func:Dropdown({
    Title    = T("sel_esp_rar"),
    List     = get_rarities(),
    Multi    = true,
    Default  = get_rarities(),
    Callback = function(value)
        select_esp_rarity = value
        refresh_esp()
    end,
})

UI_CONTROLS["esp_placed_eggs"] = esp_func:Toggle({
    Title    = T("esp_placed"),
    Default  = true,
    Callback = function(value)
        esp_placed_eggs = value
        if not value then
            for obj, data in pairs(esp_objects) do
                if data and data.isPlaced then
                    remove_esp(obj)
                end
            end
        else
            refresh_placed_esp()
        end
    end,
}, false)

local dash_card = tab_esp.Toggle({
    Title    = T("dash_toggle"),
    Info     = "แสดง/ซ่อน แดชบอร์ดมอนิเตอร์ 2D Radar",
    Default  = false,
    Callback = function(value)
        dash_visible = value
        if DashFrame then
            DashFrame.Visible = value
        end
    end,
}, false)
UI_CONTROLS["dash_visible"] = dash_card
end

-- ================================================================
-- PAGE 6: กิจกรรมฮาโลวีน (Halloween Event Suite) [6/7]
-- ================================================================
do
local tab_halloween = payom.create()
tab_halloween.Header({Title = "🎃 PAYOMBØYZ • HALLOWEEN EVENT SUITE (6/7)"})
tab_halloween.Header({Title = "🍬 ออโต้แคนดี้ • เคาะประตู • ค้นหาฟักทอง • ซื้อไข่ลับ"})

local hw_card = tab_halloween.Toggle({
    Title    = T("hw_title"),
    Info     = T("hw_info"),
    Default  = false,
    Callback = function(value)
        auto_halloween_suite = value
        if value then
            -- ปิดคำสั่งขโมยไข่และปุ่มบน UI ก่อนเริ่มกิจกรรมฮาโลวีน
            if auto_collect_eggs_func then
                auto_collect_eggs_func = false
                sync_ui("auto_collect_eggs_func", false)
                stop_tween()
                noclip_enabled = false
                pcall(teleport_to_plot)
            end
            if not auto_halloween_candy and not auto_halloween_doors and not auto_halloween_pumpkins and not auto_buy_halloween_egg then
                auto_halloween_candy = true
                auto_buy_halloween_egg = true
                sync_ui("auto_halloween_candy", true)
                sync_ui("auto_buy_halloween_egg", true)
            end
            task.spawn(function()
                task.wait(0.1)
                pcall(run_halloween_pipeline)
            end)
        end
    end,
}, false)
UI_CONTROLS["auto_halloween_suite"] = hw_card

UI_CONTROLS["auto_halloween_candy"] = hw_card:Toggle({
    Title    = T("auto_hw_candy"),
    Info     = T("auto_hw_candy_info"),
    Default  = false,
    Callback = function(value)
        auto_halloween_candy = value
        if value then
            -- ปิดคำสั่งขโมยไข่และปุ่มบน UI ก่อนเริ่มกิจกรรมฮาโลวีน
            if auto_collect_eggs_func then
                auto_collect_eggs_func = false
                sync_ui("auto_collect_eggs_func", false)
                stop_tween()
                noclip_enabled = false
                pcall(teleport_to_plot)
            end
            task.spawn(function()
                task.wait(0.1)
                pcall(run_halloween_pipeline)
            end)
        end
    end,
}, false)

UI_CONTROLS["auto_halloween_doors"] = hw_card:Toggle({
    Title    = T("auto_hw_doors"),
    Info     = T("auto_hw_doors_info"),
    Default  = false,
    Callback = function(value)
        auto_halloween_doors = value
        if value then
            if auto_collect_eggs_func then
                auto_collect_eggs_func = false
                sync_ui("auto_collect_eggs_func", false)
                stop_tween()
                noclip_enabled = false
                pcall(teleport_to_plot)
            end
            task.spawn(function()
                task.wait(0.1)
                pcall(run_halloween_pipeline)
            end)
        end
    end,
}, false)

UI_CONTROLS["auto_halloween_pumpkins"] = hw_card:Toggle({
    Title    = T("auto_hw_pumpkins"),
    Info     = T("auto_hw_pump_info"),
    Default  = false,
    Callback = function(value)
        auto_halloween_pumpkins = value
        if value then
            if auto_collect_eggs_func then
                auto_collect_eggs_func = false
                sync_ui("auto_collect_eggs_func", false)
                stop_tween()
                noclip_enabled = false
                pcall(teleport_to_plot)
            end
            task.spawn(function()
                task.wait(0.1)
                pcall(run_halloween_pipeline)
            end)
        end
    end,
}, false)

local hw_shop_card = tab_halloween.Toggle({
    Title    = (LANG == "TH" and "ร้านค้าและแลกของกิจกรรม (Shop & Exchange)" or "Shop & Exchange"),
    Info     = (LANG == "TH" and "เลือกไอเทมแลกของฮาโลวีน • ฝากลูกอม • วาร์ปเกาะ" or "Exchange Halloween items, deposit candy, teleport"),
    Default  = false,
    Callback = function(_) end,
}, false)

UI_CONTROLS["select_hw_exchange_item"] = hw_shop_card:Dropdown({
    Title    = "🎁 " .. (LANG == "TH" and "เลือกไอเทมแลกของกิจกรรม" or "Select Event Item"),
    List     = {"Halloween Egg (350 ลูกอม)", "Headless Egg (หม้อพิธีกรรม 50 ลูกอม)"},
    Multi    = false,
    Default  = select_hw_exchange_item or "Halloween Egg (350 ลูกอม)",
    Callback = function(value)
        select_hw_exchange_item = value
    end,
})

UI_CONTROLS["auto_buy_halloween_egg"] = hw_shop_card:Toggle({
    Title    = "🔄 " .. (LANG == "TH" and "ออโต้แลกของกิจกรรมฮาโลวีน" or "Auto Exchange Halloween Item"),
    Info     = "แลกไข่ฮาโลวีน (350 ลูกอม) หรือฝากหม้อพิธีกรรม (50 ลูกอม) อัตโนมัติ",
    Default  = false,
    Callback = function(value)
        auto_buy_halloween_egg = value
        if value then
            task.spawn(function()
                task.wait(0.1)
                pcall(run_halloween_pipeline)
            end)
        end
    end,
}, false)

hw_shop_card:Button({
    Title    = "🍬 " .. (LANG == "TH" and "ฝากลูกอมทันที (Deposit Carried Candy Now)" or "Deposit Carried Candy Now"),
    Callback = function()
        pcall(function()
            safe_move_root(CFrame.new(-45839.9, 40375, -20118.0))
        end)
    end,
})

hw_shop_card:Button({
    Title    = "🛒 " .. (LANG == "TH" and "เปิดร้านค้าฮาโลวีน (Open Halloween Shop)" or "Open Halloween Shop"),
    Callback = function()
        pcall(function()
            local rem = game:GetService("ReplicatedStorage"):FindFirstChild("Remotes") and game.ReplicatedStorage.Remotes:FindFirstChild("Game") and game.ReplicatedStorage.Remotes.Game:FindFirstChild("OpenHalloweenShop")
            if rem then rem:FireServer() end
        end)
    end,
})

hw_shop_card:Button({
    Title    = "🎃 " .. T("hw_tp_island_btn"),
    Callback = function()
        pcall(function()
            local cs = game:GetService("CollectionService")
            local portal = cs:GetTagged("HalloweenPortal")[1]
            local prompt = portal and portal:FindFirstChildWhichIsA("ProximityPrompt", true)
            if portal and prompt then
                safe_move_root(portal.CFrame + Vector3.new(0, 3, 0))
                task.wait(0.2)
                if typeof(fireproximityprompt) == "function" then
                    fireproximityprompt(prompt, prompt.HoldDuration or 0.2)
                end
            else
                safe_move_root(CFrame.new(-46040.8, 40377.5, -20327.3))
            end
        end)
    end,
})

hw_shop_card:Button({
    Title    = "🏡 " .. T("hw_tp_plot_btn"),
    Callback = function()
        pcall(teleport_to_plot)
    end,
})
end

-- ================================================================
-- PAGE 7: การตั้งค่า & Webhook (Settings & Webhook) [7/7]
-- ================================================================
do
local tab_cfg = payom.create()
tab_cfg.Header({Title = "⚙️ PAYOMBØYZ • CONFIG PROFILES & WEBHOOK (7/7)"})
tab_cfg.Header({Title = "💾 บันทึกโปรไฟล์ • สลับภาษา • แจ้งเตือน Discord"})

local lang_card = tab_cfg.Toggle({
    Title    = T("lang_sec"),
    Info     = "คลิกสวิตช์ หรือกดปุ่มด้านล่างเพื่อสลับภาษา (TH / EN)",
    Default  = (LANG == "EN"),
    Callback = function(isEnglish)
        local target = isEnglish and "EN" or "TH"
        if target ~= LANG then
            set_language(target)
        end
    end,
}, false)
UI_CONTROLS["lang_toggle"] = lang_card

lang_card:Button({
    Title    = "🌐 " .. T("lang_btn"),
    Callback = function()
        local nextLang = (LANG == "TH") and "EN" or "TH"
        set_language(nextLang)
    end,
})

local particle_card = tab_cfg.Toggle({
    Title    = T("particle_tog"),
    Info     = "แสดงเอฟเฟกต์ตามเทศกาลหรือฤดูกาล (5 Seasons & Festivals)",
    Default  = true,
    Callback = function(value)
        particle_enabled = value
        if clear_all_particles then
            clear_all_particles()
        end
    end,
}, false)
UI_CONTROLS["particle_enabled"] = particle_card

UI_CONTROLS["particle_theme_setting"] = particle_card:Dropdown({
    Title    = T("particle_drop"),
    List     = {
        "Auto (ตามปฏิทินจริง)",
        "ฤดูร้อน (Summer)",
        "ฤดูฝน (Rainy)",
        "ฤดูหนาว (Winter)",
        "ฤดูใบไม้ผลิ (Spring)",
        "ฤดูใบไม้ร่วง (Autumn)",
        "คริสต์มาส (Christmas)",
        "วาเลนไทน์ (Valentine)",
        "ฮาโลวีน (Halloween)",
        "ลอยกระทง (Loy Krathong)",
        "สงกรานต์ (Songkran)",
        "ปีใหม่ (New Year)",
    },
    Multi    = false,
    Default  = "Auto (ตามปฏิทินจริง)",
    Callback = function(value)
        particle_theme_setting = value
        if clear_all_particles then
            clear_all_particles()
        end
    end,
})

local cfg_card = tab_cfg.Toggle({
    Title    = "บันทึกการตั้งค่า & Webhook",
    Info     = "Save, Load & Discord Webhook",
    Default  = true,
    Callback = function(_) end,
}, false)

UI_CONTROLS["auto_save_enabled"] = cfg_card:Toggle({
    Title    = T("auto_save"),
    Default  = true,
    Callback = function(value)
        auto_save_enabled = value
    end,
}, false)

UI_CONTROLS["auto_load_on_start"] = cfg_card:Toggle({
    Title    = "โหลด Config ล่าสุดอัตโนมัติเมื่อเริ่มเกม (Auto Load on Start)",
    Default  = true,
    Callback = function(value)
        auto_load_on_start = value
    end,
}, false)

cfg_card:Line()

-- 1. Profile Name Textbox
UI_CONTROLS["new_config_profile_name"] = cfg_card:Textbox({
    Title    = T("cfg_name_box"),
    Default  = new_config_profile_name or "default",
    Callback = function(value)
        if value and value ~= "" then
            new_config_profile_name = value
        end
    end,
})

-- 2. Save Named Profile Button
cfg_card:Button({
    Title    = "💾 " .. T("save_named_btn"),
    Callback = function()
        local inputVal = nil
        pcall(function()
            if UI_CONTROLS["new_config_profile_name"] and UI_CONTROLS["new_config_profile_name"].Get then
                inputVal = UI_CONTROLS["new_config_profile_name"]:Get()
            end
        end)
        local nameToSave = (inputVal and inputVal ~= "" and inputVal) or new_config_profile_name or selected_config_profile or "default"
        save_config(nameToSave, false)
    end,
})

-- 3. Profile Selector Dropdown
config_dropdown_ctrl = cfg_card:Dropdown({
    Title    = T("cfg_select_drop"),
    List     = get_saved_configs(),
    Multi    = false,
    Default  = selected_config_profile or "default",
    Callback = function(value)
        if value and value ~= "" then
            selected_config_profile = value
            new_config_profile_name = value
            sync_ui("new_config_profile_name", value)
        end
    end,
})
UI_CONTROLS["selected_config_profile"] = config_dropdown_ctrl

-- 4. Load Selected Profile Button
cfg_card:Button({
    Title    = "📂 " .. T("load_selected_btn"),
    Callback = function()
        local dropVal = nil
        pcall(function()
            if config_dropdown_ctrl and config_dropdown_ctrl.Get then
                dropVal = config_dropdown_ctrl:Get()
            end
        end)
        local nameToLoad = (dropVal and dropVal ~= "" and dropVal) or selected_config_profile or "default"
        load_config(nameToLoad, false)
    end,
})

-- 5. Delete Selected Profile Button
cfg_card:Button({
    Title    = "🗑️ " .. T("delete_selected_btn"),
    Callback = function()
        local dropVal = nil
        pcall(function()
            if config_dropdown_ctrl and config_dropdown_ctrl.Get then
                dropVal = config_dropdown_ctrl:Get()
            end
        end)
        local nameToDelete = (dropVal and dropVal ~= "" and dropVal) or selected_config_profile or "default"
        delete_config(nameToDelete)
    end,
})

-- 6. Refresh Config List Button
cfg_card:Button({
    Title    = "🔄 " .. T("refresh_cfg_btn"),
    Callback = function()
        refresh_config_dropdown()
    end,
})

cfg_card:Line()

UI_CONTROLS["webhook_enabled"] = cfg_card:Toggle({
    Title    = T("webhook_tog"),
    Default  = false,
    Callback = function(value)
        webhook_enabled = value
    end,
}, false)

UI_CONTROLS["webhook_url"] = cfg_card:Textbox({
    Title    = T("webhook_box"),
    Default  = webhook_url,
    Callback = function(value)
        webhook_url = value
    end,
})

cfg_card:Button({
    Title    = T("webhook_test"),
    Callback = function()
        send_discord_webhook("**ข้อความทดสอบ Webhook จากในเกม Ride A Pet**")
        pcall(function()
            game:GetService("StarterGui"):SetCore("SendNotification", {
                Title    = "Discord Webhook",
                Text     = "ส่งข้อความทดสอบเรียบร้อยแล้ว!",
                Duration = 3,
            })
        end)
    end,
})

-- ─── Script Title & Credit Display ───────────────────────────
pcall(function()
    local CoreGui = game:GetService("CoreGui")
    for _, gui in CoreGui:GetChildren() do
        if gui:IsA("ScreenGui") and gui:FindFirstChild("@main") then
            local main = gui["@main"]
            if not main:FindFirstChild("ScriptTitleLabel") then
                local tLbl = Instance.new("TextLabel")
                tLbl.Name = "ScriptTitleLabel"
                tLbl.Size = UDim2.new(1, -40, 0, 24)
                tLbl.Position = UDim2.new(0, 16, 0, 6)
                tLbl.BackgroundTransparency = 1
                tLbl.Text = "PAYOMBØYZ ขี่สัตว์ไปกับพยอมบอย"
                tLbl.TextColor3 = Color3.fromRGB(255, 35, 55)
                tLbl.Font = Enum.Font.GothamBlack
                tLbl.TextSize = 13
                tLbl.TextXAlignment = Enum.TextXAlignment.Left
                tLbl.ZIndex = 50
                tLbl.Parent = main
            else
                main.ScriptTitleLabel.Text = "PAYOMBØYZ ขี่สัตว์ไปกับพยอมบอย"
                main.ScriptTitleLabel.TextColor3 = Color3.fromRGB(255, 35, 55)
            end
            if not main:FindFirstChild("CreditLabel") then
                local cLbl = Instance.new("TextLabel")
                cLbl.Name = "CreditLabel"
                cLbl.Size = UDim2.new(0, 160, 0, 18)
                cLbl.Position = UDim2.new(1, -34, 1, -22)
                cLbl.BackgroundTransparency = 1
                cLbl.Text = "ย่อและขยายหน้าต่างสคริป"
                cLbl.TextColor3 = Color3.fromRGB(155, 165, 185)
                cLbl.Font = Enum.Font.GothamMedium
                cLbl.TextSize = 11
                cLbl.TextXAlignment = Enum.TextXAlignment.Right
                cLbl.ZIndex = 50
                cLbl.Parent = main
            else
                main.CreditLabel.Text = "ย่อและขยายหน้าต่างสคริป"
                main.CreditLabel.Position = UDim2.new(1, -34, 1, -22)
                main.CreditLabel.Size = UDim2.new(0, 160, 0, 18)
            end
            if not main:FindFirstChild("PagePrevBtn") then
                local prevBtn = Instance.new("TextButton")
                prevBtn.Name = "PagePrevBtn"
                prevBtn.Size = UDim2.new(0, 26, 0, 20)
                prevBtn.Position = UDim2.new(1, -66, 0, 8)
                prevBtn.BackgroundColor3 = Color3.fromRGB(22, 28, 44)
                prevBtn.BorderSizePixel = 0
                prevBtn.Text = "◀"
                prevBtn.TextColor3 = Color3.fromRGB(255, 35, 55)
                prevBtn.Font = Enum.Font.GothamBold
                prevBtn.TextSize = 11
                prevBtn.ZIndex = 60
                prevBtn.Parent = main
                local c = Instance.new("UICorner", prevBtn)
                c.CornerRadius = UDim.new(0, 6)
                prevBtn.MouseButton1Click:Connect(function()
                    pcall(function()
                        local page = main:FindFirstChild("@page")
                        local uipage = page and page:FindFirstChildWhichIsA("UIPageLayout")
                        if uipage then uipage:Previous() end
                    end)
                end)
            else
                main.PagePrevBtn.TextColor3 = Color3.fromRGB(255, 35, 55)
            end
            if not main:FindFirstChild("PageNextBtn") then
                local nextBtn = Instance.new("TextButton")
                nextBtn.Name = "PageNextBtn"
                nextBtn.Size = UDim2.new(0, 26, 0, 20)
                nextBtn.Position = UDim2.new(1, -34, 0, 8)
                nextBtn.BackgroundColor3 = Color3.fromRGB(22, 28, 44)
                nextBtn.BorderSizePixel = 0
                nextBtn.Text = "▶"
                nextBtn.TextColor3 = Color3.fromRGB(255, 35, 55)
                nextBtn.Font = Enum.Font.GothamBold
                nextBtn.TextSize = 11
                nextBtn.ZIndex = 60
                nextBtn.Parent = main
                local c = Instance.new("UICorner", nextBtn)
                c.CornerRadius = UDim.new(0, 6)
                nextBtn.MouseButton1Click:Connect(function()
                    pcall(function()
                        local page = main:FindFirstChild("@page")
                        local uipage = page and page:FindFirstChildWhichIsA("UIPageLayout")
                        if uipage then uipage:Next() end
                    end)
                end)
            else
                main.PageNextBtn.TextColor3 = Color3.fromRGB(255, 35, 55)
            end
        end
    end
end)
end -- Close Tab 6
end
init_main_tabs()

local function init_particles_engine()
-- ─── Festival & Seasonal Particles Engine ─────────────────────

local function get_main_particles_layer()
    local CoreGui = game:GetService("CoreGui")
    for _, g in ipairs(CoreGui:GetChildren()) do
        if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
            local main = g["@main"]
            local pLayer = main:FindFirstChild("@particles")
            if not pLayer then
                pLayer = Instance.new("Frame")
                pLayer.Name = "@particles"
                pLayer.BackgroundTransparency = 1
                pLayer.Size = UDim2.fromScale(1, 1)
                pLayer.ClipsDescendants = true
                pLayer.ZIndex = 1
                local c = Instance.new("UICorner", pLayer)
                c.CornerRadius = UDim.new(0, 10)
                pLayer.Parent = main
            end
            return pLayer
        end
    end
    local PlayerGui = LocalPlayer:FindFirstChild("PlayerGui")
    if PlayerGui then
        for _, g in ipairs(PlayerGui:GetChildren()) do
            if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                local main = g["@main"]
                local pLayer = main:FindFirstChild("@particles")
                if not pLayer then
                    pLayer = Instance.new("Frame")
                    pLayer.Name = "@particles"
                    pLayer.BackgroundTransparency = 1
                    pLayer.Size = UDim2.fromScale(1, 1)
                    pLayer.ClipsDescendants = true
                    pLayer.ZIndex = 1
                    local c = Instance.new("UICorner", pLayer)
                    c.CornerRadius = UDim.new(0, 10)
                    pLayer.Parent = main
                end
                return pLayer
            end
        end
    end
    return nil
end

clear_all_particles = function()
    particle_generation = particle_generation + 1
    active_particles_count = 0
    local pLayer = get_main_particles_layer()
    if pLayer then
        for _, ch in ipairs(pLayer:GetChildren()) do
            if ch:IsA("GuiObject") and ch.Name ~= "UICorner" then
                pcall(function() ch:Destroy() end)
            end
        end
    end
end
_G.RideAPet_ClearParticles = clear_all_particles

local FESTIVALS = {
    {
        name = "NewYear",
        label = "ปีใหม่ (New Year)",
        check = function(m, d) return (m == 12 and d >= 31) or (m == 1 and d <= 5) end,
        color = Color3.fromRGB(255, 215, 0), secondaryColor = Color3.fromRGB(255, 80, 140),
        spawnRate = 0.18, size = {8, 14}, direction = "down", duration = {4, 7}, shape = "confetti", maxOnScreen = 20,
    },
    {
        name = "Valentine",
        label = "วาเลนไทน์ (Valentine)",
        check = function(m, d) return m == 2 and d >= 10 and d <= 16 end,
        color = Color3.fromRGB(255, 90, 120), secondaryColor = Color3.fromRGB(255, 150, 170),
        spawnRate = 0.5, size = {12, 18}, direction = "up", duration = {5, 8}, shape = "heart", maxOnScreen = 8,
    },
    {
        name = "Songkran",
        label = "สงกรานต์ (Songkran)",
        check = function(m, d) return m == 4 and d >= 12 and d <= 16 end,
        color = Color3.fromRGB(0, 210, 255), secondaryColor = Color3.fromRGB(60, 160, 255),
        spawnRate = 0.15, size = {7, 12}, direction = "down", duration = {3.5, 6}, shape = "drop", maxOnScreen = 22,
    },
    {
        name = "Halloween",
        label = "ฮาโลวีน (Halloween)",
        check = function(m, d) return m == 10 and d >= 24 and d <= 31 end,
        color = Color3.fromRGB(255, 140, 20), secondaryColor = Color3.fromRGB(255, 166, 64),
        spawnRate = 0.7, size = {16, 24}, direction = "down", duration = {4, 6.5}, shape = "pumpkin", maxOnScreen = 8,
    },
    {
        name = "LoyKrathong",
        label = "ลอยกระทง (Loy Krathong)",
        check = function(m, d) return m == 11 and d >= 10 and d <= 25 end,
        color = Color3.fromRGB(255, 196, 102), secondaryColor = Color3.fromRGB(255, 150, 60),
        spawnRate = 0.35, size = {6, 11}, direction = "up", duration = {6, 10}, shape = "glow", maxOnScreen = 16,
    },
    {
        name = "Christmas",
        label = "คริสต์มาส (Christmas)",
        check = function(m, d) return m == 12 and d >= 20 and d <= 30 end,
        color = Color3.fromRGB(255, 255, 255), secondaryColor = Color3.fromRGB(225, 240, 255),
        spawnRate = 0.12, size = {3, 7}, direction = "down", duration = {4, 7}, shape = "circle", maxOnScreen = 25,
    },
}

local SEASONS = {
    Summer = {
        name = "Summer",
        label = "ฤดูร้อน (Summer)",
        check = function(m, d) return m == 3 or m == 4 or (m == 5 and d <= 15) end,
        color = Color3.fromRGB(255, 200, 60), secondaryColor = Color3.fromRGB(255, 130, 30),
        spawnRate = 0.28, size = {5, 10}, direction = "up", duration = {5, 9}, shape = "glow", maxOnScreen = 16,
    },
    Rainy = {
        name = "Rainy",
        label = "ฤดูฝน (Rainy)",
        check = function(m, d) return (m == 5 and d > 15) or (m >= 6 and m <= 9) or (m == 10 and d <= 15) end,
        color = Color3.fromRGB(100, 200, 255), secondaryColor = Color3.fromRGB(160, 230, 255),
        spawnRate = 0.18, size = {6, 11}, direction = "down", duration = {3.5, 6}, shape = "drop", maxOnScreen = 20,
    },
    Autumn = {
        name = "Autumn",
        label = "ฤดูใบไม้ร่วง (Autumn)",
        check = function(m, d) return (m == 10 and d > 15) or m == 11 end,
        color = Color3.fromRGB(225, 115, 35), secondaryColor = Color3.fromRGB(210, 160, 40),
        spawnRate = 0.24, size = {9, 15}, direction = "down", duration = {4.5, 7.5}, shape = "leaf", maxOnScreen = 16,
    },
    Winter = {
        name = "Winter",
        label = "ฤดูหนาว (Winter)",
        check = function(m, d) return m == 12 or m == 1 end,
        color = Color3.fromRGB(240, 248, 255), secondaryColor = Color3.fromRGB(180, 220, 255),
        spawnRate = 0.15, size = {3, 6}, direction = "down", duration = {4, 7}, shape = "circle", maxOnScreen = 22,
    },
    Spring = {
        name = "Spring",
        label = "ฤดูใบไม้ผลิ (Spring)",
        check = function(m, d) return m == 2 end,
        color = Color3.fromRGB(255, 180, 210), secondaryColor = Color3.fromRGB(255, 140, 185),
        spawnRate = 0.22, size = {8, 14}, direction = "down", duration = {4.5, 7.5}, shape = "petal", maxOnScreen = 18,
    },
}

local function get_active_particle_theme()
    local sel = tostring(particle_theme_setting or "Auto")
    if sel:find("Auto") then
        local now = os.date("*t")
        local m, d = now.month, now.day
        for _, fest in ipairs(FESTIVALS) do
            if fest.check(m, d) then
                return fest
            end
        end
        for _, sea in pairs(SEASONS) do
            if sea.check(m, d) then
                return sea
            end
        end
        return SEASONS.Rainy
    end

    for _, fest in ipairs(FESTIVALS) do
        if sel == fest.label or sel:find(fest.name, 1, true) or fest.label:find(sel, 1, true) then
            return fest
        end
    end
    for _, sea in pairs(SEASONS) do
        if sel == sea.label or sel:find(sea.name, 1, true) or sea.label:find(sel, 1, true) then
            return sea
        end
    end
    return SEASONS.Rainy
end

local function buildParticleShape(shape, size, color)
    local container = Instance.new("Frame")
    container.BackgroundTransparency = 1
    container.BorderSizePixel = 0
    container.ZIndex = 1
    container.AnchorPoint = Vector2.new(0.5, 0.5)
    local parts = {}
    local function addPart(obj, prop)
        table.insert(parts, {object = obj, property = prop})
    end

    if shape == "drop" then
        local w = size * 0.8
        container.Size = UDim2.fromOffset(w, size * 1.3)
        local bulb = Instance.new("Frame", container)
        bulb.AnchorPoint = Vector2.new(0.5, 1)
        bulb.Position = UDim2.new(0.5, 0, 1, 0)
        bulb.Size = UDim2.fromOffset(w, w)
        bulb.BackgroundColor3 = color
        bulb.BorderSizePixel = 0
        bulb.ZIndex = 1
        Instance.new("UICorner", bulb).CornerRadius = UDim.new(1, 0)
        addPart(bulb, "BackgroundTransparency")

        local tip = Instance.new("Frame", container)
        tip.AnchorPoint = Vector2.new(0.5, 0.5)
        tip.Position = UDim2.new(0.5, 0, 0.32, 0)
        tip.Size = UDim2.fromOffset(w * 0.72, w * 0.72)
        tip.Rotation = 45
        tip.BackgroundColor3 = color
        tip.BorderSizePixel = 0
        tip.ZIndex = 1
        Instance.new("UICorner", tip).CornerRadius = UDim.new(0, 2)
        addPart(tip, "BackgroundTransparency")

    elseif shape == "glow" then
        container.Size = UDim2.fromOffset(size * 2.2, size * 2.2)
        local halo = Instance.new("Frame", container)
        halo.AnchorPoint = Vector2.new(0.5, 0.5)
        halo.Position = UDim2.fromScale(0.5, 0.5)
        halo.Size = UDim2.fromScale(1, 1)
        halo.BackgroundColor3 = color
        halo.BackgroundTransparency = 0.65
        halo.BorderSizePixel = 0
        halo.ZIndex = 1
        Instance.new("UICorner", halo).CornerRadius = UDim.new(1, 0)
        addPart(halo, "BackgroundTransparency")

        local core = Instance.new("Frame", container)
        core.AnchorPoint = Vector2.new(0.5, 0.5)
        core.Position = UDim2.fromScale(0.5, 0.5)
        core.Size = UDim2.fromOffset(size, size)
        core.BackgroundColor3 = Color3.fromRGB(255, 240, 210)
        core.BorderSizePixel = 0
        core.ZIndex = 1
        Instance.new("UICorner", core).CornerRadius = UDim.new(1, 0)
        addPart(core, "BackgroundTransparency")

    elseif shape == "confetti" then
        container.Size = UDim2.fromOffset(size * 1.4, size * 0.7)
        container.Rotation = math.random(0, 360)
        local rect = Instance.new("Frame", container)
        rect.Size = UDim2.fromScale(1, 1)
        rect.BackgroundColor3 = color
        rect.BorderSizePixel = 0
        rect.ZIndex = 1
        Instance.new("UICorner", rect).CornerRadius = UDim.new(0, 2)
        addPart(rect, "BackgroundTransparency")

    elseif shape == "heart" then
        container.Size = UDim2.fromOffset(size * 1.4, size * 1.4)
        local icon = Instance.new("ImageLabel", container)
        icon.BackgroundTransparency = 1
        icon.Size = UDim2.fromScale(1, 1)
        icon.Image = "rbxassetid://86573834471213"
        icon.ImageColor3 = color
        icon.ImageTransparency = 0.3
        icon.ScaleType = Enum.ScaleType.Fit
        icon.ZIndex = 1
        addPart(icon, "ImageTransparency")

    elseif shape == "pumpkin" then
        container.Size = UDim2.fromOffset(size * 1.6, size * 1.6)
        local icon = Instance.new("ImageLabel", container)
        icon.BackgroundTransparency = 1
        icon.Size = UDim2.fromScale(1, 1)
        icon.Image = "rbxassetid://110693415684859"
        icon.ImageColor3 = color
        icon.ImageTransparency = 0.35
        icon.ScaleType = Enum.ScaleType.Fit
        icon.ZIndex = 1
        addPart(icon, "ImageTransparency")

    elseif shape == "petal" then
        container.Size = UDim2.fromOffset(size * 1.3, size * 0.8)
        container.Rotation = math.random(0, 360)
        local petal = Instance.new("Frame", container)
        petal.Size = UDim2.fromScale(1, 1)
        petal.BackgroundColor3 = color
        petal.BorderSizePixel = 0
        petal.ZIndex = 1
        Instance.new("UICorner", petal).CornerRadius = UDim.new(0.6, 0)
        addPart(petal, "BackgroundTransparency")

    elseif shape == "leaf" then
        container.Size = UDim2.fromOffset(size * 1.4, size * 0.9)
        container.Rotation = math.random(0, 360)
        local leaf = Instance.new("Frame", container)
        leaf.Size = UDim2.fromScale(1, 1)
        leaf.BackgroundColor3 = color
        leaf.BorderSizePixel = 0
        leaf.ZIndex = 1
        Instance.new("UICorner", leaf).CornerRadius = UDim.new(0.5, 0)
        addPart(leaf, "BackgroundTransparency")

    else -- circle
        container.Size = UDim2.fromOffset(size, size)
        local dot = Instance.new("Frame", container)
        dot.Size = UDim2.fromScale(1, 1)
        dot.BackgroundColor3 = color
        dot.BorderSizePixel = 0
        dot.ZIndex = 1
        Instance.new("UICorner", dot).CornerRadius = UDim.new(1, 0)
        addPart(dot, "BackgroundTransparency")
    end

    return container, parts
end

-- Particle lifecycle background loop
_G.RideAPet_StopParticles = function()
    particle_generation = particle_generation + 1
    active_particles_count = 0
    if clear_all_particles then
        clear_all_particles()
    end
end

task.spawn(function()
    local mySession = CURRENT_SESSION_ID
    while _G.RideAPet_Session == mySession do
        task.wait(0.18)
        if _G.RideAPet_Session ~= mySession then break end
        if particle_enabled then
            local pLayer = get_main_particles_layer()
            if pLayer and pLayer.Parent and pLayer.Parent.Visible then
                local theme = get_active_particle_theme()
                local maxOnScreen = theme.maxOnScreen or 20
                if active_particles_count < maxOnScreen then
                    active_particles_count = active_particles_count + 1
                    local thisGen = particle_generation
                    task.spawn(function()
                        if _G.RideAPet_Session ~= mySession or particle_generation ~= thisGen then
                            active_particles_count = math.max(0, active_particles_count - 1)
                            return
                        end
                        local size = math.random(theme.size[1], theme.size[2])
                        local color = math.random() > 0.5 and theme.color or theme.secondaryColor
                        local particle, parts = buildParticleShape(theme.shape, size, color)
                        if not particle then
                            active_particles_count = math.max(0, active_particles_count - 1)
                            return
                        end
                        particle.Parent = pLayer

                        local goingUp = theme.direction == "up"
                        local half = particle.Size.Y.Offset / 2
                        local halfX = particle.Size.X.Offset / 2
                        local layerWidth = math.max(pLayer.AbsoluteSize.X, 1)
                        local insetScaleX = math.clamp(halfX / layerWidth, 0, 0.5)
                        local minX, maxX = insetScaleX, 1 - insetScaleX
                        local startX = minX + math.random() * (maxX - minX)
                        local startEdge = goingUp and 1 or 0
                        local endEdge = goingUp and 0 or 1
                        local startOffset = goingUp and -half or half
                        local endOffset = goingUp and half or -half
                        particle.Position = UDim2.new(startX, 0, startEdge, startOffset)

                        local duration = theme.duration[1] + math.random() * (theme.duration[2] - theme.duration[1])
                        local drift = math.random(-180, 180) / 1000

                        local moveTween = TweenService:Create(particle, TweenInfo.new(duration, Enum.EasingStyle.Linear), {
                            Position = UDim2.new(math.clamp(startX + drift, minX, maxX), 0, endEdge, endOffset)
                        })
                        moveTween:Play()

                        local fadeIn = math.min(duration * 0.25, 0.35)
                        local fadeOut = math.min(duration * 0.25, 0.35)
                        for _, part in ipairs(parts) do
                            part.object[part.property] = 1
                            TweenService:Create(part.object, TweenInfo.new(fadeIn, Enum.EasingStyle.Linear), {
                                [part.property] = (part.property == "ImageTransparency" and 0.3 or 0)
                            }):Play()
                        end

                        task.delay(math.max(duration - fadeOut, fadeIn), function()
                            if particle_generation == thisGen and _G.RideAPet_Session == mySession then
                                for _, part in ipairs(parts) do
                                    if part.object and part.object.Parent then
                                        TweenService:Create(part.object, TweenInfo.new(fadeOut, Enum.EasingStyle.Linear), {
                                            [part.property] = 1
                                        }):Play()
                                    end
                                end
                            end
                        end)

                        if theme.shape == "confetti" or theme.shape == "drop" then
                            TweenService:Create(particle, TweenInfo.new(duration, Enum.EasingStyle.Linear), {
                                Rotation = particle.Rotation + math.random(180, 540) * (goingUp and -1 or 1)
                            }):Play()
                        elseif theme.shape == "pumpkin" then
                            local spinDir = math.random() > 0.5 and 1 or -1
                            TweenService:Create(particle, TweenInfo.new(duration, Enum.EasingStyle.Linear), {
                                Rotation = particle.Rotation + (60 * spinDir)
                            }):Play()
                        elseif theme.shape == "petal" or theme.shape == "leaf" then
                            local spinDir = math.random() > 0.5 and 1 or -1
                            TweenService:Create(particle, TweenInfo.new(duration, Enum.EasingStyle.Linear), {
                                Rotation = particle.Rotation + math.random(90, 270) * spinDir
                            }):Play()
                        end

                        task.delay(duration, function()
                            if particle and particle.Parent then
                                particle:Destroy()
                            end
                            if particle_generation == thisGen then
                                active_particles_count = math.max(0, active_particles_count - 1)
                            end
                        end)
                    end)
                end
                task.wait(theme.spawnRate or 0.2)
            end
        end
    end
end)
end
init_particles_engine()

-- ─── Floating HUD Button & Dashboard ──────────────────────────

local HudGui, DashFrame
local dash_visible = true
local coinsVal, coinsTop, rebirthVal, rebirthTop, eggsVal, eggsTop, petsVal, petsTop
local BestNameLabel, BestRarityLabel, BestImg, SessionLbl, DashTitle, BestTitleLabel
local toggle_script_window
local isMobile = UserInputService.TouchEnabled and not UserInputService.MouseEnabled

local function init_floating_hud()
    HudGui = Instance.new("ScreenGui")
    HudGui.Name           = "RideAPetHUD"
    HudGui.ResetOnSpawn   = false
    HudGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    HudGui.DisplayOrder   = 999
    pcall(function() HudGui.Parent = game:GetService("CoreGui") end)
    if not HudGui.Parent then
        HudGui.Parent = LocalPlayer:WaitForChild("PlayerGui")
    end

-- Pill container
local HudFrame = Instance.new("Frame")
HudFrame.Name                  = "HudFrame"
HudFrame.Size                  = UDim2.new(0, 195, 0, 54)
HudFrame.Position              = isMobile
    and UDim2.new(0, 10, 0, 70)
    or  UDim2.new(0, 10, 0.5, -27)
HudFrame.BackgroundColor3      = Color3.fromRGB(8, 11, 20)
HudFrame.BackgroundTransparency = 0.12
HudFrame.BorderSizePixel        = 0
HudFrame.Active                 = true
HudFrame.Parent                 = HudGui
Instance.new("UICorner", HudFrame).CornerRadius = UDim.new(1, 0)

local hudStroke = Instance.new("UIStroke")
hudStroke.Color       = Color3.fromRGB(255, 35, 55)
hudStroke.Thickness   = 1.5
hudStroke.Transparency = 0.20
hudStroke.Parent      = HudFrame

-- Avatar thumbnail
local AvatarImg = Instance.new("ImageLabel")
AvatarImg.Name               = "Avatar"
AvatarImg.Size               = UDim2.new(0, 40, 0, 40)
AvatarImg.Position           = UDim2.new(0, 7, 0.5, -20)
AvatarImg.BackgroundColor3   = Color3.fromRGB(18, 22, 34)
AvatarImg.BorderSizePixel    = 0
AvatarImg.ScaleType          = Enum.ScaleType.Fit
AvatarImg.Parent             = HudFrame
Instance.new("UICorner", AvatarImg).CornerRadius = UDim.new(1, 0)

pcall(function()
    AvatarImg.Image = Players:GetUserThumbnailAsync(
        LocalPlayer.UserId,
        Enum.ThumbnailType.HeadShot,
        Enum.ThumbnailSize.Size48x48
    )
end)

local avatarStroke = Instance.new("UIStroke")
avatarStroke.Color        = Color3.fromRGB(255, 35, 55)
avatarStroke.Thickness    = 1.5
avatarStroke.Transparency = 0.15
avatarStroke.Parent       = AvatarImg

-- Username
local UserLabel = Instance.new("TextLabel")
UserLabel.Name               = "UserName"
UserLabel.Size               = UDim2.new(1, -57, 0, 19)
UserLabel.Position           = UDim2.new(0, 53, 0, 7)
UserLabel.BackgroundTransparency = 1
UserLabel.Text               = LocalPlayer.DisplayName
UserLabel.TextColor3         = Color3.fromRGB(240, 250, 255)
UserLabel.TextSize           = 13
UserLabel.Font               = Enum.Font.GothamBold
UserLabel.TextXAlignment     = Enum.TextXAlignment.Left
UserLabel.TextTruncate       = Enum.TextTruncate.AtEnd
UserLabel.Parent             = HudFrame

-- FPS / Ping stats
StatsLabel = Instance.new("TextLabel")
StatsLabel.Name               = "Stats"
StatsLabel.Size               = UDim2.new(1, -57, 0, 16)
StatsLabel.Position           = UDim2.new(0, 53, 0, 28)
StatsLabel.BackgroundTransparency = 1
StatsLabel.Text               = T("hud_fps") .. ": -- | " .. T("hud_ping") .. ": --"
StatsLabel.TextColor3         = Color3.fromRGB(255, 45, 65)
StatsLabel.TextSize           = 11
StatsLabel.Font               = Enum.Font.GothamMedium
StatsLabel.TextXAlignment     = Enum.TextXAlignment.Left
StatsLabel.Parent             = HudFrame

-- Invisible click area
local HudBtn = Instance.new("TextButton")
HudBtn.Size             = UDim2.new(1, 0, 1, 0)
HudBtn.BackgroundTransparency = 1
HudBtn.Text             = ""
HudBtn.Parent           = HudFrame

-- Drag
do
    local dragging, dragStart, startPos, dragInput
    HudBtn.InputBegan:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseButton1
        or inp.UserInputType == Enum.UserInputType.Touch then
            dragging  = true
            dragStart = inp.Position
            startPos  = HudFrame.Position
            inp.Changed:Connect(function()
                if inp.UserInputState == Enum.UserInputState.End then dragging = false end
            end)
        end
    end)
    HudBtn.InputChanged:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseMovement
        or inp.UserInputType == Enum.UserInputType.Touch then
            dragInput = inp
        end
    end)
    UserInputService.InputChanged:Connect(function(inp)
        if inp == dragInput and dragging then
            local delta = inp.Position - dragStart
            HudFrame.Position = UDim2.new(
                startPos.X.Scale, startPos.X.Offset + delta.X,
                startPos.Y.Scale, startPos.Y.Offset + delta.Y
            )
        end
    end)
end

-- Toggle main UI window on click (Mobile & PC)
local ui_visible = true

function toggle_script_window()
    ui_visible = not ui_visible
    pcall(function()
        local CoreGui = game:GetService("CoreGui")
        for _, g in ipairs(CoreGui:GetChildren()) do
            if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                g.Enabled = ui_visible
                g["@main"].Visible = ui_visible
            end
        end
        local PlayerGui = LocalPlayer:FindFirstChild("PlayerGui")
        if PlayerGui then
            for _, g in ipairs(PlayerGui:GetChildren()) do
                if g:IsA("ScreenGui") and g:FindFirstChild("@main") then
                    g.Enabled = ui_visible
                    g["@main"].Visible = ui_visible
                end
            end
        end
    end)
    -- Visual feedback via stroke color on mobile HUD pill
    TweenService:Create(hudStroke, TweenInfo.new(0.2), {
        Color = ui_visible
            and Color3.fromRGB(0, 210, 255)
            or  Color3.fromRGB(255, 75, 100)
    }):Play()
end

HudBtn.MouseButton1Click:Connect(toggle_script_window)

UserInputService.InputBegan:Connect(function(inp, processed)
    if not processed and (inp.KeyCode == Enum.KeyCode.RightControl or inp.KeyCode == Enum.KeyCode.Insert) then
        toggle_script_window()
    end
end)
end
init_floating_hud()

local function init_dashboard()
-- ─── 2D Radar / Monitoring Dashboard (PayomboyZ Crimson & Obsidian) ──────

DashFrame = Instance.new("Frame")
DashFrame.Name                   = "MonitoringDashboard"
DashFrame.Size                   = UDim2.new(0, 310, 0, 292)
DashFrame.Position               = isMobile
    and UDim2.new(0.5, -155, 0.5, -146)
    or  UDim2.new(1, -325, 0, 60)
DashFrame.BackgroundColor3       = Color3.fromRGB(11, 14, 22)
DashFrame.BackgroundTransparency  = 0.05
DashFrame.BorderSizePixel         = 0
DashFrame.Visible                = true
DashFrame.Active                 = true
DashFrame.Parent                 = HudGui
Instance.new("UICorner", DashFrame).CornerRadius = UDim.new(0, 12)

local dashStroke = Instance.new("UIStroke")
dashStroke.Color        = Color3.fromRGB(255, 36, 66)
dashStroke.Thickness    = 1.5
dashStroke.Transparency = 0.35
dashStroke.Parent       = DashFrame

-- Header Title
local DashHeader = Instance.new("Frame")
DashHeader.Name                   = "Header"
DashHeader.Size                   = UDim2.new(1, 0, 0, 32)
DashHeader.BackgroundColor3       = Color3.fromRGB(16, 20, 32)
DashHeader.BorderSizePixel         = 0
DashHeader.Parent                 = DashFrame
Instance.new("UICorner", DashHeader).CornerRadius = UDim.new(0, 12)

DashTitle = Instance.new("TextLabel")
DashTitle.Name                   = "Title"
DashTitle.Size                   = UDim2.new(1, -70, 1, 0)
DashTitle.Position               = UDim2.new(0, 12, 0, 0)
DashTitle.BackgroundTransparency  = 1
DashTitle.Text                   = "⚡ " .. T("dash_title")
DashTitle.TextColor3             = Color3.fromRGB(255, 45, 75)
DashTitle.TextSize               = 12
DashTitle.Font                   = Enum.Font.GothamBold
DashTitle.TextXAlignment         = Enum.TextXAlignment.Left
DashTitle.Parent                 = DashHeader

-- Quick Teleport to Plot Button on Dashboard Header
local DashTpBtn = Instance.new("TextButton")
DashTpBtn.Name                   = "TpPlot"
DashTpBtn.Size                   = UDim2.new(0, 26, 0, 22)
DashTpBtn.Position               = UDim2.new(1, -58, 0, 5)
DashTpBtn.BackgroundColor3       = Color3.fromRGB(24, 28, 44)
DashTpBtn.BorderSizePixel         = 0
DashTpBtn.Text                   = "🏠"
DashTpBtn.TextSize               = 12
DashTpBtn.TextColor3             = Color3.fromRGB(255, 255, 255)
DashTpBtn.Parent                 = DashHeader
Instance.new("UICorner", DashTpBtn).CornerRadius = UDim.new(0, 6)

DashTpBtn.MouseButton1Click:Connect(function()
    pcall(function()
        local tpRemote = Remotes.Game:FindFirstChild("TeleportToPlot")
        if tpRemote then tpRemote:FireServer() end
        local plot = get_my_plot()
        if plot and LocalPlayer.Character and LocalPlayer.Character.PrimaryPart then
            LocalPlayer.Character.PrimaryPart.AssemblyLinearVelocity = Vector3.zero
            LocalPlayer.Character.PrimaryPart.CFrame = plot:GetPivot() + Vector3.new(0, 6, 0)
        end
    end)
end)

-- Close Button
local DashCloseBtn = Instance.new("TextButton")
DashCloseBtn.Name                   = "Close"
DashCloseBtn.Size                   = UDim2.new(0, 24, 0, 22)
DashCloseBtn.Position               = UDim2.new(1, -28, 0, 5)
DashCloseBtn.BackgroundColor3       = Color3.fromRGB(38, 16, 24)
DashCloseBtn.BorderSizePixel         = 0
DashCloseBtn.Text                   = "✕"
DashCloseBtn.TextSize               = 11
DashCloseBtn.TextColor3             = Color3.fromRGB(255, 80, 100)
DashCloseBtn.Font                   = Enum.Font.GothamBold
DashCloseBtn.Parent                 = DashHeader
Instance.new("UICorner", DashCloseBtn).CornerRadius = UDim.new(0, 6)

DashCloseBtn.MouseButton1Click:Connect(function()
    dash_visible = false
    DashFrame.Visible = false
end)

-- Dragging for Dashboard
do
    local dDragging, dStart, dPos, dInput
    DashHeader.InputBegan:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseButton1
        or inp.UserInputType == Enum.UserInputType.Touch then
            dDragging = true
            dStart = inp.Position
            dPos = DashFrame.Position
            inp.Changed:Connect(function()
                if inp.UserInputState == Enum.UserInputState.End then dDragging = false end
            end)
        end
    end)
    DashHeader.InputChanged:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseMovement
        or inp.UserInputType == Enum.UserInputType.Touch then
            dInput = inp
        end
    end)
    UserInputService.InputChanged:Connect(function(inp)
        if inp == dInput and dDragging then
            local delta = inp.Position - dStart
            DashFrame.Position = UDim2.new(
                dPos.X.Scale, dPos.X.Offset + delta.X,
                dPos.Y.Scale, dPos.Y.Offset + delta.Y
            )
        end
    end)
end

-- Best Egg / Pet Feature Box
local BestBox = Instance.new("Frame")
BestBox.Name                   = "BestBox"
BestBox.Size                   = UDim2.new(1, -20, 0, 62)
BestBox.Position               = UDim2.new(0, 10, 0, 38)
BestBox.BackgroundColor3       = Color3.fromRGB(15, 18, 28)
BestBox.BorderSizePixel         = 0
BestBox.Parent                 = DashFrame
Instance.new("UICorner", BestBox).CornerRadius = UDim.new(0, 8)

local bestStroke = Instance.new("UIStroke")
bestStroke.Color        = Color3.fromRGB(255, 36, 66)
bestStroke.Thickness    = 1
bestStroke.Transparency = 0.65
bestStroke.Parent       = BestBox

BestImg = Instance.new("ImageLabel")
BestImg.Name                   = "BestImg"
BestImg.Size                   = UDim2.new(0, 50, 0, 50)
BestImg.Position               = UDim2.new(0, 6, 0.5, -25)
BestImg.BackgroundColor3       = Color3.fromRGB(22, 26, 40)
BestImg.BorderSizePixel         = 0
BestImg.ScaleType              = Enum.ScaleType.Fit
BestImg.Parent                 = BestBox
Instance.new("UICorner", BestImg).CornerRadius = UDim.new(0, 6)

BestTitleLabel = Instance.new("TextLabel")
BestTitleLabel.Name                   = "BestTitleLabel"
BestTitleLabel.Size                   = UDim2.new(1, -66, 0, 15)
BestTitleLabel.Position               = UDim2.new(0, 62, 0, 7)
BestTitleLabel.BackgroundTransparency  = 1
BestTitleLabel.Text                   = T("dash_best_egg")
BestTitleLabel.TextColor3             = Color3.fromRGB(150, 165, 185)
BestTitleLabel.TextSize               = 10
BestTitleLabel.Font                   = Enum.Font.GothamMedium
BestTitleLabel.TextXAlignment         = Enum.TextXAlignment.Left
BestTitleLabel.Parent                 = BestBox

BestNameLabel = Instance.new("TextLabel")
BestNameLabel.Name                   = "BestNameLabel"
BestNameLabel.Size                   = UDim2.new(1, -66, 0, 18)
BestNameLabel.Position               = UDim2.new(0, 62, 0, 23)
BestNameLabel.BackgroundTransparency  = 1
BestNameLabel.Text                   = "--"
BestNameLabel.TextColor3             = Color3.fromRGB(255, 255, 255)
BestNameLabel.TextSize               = 13
BestNameLabel.Font                   = Enum.Font.GothamBold
BestNameLabel.TextXAlignment         = Enum.TextXAlignment.Left
BestNameLabel.TextTruncate           = Enum.TextTruncate.AtEnd
BestNameLabel.Parent                 = BestBox

BestRarityLabel = Instance.new("TextLabel")
BestRarityLabel.Name                   = "BestRarityLabel"
BestRarityLabel.Size                   = UDim2.new(1, -66, 0, 14)
BestRarityLabel.Position               = UDim2.new(0, 62, 0, 42)
BestRarityLabel.BackgroundTransparency  = 1
BestRarityLabel.Text                   = "Rarity: --"
BestRarityLabel.TextColor3             = Color3.fromRGB(255, 180, 30)
BestRarityLabel.TextSize               = 10
BestRarityLabel.Font                   = Enum.Font.GothamBold
BestRarityLabel.TextXAlignment         = Enum.TextXAlignment.Left
BestRarityLabel.Parent                 = BestBox

-- ─── QUICK COMMAND DECK (Manga/Crimson PayomboyZ UI 2.0) ─────────
local QuickDeck = Instance.new("Frame")
QuickDeck.Name                   = "QuickCommandDeck"
QuickDeck.Size                   = UDim2.new(1, -20, 0, 32)
QuickDeck.Position               = UDim2.new(0, 10, 0, 106)
QuickDeck.BackgroundTransparency  = 1
QuickDeck.Parent                 = DashFrame

local function create_quick_btn(parent, pos, size, label, callback, activeCheck)
    local btn = Instance.new("TextButton")
    btn.Size                   = size
    btn.Position               = pos
    btn.BackgroundColor3       = Color3.fromRGB(18, 22, 34)
    btn.BorderSizePixel         = 0
    btn.Text                   = label
    btn.TextColor3             = Color3.fromRGB(255, 255, 255)
    btn.Font                   = Enum.Font.GothamBold
    btn.TextSize               = 10
    btn.Parent                 = parent
    Instance.new("UICorner", btn).CornerRadius = UDim.new(0, 6)

    local stroke = Instance.new("UIStroke")
    stroke.Color        = Color3.fromRGB(255, 36, 66)
    stroke.Thickness    = 1
    stroke.Transparency = 0.5
    stroke.Parent       = btn

    btn.MouseButton1Click:Connect(function()
        pcall(callback, btn, stroke)
    end)
    return btn, stroke
end

local btnWidth = UDim2.new(0.185, 0, 1, 0)
local qEgg, qEggStroke = create_quick_btn(QuickDeck, UDim2.new(0, 0, 0, 0), btnWidth, "🥚 ขโมย", function(btn, strk)
    auto_collect_eggs_func = not auto_collect_eggs_func
    sync_ui("auto_collect_eggs_func", auto_collect_eggs_func)
    if auto_collect_eggs_func then
        btn.BackgroundColor3 = Color3.fromRGB(30, 80, 50)
        strk.Color = Color3.fromRGB(76, 238, 133)
        -- ปิดคำสั่งและปุ่ม UI ของกิจกรรมฮาโลวีน
        if auto_halloween_suite or auto_halloween_candy then
            auto_halloween_suite = false
            auto_halloween_candy = false
            sync_ui("auto_halloween_suite", false)
            sync_ui("auto_halloween_candy", false)
        end
        task.spawn(function()
            if not is_player_riding() then pcall(mount_best_pet_on_plot) end
            task.wait(0.1)
            pcall(collect_egg)
        end)
    else
        btn.BackgroundColor3 = Color3.fromRGB(18, 22, 34)
        strk.Color = Color3.fromRGB(255, 36, 66)
        stop_tween()
        noclip_enabled = false
        pcall(teleport_to_plot)
    end
end)
UI_CONTROLS["qEgg"] = qEgg
UI_CONTROLS["qEggStroke"] = qEggStroke

local qMount, qMountStroke = create_quick_btn(QuickDeck, UDim2.new(0.203, 0, 0, 0), btnWidth, "🏇 ขี่ท็อป", function(btn, strk)
    btn.BackgroundColor3 = Color3.fromRGB(80, 65, 20)
    strk.Color = Color3.fromRGB(255, 198, 62)
    pcall(mount_best_pet_on_plot)
    task.delay(0.6, function()
        btn.BackgroundColor3 = Color3.fromRGB(18, 22, 34)
        strk.Color = Color3.fromRGB(255, 36, 66)
    end)
end)

local qHome, qHomeStroke = create_quick_btn(QuickDeck, UDim2.new(0.406, 0, 0, 0), btnWidth, "🏠 แปลง", function(btn, strk)
    btn.BackgroundColor3 = Color3.fromRGB(24, 45, 65)
    strk.Color = Color3.fromRGB(0, 180, 230)
    pcall(teleport_to_plot)
    task.delay(0.6, function()
        btn.BackgroundColor3 = Color3.fromRGB(18, 22, 34)
        strk.Color = Color3.fromRGB(255, 36, 66)
    end)
end)

local qRebirth, qRebirthStroke = create_quick_btn(QuickDeck, UDim2.new(0.609, 0, 0, 0), btnWidth, "🔄 จุติ", function(btn, strk)
    auto_rebirth_func = not auto_rebirth_func
    if auto_rebirth_func then
        btn.BackgroundColor3 = Color3.fromRGB(30, 80, 50)
        strk.Color = Color3.fromRGB(76, 238, 133)
    else
        btn.BackgroundColor3 = Color3.fromRGB(18, 22, 34)
        strk.Color = Color3.fromRGB(255, 36, 66)
    end
end)

local qEsp, qEspStroke = create_quick_btn(QuickDeck, UDim2.new(0.812, 0, 0, 0), btnWidth, "👁️ เรดาร์", function(btn, strk)
    esp_placed_eggs = not esp_placed_eggs
    if esp_placed_eggs then
        btn.BackgroundColor3 = Color3.fromRGB(30, 80, 50)
        strk.Color = Color3.fromRGB(76, 238, 133)
        refresh_placed_esp()
    else
        btn.BackgroundColor3 = Color3.fromRGB(18, 22, 34)
        strk.Color = Color3.fromRGB(255, 36, 66)
        refresh_placed_esp()
    end
end)

-- Stats Grid (Coins, Rebirths, Eggs, Pets)
local StatsGrid = Instance.new("Frame")
StatsGrid.Name                   = "StatsGrid"
StatsGrid.Size                   = UDim2.new(1, -20, 0, 115)
StatsGrid.Position               = UDim2.new(0, 10, 0, 144)
StatsGrid.BackgroundTransparency  = 1
StatsGrid.Parent                 = DashFrame

local function create_stat_card(parent, pos, size, labelKey, icon)
    local card = Instance.new("Frame")
    card.Size                   = size
    card.Position               = pos
    card.BackgroundColor3       = Color3.fromRGB(15, 18, 28)
    card.BorderSizePixel         = 0
    card.Parent                 = parent
    Instance.new("UICorner", card).CornerRadius = UDim.new(0, 8)
    
    local cStroke = Instance.new("UIStroke")
    cStroke.Color        = Color3.fromRGB(255, 36, 66)
    cStroke.Thickness    = 1
    cStroke.Transparency = 0.7
    cStroke.Parent       = card
    
    local topLbl = Instance.new("TextLabel")
    topLbl.Size                   = UDim2.new(1, -8, 0, 14)
    topLbl.Position               = UDim2.new(0, 6, 0, 4)
    topLbl.BackgroundTransparency  = 1
    topLbl.Text                   = icon .. " " .. T(labelKey)
    topLbl.TextColor3             = Color3.fromRGB(150, 165, 185)
    topLbl.TextSize               = 9
    topLbl.Font                   = Enum.Font.GothamMedium
    topLbl.TextXAlignment         = Enum.TextXAlignment.Left
    topLbl.Parent                 = card
    
    local valLbl = Instance.new("TextLabel")
    valLbl.Size                   = UDim2.new(1, -8, 0, 26)
    valLbl.Position               = UDim2.new(0, 6, 0, 18)
    valLbl.BackgroundTransparency  = 1
    valLbl.Text                   = "--"
    valLbl.TextColor3             = Color3.fromRGB(255, 255, 255)
    valLbl.TextSize               = 13
    valLbl.Font                   = Enum.Font.GothamBold
    valLbl.TextXAlignment         = Enum.TextXAlignment.Left
    valLbl.Parent                 = card
    
    return valLbl, topLbl
end

coinsVal, coinsTop     = create_stat_card(StatsGrid, UDim2.new(0, 0, 0, 0), UDim2.new(0.485, 0, 0, 48), "dash_coins", "💰")
rebirthVal, rebirthTop = create_stat_card(StatsGrid, UDim2.new(0.515, 0, 0, 0), UDim2.new(0.485, 0, 0, 48), "dash_rebirth", "🔄")
eggsVal, eggsTop       = create_stat_card(StatsGrid, UDim2.new(0, 0, 0, 54), UDim2.new(0.485, 0, 0, 48), "dash_eggs", "🥚")
petsVal, petsTop       = create_stat_card(StatsGrid, UDim2.new(0.515, 0, 0, 54), UDim2.new(0.485, 0, 0, 48), "dash_pets", "🐾")

-- Session Time footer
SessionLbl = Instance.new("TextLabel")
SessionLbl.Name                   = "SessionTime"
SessionLbl.Size                   = UDim2.new(1, -20, 0, 16)
SessionLbl.Position               = UDim2.new(0, 10, 0, 268)
SessionLbl.BackgroundTransparency  = 1
SessionLbl.Text                   = T("dash_session") .. ": 00:00:00"
SessionLbl.TextColor3             = Color3.fromRGB(140, 150, 175)
SessionLbl.TextSize               = 9
SessionLbl.Font                   = Enum.Font.GothamMedium
SessionLbl.TextXAlignment         = Enum.TextXAlignment.Center
SessionLbl.Parent                 = DashFrame
end
init_dashboard()

-- Add Dashboard Toggle button to Utility Section
if auto_func and auto_func.Button then
    auto_func:Button({
        Title    = T("dash_toggle"),
        Callback = function()
            dash_visible = not dash_visible
            DashFrame.Visible = dash_visible
        end,
    })
end

-- Helper to find most valuable egg in RenderedEggs or Backpack
local function get_highest_value_egg_or_pet()
    local bestObj = nil
    local bestScore = -1
    local bestRarity = "Common"
    local bestName = "--"
    
    -- Check world rendered eggs first
    local rEggs = workspace:FindFirstChild("RenderedEggs")
    if rEggs then
        for _, egg in ipairs(rEggs:GetChildren()) do
            local clean = clean_egg_name(egg.Name)
            local eggData = Eggs[clean]
            local rar = eggData and eggData.Rarity or "Common"
            local score = EGG_TIER_ORDER[rar] or 0
            if score > bestScore then
                bestScore = score
                bestRarity = rar
                bestName = clean
                bestObj = egg
            end
        end
    end
    
    -- Check player backpack pets/eggs
    if LocalPlayer.Backpack then
        for _, item in ipairs(LocalPlayer.Backpack:GetChildren()) do
            if item:IsA("Tool") then
                local petName = item:GetAttribute("PetName")
                if petName then
                    local rar = get_rarity_from_pet_name(petName) or "Common"
                    local score = (EGG_TIER_ORDER[rar] or 0) + 0.5
                    if score > bestScore then
                        bestScore = score
                        bestRarity = rar
                        bestName = petName
                        bestObj = item
                    end
                end
            end
        end
    end
    
    return bestName, bestRarity, get_pet_image_id(bestName)
end

-- Dashboard update loop
task.spawn(function()
    while true do
        task.wait(1)
        if dash_visible then
            pcall(function()
                -- Update Labels with Language
                if DashTitle then DashTitle.Text = "⚡ " .. T("dash_title") end
                if BestTitleLabel then BestTitleLabel.Text = T("dash_best_egg") end
                if coinsTop then coinsTop.Text = "💰 " .. T("dash_coins") end
                if rebirthTop then rebirthTop.Text = "🔄 " .. T("dash_rebirth") end
                if eggsTop then eggsTop.Text = "🥚 " .. T("dash_eggs") end
                if petsTop then petsTop.Text = "🐾 " .. T("dash_pets") end
                
                -- Values
                local savedData = LocalPlayer:FindFirstChild("SavedData")
                local cashVal = savedData and savedData:FindFirstChild("Cash")
                local cash = (cashVal and tonumber(cashVal.Value)) or 0
                if coinsVal then
                    if cash >= 1e15 then
                        coinsVal.Text = string.format("%.2fQa", cash / 1e15)
                    elseif cash >= 1e12 then
                        coinsVal.Text = string.format("%.2fT", cash / 1e12)
                    elseif cash >= 1e9 then
                        coinsVal.Text = string.format("%.2fB", cash / 1e9)
                    elseif cash >= 1e6 then
                        coinsVal.Text = string.format("%.2fM", cash / 1e6)
                    elseif cash >= 1e3 then
                        coinsVal.Text = string.format("%.1fK", cash / 1e3)
                    else
                        coinsVal.Text = tostring(cash)
                    end
                end
                
                local rebVal = savedData and savedData:FindFirstChild("Rebirths")
                local rebirths = (rebVal and tonumber(rebVal.Value)) or 0
                if rebirthVal then
                    rebirthVal.Text = tostring(rebirths)
                end
                
                local plot = get_my_plot()
                local eggCount = (plot and plot:FindFirstChild("Eggs") and #plot.Eggs:GetChildren()) or 0
                if eggsVal then
                    eggsVal.Text = eggCount .. " / 10"
                end
                
                local petCount = (plot and plot:FindFirstChild("Pets") and #plot.Pets:GetChildren()) or 0
                local maxPets = tonumber(LocalPlayer:GetAttribute("MaxPets")) or 10
                if petsVal then
                    petsVal.Text = petCount .. " / " .. maxPets
                end
                
                -- Best Item
                local bName, bRar, bImg = get_highest_value_egg_or_pet()
                if BestNameLabel then BestNameLabel.Text = bName end
                if BestRarityLabel then
                    BestRarityLabel.Text = "Rarity: " .. bRar
                    local rarCol = RARITY_COLORS and RARITY_COLORS[bRar]
                    if not rarCol then
                        if bRar == "Mythic" or bRar == "Godly" or bRar == "Secret" then
                            rarCol = Color3.fromRGB(255, 45, 75)
                        elseif bRar == "Legendary" then
                            rarCol = Color3.fromRGB(255, 180, 30)
                        elseif bRar == "Epic" then
                            rarCol = Color3.fromRGB(180, 70, 255)
                        elseif bRar == "Rare" then
                            rarCol = Color3.fromRGB(60, 160, 255)
                        elseif bRar == "Uncommon" then
                            rarCol = Color3.fromRGB(80, 220, 120)
                        else
                            rarCol = Color3.fromRGB(170, 175, 190)
                        end
                    end
                    BestRarityLabel.TextColor3 = rarCol
                end
                if BestImg and bImg then
                    BestImg.Image = "rbxassetid://" .. bImg:gsub("rbxassetid://", "")
                end
                
                -- Session Time
                local elapsed = math.floor(tick() - session_start_time)
                local hrs = math.floor(elapsed / 3600)
                local mins = math.floor((elapsed % 3600) / 60)
                local secs = elapsed % 60
                if SessionLbl then
                    SessionLbl.Text = string.format("%s: %02d:%02d:%02d", T("dash_session"), hrs, mins, secs)
                end
            end)
        end
    end
end)

-- ─── Anti-Void Protection Loop ───────────────────────────────

task.spawn(function()
    while true do
        task.wait(0.4)
        if anti_void_func then
            pcall(function()
                local char = LocalPlayer.Character
                local hrp = char and char:FindFirstChild("HumanoidRootPart")
                if hrp then
                    local plot = get_my_plot()
                    local plotY = (plot and plot:GetPivot().Position.Y) or 40300
                    if hrp.Position.Y < (plotY - 150) then
                        local tpRemote = Remotes.Game:FindFirstChild("TeleportToPlot")
                        if tpRemote then tpRemote:FireServer() end
                        hrp.AssemblyLinearVelocity = Vector3.zero
                        if plot then
                            safe_move_root(plot:GetPivot() + Vector3.new(0, 6, 0))
                        end
                        pcall(function()
                            game:GetService("StarterGui"):SetCore("SendNotification", {
                                Title    = "🛡️ Anti-Void",
                                Text     = LANG == "TH" and "วาร์ปกลับขึ้นฟาร์มอย่างปลอดภัยแล้ว!" or "Teleported back to farm safely!",
                                Duration = 2.5,
                            })
                        end)
                    end
                end
            end)
        end
    end
end)

local function init_runtime_loops()
-- FPS & Ping update loop (Throttled twice per second)
local fps_samples = {}
local _lastStatsUpdate = 0
RunService.RenderStepped:Connect(function(dt)
    table.insert(fps_samples, 1 / math.max(dt, 0.001))
    if #fps_samples > 24 then table.remove(fps_samples, 1) end
    local now = os.clock()
    if now - _lastStatsUpdate >= 0.5 then
        _lastStatsUpdate = now
        local sum = 0
        for _, v in fps_samples do sum = sum + v end
        local fps  = math.floor(sum / #fps_samples)
        local ping = math.floor(LocalPlayer:GetNetworkPing() * 1000)
        StatsLabel.Text = T("hud_fps") .. ": " .. fps .. " | " .. T("hud_ping") .. ": " .. ping .. "ms"
    end
end)

-- ─── Runtime ─────────────────────────────────────────────────

local collision_cache = {}
RunService.Stepped:Connect(function()
    if not noclip_enabled then
        if next(collision_cache) ~= nil then
            for part, old in pairs(collision_cache) do
                if part.Parent then part.CanCollide = old end
            end
            table.clear(collision_cache)
        end
        return
    end
    local character = LocalPlayer.Character
    if not character then return end
    local root = character.PrimaryPart
    if root then
        root.AssemblyLinearVelocity  = Vector3.zero
        root.AssemblyAngularVelocity = Vector3.zero
    end
    for _, v in ipairs(character:GetDescendants()) do
        if v:IsA("BasePart") and v.CanCollide then
            if collision_cache[v] == nil then
                collision_cache[v] = v.CanCollide
            end
            v.CanCollide = false
        end
    end
end)

-- ESP Card Distance Updater (Dynamic metric distance - Throttled 3.5x/sec for smooth 60 FPS)
local _lastEspDistUpdate = 0
RunService.Heartbeat:Connect(function()
    if not esp_eggs and not esp_placed_eggs then return end
    local now = os.clock()
    if now - _lastEspDistUpdate < 0.28 then return end
    _lastEspDistUpdate = now

    local char = LocalPlayer.Character
    local root = char and char:FindFirstChild("HumanoidRootPart")
    local rootPos = root and root.Position
    if not rootPos then return end

    for obj, data in pairs(esp_objects) do
        if typeof(obj) ~= "Instance" then continue end
        if not obj.Parent then
            remove_esp(obj)
            continue
        end
        if data.distLbl then
            local pos = obj:GetPivot().Position
            local dist = math.floor((pos - rootPos).Magnitude)
            data.distLbl.Text = (data.rarity and ("[" .. data.rarity .. "] ") or "") .. dist .. "m"
        end
    end
end)

-- World egg events (Debounced to prevent sunrise spawn spam)
local _espDebounce = false
workspace.RenderedEggs.ChildAdded:Connect(function()
    if not _espDebounce then
        _espDebounce = true
        task.delay(0.5, function()
            _espDebounce = false
            if esp_eggs then pcall(refresh_esp) end
        end)
    end
end)
workspace.RenderedEggs.ChildRemoved:Connect(function(obj)
    remove_esp(obj)
end)

-- ESP periodic refresh (catches newly spawned and hatched eggs)
task.spawn(function()
    while _G.RideAPet_Session == CURRENT_SESSION_ID do
        task.wait(2.5)
        if esp_eggs then
            pcall(refresh_esp)
        end
        if esp_placed_eggs then
            pcall(refresh_placed_esp)
        end
    end
end)

local _system_busy_start = 0
local _rebirth_busy_start = 0

local run_master_pipeline = function()
    -- Watchdog: Auto-recover if an operation hangs for more than 45 seconds (never kill during live egg carry)
    if system_busy then
        if _system_busy_start == 0 then
            _system_busy_start = os.clock()
        elseif is_carries_eggs() then
            _system_busy_start = os.clock()
        elseif os.clock() - _system_busy_start > 45 then
            system_busy = false
            _system_busy_start = 0
        end
    end
    if smart_rebirth_busy then
        if _rebirth_busy_start == 0 then
            _rebirth_busy_start = os.clock()
        elseif os.clock() - _rebirth_busy_start > 45 then
            smart_rebirth_busy = false
            _rebirth_busy_start = 0
        end
    end

    if system_busy or smart_rebirth_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 1. Check & Hatch Ready Eggs first (only when not riding or carrying eggs)
    if auto_hatch_eggs_func and not is_player_riding() and not is_carries_eggs() then
        pcall(hatch_eggs)
    end
    if auto_hatch_luck_func then
        pcall(hacth_luck)
    end

    if system_busy or smart_rebirth_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 2. Egg Heist Collection (Steals eggs from world into backpack)
    local isNight = DayNight and DayNight.IsNight and DayNight.IsNight()
    if was_night_cached and not isNight then
        -- Sunrise! Night just ended, eggs respawned!
        task.wait(1.5) -- Human-like delay (1.5 seconds)
        if auto_collect_eggs_func and not is_carries_eggs() and not (auto_halloween_suite or auto_halloween_candy) then
            pcall(collect_egg)
        end
    elseif auto_collect_eggs_func and not is_carries_eggs() and not (auto_halloween_suite or auto_halloween_candy) then
        pcall(collect_egg)
    end
    was_night_cached = isNight

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 3. Deposit Carried Eggs or Place Backpack Eggs on Plot (Nests first, then plot, max 10)
    if auto_place_eggs_func and not is_carries_eggs() then
        pcall(place_eggs)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 4. Selling Automation (Pets & Eggs — strictly requires user toggle ON)
    if auto_sell_pets_func and not is_player_riding() and not is_carries_eggs() then
        pcall(sell_pet)
    end
    if auto_sell_eggs_func and not is_player_riding() and not is_carries_eggs() then
        pcall(sell_egg)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 5. Equip Best Pets (Ensure top 10 pets active on farm at all times)
    if auto_smart_place_func and not is_carries_eggs() then
        pcall(smart_place_best_pets)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 6. Priority Feeding (Feed highest power pet until level 100, then next)
    if auto_feed_best_pet_func and not is_player_riding() and not is_carries_eggs() then
        pcall(feed_best_pet)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 7. Controlled Shop Purchases (Check stock, no spam)
    if auto_buy_gear_func then
        pcall(auto_buy_gear)
    end
    if auto_buy_food_func then
        pcall(auto_buy_food)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 8. Passive Income, Claims & Rebirth Check
    if auto_collect_coins_func then
        pcall(auto_collect_coins)
    end
    if auto_unlock_nest_func then
        pcall(auto_unlock_next_nest)
    end
    if auto_rewards_func then
        pcall(auto_claim_free_rewards)
    end
    if auto_claim_index_func then
        pcall(cliam_index)
    end
    if auto_rebirth_func then
        pcall(smart_rebirth)
    end

    if system_busy or _G.RideAPet_Session ~= CURRENT_SESSION_ID then return end

    -- 9. Pet Fusion & Volcano Magma Dip
    if auto_fusion_func and not is_carries_eggs() then
        pcall(auto_fuse_pets)
    end
    if auto_volcano_dip_func and not is_carries_eggs() then
        pcall(auto_volcano_dip)
    end

    -- 10. Halloween Event Suite (Candy Farm, Knock Doors, Harvest Pumpkins, Auto-Buy Eggs)
    if (auto_halloween_suite or auto_halloween_candy or auto_halloween_doors or auto_halloween_pumpkins or auto_buy_halloween_egg) and not is_carries_eggs() and not auto_collect_eggs_func then
        pcall(run_halloween_pipeline)
    end
end

-- Master Orchestrator Thread
task.spawn(function()
    while _G.RideAPet_Session == CURRENT_SESSION_ID do
        task.wait(1.0)
        pcall(run_master_pipeline)
    end
end)

-- 15. Discord Webhook Loop (every 2 minutes)
task.spawn(function()
    while _G.RideAPet_Session == CURRENT_SESSION_ID do
        task.wait(120)
        if webhook_enabled and webhook_url ~= "" then
            pcall(send_discord_webhook)
        end
    end
end)

-- 16. Auto Save Loop (every 30 seconds)
task.spawn(function()
    while _G.RideAPet_Session == CURRENT_SESSION_ID do
        task.wait(30)
        if auto_save_enabled then
            pcall(function() save_config(nil, true) end)
        end
    end
end)

-- Initial ESP Render & Config Load
task.defer(function()
    task.wait(0.4)
    pcall(refresh_esp)
    pcall(refresh_placed_esp)
    if auto_load_on_start then
        pcall(function() load_config(nil, true) end)
    end
end)
end
init_runtime_loops()

getgenv().loaded = true


-- ================================================================================
local function init_anti_afk()
-- ─── PAYOMBØYZ HUB ADDITIONS: ANTI-AFK, DISCONNECT GUARD & ENHANCED UTILITIES ───
-- ================================================================================

local AntiAfkState = {
    Enabled = true,
    Alive = true,
    Silenced = {}
}

local function getActiveIdledConnections()
    if type(getconnections) ~= "function" then
        return {}
    end
    local success, conns = pcall(getconnections, LocalPlayer.Idled)
    if success and type(conns) == "table" then
        return conns
    end
    return {}
end

local function silenceDefaultIdled()
    for _, conn in ipairs(getActiveIdledConnections()) do
        pcall(function()
            conn:Disable()
            table.insert(AntiAfkState.Silenced, conn)
        end)
    end
end

local function restoreIdled()
    for _, conn in ipairs(AntiAfkState.Silenced) do
        pcall(function()
            conn:Enable()
        end)
    end
    table.clear(AntiAfkState.Silenced)
end

-- 1. Anti-AFK Controller Click Hook
local idledConnection = LocalPlayer.Idled:Connect(function()
    if AntiAfkState.Alive and AntiAfkState.Enabled then
        pcall(function()
            local VirtualUser = game:GetService("VirtualUser")
            VirtualUser:CaptureController()
            VirtualUser:ClickButton2(Vector2.new(0, 0))
        end)
    end
end)

-- 2. Error Message Watcher (Kick / Error Screen Auto-Rejoin)
local GuiService = game:GetService("GuiService")
local TeleportService = game:GetService("TeleportService")

local errorConnection = GuiService.ErrorMessageChanged:Connect(function(errorMessage)
    if AntiAfkState.Alive and AntiAfkState.Enabled and type(errorMessage) == "string" and string.find(string.lower(errorMessage), "idle", 1, true) then
        task.delay(2, function()
            pcall(function()
                TeleportService:Teleport(game.PlaceId, LocalPlayer)
            end)
        end)
    end
end)

-- 3. ProximityPrompt Instant Pickup Engine
if ProximityPromptService then
    ProximityPromptService.PromptButtonHoldBegan:Connect(function(prompt)
        pcall(function()
            if typeof(fireproximityprompt) == "function" then
                fireproximityprompt(prompt, 0)
            end
        end)
    end)
end

-- 4. Infinite Jump Hook
UserInputService.JumpRequest:Connect(function()
    if _G.InfiniteJumpEnabled then
        local character = LocalPlayer.Character
        local humanoid = character and character:FindFirstChildOfClass("Humanoid")
        if humanoid then
            pcall(function()
                humanoid:ChangeState(Enum.HumanoidStateType.Jumping)
            end)
        end
    end
end)

-- Clean Session Hook
table.insert(session_cleanups, function()
    AntiAfkState.Alive = false
    pcall(function() idledConnection:Disconnect() end)
    pcall(function() errorConnection:Disconnect() end)
    restoreIdled()
end)
end
init_anti_afk()
