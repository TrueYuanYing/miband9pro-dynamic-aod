from pathlib import Path
import json
from lupa.lua54 import LuaRuntime
from band9pro_aod.runtime import RUNTIME
source=(RUNTIME/'loader.lua').read_text(encoding='utf-8')
manifest=json.loads((Path(__file__).parents[1]/'native/target.json').read_text())
def case(fault=None):
 l=LuaRuntime(unpack_returned_tuples=True,encoding=None)
 l.globals().FINGERPRINT_LIST=l.table_from([l.table_from(p) for p in manifest['firmware_fingerprints']])
 l.globals().FAULT=fault.encode() if fault else None
 l.execute(rb'''
 files={};words={};commands={};nativeCalls=0;ownerSaved=nil
 local base='/data/codex-aod16-810111616'
 words[0x200b17f4]=0x3cf7e080;words[0x3cf7e094]=0x3cf7e080;words[0x3cf7e098]=0x3dff0000
 words[0xe000ed94]=5;words[0xe000edc0]=0x00447722
 words[0x07ffa000]=3;words[0x07ffc000]=3;words[0x200b688c]=0x0c368c6d
 for _,p in ipairs(FINGERPRINT_LIST) do words[p[1]]=p[2] end
 if FAULT=='fingerprint' then words[FINGERPRINT_LIST[1][1]]=0 end
 if FAULT=='mpu' then words[0xe000ed94]=0 end
 if FAULT=='cache' then words[0x07ffa000]=0 end
 if FAULT=='foreign-hook' then words[0x200b688c]=0x12345 end
 io.open=function(path,mode)
   if mode=='rb' and files[path]==nil then return nil,'No such file',2 end
   return {read=function() return files[path] end,write=function(self,s)
     if FAULT=='marker' and path==base..'/attempt.txt' then return nil end
     if FAULT=='receipt' and path==base..'/native.ptr' then return nil end
     if FAULT=='result' and path==base..'/result.txt' then return nil end
     files[path]=s;return self end,close=function() return true end}
 end
 os.remove=function(path) files[path]=nil;return true end
 debug.upvalueid=function(owner,index)
   local _,payload=debug.getupvalue(owner,index);ownerSaved=owner
   words[0x3d000208]=0x3d000210;words[0x3d000218]=0x54;words[0x3d000210]=0x3d001000
   words[0x3d001004]=0x14;words[0x3d00100c]=#payload
   for p=1,#payload-3,4 do words[0x3d001010+p-1]=string.unpack('<I4',payload,p) end
   if FAULT=='layout' then words[0x3d00100c]=1 end
   return '0x3d000200'
 end
 os.execute=function(cmd)
   commands[#commands+1]=cmd
   if cmd:match('^mkdir ') then
     if files[base..'/owner.txt'] then return false end
     return true
   end
   local p,out=cmd:match('^mw (%x+) 4 > (.+)$')
   if p then
     p=tonumber(p,16);assert(p%4==0);assert(words[p]~=nil,'unmapped read '..cmd)
     files[out]=string.format(' = 0x%08x',words[p]);return true
   end
   local a,v=cmd:match('^mw (%x+)=(%x+)$')
   if a then
     a,v=tonumber(a,16),tonumber(v,16)
     assert((a>=0x3d001010 and a<=0x3d001080) or a==0x3d100008 or a==0x3d10017c or a==0x3d1002a0,'write outside owned mailbox/context')
     words[a]=v;if a==0x3d10017c or a==0x3d1002a0 then words[a-0x20000000]=v end;return true
   end
   if cmd:match('^exec 0x1d001031 ') then
     nativeCalls=nativeCalls+1
     assert(files[base..'/attempt.txt']~=nil,'exec before persistent attempt')
     assert(ownerSaved()~=nil,'GC owner not retained')
     local mailbox=0x3d001010
     if FAULT=='native' then words[mailbox]=0xffffffff;return false end
     words[mailbox]=0;words[mailbox+4]=0x3d100000
     words[0x3d100000]=0x36314f41;words[0x3d100004]=16;words[0x3d100008]=1
     words[0x3d100090]=0x3d1000a0;words[0x3d100094]=words[mailbox+12]
     words[0x3d100080]=0x1d1000a0+(words[mailbox+16]&~1)+1
     words[0x200b688c]=words[0x3d100080];words[0x3d1000a4]=0x3d100000
     return true
   end
   if cmd:match('^exec 0x0c') then return true end
   error('unexpected shell effect '..cmd)
 end
 ''')
 m=l.execute(source.encode())
 assert not m.reuse() and l.globals().nativeCalls==0
 ok,message=m.load(True)
 return l,m,ok,message
