import sys
 
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import * 

from io import StringIO

class RegistersGUI(QWidget):
    _addresses = [0x80, 0x81]
    _update_sgl = Signal()
    format_data = """
<html>
	<head>
		<title>HTML Online Editor Sample</title>
	</head>
	<body>
		<p>
			&nbsp;</p>
		<table border="0" cellpadding="0" cellspacing="0" style="width: 100px;">
			<tbody>
				<tr>
					<td>
						<span style="font-size:12px;">A</span></td>
					<td>
						<span style="font-size:12px;">0x{A:X}</span></td>
				</tr>
				<tr>
					<td colspan="2">
						<span style="font-size:12px;">Flags</span>
						<table border="0" cellpadding="1" cellspacing="1" style="width: 100px;">
							<tbody>
								<tr>
									<td style="text-align: center;">
										<span style="font-size:12px;">S</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">Z</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">F5</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">H</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">F3</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">PV</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">N</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">C</span></td>
								</tr>
								<tr>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FS}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FZ}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FF5}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FH}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FF3}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FPV}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FN}</span></td>
									<td style="text-align: center;">
										<span style="font-size:12px;">{FC}</span></td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">BC</span></td>
					<td>
						<span style="font-size:12px;">0x{BC:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">DE</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{DE:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">HL</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{HL:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">PC</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{PC:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">SP</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{SP:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">IX</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{IX:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">IY</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{IY:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">I</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{I:X}</span></td>
				</tr>
				<tr>
					<td>
						<span style="font-size:12px;">R</span></td>
					<td>
						<span style="font-size: 12px;">0x</span><span style="font-size: 12px;">{R:X}</span></td>
				</tr>
			</tbody>
		</table></body>
</html>

    
    """
    def __init__(self, registers):
        super(RegistersGUI, self).__init__()

        vbox=QVBoxLayout()
        self.setLayout(vbox)

        self._view = QWebEngineView(self)
        vbox.addWidget(self._view)
        
        
        
        #self.setPlainText("")
        #self.setFontFamily("Mono")
        #self.setFontPointSize(8)
        #self._modifiers = {}
        #self.setCursorWidth(0)
        self._registers = registers
        self._update_sgl.connect(self._update)
        #self.setReadOnly(True)
        self.setGeometry(100, 0, 200, 480)

        self.update()
    
    @Slot()
    def update(self):
        #print "WRITE ", address
        self._update_sgl.emit()
        
    def _update(self):
        fields = {}
        for f in "A,BC,DE,HL,SP,IX,IY,I,R,PC".split(","):
            fields[f] = self._registers[f]
        for b in ["S", "Z", "F5", "H", "F3", "PV", "N", "C"]:
            fields["F{}".format(b)] = getattr(self._registers.condition, b)
        self._view.setHtml(self.format_data.format(**fields))

    

class MemoryView(QWidget):
    _update_sgl = Signal(int)
    def __init__(self, memory, registers):
        super(MemoryView, self).__init__()
        self._modifiers = {}

        self._page_height = 16

        self._memory = memory
        self._registers = registers
        self._update_sgl.connect(self._update)
        self._web_view = QWebEngineView(self)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        hbox =  QHBoxLayout()
        self._offset_entry = QLineEdit()
        self._offset_entry.returnPressed.connect(self.address_change)
        self._offset = 0x0
        self._offset_entry.setText(hex(self._offset))
        self._offset_next = QPushButton(">>")
        self._offset_prev = QPushButton("<<")
        self._offset_next.clicked.connect(self.on_next)
        self._offset_prev.clicked.connect(self.on_prev)
        hbox.addWidget(self._offset_entry)
        hbox.addWidget(self._offset_prev)
        hbox.addWidget(self._offset_next)
        hbox.addStretch(1)
        
        vbox.addLayout(hbox)
        vbox.addWidget(self._web_view)

        self.setGeometry(100, 580, 840, 480)
        self.update()

    def on_next(self):
        self._offset += self._page_height * 16
        self._offset_entry.setText(hex(self._offset))
        self.update()
        pass
    def on_prev(self):
        if self._offset < 1:
            return
        self._offset -= self._page_height *  16
        self._offset_entry.setText(hex(self._offset))
        self.update()
        pass

    def address_change(self):
        new_val=self._offset_entry.text()
        val=0
        ln=0
        try:
            val=int(new_val,16)
            ln=(val-(val%16))# * 16
            pg = ln - ln%(self._page_height*16)
        except:
            return
        
        self._offset_entry.setText(hex(pg))
        self._offset=pg
        self.update(val)

    
    @Slot()
    def update(self,highlight=-1):
        self._update_sgl.emit(highlight)
        
    def _update(self,highlight):

        sp = self._registers.SP
        txt = StringIO()
        txt.write("<table><tr><td>Offset</td>")
        for i in range(16):
            txt.write("<td>{:X}</td>".format(i))
        txt.write("<td>ASCII</td></tr>")

        for i in range(self._offset, min(len(self._memory),
                                         self._offset+16*self._page_height), 16):
            txt.write("<tr>")
            offset = i 
            txt.write("<td>{}</td>".format(hex(offset)))
            ascii = ""
            for j in range(16):
                v = self._memory[offset+j]
                if v > 31 and v < 127:
                    ascii += chr(self._memory[offset+j])
                else:
                    ascii += "."
                if offset+j == sp:
                    txt.write("<td style=\"color:red\">{:2X}</td>".format(v))
                elif highlight > 0 and offset+j==highlight:
                    txt.write("<td style=\"color:blue\">{:2X}</td>".format(v))
                else:
                    txt.write("<td>{:2X}</td>".format(v))
            txt.write("<td><tt>{}</tt></td>".format(ascii))
            txt.write("</tr>")
        txt.write( "</table>")
        text = txt.getvalue()
        txt.close()
        self._web_view.setHtml(text)

        
        pass
    
