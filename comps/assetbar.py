from typing import Any
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from procmottifx.systems.infile.history import make_history
from procmottifx.systems.parsing.cacheframe import run_removch
from procmottifx.systems.projects.addproject import create_asset, create_effect, create_layer
from procmottifx.systems.projects.getproject import get_project, get_projectfile
from guimottifx.utils.configediting import ConfigTimeLine
from guimottifx.utils.currentprj import CurrentPrj, UpdHistory
from procmottifx.systems.protos import schema_pb2 as sch
from guimottifx.utils.information.fileasset import get_information_audio, get_information_image, get_information_video
from guimottifx.utils.signal import UTILSASSETBAR, UTILSPREVIEW, UTILSRENDER, UTILSSETUP


dumy = [f"Project_{i}_{i*10}_____________________________.mp4" for i in range(20)]
iconasset = ["\ueb87","\ue3f4","\ueb82","\uf720","\uf49a","\uf866"]
# video,image,audio,comps/grup/container,frame,adjusment
LIST_TYPE = [".mp4",".avi",".mov",".mp3",".wav",".png",".jpg",".jpeg"]


colorlayer = [
    {"type": sch.TypAss.TYP_ASS_IMAGE, "color": "#ff3030", "icon": "\ue3f4"},
    {"type": sch.TypAss.TYP_ASS_VIDEO, "color": "#3e30ff", "icon": "\ueb87"},
    # {"type": sch.TypAss.TYP_ASS_GROUP, "color":"#f2ff3a","icon": "\uf720"},
    {"type": sch.TypAss.TYP_ASS_AUDIO, "color":"#9900ff","icon": "\ueb82"},
    # {"type": sch.TypAss.TYP_ASS_ADJUSMENT, "color": "#3a4dff", "icon": "\uf866"},
    {"type": sch.TypAss.TYP_ASS_FRAMES, "color": "#fff23a", "icon": "\uf49a"},
]

class CustomList(QFrame):
    def __init__(self,l: Any | None, r: Any | None,ic: Any | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.hlyt = QHBoxLayout()
        self.hlyt.setSpacing(8)
        self.hlyt.setContentsMargins(0,0,0,0)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setLayout(self.hlyt)
        self.hlyt.addWidget(ic,0,alignment=Qt.AlignmentFlag.AlignLeft)
        self.hlyt.addWidget(l,1,alignment=Qt.AlignmentFlag.AlignLeft)
        self.hlyt.addWidget(r,0,alignment=Qt.AlignmentFlag.AlignRight)


class BackProses(CurrentPrj):
    def addfile(self,event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        extensionfile = "".join([f" *{ex} " for ex in LIST_TYPE])
        pathfile,_ = QFileDialog.getOpenFileName(
            dir="/",
            filter=f"Files ({extensionfile})"
            )
        typass = None
        if pathfile:
            namefile = QFileInfo(pathfile).baseName()
            exfile = f".{QFileInfo(pathfile).suffix()}"
            # print(f"{exfile},{namefile}")
            loadproj = get_project()
            fps = loadproj.fps
            width = None
            height = None
            duration = None

            if exfile in LIST_TYPE[0:3]: 
                infovideo = get_information_video(pathfile)
                fps = float(infovideo["fps"])
                width = int(infovideo["width"])
                height = int(infovideo["height"])
                duration = float(infovideo["duration"])
                typass = sch.TypAss.TYP_ASS_VIDEO
            elif exfile in LIST_TYPE[3:5]:
                infoaudio = get_information_audio(pathfile)
                duration = float(infoaudio["duration"])
                fps = 0.00
                width = 0
                height = 0
                typass = sch.TypAss.TYP_ASS_AUDIO
            elif exfile in LIST_TYPE[5:]: 
                infimage = get_information_image(pathfile)
                width = int(infimage["width"])
                height = int(infimage["height"])
                duration = 5.0
                typass = sch.TypAss.TYP_ASS_IMAGE

            data ={
                "file": self.pathfile,
                "name": namefile,
                "typass": typass,
                "path":pathfile,
                "fps": fps,
                "height": height,
                "width": width,
                "duration": duration
            }
            print("\n")
            print(data)
            create_asset(data=data)
            make_history(UpdHistory.ASSETBAR)
            proj,_ = get_projectfile()
            self.refreshasset(proj.assets)

    def searchfile(self):
        text = self.iptsearch.text()
        if self.pathfile:
            proj,_ = get_projectfile()
            data = [ass for ass in proj.assets if text.lower() in ass.name.lower()]
            self.refreshasset(data)

class AssetBar(QFrame,BackProses):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("frame_content")
        main_lyout = QVBoxLayout()
        main_lyout.setContentsMargins(15,15,15,15)
        main_lyout.setSpacing(20)
        self.setLayout(main_lyout)

        main_lyout.addWidget(self.mainbar(),0)
        main_lyout.addWidget(self.listasset(),1)
        main_lyout.addStretch()
        UTILSSETUP.RESETGUI.connect(self.showAsset)
        UTILSPREVIEW.preview_play.connect(self.pauseAssetBar)
        UTILSRENDER.RENDERSTART.connect(self.pauseAssetBar)

    def pauseAssetBar(self):
        if self.isEnabled():
            self.setEnabled(False)
        else: self.setEnabled(True)

    def mainbar(self):
        frame = QFrame()
        # frame.showEvent = lambda e: print("hello")
        # frame.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
        # frame.setObjectName("cont")
        hlyt = QHBoxLayout()
        hlyt.setContentsMargins(0,0,0,0)
        hlyt.setSpacing(10)
        frame.setLayout(hlyt)

        uploadlabel = QLabel("\ue9fc")
        uploadlabel.setObjectName("icon_upload")
        uploadlabel.setCursor(Qt.CursorShape.PointingHandCursor)
        uploadlabel.mousePressEvent = self.addfile
        self.iptsearch = QLineEdit()
        self.iptsearch.setObjectName("search_file")
        self.iptsearch.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.iptsearch.setPlaceholderText("Search")
        self.iptsearch.textChanged.connect(self.searchfile)

        hlyt.addWidget(self.iptsearch,1)
        hlyt.addWidget(uploadlabel)

        return frame
    
    def listasset(self):
        scrollarea = QScrollArea()
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setWidgetResizable(True)
        scrollarea.setFrameShape(QFrame.Shape.NoFrame)
        widget = QWidget()
        # widget.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
        self.scrollist = QVBoxLayout()
        self.scrollist.setContentsMargins(0,0,0,0)
        widget.setLayout(self.scrollist)
        self.scrollist.setSpacing(15)

        scrollarea.setWidget(widget)

        return scrollarea
    

    def hoverAsset(self,ishover,w):
        # state = variable (can change)
        state = "hover" if ishover else "normal"
        # change status qss hover or normal
        w.setProperty("state",state)
        # delete olde style
        w.style().unpolish(w)
        # update to new style
        w.style().polish(w)

    def showAsset(self):
        if self.pathfile:
            proj,_ = get_projectfile()
            self.refreshasset(proj.assets)
            
    def refreshasset(self,d):
        while self.scrollist.count():
            ch = self.scrollist.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()
        
        self.assetadd(d)
                
    def assetadd(self,data):
        for obj in data:
            color = None
            ic = QLabel()
            for cly in colorlayer:
                if obj.typass == cly["type"]: 
                    color = cly["color"]
                    ic.setText(cly["icon"])
            ln = QLabel(obj.name)
            rn = QLabel("\ue5d4")
            ln.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
            ln.setObjectName("content_text")
            ln.setProperty("state","normal")
            ln.setToolTip("Click to add")
            rn.setObjectName("content_icon")
            rn.mouseDoubleClickEvent = lambda e: print("t")
            rn.setProperty("state","normal")
            ic.setObjectName("content_icon")
            ic.setProperty("state","normal")

            combs = CustomList(ln,rn,ic)
            combs.setObjectName("custom_list")
            combs.enterEvent = lambda event,ishvr=True,w1=ln,w2=rn,w3=ic: (
                self.hoverAsset(ishover=ishvr,w=w1),
                self.hoverAsset(ishover=ishvr,w=w2),
                self.hoverAsset(ishover=ishvr,w=w3),
            )
            combs.leaveEvent = lambda event,ishvr=False,w1=ln,w2=rn,w3=ic: (
                self.hoverAsset(ishover=ishvr,w=w1),
                self.hoverAsset(ishover=ishvr,w=w2),
                self.hoverAsset(ishover=ishvr,w=w3),
            )
            combs.mousePressEvent = lambda e, name=obj.name,duration=obj.duration,typass=obj.typass,uid=obj.uid,color=color: (
                self.addLayer(name,duration,typass,uid,color)
            )
            self.scrollist.addWidget(combs)
        self.scrollist.addStretch()
    
    def addLayer(self,name,duration,typass,uid,color):        
        data = {
            "name": name,
            "start": ConfigTimeLine.CURRENTPOS,
            "end": ConfigTimeLine.CURRENTPOS + duration,
            "duration": duration,
            "typass": typass,
            "visible": False,
            "asset_uids": uid,
            "color": color
        }
        lastpos = ConfigTimeLine.CURRENTPOS
        newpos = ConfigTimeLine.CURRENTPOS + duration

        print(data)
        create_layer(data)
        make_history(UpdHistory.LAYER)
        run_removch(lastpos,newpos)
        UTILSASSETBAR.asset_and_timeline_1.emit()
        UTILSASSETBAR.asset_and_layerset_1.emit()

