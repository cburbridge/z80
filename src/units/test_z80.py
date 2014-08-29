import random
import unittest
from time import sleep
import logging
logging.basicConfig(level=logging.ERROR)
import subprocess
from subprocess import PIPE, STDOUT, Popen
from z80 import util, registers, instructions
import tempfile
import string
import inspect
import os

def compile_code(code):
    p = Popen(["z80asm", "-o", "-"], stdout=PIPE, stdin=PIPE)
    
    by = p.communicate(input=code)[0]
    object_code = [ord(b) for b in by]
    return object_code
    
class TestZ80Instructions(unittest.TestCase):

    def setUp(self):
        self.registers = registers.Registers(power=None)
        self.instructions = instructions.InstructionSet(self.registers)
        
        self.mem = bytearray(48*1024)
        
    def pass_bytes(self, bytes):
        for i in bytes:
            ins, args = self.instructions << i
            if ins:
                yield ins, args
        
    def execute(self, ins):
        rd =  ins[0].get_read_list(ins[1])
        data = [self.mem[i] for i in rd]
        wrt = ins[0].execute(data, ins[1])
        for i in wrt:
            self.mem[i[0]] = i[1]

    def test_ld(self):
        by = [0x3E, 0x45]
        for ins in self.pass_bytes(by):
            print ins
            self.execute(ins)
        self.assertEqual(self.registers.A, 0x45)

    def _test_assembler(self, file_name):
    	file = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
    						file_name)
        with open(file, "r") as f:
            asm = f.read()
        by = subprocess.check_output(["z80asm", "-i", file, "-o", "-"])
        byts = [ord(b) for b in by]
        res = ""
        for ins, a in zip(self.pass_bytes(byts), asm.split("\n")):
            res = ins[0].assembler(ins[1])
            self.assertEqual(res, a.strip().upper())
            print res
        res = res[:-1]
        
    def test_assembler_8bit_load(self):
        self._test_assembler("8bit_load.asm")
        
    def test_assembler_16bit_load(self):
        self._test_assembler("16bit_load.asm")
        
    def test_assembler_exchange_block_transfer(self):
        self._test_assembler("exchange.asm")

    def test_assembler_8bit_arith(self):
        self._test_assembler("8bit_arith.asm")
    
    def test_assembler_16bit_arith(self):
        self._test_assembler("16bit_arith.asm")
    
    def test_assembler_general_arith(self):
        self._test_assembler("general_purp.asm")
    

    def test_assembler_rotate_and_shift_group(self):
        self._test_assembler("rotate_shift.asm")        
            
    
    def test_assembler_bit_set_and_test_group(self):
        self._test_assembler("bit_set.asm")  
    
    def test_assembler_jump_group(self):
        self._test_assembler("jump_group.asm")        
            
    def test_assembler_call_return_group(self):
        self._test_assembler("call_return.asm")        
    
    def test_assembler_input_output(self):
        self._test_assembler("input_output.asm") 

    def compile_and_load(self,program):
        obj = compile_code(program)
        p=0
        for i in obj:
            self.mem[p]=i
            p+=1
        self.registers.reset()
        self.assertGreater(p, 0, msg="Zero length program, bad compile")
        return p

    def test_program1(self):
        program = ("LD A, 54H",
                   "NOP",
                   "LD BC, 6543H",
                   "LD HL, 1234H",
                   "ADD HL, BC", 
                   "ADD A, A",
                   "SUB A, 37H",
#                   "LD B, 0H",
#                   "LD C, 54H",
                   "LD BC, 54H",
                   "INC BC", 
                   "SBC HL, BC",
                   "ADD IX, BC",
                   "ADD IX, IX", 
                   "ADD IX, SP",
                   "inc ix", 
                   "inc iy", 
                   "inc iy", 
                   "dec iy",
                   "ld b, a", 
                   "ld a, 0x01",
                   "rla",
                   "ld C, 1H",
                   "rlc c", 
                   "rlc c", 
                   "rlc c",
                   "ld iy, 1ffH",
                   "ld (iy+0H), 0x8", 
                   "rlc (iy+0H)", 
                   "HALT"
                   )
        program = string.join(program, "\n")
        self.compile_and_load(program)
        while not self.registers.HALT:
            ins, args = False, []
            while not ins:
                ins, args = self.instructions << self.mem[self.registers.PC]
                self.registers.PC = util.inc8(self.registers.PC)

            self.execute((ins, args))
        print self.registers.A
        
        self.assertEqual(self.registers.B, 0x54+0x54-0x37)
        self.assertEqual(self.registers.HL, 0x6543+0x1234-0x55)
        self.assertEqual(self.registers.IX, 0x55 + 0x55 + 1)
#        self.assertEqual(self.registers.IY, 0x01)
        self.assertEqual(self.registers.A, 2)
        self.assertEqual(self.registers.C, 8)
        self.assertEqual(self.mem[0x1ff], 16)

class TestAdditionSubtraction(unittest.TestCase):

    def setUp(self):
        self.registers = registers.Registers(power=None)
        
    def test_addition_overflow1_flag(self):
        res = util.add8(util.make_8bit_twos_comp(10), util.make_8bit_twos_comp(10),
                  self.registers)
        self.assertEqual(util.get_8bit_twos_comp(res), 20)
        self.assertFalse(self.registers.condition.PV)
        
    def test_addition_overflow2_flag(self):
        res = util.add8(util.make_8bit_twos_comp(-10), util.make_8bit_twos_comp(10),
                  self.registers)
        print util.get_8bit_twos_comp(res)
        self.assertEqual(util.get_8bit_twos_comp(res), 0)
        self.assertFalse(self.registers.condition.PV)
        self.assertFalse(self.registers.condition.S)
        
    def test_addition_overflow3_flag(self):
        res = util.add8(util.make_8bit_twos_comp(-10), util.make_8bit_twos_comp(-10),
                  self.registers)
        self.assertEqual(util.get_8bit_twos_comp(res), util.get_8bit_twos_comp(-20))
        print util.get_8bit_twos_comp(res)
        self.assertFalse(self.registers.condition.PV)
        self.assertTrue(self.registers.condition.S)
        
    def test_addition_overflow4_flag(self):
        res = util.add8(util.make_8bit_twos_comp(-100), util.make_8bit_twos_comp(-100),
                  self.registers)
        self.assertTrue(self.registers.condition.PV)
        
    def test_addition_overflow5_flag(self):
        res = util.add8(util.make_8bit_twos_comp(100), util.make_8bit_twos_comp(100),
                  self.registers)
        self.assertTrue(self.registers.condition.PV)
        
    def test_subtraction_overflow_flag_1(self):
        res = util.subtract8_check_overflow(util.make_8bit_twos_comp(10), util.make_8bit_twos_comp(10),
                  self.registers)
        self.assertEqual(res, util.get_8bit_twos_comp(0))
        self.assertFalse(self.registers.condition.PV)
        
    def test_subtraction_overflow_flag_2(self):
        res = util.subtract8_check_overflow(util.make_8bit_twos_comp(-10), util.make_8bit_twos_comp(10),
                  self.registers)
        self.assertEqual(util.get_8bit_twos_comp(res), -20)
        self.assertFalse(self.registers.condition.PV)
        self.assertTrue(self.registers.condition.S)
        
    def test_subtraction_overflow_flag_3(self):
        res = util.subtract8_check_overflow(util.make_8bit_twos_comp(-10), util.make_8bit_twos_comp(-10),
                  self.registers)
        self.assertEqual(util.get_8bit_twos_comp(res), 0)
        self.assertFalse(self.registers.condition.PV)
        
    def test_subtraction_overflow_flag_4(self):
        res = util.subtract8_check_overflow(util.make_8bit_twos_comp(-100), util.make_8bit_twos_comp(100),
                  self.registers)
        self.assertTrue(self.registers.condition.PV)
        
    def test_subtraction_overflow_flag_5(self):
        res = util.subtract8_check_overflow(util.make_8bit_twos_comp(100), util.make_8bit_twos_comp(-100),
                  self.registers)
        self.assertTrue(self.registers.condition.PV)
        
    def test_twos_comp(self):
        self.assertEqual(util.get_8bit_twos_comp(0b100), 4)
        self.assertEqual(util.get_8bit_twos_comp(0b11100011), -29)
        self.assertEqual(util.make_8bit_twos_comp(-29),0b11100011) 
        self.assertEqual(util.make_8bit_twos_comp(25),0b00011001) 
        
if __name__ == '__main__':
    unittest.main()
    raw_input()