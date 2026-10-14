-- No visible button. Native initialization is independent of UI creation.
local lvgl=require('lvgl')
local ok,loader=pcall(function()
    local chunk,message=load(LOADER_SOURCE,'AOD16.2-loader')
    assert(chunk,message)
    local value=chunk()
    assert(type(value)=='table' and type(value.load)=='function','loader unavailable')
    return value
end)
local busy=false
local function feedback()
    local found,vibrator=pcall(require,'vibrator')
    if found and type(vibrator)=='table' and type(vibrator.start)=='function'
       and type(vibrator.type)=='table' and vibrator.type.SUCCESS~=nil then
        pcall(vibrator.start,{type=vibrator.type.SUCCESS,is_repeat=false})
    end
end
local function activate(mode)
    if busy or not ok then return false end
    busy=true
    local called,loaded,message
    if mode=='auto' and type(loader.reuse)=='function' then
        called,loaded=pcall(loader.reuse)
    end
    if not (called and loaded) then called,loaded,message=pcall(loader.load,mode) end
    local success=called and loaded==true
    if success then feedback() end
    print('[AOD16.2] '..tostring(success and 'ACTIVE' or (called and message or loaded)))
    busy=false
    return success
end
-- bg_opa=0 is transparent; FLAG.HIDDEN would also prevent input.
-- UI failure must not abort the independent automatic initialization path.
local hitbox
pcall(function()
    hitbox=lvgl.Object(nil,{x=10,y=134,w=42,h=38,bg_opa=0,
        border_width=0,outline_width=0,shadow_width=0,pad_all=0,radius=0})
    hitbox:clear_flag(lvgl.FLAG.SCROLLABLE)
    hitbox:add_flag(lvgl.FLAG.CLICKABLE)
    hitbox:add_flag(lvgl.FLAG.EVENT_BUBBLE)
    hitbox:onClicked(function() activate(true) end)
end)
-- Let the first normal frame render, then make one automatic attempt.
local startupTimer
local scheduled=pcall(function()
    startupTimer=lvgl.Timer{period=500,paused=false,cb=function(t)
        pcall(function() (t or startupTimer):pause() end)
        activate('auto')
    end}
    assert(startupTimer~=nil)
end)
if not scheduled then activate('auto') end

-- Wait until the original deferred initialization has completed in the UI loop.
local tuneTimer
local tries=0
local tunedForPage=false
local function tuneOnce(t)
    tries=tries+1
    local called,tuned,message=pcall(loader.tune)
    if called and tuned then tunedForPage=true end
    if (called and tuned) or tries>=8 then
        pcall(function() (t or tuneTimer):pause() end)
    end
    print('[AOD-Smooth] '..tostring(called and message or tuned))
end
pcall(function()
    if ok then tuneTimer=lvgl.Timer{period=500,paused=false,cb=tuneOnce} end
end)
function ScreenStateChangedCB(previous,state,reason)
    if state=='ON' and tuneTimer and not tunedForPage then
        tries=0;pcall(function() tuneTimer:resume() end)
    end
end
function pageOnDestroy()
    if tuneTimer then pcall(function() tuneTimer:pause() end) end
end
