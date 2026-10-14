local nativeLoader=assert(load(LOADER_SOURCE,'AOD16-loader'))()
local reused=nativeLoader.reuse()
if not reused then
    local called,active=pcall(nativeLoader.load,'auto')
    if called and active then
        local found,vibrator=pcall(require,'vibrator')
        if found and type(vibrator)=='table' and type(vibrator.start)=='function'
           and type(vibrator.type)=='table' and vibrator.type.SUCCESS~=nil then
            pcall(vibrator.start,{type=vibrator.type.SUCCESS,is_repeat=false})
        end
    end
end
-- Bounded direct frame updates. The firmware still controls AOD wake cadence.
local lvgl = require('lvgl')
local fsRoot = SCRIPT_PATH
local frameFiles=__FRAME_FILES__
local frameOffsets=__FRAME_OFFSETS__
local displayedFile=nil
local last = __LAST_FRAME__
local period = 40
local current = -1
local alive = true
local session = false
local playing = false
local generation = 0
local screenState = 'IDLE'
local startedAt = nil
local timer = nil
local image = lvgl.Image(nil, {
    x = frameOffsets[frameFiles[1]][1], y = frameOffsets[frameFiles[1]][2],
    src = fsRoot .. 'f000.png',
    zoom = lvgl.IMG_ZOOM_NONE,
})
displayedFile=frameFiles[1]

local function wallTime()
    if type(os) ~= 'table' or type(os.time) ~= 'function' then
        return nil
    end
    local ok, value = pcall(os.time)
    if ok and type(value) == 'number' then
        return value
    end
    return nil
end

local function showFrame(index, force)
    if not alive then return false end
    index = math.max(0, math.min(last, math.floor(index)))
    if not force and index == current then return true end
    local ok = pcall(function()
        local file=frameFiles[index+1]
        local changed=displayedFile~=file
        if changed then
            local position=frameOffsets[file]
            image:set {src = fsRoot .. file, x=position[1], y=position[2]}
            displayedFile=file
        end
        -- This requests redraw; it is not a physical panel flush acknowledgement.
        if (changed or force) and type(image.invalidate) == 'function' then image:invalidate() end
    end)
    if ok then current = index end
    return ok
end

local function pauseTimer()
    if timer then pcall(function() timer:pause() end) end
end

local function finish()
    playing = false
    if showFrame(last, true) then nativeLoader.done() end
    -- The native time/date/week components remain managed by the firmware.
    pauseTimer()
end

local function cancel()
    generation = generation + 1
    session = false
    playing = false
    pauseTimer()
end

local function destroy()
    nativeLoader.enabled(false)
    alive = false
    cancel()
    if timer then
        pcall(function() timer:delete() end)
        timer = nil
    end
end

local function advance(token, activeTimer)
    if not alive or not playing or token ~= generation or activeTimer ~= timer then
        return
    end
    local now = wallTime()
    if startedAt and now then
        if now < startedAt then
            -- A backwards clock adjustment must not create an unbounded wait.
            startedAt = now
        elseif now - startedAt >= 10 then
            -- If AOD only dispatches at a minute boundary, request the final
            -- image on that dispatch instead of taking 69 minutes to finish.
            finish()
            return
        end
    end
    if current + 1 >= last then
        finish()
    elseif not showFrame(current + 1) then
        playing = false
        pauseTimer()
    end
end

local function enter()
    if not alive or session then return end
    nativeLoader.enabled(true)
    session = true
    playing = true
    generation = generation + 1
    local token = generation
    startedAt = wallTime()
    current = -1
    if not showFrame(0, true) then
        playing = false
        return
    end
    if type(lvgl.Timer) ~= 'function' then
        finish()
        return
    end
    local properties = {
        period = period,
        paused = true,
        cb = function(t) advance(token, t) end,
    }
    local ok = pcall(function()
        if timer then
            timer:set(properties)
        else
            timer = lvgl.Timer(properties)
            assert(timer ~= nil)
        end
        timer:resume()
    end)
    if not ok then finish() end
end

function pageOnPause()
    -- The AOD page can receive pause while it remains the visible idle page.
    -- ON/OFF notifications and deletion cancel our timer explicitly.
end

function pageOnResume()
    if screenState == 'IDLE' then enter() end
end

function pageOnDestroy()
    destroy()
end

function ScreenStateChangedCB(previous, state, reason)
    if not alive then return end
    if state == 'IDLE' then
        screenState = 'IDLE'
        enter()
    elseif state == 'ON' or state == 'OFF' then
        screenState = state
        cancel()
    end
end

-- Stop even when the framework destroys objects without pageOnDestroy.
pcall(function()
    if lvgl.EVENT and lvgl.EVENT.DELETE and type(image.onevent) == 'function' then
        image:onevent(lvgl.EVENT.DELETE, function() destroy() end)
    end
end)

-- The observed AOD creation path can omit pageOnResume.
enter()
