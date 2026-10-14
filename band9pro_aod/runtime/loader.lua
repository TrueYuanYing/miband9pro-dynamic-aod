local MODULE_SHA='fe8b72fb3faf1ba306a6caf9d74fe10e89d078c7349e20eec654110546e81c4e'
local MODULE=('00f002b800000000aff20800006800f041b9aff21002126800f0aeb8f0b581b00468002c00f08080206844f64171c3f23161884278d1e068002875d0a06820b34af6a517c0f64447b847012822d1a06e44f69151c0f611418847d4e91a01d0e95065f1b1e16f00200029e0665cd142f6e06292194ff0010145f10003c4e91c23c4e91e11c4f898000ee00020e066c4e91e0036e0e0680021e166a167e16780bb42e0a06f00283fd045f62920c0f645408047d4f89800a1680130c4f89800d1b1b847012817d1a068022827d0d4e91c10721a75eb00021ed28a1ba8416421642a28bf0a46002818bf0a462046002301b0bde8f0401ae0e1680020e066a067e06791b141f6637104f11000c0f6114101b0bde8f04008470520c4f89c00e16800200029a067e066ecd101b0f0bd2de9f04182b0054641f66370c0f6114005f11007d5f88410804600f583740026384600960196a04768b10420c5f89c00e868ee66ae67ee6728b13846414602b0bde8f041084702b0bde8f081b0b5144648f66d42c0f6364205469047b4b1206844f64171c3f2316188420fd1e06868b16db1002141f66372e166a16704f11000c0f61142e167bde8b0401047b0bda0680028eed02046bde8b040ffe72de9f04182b00446806818b1e06808b1e06f10b102b0bde8f08141f66372c0f61142012004f11007d4f88410e066904602f58375002638466422002300960196a8470028e6d00420c4f89c00e068e6660028a667e667ddd03846414602b0bde8f041084710b5c468017d41f00101017544b1206844f64171c3f23161884201d1e06800b110bd46f28060c2f20b000068a06648b141f6317204f11001c0f61142904728b1022000e00120c4f89c0010bd0120c4e903044af6a510c0f6444080470128dfd12046bde8104099e72de9f04f87b0002878d041f2f47bc2f20b0b0446dbf800004ef28006c3f6f746b0426bd14ff6e47ac3f6fe5a706954454ff0ff3764d80af11b08444560d8a0425ed2b06904f11c01814259d86ff064072760eff31480eff3058100f0010008434ed14ef69450cef200000168052947d1c06a47f22271c0f24401884240d1d4e9020100f026f9002842d0e06844f201014cf21f02411acff6ff72914234d32169814231d2616981422ed2a16981422bd246f68c00c2f20b00006848f66d41c0f63641884227d101ad41f6013728461821c0f60f4700f05ff907f5b872284631469047e0681f3020f01f09049809f58031a031884212d26ff0670707e04ff0ff37384607b0bde8f08f6ff065072760f7e76ff06407f4e76ff06607f7e709f1a00542f2ed12c0f60f42202029469047009088b3dbf80000b04230d1706900996ff069074145e2d800998842dfd20098aaeb00001c30a842d9d3b069009929448142d4d80098494600f1a006304600f0b1f8b8b12db100990020013d01f8010bfbd1e068b8b10021a068405c7054e06801318142f8d30fe06ff06807b7e76ff06907b4e7009841f60131c0f60f4188476ff06a07abe7002044f64171009fc3f231611022012387e80e0004f11002c7e9246007ca07f1604320f00100a13321f0010122f00102184419441a4407f1800307c34af20000c7f8a470c0f2ff700068c00706d04cf20000c0f2ff700068c00708d1009841f60131c0f60f4188476ff06b0774e742f28b05c0f60845a847bff34f8fbff36f8f05f118008047bff34f8fbff36f8f46f68c01eff3108072b6c2f20b01096848f66d42c0f6364291422ed1009d46f68c02d5f88010c2f20b021160bff34f8fbff36f8f80f31088d5f888004cf68d33c0f6254300212a466560002798470028c5f88c007ff439af009903208f60c1f89c0046f68c0048f66d41c2f20b00c0f636416ff06d07016027e780f31088009841f60131c0f60f4188476ff06c071ce7f0b541f2f472c2f20b0212684ef28003c3f6f7439a421cbf0020f0bd4ff6ff7cc3f6fe5c024660454ff000005c6998bf944200d3f0bdaceb020401348c42f9d398698b1883424ff0000088bff0bd4ef69853cef2000302f16042eff3108c72b68818d3f800e0411e0024012000bf1c605d689e6825f01f0546f01f07a9424ff0000538bf0546ba4288bf0546f60704f1010418bf2846082ce9d1c3f800e0bff34f8fbff36f8f8cf31088f0bd70470a46002100f000b822b1034603f8011b013afbd17047fff7f3bf'):gsub('%x%x',function(s) return string.char(tonumber(s,16)) end)
local HOOK_OFFSET=19
local PULSE_OFFSET=29
local DEFER_OFFSET=557
local FINGERPRINTS={{0x2c368c6c,0xaf00b580},{0x2c44a9a4,0x4b05b580},{0x2c455a28,0xaf00b580},{0x2c44ce88,0x2006b5b0},{0x2c111f30,0x720b230d},{0x2c111f60,0xe92dbd80},{0x2c112068,0x47f0e92d},{0x2c114d90,0xb084b5b0},{0x2c25cb8c,0x41f0e92d},{0x2c0f1c70,0x460cb5f0},{0x2c0f21ec,0x4300f06f},{0x2c0f1b00,0x4b03b580},{0x2c082088,0x4b07d109},{0x2c0820a0,0x4b024770},{0x2c51d704,0xf3bf3094}}
-- Generated constants precede this source. Dedicated files only; no firmware IO.
local M={}
local owner
local base='/data/codex-aod16-810111616'
local tag='AOD16:'..MODULE_SHA
local function run(cmd)
    local ok,v=pcall(os.execute,cmd)
    return ok and (v==true or v==0)
end
local function read(path)
    local f=io.open(path,'rb');if not f then return nil end
    local ok,s=pcall(f.read,f,'*a');pcall(f.close,f)
    return ok and s or nil
end
local function write(path,s)
    local f=io.open(path,'wb');if not f then return false end
    local ok,v=pcall(f.write,f,s);local closed,c=pcall(f.close,f)
    return ok and v~=nil and closed and c~=nil and read(path)==s
end
local function word(p)
    assert(type(p)=='number' and p%4==0,'unaligned read')
    local path=base..'/word.txt'
    pcall(os.remove,path)
    assert(run(string.format('mw %08x 4 > %s',p,path)),'mw read')
    local s=read(path) or '';pcall(os.remove,path)
    local hex=s:match('=%s*0[xX](%x+)') or s:match('%-%>%s*0[xX](%x+)')
    local n=hex and tonumber(hex,16);assert(n and n<=0xffffffff,'word result')
    return n
end
local function workspace()
    if run('mkdir '..base) then assert(write(base..'/owner.txt',tag),'workspace tag') end
    assert(read(base..'/owner.txt')==tag,'workspace conflict')
end
local fingerprintChecked=false
local function validateFirmware()
    if fingerprintChecked then return end
    for _,item in ipairs(FINGERPRINTS) do assert(word(item[1])==item[2],'firmware mismatch') end
    assert(word(0xe000ed94)==5 and word(0xe000edc0)==0x00447722,'MPU state')
    assert((word(0x07ffa000)&1)==1 and (word(0x07ffc000)&1)==1,'cache state')
    fingerprintChecked=true
end
local function heap_bounds()
    validateFirmware()
    assert(word(0x200b17f4)==0x3cf7e080,'heap identity')
    local lo,hi=word(0x3cf7e094),word(0x3cf7e098)
    assert(lo>=0x3cf7e080 and hi>lo and hi<=0x3dff0000,'heap bounds')
    return function(p,n) return type(p)=='number' and p%4==0 and p>lo and p<hi and n<=hi-p end
end
local function resident(inside)
    local p=tonumber(read(base..'/native.ptr') or '',16)
    if not inside(p,160) then return nil end
    if word(0x200b688c)==0x0c368c6d then return nil end -- reboot: old pointer is stale
    if word(p)~=0x36314f41 or word(p+4)~=16 then return nil end
    local code,n=word(p+144),word(p+148)
    if n~=#MODULE or not inside(code,n) then return nil end
    local hook=code-0x20000000+(HOOK_OFFSET&~1)+1
    if word(p+128)~=hook or word(0x200b688c)~=hook or word(code+4)~=p then return nil end
    return p
end
local function poke(p,v,inside)
    assert(inside(p,4),'owned write range')
    assert(run(string.format('mw %08x=%08x',p,v)) and word(p)==v,'owned write')
end
local isolation=base..'/tune-in-progress.txt'
local function absent(path)
    local f,err,errno=io.open(path,'rb')
    if f then pcall(f.close,f);return false end
    assert(errno==2,'file existence check failed')
    return true
end
local function allowEnable()
    assert(absent(isolation),'tuning isolated: reboot required')
end
local function clearIsolation()
    pcall(os.remove,isolation)
    assert(absent(isolation),'isolation receipt removal')
end
function M.enabled(value)
    local ok=pcall(function()
        workspace();local inside=heap_bounds();local p=resident(inside)
        assert(p,'native absent');if value then allowEnable() end;poke(p+8,value and 1 or 0,inside)
    end)
    return ok
end
function M.done()
    return pcall(function()
        workspace();local inside=heap_bounds();local p=resident(inside)
        assert(p,'native absent');allowEnable();poke(p+8,2,inside)
    end)
end
function M.reuse()
    local ok,active=pcall(function()
        workspace();local inside=heap_bounds();local p=resident(inside)
        if not p then return false end
        allowEnable();poke(p+8,1,inside);return true
    end)
    return ok and active==true
end
function M.load(manual)
    local created,created_inside
    local ok,result=pcall(function()
        assert(type(debug.upvalueid)=='function' and type(string.pack)=='function','Lua API')
        workspace()
        local inside=heap_bounds();local old=resident(inside)
        if old then allowEnable();poke(old+8,1,inside);return 'ACTIVE' end
        assert(manual==true or manual=='auto','ACTIVATION MODE')
        assert(word(0x200b688c)==0x0c368c6d,'another native hook')
        clearIsolation() -- Verified stock hook: the previous RAM module is no longer active.
        -- An old successful receipt permits one automatic initialization after reboot.
        -- Consume it before attempting native execution; a crash cannot replay it.
        local permitted=manual==true or (manual=='auto' and read(base..'/auto-ok-v162.txt')==tag)
        pcall(os.remove,base..'/auto-ok-v162.txt')
        assert(absent(base..'/auto-ok-v162.txt'),'automatic receipt consumption')
        if permitted then
            pcall(os.remove,base..'/attempt.txt')
        end
        assert(absent(base..'/attempt.txt'),'REBOOT: TAP N')
        local payload=string.pack('<i4I4I4I4I4I4I4',0x7ffffffe,0,0,#MODULE,HOOK_OFFSET,PULSE_OFFSET,DEFER_OFFSET)
            ..string.rep('\0',4)..MODULE..string.rep('\0',32)
        local function retain(s) return function() return s end end
        owner=retain(payload)
        local up=tostring(debug.upvalueid(owner,1))
        up=tonumber(up:match('0[xX](%x+)$') or up:match(':%s*(%x+)$'),16)
        assert(inside(up,32),'upvalue range')
        local v=word(up+8)
        assert(v==up+16 and (word(v+8)&255)==0x54,'upvalue layout')
        local obj=word(v)
        assert(inside(obj,#payload+17) and (word(obj+4)&255)==0x14 and word(obj+12)==#payload,'string layout')
        local mailbox,code=obj+16,obj+48
        assert(word(mailbox)==0x7ffffffe and word(code)==string.unpack('<I4',MODULE),'payload mismatch')
        poke(code+4,mailbox,inside);poke(mailbox+8,code,inside)
        -- Written and read back before any native entry. A reboot will not
        -- auto-run the failed experiment; explicit N tap is a new attempt.
        assert(write(base..'/attempt.txt','ONE ATTEMPT '..tag),'attempt marker')
        assert(run('exec 0x0c08208b'),'D publication')
        assert(run('exec 0x0c51d707'),'D barrier invocation')
        assert(run('exec 0x0c0820a3'),'I publication')
        assert(run('exec 0x0c51d707'),'I barrier invocation')
        local command=run(string.format('exec 0x%08x > %s/exec.txt',(code-0x20000000)|1,base))
        local status=word(mailbox)
        if status>=0x80000000 then status=status-0x100000000 end
        assert(status==0,'native rc '..status)
        local p=word(mailbox+4)
        assert(inside(p,160) and word(p)==0x36314f41 and word(p+4)==16,'native context')
        local image=word(p+144)
        assert(inside(image,#MODULE) and word(image+4)==p
            and word(0x200b688c)==image-0x20000000+(HOOK_OFFSET&~1)+1,'native hook')
        created,created_inside=p,inside
        poke(p+8,0,inside)
        assert(write(base..'/result.txt',string.format('native_rc=%d\nnsh_ok=%s\n',status,tostring(command))),'result file')
        assert(write(base..'/native.ptr',string.format('%08x',p)),'native receipt')
        assert(resident(inside)==p,'resident verification')
        assert(write(base..'/auto-ok-v162.txt',tag),'automatic receipt')
        allowEnable();poke(p+8,1,inside)
        return 'ACTIVE'
    end)
    if not ok and created then pcall(poke,created+8,0,created_inside) end
    owner=nil -- only the copied, native-owned allocation remains in callbacks
    return ok,ok and result or tostring(result)
end
-- Tune only our proven resident RAM extension; never patch firmware ROM/Flash.
function M.tune()
    local created,inside,saved,code,oldA,oldB
    local changed=false
    local function publishImage()
        assert(run('exec 0x0c08208b'),'D publication')
        assert(run('exec 0x0c51d707'),'D barrier invocation')
        assert(run('exec 0x0c0820a3'),'I publication')
        assert(run('exec 0x0c51d707'),'I barrier invocation')
    end
    local ok,result=pcall(function()
        workspace();inside=heap_bounds();created=resident(inside)
        assert(created,'native absent');allowEnable()
        assert((word(0x200b6844)&255)==2,'WAIT ON')
        assert(word(created+12)==1,'WAIT READY')
        assert(word(created+120)==0 and word(created+108)==0,'WAIT STOPPED')
        code=word(created+144)
        assert(inside(code,#MODULE),'image range')
        oldA,oldB=word(code+0xdc),word(code+0x200)
        assert((oldA==0x2a642164 and oldB==0x23002264)
            or (oldA==0x2a322132 and oldB==0x23002232)
            or (oldA==0x2a282128 and oldB==0x23002228),'interval signature')
        if oldA==0x2a282128 then return '40ms' end
        saved=word(created+8)
        assert(saved==1 or saved==2,'gate state')
        -- With the gate disabled, a concurrent OFF/IDLE event cannot arm us.
        assert(write(isolation,string.format('%08x',created)),'isolation receipt')
        poke(created+8,0,inside)
        assert((word(0x200b6844)&255)==2,'WAIT ON')
        changed=true
        poke(code+0xdc,0x2a282128,inside)
        poke(code+0x200,0x23002228,inside)
        publishImage()
        assert(word(code-0x20000000+0xdc)==0x2a282128
            and word(code-0x20000000+0x200)==0x23002228,'instruction alias')
        poke(created+8,saved,inside)
        clearIsolation()
        return '40ms'
    end)
    if not ok and saved then
        -- A persistent marker is shared by the normal and AOD loader instances.
        -- No later enter/reuse may reopen an image whose rollback is unconfirmed.
        local restored=pcall(function()
            assert(write(isolation,string.format('%08x',created)),'rollback isolation receipt')
            poke(created+8,0,inside)
            if changed then
                poke(code+0xdc,oldA,inside)
                poke(code+0x200,oldB,inside)
                publishImage()
                assert(word(code-0x20000000+0xdc)==oldA
                    and word(code-0x20000000+0x200)==oldB,'rollback instruction alias')
            end
            poke(created+8,saved,inside)
            clearIsolation()
        end)
        if not restored then pcall(poke,created+8,0,inside) end
    end
    return ok,ok and result or tostring(result)
end
return M
