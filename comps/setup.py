from itertools import zip_longest
import os
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

from procmottifx.systems.infile.history import make_history
from procmottifx.systems.infile.saveinfo import delinfo, loadinfo, makeinfo, updinfo
from procmottifx.systems.projects.addproject import create_project
from procmottifx.systems.projects.getproject import get_project
from guimottifx.utils.configediting import ConfigTimeLine
from guimottifx.utils.currentprj import CurrentPrj
from guimottifx.utils.signal import UTILSLAYER, UTILSSETUP

monitor = get_monitors()[0]
w,h = int(int(monitor.width/1.1)/1.5), int(int(monitor.height/1.1)/1.3)
# dumy = [{"namefile": f"coba_{i}","datetime": "2010-20-02 10:05:03"} for i in range(20)]
datacreate: dict[Any , None] = {
    "name":None,
    "fps": None,
    "width": None,
    "height": None,
    "folder": None,
    "duration": None,
}

class CustomForm(QFrame):
    def __init__(self,lbl: Any | None,ipt: Any | None,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.boxv = QVBoxLayout()
        self.setLayout(self.boxv)
        self.boxv.setContentsMargins(0,0,0,0)
        self.boxv.setSpacing(8)

        self.boxv.addStretch()
        if lbl:
            self.boxv.addWidget(lbl,0)
        if ipt:
            self.boxv.addWidget(ipt,0)
        self.boxv.addStretch()

class CustomList(QFrame):
    def __init__(self,l: Any | None,r: Any | None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.boxh = QHBoxLayout()
        self.setLayout(self.boxh)
        self.boxh.setContentsMargins(0,0,0,0)
        self.boxh.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.boxh.addWidget(l,alignment=Qt.AlignmentFlag.AlignLeft)
        self.boxh.addWidget(r,alignment=Qt.AlignmentFlag.AlignRight)

class BackProse:
    def getfolder(self):
        dialogfl = QFileDialog.getExistingDirectory(dir="/")
        if dialogfl:
            print(dialogfl)
            datacreate["folder"] = dialogfl
        else: print("NO DIR")
    def getname(self):
        nameipt = self.inputname.text()
        datacreate["name"] = nameipt.lower()
        # print(datacreate["name"])
    def getfps(self):
        fpsipt = self.inputfps.value()
        datacreate["fps"] = int(fpsipt)
    def getwidth(self):
        widthipt = self.inputwidth.value()
        datacreate["width"] = widthipt
    def getheight(self):
        heightipt = self.inputheight.value()
        datacreate["height"] = heightipt
    def getduration(self):
        time = self.inputduration.time()
        time_convert_second = QTime(0,0,0,0).msecsTo(time)
        mildetik_to_detik = time_convert_second / 1000.0
        datacreate["duration"] = mildetik_to_detik
        print(datacreate["duration"])
    def createproj(self):
        check = next((True for x in datacreate.values() if x is None or not x),False)
        namefile = datacreate["name"]
        folder = datacreate["folder"]
        pathfile = f"{folder}/{namefile}/{namefile}.mpj"
        folderfile  = f"{folder}/{namefile}"
        entryinfo = {"name":namefile,"path":pathfile,"folder":folderfile}
        existfile = next((True for x in loadinfo() if x["namefile"] == namefile 
        and x["folderfile"] == folderfile),False)
        checkfolder = os.path.exists(folderfile)
        # print(datacreate["fps"])
        if check:
            QMessageBox.information(self,"Information","fill in the fields correctly")
        else:
            if existfile or checkfolder:
                QMessageBox.information(self,"Information","file already exist")
            else:
                # print("good")
                CurrentPrj.namefile = namefile
                CurrentPrj.folderfile = folderfile
                CurrentPrj.pathfile = pathfile
                ConfigTimeLine.DURATION = datacreate["duration"]
                ConfigTimeLine.FPS = datacreate["fps"]
                makeinfo(entryinfo)
                create_project(data=datacreate)
                make_history(CurrentPrj.fl_updhistory)
                self.menubarw.show()
                self.page.setCurrentIndex(0)
                UTILSSETUP.RESETGUI.emit()
                UTILSLAYER.setup_frame.emit()
    def loadproj(self,event):
        pathfile,_ = QFileDialog.getOpenFileName(dir="/",filter="Files (*.mpj)")
        namefile = QFileInfo(pathfile).baseName().lower()
        folderfile = QFileInfo(pathfile).path()
        existfile = next((True for x in loadinfo() if x["namefile"] == namefile and x["folderfile"] == folderfile),False)
        entryinfo = {"name":namefile,"path":pathfile,"folder":folderfile}
        if pathfile:
            CurrentPrj.namefile = namefile
            CurrentPrj.folderfile = folderfile
            CurrentPrj.pathfile = pathfile
            project = get_project()
            ConfigTimeLine.DURATION = project.duration
            ConfigTimeLine.FPS = project.fps
            make_history(CurrentPrj.fl_updhistory)
            if existfile:
                updinfo(pathfile)
                print("exist file")
                self.menubarw.show()
                self.page.setCurrentIndex(0)
            else:
                makeinfo(entryinfo)
                self.menubarw.show()
                self.page.setCurrentIndex(0)
            UTILSSETUP.RESETGUI.emit()
            UTILSLAYER.setup_frame.emit()
        # print(f"path: {folderfile}, name: {namefile}")

    def selectproject(self,filepath,idxprj,filename,filefolder):
        check = Path(filepath).exists()
        if check:
            CurrentPrj.pathfile = filepath
            CurrentPrj.namefile = filename
            CurrentPrj.folderfile = filefolder
            project = get_project()
            ConfigTimeLine.DURATION = project.duration
            ConfigTimeLine.FPS = project.fps

            updinfo(filepath)
            make_history(CurrentPrj.fl_updhistory)
            print(CurrentPrj.pathfile)
            self.menubarw.show()
            self.page.setCurrentIndex(0)
            UTILSSETUP.RESETGUI.emit()
            UTILSLAYER.setup_frame.emit()
            # print("good")
        else:
            print(idxprj)
            delinfo(idxprj)
            self.warninfo()
            self.updrecent()
            print("not exist")



class SetupApp(QFrame,BackProse):
    def __init__(self, menubar,page,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedSize(w,h)
        self.page = page
        self.menubarw = menubar
        # self.setObjectName("frame_content")
        grdlyot = QGridLayout()
        self.setLayout(grdlyot)
        self.menubarw.hide()

        grdlyot.setColumnStretch(0,1)
        grdlyot.setColumnStretch(1,2)

        grdlyot.addWidget(self.addProject(),0,0)
        grdlyot.addWidget(self.recentProject(),0,1)

    def addProject(self):
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
        frame.setObjectName("frame_content")

        vetical = QVBoxLayout()
        frame.setLayout(vetical)
        vetical.setSpacing(25)
        vetical.setContentsMargins(30,30,30,30)

        labelname = QLabel("Name:")
        self.inputname = QLineEdit()
        self.inputname.setObjectName("input_str")
        self.inputname.setMaxLength(15)
        self.inputname.textChanged.connect(self.getname)
        labelfps = QLabel("Fps:")
        self.inputfps = QDoubleSpinBox()
        self.inputfps.setObjectName("input_float")
        self.inputfps.setRange(1,120)
        self.inputfps.valueChanged.connect(self.getfps)
        labelwidth = QLabel("Width:")
        self.inputwidth = QSpinBox()
        self.inputwidth.setObjectName("input_int")
        self.inputwidth.setRange(1,20000)
        self.inputwidth.valueChanged.connect(self.getwidth)
        labelheight = QLabel("Height:")
        self.inputheight = QSpinBox()
        self.inputheight.setRange(1,20000)
        self.inputheight.setObjectName("input_int")
        self.inputheight.valueChanged.connect(self.getheight)
        label_duration = QLabel("Duration:")
        self.inputduration = QTimeEdit()
        self.inputduration.setDisplayFormat("HH:mm:ss.zzz")
        self.inputduration.setTimeRange(QTime(0,0,0,0),QTime(2,0,0,0))
        self.inputduration.setObjectName("input_time")
        self.inputduration.timeChanged.connect(self.getduration)
        self.inputname.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.inputfps.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.inputwidth.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.inputheight.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.inputduration.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        upfolder = QPushButton("Select Directory")
        upfolder.setObjectName("input_file")
        upfolder.clicked.connect(self.getfolder)
        upfolder.setCursor(Qt.CursorShape.PointingHandCursor)
        upfolder.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        createproj = QPushButton("Create")
        createproj.setObjectName("input_file")
        createproj.setCursor(Qt.CursorShape.PointingHandCursor)
        createproj.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        createproj.clicked.connect(self.createproj)
        loadproject = QLabel("Load Project")
        loadproject.setObjectName("input_file")
        loadproject.setCursor(Qt.CursorShape.PointingHandCursor)
        loadproject.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loadproject.mousePressEvent = self.loadproj

        frame.showEvent = self.showProj

        tolbllist = [labelname,labelfps,labelwidth,labelheight,label_duration]
        toiptlist = [self.inputname,self.inputfps,self.inputwidth,self.inputheight,self.inputduration,upfolder,createproj]
        vetical.addStretch()
        for lbl,ipt in zip_longest(tolbllist,toiptlist):
            if lbl:
                lbl.setObjectName("label_form")
            lywi = CustomForm(lbl,ipt)
            lywi.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            vetical.addWidget(lywi)
        vetical.addWidget(loadproject)
        vetical.addStretch()

        return frame

    def showProj(self,e):
        self.inputname.clear()
        self.inputfps.clear()
        self.inputwidth.clear()
        self.inputheight.clear()
        datacreate.update({key:None for key in datacreate})


    def recentProject(self):
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
        frame.setObjectName("frame_content")
        vetical = QVBoxLayout()
        frame.setLayout(vetical)
        vetical.setSpacing(25)
        vetical.setContentsMargins(30,30,30,30)

        labelname = QLabel("Name")
        labeldate = QLabel("Datetime")
        labelname.setObjectName("title_list")
        labeldate.setObjectName("title_list")

        headerlist = CustomList(labelname,labeldate)
        vetical.addWidget(headerlist)
        
        scrolarea = QScrollArea()
        scrolarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrolarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrolarea.setWidgetResizable(True)
        scrolarea.setFrameShape(QFrame.NoFrame)
        scrolwidget = QWidget()
        self.scrollyot = QVBoxLayout()
        scrolwidget.setLayout(self.scrollyot)
        self.scrollyot.setContentsMargins(0,0,0,0)
        self.scrollyot.setSpacing(20)
        # self.scrollyot.setAlignment(Qt.AlignmentFlag.AlignTop)  # bikin auto ke atas default

        for i,infl in enumerate(loadinfo()):
            nm = QLabel(infl["namefile"])
            dt = QLabel(infl["datetime"])
            comb = CustomList(nm,dt)
            nm.setObjectName("file_list")
            dt.setObjectName("file_list")
            nm.setProperty("state", "normal")
            dt.setProperty("state", "normal")
            comb.enterEvent = lambda event, ishvr=True,w1=nm,w2=dt: (
                self.hoverInfo(ishover=ishvr,w=w1),
                self.hoverInfo(ishover=ishvr,w=w2),
            )
            comb.leaveEvent = lambda event, ishvr=False,w1=nm,w2=dt: (
                self.hoverInfo(ishover=ishvr,w=w1),
                self.hoverInfo(ishover=ishvr,w=w2),
            )
            comb.mousePressEvent = lambda event,pathfile=infl["pathfile"],idx=i,filename=infl["namefile"],folderfile=infl["folderfile"]: self.selectproject(pathfile,idx,filename,folderfile) # done
            comb.setCursor(Qt.CursorShape.PointingHandCursor)
            comb.setObjectName("custom_list")
            comb.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            self.scrollyot.addWidget(comb)
        self.scrollyot.addStretch() # bikin auto keatas jika widget yang dibawahnya kosong
        scrolarea.setWidget(scrolwidget)
        vetical.addWidget(scrolarea,1)
        vetical.addStretch()

        return frame
    
    def updrecent(self):
        while self.scrollyot.count():
            ch = self.scrollyot.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()

        for i,infl in enumerate(loadinfo()):
            nm = QLabel(infl["namefile"])
            dt = QLabel(infl["datetime"])
            comb = CustomList(nm,dt)
            nm.setObjectName("file_list")
            dt.setObjectName("file_list")
            nm.setProperty("state", "normal")
            dt.setProperty("state", "normal")
            comb.enterEvent = lambda event, ishvr=True,w1=nm,w2=dt: (
                self.hoverInfo(ishover=ishvr,w=w1),
                self.hoverInfo(ishover=ishvr,w=w2),
            )
            comb.leaveEvent = lambda event, ishvr=False,w1=nm,w2=dt: (
                self.hoverInfo(ishover=ishvr,w=w1),
                self.hoverInfo(ishover=ishvr,w=w2),
            )
            comb.mousePressEvent = lambda event,pathfile=infl["pathfile"],idx=i,filename=infl["namefile"],folderfile=infl["folderfile"]: self.selectproject(pathfile,idx,filename,folderfile) # done
            comb.setCursor(Qt.CursorShape.PointingHandCursor)
            comb.setObjectName("custom_list")
            comb.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            self.scrollyot.addWidget(comb)
        self.scrollyot.addStretch()

    def warninfo(self):
        QMessageBox.warning(self,"warning","File Not Exist",QMessageBox.StandardButton.Ok)

    def hoverInfo(self, ishover,w):
        state = "hover" if ishover else "normal"
        w.setProperty("state",state)
        w.style().unpolish(w)
        w.style().polish(w)
