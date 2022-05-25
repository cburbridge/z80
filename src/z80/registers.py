class BitAccesser(object):
    def __init__(self, bit_names, registers, reg):
        object.__setattr__(self, "bits",
                           dict(zip(bit_names, range(7, -1, -1))))
        self.registers = registers
        #self.registers = registers
        self.reg = reg
        
    def __getattr__(self, b):
        return (self.registers[self.reg] >>  self.bits[b]) &  1 
    
    def __setattr__(self, b, v):
        if not b in self.bits:
            object.__setattr__(self, b, v)
            return

        if v:
            self.registers[self.reg] = self.registers[self.reg] | (1 <<  self.bits[b])
        else:
            self.registers[self.reg] = self.registers[self.reg] & ((1 <<  self.bits[b]) ^  0xFF)
            
class Registers(dict):
    def __init__(self, *arg, **kw):
        super(Registers, self).__init__(*arg, **kw)

        self.reset()
        
    def reset(self):
        self["PC"] = 0 # Program Counter (16bit)
        self["SP"] = 0 # Stack Pointer (16bit)
        self["IX"] = 0 # Index Register X (16bit)
        self["IY"] = 0 # Index Register Y (16bit)
        self["I"] = 0  # Interrupt Page Address (8bit)
        self["R"] = 0  # Memory Refresh (8bit)

        self["A"] = 0 # Accumulator (8bit)
        self["F"] = 0 # Flags (8bit)
        self["A_"] = 0 # Alt. Accumulator (8bit)
        self["F_"] = 0 # Alt. Flags (8bit)

        self["B"] = 0 # General (8bit)
        self["C"] = 0 # General (8bit)
        self["B_"] = 0 # General (8bit)
        self["C_"] = 0 # General (8bit)

        self["D"] = 0 # General (8bit)
        self["E"] = 0 # General (8bit)
        self["D_"] = 0 # General (8bit)
        self["E_"] = 0 # General (8bit)

        self["H"] = 0 # General (8bit)
        self["L"] = 0 # General (8bit)
        self["H_"] = 0 # General (8bit)
        self["L_"] = 0 # General (8bit)

        self["condition"] = BitAccesser(["S", "Z", "F5", "H", "F3", "PV", "N", "C"], self, "F")
        
        self['HALT']=False #
        self['IFF']=False  # Interrupt flip flop
        self['IFF2']=False  # NM Interrupt flip flop
        self['IM']=False   # Iterrupt mode

    def __setattr__(self, attr, val):
        if attr  in ["HL", "AF", "BC", "DE"]:
            self[attr[0]] = val >> 8
            self[attr[1]] = val &  0xFF
        else:
            self[attr] = val

    def __getattr__(self, reg):
        if reg in self:
            return self[reg]
        elif reg in ["HL", "AF", "BC", "DE"]:
            return self[reg[0]] << 8 |  self[reg[1]]
        else:
            raise AttributeError("%s Not a known register."%reg)
        
    def __getitem__(self, reg):
        if reg in ["BC", "HL", "DE", "AF"]:
            return getattr(self, reg)
        else:
            return super(Registers, self).__getitem__(reg)
        
    def __setitem__(self, reg, val):
        if reg in ["BC", "HL", "DE", "AF"]:
            return setattr(self, reg, val)
        else:
            return super(Registers, self).__setitem__(reg, val)
    
    @classmethod
    def create(cls):
        return cls()
        
