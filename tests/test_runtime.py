import importlib.util
import unittest
from band9pro_aod.frames import PreparedFrames
from band9pro_aod.runtime import aod_script
from fixtures import LUA_FIXTURE

@unittest.skipUnless(importlib.util.find_spec('lupa'), 'Optional Lua test dependency absent')
class RuntimeTests(unittest.TestCase):
    def run_player(self):
        from lupa.lua54 import LuaRuntime
        names=[f'f{i:03d}.png' for i in range(69)]
        frames=PreparedFrames(names,{name:(2+i,30) for i,name in enumerate(names)},dict.fromkeys(names,b'png'),1,1)
        vm=LuaRuntime(unpack_returned_tuples=True);vm.execute(LUA_FIXTURE)
        vm.execute('''
        done_count=0;gate=false
        local previous=load
        load=function(s,name,...)
          if name=='AOD16-loader' then return function() return {
            reuse=function() return true end,enabled=function(v) gate=v;return true end,
            done=function() assert(last_frame()==68);done_count=done_count+1;return true end
          } end end
          return previous(s,name,...)
        end
        ''')
        vm.execute(aod_script(frames).decode());return vm

    def test_terminal_frame_stops_and_next_session_replays(self):
        vm=self.run_player();self.assertEqual(vm.globals().timers[1].period,40)
        vm.execute('tick(68);tick(100)');self.assertEqual(vm.globals().done_count,1)
        self.assertEqual(vm.eval('last_frame()'),68)
        vm.execute("ScreenStateChangedCB('IDLE','ON');ScreenStateChangedCB('ON','IDLE');tick(68)")
        self.assertEqual(vm.globals().done_count,2)
        vm.execute('delete_handler()');self.assertFalse(vm.globals().gate)

    def test_failed_terminal_image_does_not_signal_completion(self):
        vm=self.run_player();vm.execute('tick(67);image_fail=true;tick(1)')
        self.assertEqual(vm.globals().done_count,0)
        self.assertTrue(vm.globals().timers[1].paused)

    def test_on_cancels_and_clock_jump_finishes(self):
        vm=self.run_player();vm.execute('tick(5)');count=len(vm.globals().history)
        vm.execute("ScreenStateChangedCB('IDLE','ON');tick(100)")
        self.assertEqual(len(vm.globals().history),count)
        vm=self.run_player();vm.execute('now=1011;tick(1)')
        self.assertEqual(vm.eval('last_frame()'),68)

if __name__=='__main__':unittest.main()
