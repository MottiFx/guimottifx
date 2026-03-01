from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from libmottifx.compact.effect import LISTEFFECT
from guimottifx.utils.signal import UTILSPREVIEW, UTILSRENDER, UTILSTIMELINE

class CustomLayoutContent(QFrame):
    def __init__(self,left,center,*args, **kwargs):
        super().__init__(*args, **kwargs)

        hlyout = QHBoxLayout()
        hlyout.setSpacing(8)
        hlyout.setContentsMargins(0,0,0,0)

        self.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Fixed)
        self.setLayout(hlyout)

        hlyout.addWidget(left,0)
        hlyout.addWidget(center,1)

class MenuFx(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("frame_content")
        lyout = QVBoxLayout(self)
        lyout.setContentsMargins(15,15,15,15)
        lyout.setObjectName("lyout_content")
        lyout.setSpacing(20)
        lyout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lyout.addWidget(self.MainBar(),0)
        lyout.addWidget(self.MainContent(),1)
        UTILSRENDER.RENDERSTART.connect(self.pauseMenufx)
        UTILSPREVIEW.preview_play.connect(self.pauseMenufx)

    def pauseMenufx(self):
        if self.isEnabled(): self.setEnabled(False)
        else: self.setEnabled(True)

    def MainBar(self):
        frame = QFrame()
        hylout = QHBoxLayout()
        frame.setLayout(hylout)
        hylout.setContentsMargins(0,0,0,0)
        hylout.setSpacing(10)

        self.iptsearch = QLineEdit()
        self.iptsearch.setObjectName("search_file")
        self.iptsearch.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.iptsearch.setPlaceholderText("Search")
        self.iptsearch.textChanged.connect(self.searchContent)
        
        hylout.addWidget(self.iptsearch,1)
        return frame

    def MainContent(self):
        scrollarea = QScrollArea()
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setWidgetResizable(True)
        scrollarea.setFrameShape(QFrame.NoFrame)
        scrollarea.showEvent = self.showContent

        widget = QWidget()
        self.contentlist = QVBoxLayout()
        self.contentlist.setContentsMargins(0,0,0,0)
        self.contentlist.setSpacing(15)
        self.contentlist.setAlignment(Qt.AlignmentFlag.AlignTop)

        widget.setLayout(self.contentlist)
        scrollarea.setWidget(widget)

        return scrollarea
    
    def hoverContent(self,ishover,w):
        # state = variable (can change)
        state = "hover" if ishover else "normal"
        # change status qss hover or normal
        w.setProperty("state",state)
        # delete olde style
        w.style().unpolish(w)
        # update to new style
        w.style().polish(w)

    def addContent(self,data):
        for obj in data:
            if obj["basic"]: continue
            lblicon = QLabel()
            lblname = QLabel()
            lblicon.setText("\uf866")
            lblname.setText(obj["name"])
            lblname.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
            lblname.setObjectName("content_text")
            lblname.setProperty("state","normal")
            lblname.setToolTip("Click to add")
            lblicon.setObjectName("content_icon")
            lblicon.setProperty("state","normal")

            combs = CustomLayoutContent(lblicon,lblname)
            combs.setObjectName("custom_list")
            combs.enterEvent = lambda e,ishvr=True,w1=lblicon,w2=lblname: (
                self.hoverContent(ishover=ishvr,w=w1),
                self.hoverContent(ishover=ishvr,w=w2),
            )
            combs.leaveEvent = lambda e,ishvr=False,w1=lblicon,w2=lblname: (
                self.hoverContent(ishover=ishvr,w=w1),
                self.hoverContent(ishover=ishvr,w=w2),
            )
            combs.mousePressEvent = lambda e,prodata=obj: (
                UTILSTIMELINE.timeline_and_assetbar_1.emit(prodata),
            )
            self.contentlist.addWidget(combs)
            # TODO: NEED FEATURE, EXPAND OR NOT AND DEL EFFECT AND ORDER EFFECT

    def showContent(self,e):
        self.addContent(LISTEFFECT)

    def searchContent(self):
        text = self.iptsearch.text()
        data = [ass for ass in LISTEFFECT if text.lower() in ass["name"].lower()]
        self.refreshContent(data)

    def refreshContent(self,d):
        while self.contentlist.count():
            ch = self.contentlist.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()

        self.addContent(d)

        



