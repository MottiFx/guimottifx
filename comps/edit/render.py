from typing import Any
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtOpenGLWidgets import *
from screeninfo import get_monitors

from guimottifx.utils.configediting import ConfigRender, ConfigThreadRender
from procmottifx.decode.layerdecode import ManageRender
from guimottifx.utils.signal import UTILSRENDER

monitor = get_monitors()[0]
w,h = int(monitor.width/5), int(monitor.height/4)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)
data_format = ["h264","hevc","qtrle","mpeg4","libvpx","libx264","libopus"]
datarender: dict[Any, None] = {
  "codec": None,
  "bitrate": None,
  "folder": None,
  "name": None
}


class CenterGui(QFrame):
  def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("PopUpFrame")
        vlyout = QVBoxLayout()
        vlyout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vlyout.setContentsMargins(0,0,0,0)
        vlyout.setSpacing(0)
        self.setLayout(vlyout)
        self.noproc = "(*_~_*)"

        self.lbl = QLabel("")
        self.lbl.setObjectName("tmproc")
        UTILSRENDER.PROGTEXT.connect(self.changeProg)
        vlyout.addWidget(self.lbl)

  def changeProg(self,txt):
        self.lbl.setText(txt)
        
class TopGui(QFrame):
  def __init__(self,*args, **kwargs):
      super().__init__(*args, **kwargs)
      hlyout = QHBoxLayout()
      self.setLayout(hlyout)        
      hlyout.setSpacing(10)
      hlyout.setAlignment(Qt.AlignmentFlag.AlignLeft)
      self.setObjectName("PopUpFrame")

      butt1 = QPushButton("Select Folder")
      butt1.clicked.connect(self.selFolder)
      self.butt2 = QComboBox()
      self.butt2.addItems(data_format)
      datarender["codec"] = self.butt2.currentText()
      self.butt2.currentIndexChanged.connect(self.selCodec)
      self.butt3 = QSpinBox()
      self.butt3.setRange(1,64)
      self.butt3.setValue(5)
      datarender["bitrate"] = self.butt3.value()
      self.butt3.setSuffix("Mbps")
      self.butt3.valueChanged.connect(self.getIptBitRate)
      butt4 = QPushButton("Render")
      butt1.setObjectName("buttcg")
      self.butt2.setObjectName("iptrdr")
      self.butt3.setObjectName("iptrdr")
      butt4.setObjectName("buttcg")

      butt4.clicked.connect(self.pushRender)

      hlyout.addWidget(butt1)
      hlyout.addWidget(self.butt2)
      hlyout.addWidget(self.butt3)
      hlyout.addWidget(butt4)

  def selFolder(self):
      if ConfigRender.status: return
      dlg = QFileDialog.getExistingDirectory(dir="/")
      if dlg:
        print(dlg)
        datarender["folder"] = dlg
      else: return
         
  def selCodec(self):
      if ConfigRender.status: return
      cdc = self.butt2.currentText()
      datarender["codec"] = cdc

  def getIptBitRate(self):
      if ConfigRender.status: return
      nm = self.butt3.value()
      datarender["bitrate"] = nm

  def pushRender(self):
      kl = [key for key,val in datarender.items() if val is None]
      if kl: 
          UTILSRENDER.PROGTEXT.emit("Err:"+"".join(["".join(r+"_") for r in kl]))
          return
      if not ConfigRender.status:
         ConfigThreadRender.MAINFUNC = ManageRender()
         ConfigThreadRender.MAINFUNC.renderProc(datarender["codec"],datarender["bitrate"],datarender["folder"],datarender["name"])
         ConfigRender.status = True
      else:
         ConfigRender.status = False
         ConfigThreadRender.MAINFUNC.stopProc()
         UTILSRENDER.PROGTEXT.emit("(*_~_*)")

class BottomGui(QFrame):
  def __init__(self,*args, **kwargs):
      super().__init__(*args, **kwargs)
      hlyout = QHBoxLayout()
      self.setLayout(hlyout)        
      hlyout.setSpacing(10)
      hlyout.setAlignment(Qt.AlignmentFlag.AlignLeft)
      self.setObjectName("PopUpFrame")
      self.count = 0

      self.butt1 = QLineEdit()
      self.butt1.setPlaceholderText("Example: type_output_name.mp4[always]")
      self.butt1.setObjectName("iptde")
      self.butt1.textChanged.connect(self.getNameFile)
      hlyout.addWidget(self.butt1)
        
  def getNameFile(self):
      nm = self.butt1.text()
      datarender["name"] = nm

class RenderGui(QFrame):
  def __init__(self,*args, **kwargs):
      super().__init__(*args, **kwargs)
      self.setHidden(True)
      self.setGeometry(x,y,w,h)
      # self.setObjectName("PopUpFrame")

      vlyout = QVBoxLayout()
      vlyout.setContentsMargins(10,5,10,5)
      vlyout.setAlignment(Qt.AlignmentFlag.AlignTop)
      self.setLayout(vlyout)

      vlyout.addWidget(TopGui(),0) #0
      vlyout.addWidget(CenterGui(),1) #1
      vlyout.addWidget(BottomGui(),0) #0
      # vlyout.addWidget(loadlabel,1) #1

