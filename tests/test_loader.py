import importlib.util
import unittest
from band9pro_aod.runtime import RUNTIME

@unittest.skipUnless(importlib.util.find_spec('lupa'), 'Optional Lua dependency absent')
class LoaderTests(unittest.TestCase):
    def case(self,fault=None):
        from loader_seam import case
        return case(fault)

    def ready(self):
        vm,api,ok,message=self.case();self.assertTrue(ok,message)
        for p,v in [(0x200b6844,2),(0x3d10000c,1),(0x3d100078,0),(0x3d10006c,0),
                    (0x3d10017c,0x2a642164),(0x3d1002a0,0x23002264),
                    (0x1d10017c,0x2a642164),(0x1d1002a0,0x23002264)]:vm.globals().words[p]=v
        return vm,api

    def test_receipt_and_result_failure_disable_owned_gate(self):
        for fault in ('receipt','result'):
            with self.subTest(fault=fault):
                vm,api,ok,message=self.case(fault)
                self.assertFalse(ok);self.assertEqual(vm.globals().words[0x3d100008],0)

    def test_all_startup_guard_failures(self):
        for fault in ('fingerprint','mpu','cache','foreign-hook','marker','layout','native'):
            with self.subTest(fault=fault):self.assertFalse(self.case(fault)[2])

    def test_tune_success_and_single_failure_roll_back(self):
        vm,api=self.ready();self.assertEqual(api.tune(),(True,b'40ms'))
        self.assertEqual(api.tune(),(True,b'40ms'))
        for fault in ('write','barrier','alias'):
            vm,api=self.ready();vm.globals().TUNE_FAULT=fault.encode()
            vm.execute(b'''
              local original=os.execute;local once=true
              os.execute=function(cmd)
                if once and TUNE_FAULT=='write' and cmd:match('^mw 3d1002a0=23002228') then once=false;return false end
                if once and TUNE_FAULT=='barrier' and cmd=='exec 0x0c51d707' then once=false;return false end
                if once and TUNE_FAULT=='alias' and cmd:match('^mw 1d10017c 4') then once=false;words[0x1d10017c]=0 end
                return original(cmd)
              end
            ''')
            self.assertFalse(api.tune()[0],fault)
            self.assertEqual(vm.globals().words[0x3d10017c],0x2a642164)
            self.assertEqual(vm.globals().words[0x3d1002a0],0x23002264)
            self.assertEqual(vm.globals().words[0x3d100008],1)

    def test_failed_rollback_blocks_other_loader_instance(self):
        vm,api=self.ready()
        vm.execute(b'''
          local original=os.execute;local altered=false
          os.execute=function(cmd)
            if cmd:match('^mw 3d10017c=2a282128') then altered=true end
            if altered and (cmd:match('^mw 3d1002a0=23002228') or cmd:match('^mw 3d10017c=2a642164')) then return false end
            return original(cmd)
          end
        ''')
        self.assertFalse(api.tune()[0]);self.assertEqual(vm.globals().words[0x3d100008],0)
        other=vm.execute((RUNTIME/'loader.lua').read_bytes())
        self.assertFalse(other.enabled(True));self.assertFalse(other.reuse())
        self.assertFalse(other.load(True)[0]);self.assertTrue(other.enabled(False))
        self.assertEqual(vm.globals().words[0x3d100008],0)

    def test_marker_read_error_is_not_treated_as_absent(self):
        vm,api=self.ready()
        vm.execute(b'''
          local original=io.open
          io.open=function(path,mode)
            if mode=='rb' and path:match('/tune%-in%-progress.txt$') then return nil,'I/O error',5 end
            return original(path,mode)
          end
        ''')
        other=vm.execute((RUNTIME/'loader.lua').read_bytes())
        self.assertFalse(other.enabled(True));self.assertFalse(other.reuse())
        self.assertFalse(other.load(True)[0])

    def test_failed_gate_restore_and_failed_rollback_keep_isolation(self):
        vm,api=self.ready()
        vm.execute(b'''
          local original=os.execute;local modified=false
          os.execute=function(cmd)
            if cmd:match('^mw 3d10017c=2a282128') then modified=true end
            if modified and (cmd:match('^mw 3d100008=00000001') or cmd:match('^mw 3d10017c=2a642164')) then return false end
            return original(cmd)
          end
        ''')
        self.assertFalse(api.tune()[0])
        other=vm.execute((RUNTIME/'loader.lua').read_bytes())
        self.assertFalse(other.enabled(True));self.assertFalse(other.reuse())
        self.assertEqual(vm.globals().words[0x3d100008],0)

    def test_receipt_removal_failure_cannot_replay_automatic_startup(self):
        vm,api,ok,message=self.case();self.assertTrue(ok)
        vm.execute(b'''
          words[0x200b688c]=0x0c368c6d
          FAULT='native'
          local original=os.remove
          os.remove=function(path)
            if path:match('/auto%-ok%-v162.txt$') then return nil,'I/O error',5 end
            return original(path)
          end
        ''')
        before=vm.globals().nativeCalls
        self.assertFalse(api.load(b'auto')[0]);self.assertFalse(api.load(b'auto')[0])
        self.assertEqual(vm.globals().nativeCalls,before)

if __name__=='__main__':unittest.main()
