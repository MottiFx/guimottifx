from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

monitor = get_monitors()[0]
w,h = int(monitor.width/3), int(monitor.height/1.5)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)

datasc = [
    {
        "comp":"layer:",
        "feat":"cut:right",
        "command":"alt+]"
    },
    {
        "comp":"layer:",
        "feat":"cut:left",
        "command":"alt+["
    },
    {
        "comp":"layer:",
        "feat":"del:selected",
        "command":"delete"
    },
    {
        "comp":"layer:",
        "feat":"unfocus",
        "command":"`"
    },
    {
        "comp":"timeline:",
        "feat":"zoom:in",
        "command":"ctrl+="
    },
    {
        "comp":"timeline:",
        "feat":"zoom:out",
        "command":"ctrl+-"
    },
    {
        "comp":"workspace:",
        "feat":"undo",
        "command":"ctrl+z"
    },
    {
        "comp":"workspace:",
        "feat":"redo",
        "command":"ctrl+shift+z"
    },
    {
        "comp":"workspace:",
        "feat":"render",
        "command":"ctrl+r"
    },
    {
        "comp":"workspace:",
        "feat":"manager",
        "command":"ctrl+m"
    },
] * 1

class KeyboardSc(QFrame):
    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)
        self.setHidden(True)
        self.setGeometry(x,y,w,h)
        self.setObjectName("PopUpFrame")

        main_lyout = QVBoxLayout()
        self.setLayout(main_lyout)
        main_lyout.setContentsMargins(10,15,10,15)
        main_lyout.setSpacing(20)
        main_lyout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # kybrd_sc = QShortcut(QKeySequence("ctrl+k"),self)
        # kybrd_sc.activated.connect(self.scKeyboard)

        main_lyout.addWidget(self.iptSearch(),0)
        main_lyout.addWidget(self.titlePage(),0)
        main_lyout.addWidget(self.mainPage(),1)

    def showEvent(self, event):
        self.refresContent(datasc)
        return super().showEvent(event)

    def iptSearch(self):
        self.iptsc = QLineEdit()
        self.iptsc.setObjectName("iptsc")
        self.iptsc.setPlaceholderText("Type something...")
        self.iptsc.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.iptsc.textChanged.connect(self.searchSc)
        return self.iptsc

    def titlePage(self):
        fm = QFrame()
        lbl1 = QLabel("Bindings".upper())
        lbl2 = QLabel("Commands".upper())
        lbl1.setObjectName("ttlkyc")
        lbl2.setObjectName("ttlkyc")
        lbl1.setContentsMargins(5,5,5,5)
        lbl2.setContentsMargins(5,5,5,5)
        qhb = QHBoxLayout()
        qhb.setContentsMargins(0,0,0,0)
        fm.setLayout(qhb)
        qhb.addWidget(lbl1,1)
        qhb.addWidget(lbl2,1)
        return fm

    def mainPage(self):
        fm = QFrame()
        hbox = QHBoxLayout()
        fm.setLayout(hbox)
        hbox.setContentsMargins(0,0,0,0)

        scroll1 = QScrollArea()
        scroll2 = QScrollArea()
        scroll1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll1.setWidgetResizable(True)
        scroll2.setWidgetResizable(True)
        scroll1.setFrameShape(QFrame.Shape.NoFrame)
        scroll2.setFrameShape(QFrame.Shape.NoFrame)
        scroll1.setObjectName("wkyb")
        scroll2.setObjectName("wkyb")

        wdg1 = QFrame()
        wdg2 = QFrame()
        wdg1.setObjectName("fkyb")
        wdg2.setObjectName("fkyb")

        self.scrollpg1 = QVBoxLayout()
        self.scrollpg2 = QVBoxLayout()
        self.scrollpg1.setSpacing(15)
        self.scrollpg2.setSpacing(15)
        self.scrollpg1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollpg2.setAlignment(Qt.AlignmentFlag.AlignTop)

        wdg1.setLayout(self.scrollpg1)
        wdg2.setLayout(self.scrollpg2)

        scroll1.setWidget(wdg1)
        scroll2.setWidget(wdg2)
        
        hbox.addWidget(scroll1)
        hbox.addWidget(scroll2)

        return fm

    def addContent(self,dt):
        for data in dt:
            leftlabel = QLabel(data["comp"].upper()+data["feat"].upper())
            rightlabel = QLabel(data["command"])
            leftlabel.setContentsMargins(5,5,5,5)
            rightlabel.setContentsMargins(5,5,5,5)

            leftlabel.setObjectName("lftkyb")
            rightlabel.setObjectName("rgtkyb")

            self.scrollpg1.addWidget(leftlabel)
            self.scrollpg2.addWidget(rightlabel)

    def refresContent(self,dt):
        while self.scrollpg1.count() or self.scrollpg2.count():
            ch1 = self.scrollpg1.takeAt(0)
            ch2 = self.scrollpg2.takeAt(0)
            if ch1.widget():
                ch1.widget().deleteLater()
            if ch2.widget():
                ch2.widget().deleteLater()

        self.addContent(dt)

    def searchSc(self):
        val = self.iptsc.text()
        dt = [d for d in datasc if val in d["comp"] or val in d["feat"] or val in d["command"]]
        # dt = [d for d in datasc if val in d]
        self.refresContent(dt)

    



