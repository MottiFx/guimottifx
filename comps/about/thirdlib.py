from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

monitor = get_monitors()[0]
w,h = int(monitor.width/6), int(monitor.height/3)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)

third_data = [
  {
    "key":"Python",
    "link":"https://docs.python.org/3/license.html",
    "license": "PSFL V2"
  },
  {
    "key":"Moderngl",
    "link":"https://github.com/moderngl/moderngl",
    "license": "MIT"
  },
  {
    "key":"Numpy",
    "link":"https://numpy.org/",
    "license": "BSD 3-CLAUSE"
  },
  {
    "key":"PySide6",
    "link":"https://www.qt.io/",
    "license": "LGPL V3"
  },
  {
    "key":"PyAv",
    "link":"https://pyav.org/docs/stable/development/license.html",
    "license": "BSD 3-CLAUSE"
  },
  {
    "key":"SoundDevice",
    "link":"https://github.com/spatialaudio/python-sounddevice/",
    "license": "MIT"
  },
  {
    "key":"PortAudio",
    "link":"https://portaudio.com/license.html",
    "license": "MIT"
  },
  {
    "key":"Screeninfo",
    "link":"https://github.com/rr-/screeninfo",
    "license": "MIT"
  },
  {
    "key":"Pillow",
    "link":"https://python-pillow.github.io/",
    "license": "MIT-CMU"
  },
  {
    "key":"Protobuf",
    "link":"https://protobuf.dev/",
    "license": "BSD 3-CLAUSE"
  },
  {
    "key":"Lz4",
    "link":"https://lz4.org/",
    "license": "BSD 2-CLAUSE"
  },
]

class ThirdPartyLib(QFrame):
    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)
        self.setGeometry(x,y,w,h)
        self.setObjectName("PopUpFrame")
        self.setHidden(True)
        # self.setWindowTitle("Third-party library")
        # self.setWindowIcon(QIcon("cat8600.ico"))

        titlelbl = QLabel("Third-party libraries")
        titlelbl.setObjectName("tplttl")
        titlelbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        expl = QLabel("MottiFx its build from: ")
        expl.setObjectName("expltpl")

        main_lyout = QVBoxLayout()
        main_lyout.setSpacing(5)
        main_lyout.setContentsMargins(10,10,15,15)
        main_lyout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_lyout)
        main_lyout.addWidget(titlelbl)
        main_lyout.addSpacing(5)
        main_lyout.addWidget(expl)
        main_lyout.addSpacing(5)

        for dt in third_data:
          _fm = QFrame()
          _hlyt = QHBoxLayout()
          _fm.setLayout(_hlyt)
          _hlyt.setAlignment(Qt.AlignmentFlag.AlignLeft)
          _hlyt.setContentsMargins(0,0,0,0)
          _lbl = QLabel("> "+dt["key"]+": ")
          _lbl.setCursor(Qt.CursorShape.PointingHandCursor)
          _lbl.mousePressEvent = lambda _,l=dt["link"]: self.openUrl(l)
          _lcbl = QLabel(dt["license"])

          _lbl.setObjectName("link")
          _lcbl.setObjectName("lcnthird")

          _hlyt.addWidget(_lbl)
          _hlyt.addWidget(_lcbl)
          main_lyout.addWidget(_fm)

    def openUrl(self,link):
        QDesktopServices.openUrl(link)

