from z80 import registers
import unittest

class TestZ80Registers(unittest.TestCase):

    def setUp(self):
        self.registers = registers.Registers(power=None)
        
    def test_double_register_access(self):
        self.registers.H = 0x45
        self.registers.L = 0x46
        self.assertEqual(self.registers.HL, 0x4546)
        
    def test_condition_flags(self):
        self.registers.F=0x0
        self.registers.condition.C=True
        self.assertEqual(self.registers.F, 0x01 << 0)

        self.registers.F=0x0
        self.registers.condition.S=True
        self.assertEqual(self.registers.F, 0x01 << 7)  
        
        self.registers.F=0x0
        self.registers.condition.PV=True
        self.assertEqual(self.registers.F, 0x01 << 2)        
        
        
if __name__ == '__main__':
    unittest.main()
    raw_input()
    
    