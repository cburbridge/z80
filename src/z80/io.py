import sys
 
from PySide.QtCore import *
from PySide.QtGui import *

class IO(object):
    _addresses = []
    def read(self, address):
        pass
    def write(self, address, value):
        pass
    
class Interruptable(object):
    def interrupt(self):
        print "interrupt"
        pass
    
class Console(QTextEdit, IO):
    _addresses = [0x80, 0x81]
    _wrt_sgnl = Signal(int, int)
    def __init__(self, interruptable):
        #assert isinstance(interruptable, Interruptable )
        super(Console, self).__init__()
        self.setPlainText("")
        self.setFontFamily("Courier")
        self.setFontPointSize(12)
        self._modifiers = {}
        self.setCursorWidth(0)
        self._interruptable = interruptable
        self._wrt_sgnl.connect(self._write)
        self.setReadOnly(True)
        self.setGeometry(300, 0, 640, 480)

        
        self._send_queue = None
        
    def read(self, address):
        print "READ ", address
        if address == 0x80:
            v =  ((1 << 1) | # RTS
                  ((self._send_queue is not None) << 0) | # interrupt?
                  0 )
            return v
        elif address == 0x81:
            if self._send_queue is not None:
                val = self._send_queue
                self._send_queue = None
                return val
        return 0x13
    
    
    @Slot(int, int)
    def write(self, address, value):
        print "------> WRITE ", address
        self._wrt_sgnl.emit(address, value)
        
    def _write(self, address, value):
        if address == 0x80:
            pass
        elif address == 0x81:
            if value <  128 and value > 10:
                self.setText(self.toPlainText()+chr(value))
            else:
                self.setText(self.toPlainText()+".")
        else:
            raise Exception("Trying Console IO with wrong address")
        
    def keyPressEvent(self, event):
#        print ("Event:", event)
        if isinstance(event, QKeyEvent):
            if event.key() > 255:
                self._modifiers[event.key()] = True
            #else:
                #self.setText(self.toPlainText()+chr(event.key()))
        if True:
            super(QTextEdit, self).keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
#        print ("Event:", event)
        if isinstance(event, QKeyEvent):
            key =  event.key()
            if key == Qt.Key_Return or event.key() == Qt.Key_Enter:
                key = 13
            if event.key() > 255:
                self._modifiers[event.key()] = False
            #print (key)
            
            if self._send_queue is None:
                self._send_queue = key
                self._interruptable.interrupt()
            pass
        
    
class IOMap(object):
    def __init__(self):
        self.address = {}
        pass
    def addDevice(self, dev):
        assert isinstance(dev, IO)
        for i in dev._addresses:
            self.address[i] = dev
        
    def interupt(self):
        pass
   
