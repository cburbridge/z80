from z80 import util, io, gui, registers, instructions

import copy

from time import sleep, time
import sys
from PySide.QtCore import *
from PySide.QtGui import *

import threading

#logging.basicConfig(level=logging.INFO)

class Z80SBC(io.Interruptable):
    def __init__(self):
        self.registers = registers.Registers()
        self.instructions = instructions.InstructionSet(self.registers)
        self._memory = bytearray(64*1024)
        self._read_rom("../roms/ROM.HEX")
        self._iomap = io.IOMap()
        self._console = io.Console(self)
        self._reg_gui = gui.RegistersGUI(self.registers)
        self._mem_view = gui.MemoryView(self._memory, self.registers)
        
        self._iomap.addDevice(self._console)
        self._console.show()
        self._reg_gui.show()
        self._mem_view.show()
        
        self._interrupted = False
        
    def interrupt(self):
        self._interrupted = True
    
    def _read_rom(self, romfile):
        with open(romfile,  "r") as f:
            while True:
                line =  f.readline()
                if line[0] != ":":
                    raise Exception("Bad start code in hex file.")
                count =  int(line[1:3], 16)#.decode("hex")
                address =  int(line[3:7], 16) #.decode("hex")
                if address + count > len(self._memory):
                    raise Exception("Trying to create M2764 ROM with too large a ROM file")
                rtype =  line[7:9]
                pos = 9
                if rtype == "01":
                    break
                for b in range(count):
                    byte =  int(line[pos+(2*b):pos+(2*b)+2], 16) #. decode("hex")
                    self._memory[address+b] = byte
    
    def step_instruction(self):
        ins, args = False, []
        pc = self.registers.PC
        
        if self._interrupted and self.registers.IFF:
            self.registers.IFF = False
            self._interrupted = False
            if self.registers.IM == 1:
                print "!!! Interrupt  !!!"
                ins, args = self.instructions << 0xCD
                ins, args = self.instructions << 0x38
                ins, args = self.instructions << 0x00
                self.registers.IFF = False
        else:        
            while not ins:
                ins, args = self.instructions << self._memory[self.registers.PC]
                self.registers.PC = util.inc16(self.registers.PC)
            #print( "{0:X} : {1} ".format(pc, ins.assembler(args)))
        
        rd =  ins.get_read_list(args)
        data = [0] * len(rd)
        for n, i in enumerate(rd):
            if i < 0x10000:
                data[n] = self._memory[i]
            else:
                address = i & 0xFF
                data[n] = self._iomap.address[address].read(address)
        wrt = ins.execute(data, args)
        for i in wrt:

            if i[0] > 0x10000:
                address = i[0] & 0xFF
                #iomap.address[address].write.emit(address, i[1])
                self._iomap.address[address].write(address, i[1])
                #print (chr(i[1]))
            else:
                self._memory[i[0]] = i[1]
        
        return ins, args

                    
if __name__ == '__main__':
    ''' Main Program '''
    qt_app = QApplication(sys.argv)
    
    mach = Z80SBC()
    def worker():
        t = time()
             
        while True:
            # t = time()
            ins,  args =  mach.step_instruction()
            print ins.assembler(args)
            sleep(0.00000001)
            # print (time() - t) / ins.tstates
            
            # mach._mem_view.update()
            # mach._reg_gui.update()
            
    

    thread = threading.Thread(target=worker)
    thread.setDaemon(True)
    thread.start()
 
    qt_app.exec_()
