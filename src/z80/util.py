register_bits = {'A': 7, 'B': 0, 'C': 1, 'D': 2, 'E': 3, 'H': 4, 'L': 5}
index_bytes = [(0xDD, 'IX'), (0xfd, 'IY')]
#              i, name, bit, val
conditions = [(0 << 3, 'NZ', 'Z', 0),
              (1 << 3, 'Z', 'Z', 1),
              (2 << 3, 'NC', 'C', 0),
              (3 << 3, 'C', 'C', 1),
              (4 << 3, 'PO', 'PV', 0),
              (5 << 3, 'PE', 'PV', 1),
              (6 << 3, 'P', 'S', 0),
              (7 << 3, 'M', 'S', 1),]

def get_16bit_twos_comp(val):
    """ Return the value of an 8bit 2s comp number"""
    sg = val >> 15 
    if sg == 1:
        mag = - ((val ^  0xFFFF) +  1)
        return mag
    else:
        return val

def get_8bit_twos_comp(val):
    """ Return the value of an 8bit 2s comp number"""
    sg = val >> 7 
    if sg == 1:
        mag = - ((val ^  0xFF) +  1)
        return mag
    else:
        return val
        
def make_8bit_twos_comp(val):
    if val > -1:
        return val
    val = (0 - val) ^  0xFF
    val += 1
    return val

def subtract8(a, b, registers, S=True, N=True, Z=True,
              F3=True, F5=True, H=True, PV=False, C=False):
    """ subtract b from a,  return result and set flags """
    res = a - b
    if S:
        registers.condition.S = (res >> 7) &  0x01
    if N:
        registers.condition.N = 1
    if Z:
        registers.condition.Z = (res == 0)
    if F3:
        registers.condition.F3 = res & 0x08
    if F5:
        registers.condition.F5 = res & 0x20
    if H:
        if (b & 0xF) > (a & 0xF) :
            registers.condition.H = 1
        else:
            registers.condition.H = 0
    if PV:
        #if (a >> 7 != b >> 7):
            #if (b >> 7):
                #if a  > (a | (0x1 << 7)):
                    #registers.condition.PV = 1 # overflow
        a = get_8bit_twos_comp(a)
        b = get_8bit_twos_comp(b)
        if (a - b) <  -127 or (a - b) > 128:
            registers.condition.PV = 1 # overflow
        #if get_8bit_twos_comp(res) < -127 or get_8bit_twos_comp(res) > 128:
            #registers.condition.PV = 1 # overflow
        else:
            registers.condition.PV = 0
    if C:
        registers.condition.C = res > 0xFF or res < 0
    return res &  0xFF
    
def subtract8_check_overflow(a, b, registers):
    return subtract8(a, b, registers, PV=True, C=True)

def add8(a, b, registers, S=True, Z=True, H=True,
         PV=True, N=True, C=True, F3=True, F5=True):
    """ add a and b,  return result and set flags """
    res = a + b
    if S:
        registers.condition.S = (res >> 7) &  0x01
    if Z:
        registers.condition.Z = (res & 0xFF == 0)
    if H:
        if ((a & 0xF) + (b & 0xF)) > 0xF :
            registers.condition.H = 1
        else:
            registers.condition.H = 0
    if PV:
        if ((a >> 7) == (b >> 7) and (a >> 7) != ((res & 0xFF) >> 7)):
            registers.condition.PV = 1 # overflow
        else:
            registers.condition.PV = 0
    if N:
        registers.condition.N = 0
    if C:
        registers.condition.C = res > 0xFF or res < 0
    if F3:
        registers.condition.F3 = res & 0x08
    if F5:
        registers.condition.F5 = res & 0x20
    return res &  0xFF

def add16(a, b, registers):
    """ add a and b,  return result and set flags """
    res = a + b
    print (a, "+",b,"=",res)
    registers.condition.S = (res >> 15) &  0x01
    registers.condition.Z = (res == 0)
    if ((a & 0xFFF) + (b & 0xFFF)) > 0xFFF :
        registers.condition.H = 1
    else:
        registers.condition.H = 0
    if ((a >> 15) == (b >> 15) and (a >> 15) != ((res & 0xFFFF) >> 15)):
        registers.condition.PV = 1 # overflow
    else:
        registers.condition.PV = 0
    registers.condition.N = 0
    registers.condition.C = res >> 0xFFFF or res < 0
    
    registers.condition.F3 = res & 0x0800
    registers.condition.F5 = res & 0x2000
    return res &  0xFFFF

def subtract16(a, b, registers):
    """ subtract b from a,  return result and set flags """
    res = a - b
    print (a, "-", b, "=", res, "(", hex(res), ")")
    registers.condition.S = (res >> 15) &  0x01
    registers.condition.N = 1
    registers.condition.Z = (res == 0)
    registers.condition.F3 = res & 0x0800
    registers.condition.F5 = res & 0x2000
    if (b & 0xFFF) > (a & 0xFFF) :
        registers.condition.H = 1
    else:
        registers.condition.H = 0
    
    if (a >> 15 != (res&0xFFFF) >> 15):
        registers.condition.PV = 1 # overflow
    else:
        registers.condition.PV = 0

    registers.condition.C = res > 0xFFFF or res < 0
    return res &  0xFFFF

def inc16(val):
    val += 1
    if val > 0xFFFF: 
        val = 0x0
    return val

def dec16(val):
    val -= 1
    if val < 0:
        val =  0xFFFF
    return val

def inc8(val):
    val += 1
    if val > 0xFF: 
        val = 0x0
    return val

def dec8(val):
    val -= 1
    if val < 0:
        val =  0xFF
    return val

def parity(n):
    p=0
    for i in range(0,8):
        p+=(n >> i) & 0x01
    return not (p % 2) 

def a_and_n(registers, n):
    registers.A = registers.A & n
    registers.condition.H = 1
    registers.condition.N = 0
    registers.condition.PV = parity(registers.A)
    registers.condition.C = 0
    registers.condition.Z = (registers.A==0)
    registers.condition.S = (registers.A>>7)
    set_f5_f3_from_a(registers)


def a_or_n(registers, n):
    registers.A = registers.A | n
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(registers.A)
    registers.condition.C = 0
    registers.condition.Z = (registers.A==0)
    registers.condition.S = (registers.A>>7)    
    set_f5_f3_from_a(registers)    
    
def a_xor_n(registers, n):
    registers.A = registers.A ^ n
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(registers.A)
    registers.condition.C = 0
    registers.condition.Z = (registers.A==0)
    registers.condition.S = (registers.A>>7)    
    set_f5_f3_from_a(registers)
 
def rotate_left_carry(registers, n):
    c = n >> 7
    v = (n << 1 | c) & 0xFF
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def rotate_left(registers, n):
    c = n >> 7
    v = (n << 1 | registers.condition.C) & 0xFF
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


    
 
def rotate_right_carry(registers, n):
    c = n & 0x01
    v = n >> 1 | (c << 7)
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def rotate_right(registers, n):
    c = n & 0x01
    v = n >> 1 | (registers.condition.C << 7)
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def shift_left(registers, n):
    c = n >> 7
    v = (n << 1 ) & 0xFF
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def shift_left_logical(registers, n):
    c = n >> 7
    v = ((n << 1 ) & 0xFF) | 0x01
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def shift_right(registers, n):
    c = n & 0x01
    msb = n >> 7
    v = n >> 1 | (msb << 7)
    registers.condition.S = v >> 7
    registers.condition.Z = (v == 0)
    registers.condition.H = 0
    registers.condition.N = 0
    registers.condition.PV = parity(v)
    registers.condition.C = c
    return v


def offset_pc(registers, jump):
    registers.PC += get_8bit_twos_comp(jump)
    if registers.PC > 0xFFFF:
        registers.PC -= 0xFFFF - 1
    if registers.PC < 0:
        registers.PC += 0xFFFF + 1
        
def set_f5_f3(registers, v):
    registers.condition.F5 = v & 0x20
    registers.condition.F3 = v & 0x08
        
def set_f5_f3_from_a(registers):
    set_f5_f3(registers, registers.A)
    