import hashlib, json, os, re, struct, unittest
from pathlib import Path
try:
    from unicorn import *
    from unicorn.arm_const import *
except ImportError:
    raise unittest.SkipTest('Optional unicorn dependency absent')
ROOT=Path(__file__).resolve().parents[1]
path=os.environ.get('AOD_STOCK_AP')
if not path:raise unittest.SkipTest('Provide your own exact AP through AOD_STOCK_AP for native instruction checks')
AP=Path(path).read_bytes()
assert hashlib.sha256(AP).hexdigest()=='4f43b325addd6d9e6e7c7e2a4d00ffe3f23d5fb1560d8fe503544002ac1f516b'
loader=(ROOT/'band9pro_aod/runtime/loader.lua').read_text()
BLOB=bytes.fromhex(re.search(r"local MODULE=\('([a-f0-9]+)'",loader).group(1))
META=json.loads((ROOT/'native/target.json').read_text())
ROM,DATA,STOP=0xc080000,0x2c080000,0xc87f000
SOURCE,REQUEST,ALLOC=0x3d010000,0x3d000800,0x3d100000
SCREEN,LOOP,NODE,LV=0x200b6680,0x200e8000,0x200f8000,0x3d020000
class DeviceModel:
 def __init__(self):
  u=self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
  for base,size in [(ROM,0x800000),(DATA,0x800000),(0x20000000,0x200000),(0x3cf00000,0x1100000),(0x1cf00000,0x1100000),(0xe000e000,0x1000),(0x07ffa000,0x4000)]:u.mem_map(base,size)
  u.mem_write(ROM,AP);u.mem_write(DATA,AP)
  self.now=0;self.pending={};self.lv=[];self.draws=[];self.forward=[];self.allocations=[];self.locked=False
  self.fail_alloc=False;self.fail_start=False;self.free_max=0x400000;self.bank=7;self.signal_done=True;self.animation_started=None
  self.regions=[(6,0x1ffe3),(0x276406,0x3d63e3),(0xd0200006,0xd020ffe5),(0x20082d46,0x20084e03)]+[(0,0)]*4
  self.write(SCREEN,LOOP);self.state(1);self.write(SCREEN+0x20c,0xc368c6d)
  self.write(0x200b17f4,0x3cf7e080);self.write(0x3cf7e094,0x3cf7e080);self.write(0x3cf7e098,0x3dff0000)
  self.write(0xe000ed94,5);self.write(0xe000edc0,0x00447722);self.write(0xe000ed98,7)
  self.write(0x07ffa000,1);self.write(0x07ffc000,1)
  self.write(LOOP+8,LOOP+8);self.write(LOOP+12,LOOP+8)
  sentinel=SCREEN+0x454;self.write(sentinel,NODE);self.write(sentinel+4,NODE)
  u.mem_write(NODE,struct.pack('<3I',sentinel,sentinel,0xc368709))
  self.put(SOURCE,BLOB);self.write(SOURCE+4,REQUEST)
  sy=META['symbols'];self.put(REQUEST,struct.pack('<i6I',0x7ffffffe,0,SOURCE,len(BLOB),sy['screen_hook_entry'],sy['native_pulse'],sy['native_deferred']))
  u.hook_add(UC_HOOK_MEM_WRITE,self.memory_write);u.hook_add(UC_HOOK_MEM_READ,self.memory_read);u.hook_add(UC_HOOK_CODE,self.code)
 def put(self,p,b):
  self.u.mem_write(p,b)
  if 0x3cf00000<=p<0x3e000000:self.u.mem_write(p-0x20000000,b)
 def write(self,p,v):self.put(p,struct.pack('<I',v&0xffffffff))
 def read(self,p):return struct.unpack('<I',self.u.mem_read(p,4))[0]
 def state(self,s):self.u.mem_write(SCREEN+0x1c4,bytes([s]))
 def memory_write(self,u,access,p,n,v,data):
  if 0x3cf00000<=p<0x3e000000:u.mem_write(p-0x20000000,int(v).to_bytes(n,'little'))
  if p==0xe000ed98:self.bank=v
 def memory_read(self,u,access,p,n,v,data):
  if p in (0xe000ed9c,0xe000eda0):self.write(p,self.regions[self.bank][(p-0xe000ed9c)//4])
 def code(self,u,p,n,data):
  r0,r1,r2=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
  if p==0xc0f1c70:u.mem_write(r0,struct.pack('<6I',0x1071f80,10,20,self.free_max,0x10000,0x100000))
  elif p==0xc0f21ec:
   assert r0==32 and r1<20000;self.allocations.append(r1);u.reg_write(UC_ARM_REG_R0,0 if self.fail_alloc else ALLOC)
  elif p==0xc0f1b00:self.allocations.append(('free',r0))
  elif p==0xc25cb8c:
   assert r1==0;self.lv.append(r0);self.write(LV,r1);self.write(LV+8,r0);self.write(LV+12,r2);u.reg_write(UC_ARM_REG_R0,LV)
  elif p==0xc368c6c:self.forward.append((r0,r1))
  elif p==0xc0bbb10:
   assert r0==1;u.mem_write(r1,struct.pack('<qI',self.now//1000,self.now%1000*1000000)+bytes(4));u.reg_write(UC_ARM_REG_R0,0)
  elif p==0xc112068:
   delay=r2 | u.reg_read(UC_ARM_REG_R3)<<32
   repeat=struct.unpack('<Q',u.mem_read(u.reg_read(UC_ARM_REG_SP),8))[0];assert repeat==0
   if self.fail_start:u.reg_write(UC_ARM_REG_R0,0xffffffff)
   else:self.pending[r0]=(self.now+delay,r1);u.reg_write(UC_ARM_REG_R0,0)
  elif p==0xc111f62:self.pending.pop(r0,None);u.reg_write(UC_ARM_REG_R0,0)
  elif p==0xc23ca2c:u.reg_write(UC_ARM_REG_R0,0x200fa000)
  elif p==0xc23e23e:pass
  elif p==0xc0cab70:assert not self.locked;self.locked=True
  elif p==0xc0cac2c:assert self.locked;self.locked=False
  elif p==0xc25c9ec:
   assert self.locked;self.draws.append(self.now);u.reg_write(UC_ARM_REG_R0,100)
   if self.animation_started is None:self.animation_started=self.now
   if self.signal_done and self.now-self.animation_started>=2720:self.write(ALLOC+8,2)
  elif p==0xc4379f4:assert r0==11
  else:return
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def call(self,p,a=0,b=0):
  u=self.u;sp=0x201ff000
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b)
  regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
  for i,r in enumerate(regs):u.reg_write(r,0xa0160000+i)
  u.emu_start(p|1,STOP,count=300000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==sp and not self.locked
  assert all(u.reg_read(r)==0xa0160000+i for i,r in enumerate(regs))
  return u.reg_read(UC_ARM_REG_R0)
 def install(self):
  self.call(SOURCE-0x20000000);return self.read(REQUEST)
 def prepare(self):self.call(self.lv[0],LV)
 def until(self,t):
  while self.pending and min(v[0] for v in self.pending.values())<=t:
   handle=min(self.pending,key=lambda k:self.pending[k][0]);self.now,cb=self.pending.pop(handle);self.call(cb,handle)
  self.now=t

class NativeTests(unittest.TestCase):
    def install(self):
        h=DeviceModel();h.state(2);self.assertEqual(h.install(),0);h.prepare()
        code=h.read(ALLOC+144)
        self.assertEqual(h.read(code+0xdc),0x2a642164)
        h.write(ALLOC+8,0);h.write(code+0xdc,0x2a282128);h.write(code+0x200,0x23002228);h.write(ALLOC+8,1)
        h.state(1);h.call(h.read(SCREEN+0x20c),0,0);return h
    def test_40ms_then_stop_and_preserve_minute_handle(self):
        h=self.install();h.until(8000)
        self.assertEqual(h.draws,list(range(40,2800,40)))
        self.assertFalse(h.pending)
        self.assertEqual(bytes(h.u.mem_read(0x200b6890,88)),bytes(88))
    def test_hard_ceiling_and_wake_cancel(self):
        h=self.install();h.signal_done=False;h.until(13000)
        self.assertFalse(h.pending);self.assertEqual(h.read(ALLOC+156),5)
        h=self.install();h.until(500);h.state(2);h.until(1000)
        self.assertFalse(h.pending);self.assertEqual(len(h.draws),12)
