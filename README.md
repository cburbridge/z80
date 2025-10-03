## Z80 CPU Emulator

This is a Zilog Z80 CPU emulator, written in Python. 
It runs a 1978 Microsoft Basic 4.7 ROM taken from [Grant Searle's Z80 SBC project](http://searle.hostei.com/grant/z80/SimpleZ80.html)

### Why?
Just for fun. I like the Z80 CPU - it was in many devices I played with as a
kid. 

### Is it useful?
No. It runs really slowly, and is a completely non-optimal software design for
an emulator, but (in my opinion) the code is readable. If you want a CPU emulator, 
probably don't use Python. That said, an optimised python coded emulator could run 
a lot faster than this :-)

### Running
BASIC:
```
cd src
python z80sbc.py
```
Unit tests:
```
cd src
PYTHONPATH=`pwd`:$PYTHONPATH python ../tests/test_z80.py
PYTHONPATH=`pwd`:$PYTHONPATH python ../tests/test_registers.py
```

Fuse tests:
```
cd src
PYTHONPATH=`pwd`:$PYTHONPATH python ../fuse_tests/tests.py
```

The unit tests use and require [GNU z80asm][z80asm]. For non-Windows machines, you can install it using the package manager specific to your platform. For Windows, a 32-bit binary build of z80asm-1.8 is provided for your convenience.

### Missing and todo

- Most undocumented opcodes
- Undocumented flags for `CPI` and `CPIR`.

### Credits

[Grant Searle's Z80 SBC project](http://searle.hostei.com/grant/z80/SimpleZ80.html)

[FUSE - Free Unix Spectrum Emulator](http://fuse-emulator.sourceforge.net/) for the instruction set tests

### License
Public domain; do what you like.



[z80asm]: https://savannah.nongnu.org/projects/z80asm
