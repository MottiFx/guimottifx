from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

monitor = get_monitors()[0]
w,h = int(monitor.width/2.2), int(monitor.height/1.5)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)

class LicenseProduct(QScrollArea):
    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)
        self.setHidden(True)
        self.setGeometry(x,y,w,h)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setObjectName("PopUpFrame")
        
        frm = QWidget()
        titlelbl = QLabel("MottiFx - End User License Agreement")
        titlelbl.setObjectName("eulattl")
        titlelbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        main_lyout = QVBoxLayout()
        frm.setLayout(main_lyout)
        self.setWidget(frm)
        main_lyout.setContentsMargins(10,10,15,15)
        main_lyout.setSpacing(20)
        main_lyout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.elattl = QLabel()
        self.elattl.setObjectName("elattl")
        self.loadEula()
        
        main_lyout.addWidget(titlelbl,0)
        main_lyout.addWidget(self.elattl,0)

    def loadEula(self):    
        try:
           with open("styles/license.txt",mode="r",encoding="utf-8") as f:
             content = f.read()
             self.elattl.setText(content)
        except FileNotFoundError:
           self.elattl.setText("No Eula License")
                
