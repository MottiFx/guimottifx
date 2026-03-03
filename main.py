import os
from pathlib import Path
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

from guimottifx.comps import assetbar, effectset, layerset, menufx, preview, timeline
from guimottifx.comps.about import thirdlib,license
from guimottifx.comps.edit.render import RenderGui
from guimottifx.comps.help import keyboardsc
from guimottifx.comps.setup import SetupApp
from guimottifx.utils.resource import resource_path
from styles.styles import CustomStyle
from procmottifx.systems.infile.history import del_allhistory, get_history
from procmottifx.systems.parsing.cacheframe import delall_chcfrm
from procmottifx.systems.projects.getproject import get_projectfile
from guimottifx.utils.configediting import ConfigFrame, ConfigRender, ConfigThreadRender, ConfigTimeLine, ScrollTimeLine
from guimottifx.utils.currentprj import CurrentPrj, CurrentThread, UndoRedo, UpdHistory
from procmottifx.decode.layerdecode import ManageRender
from procmottifx.encode.layerencode import ManageThread
from guimottifx.utils.signal import UTILSPREVIEW, UTILSRENDER

monitor = get_monitors()[0]
w,h = int(monitor.width/1.1), int(monitor.height/1.1)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)

top = [effectset.EffectSet,preview.Preview,menufx.MenuFx]
bottom = [layerset.LayerSettings,timeline.TimeLine,assetbar.AssetBar]


class RootApp(QMainWindow):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("MottiFx")
        icfull = resource_path("styles/mottifx.png")
        self.setWindowIcon(QIcon(icfull))
        self.setGeometry(x,y,w,h)

        self.stacking = QStackedLayout()
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        CustomStyle.load_font()
        # self.changeEvent = lambda e: print("hai") if self.isActiveWindow() else print("bye")

        self.widget = QWidget()
        self.widget.setLayout(self.stacking)
        self.setCentralWidget(self.widget)
        
        self.menubarw = self.menuBar()
        self.menulist = ["&File","&Edit","&Help","&About"]
        
        self.textmenu=[self.menubarw.addMenu(mn) for mn in self.menulist]
        [txmn.setCursor(Qt.CursorShape.PointingHandCursor) for txmn in self.textmenu]

        self.stacking.addWidget(self.mainediting()) #0
        self.stacking.addWidget(self.mainproject()) #1
        self.stacking.setCurrentIndex(1)

        about_widget = [None,None,license.LicenseProduct,thirdlib.ThirdPartyLib]
        help_widget = [keyboardsc.KeyboardSc]
        _funcfile = [self.backManagerProject]

        # file component
        _filetext = ["Manager"]

        for v,f in zip(_filetext,_funcfile):
            _act = QAction(v,self)
            if f:
                _act.triggered.connect(f)
            self.textmenu[0].addAction(_act)

        # edit component
        _editcomp = ["Render"]
        self.rendergui = RenderGui(self)
        _funcedit = [self.openRender]
        
        for v,f in zip(_editcomp,_funcedit):
            _act = QAction(v,self)
            if f:
                _act.triggered.connect(f)
            self.textmenu[1].addAction(_act)

        # help component
        _helpcomp = ["Keyboard"]
        for v,f in zip(_helpcomp,help_widget):
            _act = QAction(v,self)
            if f:
                fw = f(self)
                _act.triggered.connect(lambda _,w=fw: self.openWdg(w))
            self.textmenu[2].addAction(_act)

        # about component
        _aboutcomp = ["Website","Author","License","Third-party libraries"]
        for v,f in zip(_aboutcomp,about_widget):
            _act = QAction(v,self)
            if f:
                fw = f(self)
                _act.triggered.connect(lambda _, w=fw: self.openWdg(w))
            if v == "Website":
                d = "https://mottifx.vercel.app/"
                _act.triggered.connect(lambda _,l=d: self.openUrl(l))
            self.textmenu[3].addAction(_act)

        # shortcuts
        manager_sc = QShortcut(QKeySequence("ctrl+m"),self)
        manager_sc.activated.connect(self.backManagerProject)

        render_sc = QShortcut(QKeySequence("ctrl+r"),self)
        render_sc.activated.connect(self.openRender)

        UTILSPREVIEW.preview_play.connect(self.pauseMenubarW)
        UTILSRENDER.RENDERSTART.connect(self.pauseMenubarW)

    def openUrl(self,link):
        QDesktopServices.openUrl(link)

    def pauseMenubarW(self):
        if self.menubarw.isEnabled():
           self.menubarw.setEnabled(False)
        else: self.menubarw.setEnabled(True)
        
    def openWdg(self,wdg:QFrame):
        """
            for open widget from qaction in menu
        """
        if self.stacking.currentIndex() == 1 or ConfigRender.status: return
        if wdg.isHidden(): wdg.setHidden(False)
        else: wdg.setHidden(True)

    def openRender(self):
        if self.stacking.currentIndex() == 1 or ConfigRender.status: return
        if self.rendergui.isHidden(): 
            UTILSRENDER.PROGTEXT.emit("(*_~_*)")
            self.rendergui.setHidden(False)
        else: self.rendergui.setHidden(True)

    def backManagerProject(self):
        if self.stacking.currentIndex() == 1: return
        if ConfigTimeLine.PREVIEW: return
        self.menubarw.hide()
        CurrentThread.MAINPROC.stopproc()
        del_allhistory()
        self.stacking.setCurrentIndex(1)
        CurrentPrj.fl_updhistory = UpdHistory.EMPETY
        CurrentPrj.index_history = 0
        CurrentPrj.namefile = None
        CurrentPrj.folderfile = None
        CurrentPrj.pathfile = None
        ConfigTimeLine.CURRENTPOS = 0
        ConfigTimeLine.ZOOM = 1.
        UndoRedo.same_redo = 0
        ConfigFrame.SETUPFRAME = False
        UndoRedo.same_undo = 0
        ScrollTimeLine.X = 0
        ScrollTimeLine.Y = 0
        CurrentThread.MAINPROC = ManageThread()
        CurrentThread.MAINPROC.safetyproc()

    def mainediting(self):
        gridlyout = QGridLayout()
        gridlyout.setColumnStretch(0,2)
        gridlyout.setColumnStretch(1,7)
        gridlyout.setColumnStretch(2,2)
        gridlyout.setRowStretch(0,4)
        gridlyout.setRowStretch(1,3)
        # gridlyout.setSpacing(0)

        widget = QWidget()
        widget.setLayout(gridlyout)

        for i,t in enumerate(top):
            topwi = t()
            # Ignored = maksa untuk tidak melebihi frame/container
            topwi.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
            gridlyout.addWidget(topwi,0,i)
            # add to self.obj
            # setattr(self,t.__name__.lower(),topwi)
            setattr(self,t.__name__,topwi)
        for i,b in enumerate(bottom):
            botwi = b()
            # Ignored = maksa untuk tidak melebihi frame/container
            botwi.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored)
            gridlyout.addWidget(botwi,1,i)
            # add to self.obj
            # setattr(self,b.__name__.lower(),botwi)
            setattr(self,b.__name__,botwi)

        return widget
    
    def mainproject(self):
        widget = QWidget()
        bxlyout = QVBoxLayout()
        widget.setLayout(bxlyout)
        
        frame = SetupApp(self.menubarw,self.stacking)
        bxlyout.addWidget(frame)
        bxlyout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return widget



if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar_theme = QPalette()
    # bar_theme.setColor(QPalette.WindowText,Qt.white)
    bar_theme.setColor(QPalette.Window,QColor(30,30,30))
    app.setPalette(bar_theme)
    pfull = resource_path("styles/main.qss")
    with open(pfull,mode="r",encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    window = RootApp()

    def undo(): #NOSONAR
        if window.stacking.currentIndex() == 1: return
        if window.isActiveWindow() and CurrentPrj.pathfile and not ConfigTimeLine.PREVIEW:
            indx = CurrentPrj.index_history
            CurrentPrj.index_history = max(0,indx-1)
            if UndoRedo.same_undo == 1: return
            if CurrentPrj.index_history == 0: UndoRedo.same_undo = 1
            else: UndoRedo.same_undo = 0
            UndoRedo.same_redo = 0

            fl_upd = ""
            listfile = [x for x in os.listdir(f"{CurrentPrj.folderfile}/history") if x.endswith(".mpj")]
            selectfile = listfile[CurrentPrj.index_history].rsplit("_",1)[-1].rsplit(".",1)[0]
            print(selectfile)

            for vx in UpdHistory.LISTHISTORY:
                if vx == selectfile:
                    fl_upd = vx
                    break
            
            # print(selectfile)
            # print(fl_upd)
            # print(CurrentPrj.fl_updhistory)
            get_history(fl_upd)
            assetbar = window.AssetBar
            timeline = window.TimeLine
            layerset = window.LayerSettings
            effectset = window.EffectSet

            if CurrentPrj.fl_updhistory == UpdHistory.ASSETBAR:
                proj,_ = get_projectfile()
                assetbar.refreshasset(proj.assets)
            if CurrentPrj.fl_updhistory == UpdHistory.LAYER:
                delall_chcfrm()
                timeline.refreshLayer()
            if CurrentPrj.fl_updhistory == UpdHistory.EFFXSET:
                effectset.UndoOrRedoContent()
            if CurrentPrj.fl_updhistory == UpdHistory.LAYERSETANDTMLN:
                delall_chcfrm()
                timeline.refreshLayer()
                layerset.refreshContent()
            if CurrentPrj.fl_updhistory == UpdHistory.LYSFXSTTMLN:
                delall_chcfrm()
                timeline.refreshLayer()
                layerset.refreshContent()
                effectset.deleteAllContent()

            # continue the any type

            CurrentPrj.fl_updhistory = fl_upd

            
    def redo(): # NOSONAR
        if window.stacking.currentIndex() == 1: return
        if window.isActiveWindow() and CurrentPrj.pathfile and not ConfigTimeLine.PREVIEW:
            indx = CurrentPrj.index_history
            get_total_his = len([x for x in os.listdir(rf"{CurrentPrj.folderfile}/history") if x.endswith(".mpj")])
            CurrentPrj.index_history = min(get_total_his - 1,indx+1)
            if UndoRedo.same_redo == 1: return
            if get_total_his - 1 == CurrentPrj.index_history: UndoRedo.same_redo = 1
            else: UndoRedo.same_redo = 0
            UndoRedo.same_undo = 0

            listfile = [x for x in os.listdir(f"{CurrentPrj.folderfile}/history") if x.endswith(".mpj")]
            selectfile = listfile[CurrentPrj.index_history].rsplit("_",1)[-1].rsplit(".",1)[0]

            for vx in UpdHistory.LISTHISTORY:
                if vx == selectfile:
                    CurrentPrj.fl_updhistory = vx
                    print(vx)
                    break

            get_history(CurrentPrj.fl_updhistory)
            assetbar = window.AssetBar
            timeline = window.TimeLine
            layerset = window.LayerSettings
            effectset = window.EffectSet

            if CurrentPrj.fl_updhistory == UpdHistory.ASSETBAR:
                proj,_ = get_projectfile()
                assetbar.refreshasset(proj.assets)
            if CurrentPrj.fl_updhistory == UpdHistory.LAYER:
                delall_chcfrm()
                timeline.refreshLayer()
            if CurrentPrj.fl_updhistory == UpdHistory.EFFXSET:
                effectset.UndoOrRedoContent()
            if CurrentPrj.fl_updhistory == UpdHistory.LAYERSETANDTMLN:
                delall_chcfrm()
                timeline.refreshLayer()
                layerset.refreshContent()
            if CurrentPrj.fl_updhistory == UpdHistory.LYSFXSTTMLN:
                delall_chcfrm()
                timeline.refreshLayer()
                layerset.refreshContent()
                effectset.deleteAllContent()


    scundo = QShortcut(QKeySequence("ctrl+z"),window)
    scundo.activated.connect(undo)

    scredo = QShortcut(QKeySequence("ctrl+shift+z"),window)
    scredo.activated.connect(redo)

    UTILSPREVIEW.preview_udo.connect(undo)
    UTILSPREVIEW.preview_redo.connect(redo)

    window.closeEvent = lambda e: del_allhistory() if CurrentPrj.pathfile else print("nope")
    window.show()

    CurrentThread.MAINPROC = ManageThread()
    CurrentThread.MAINPROC.safetyproc()

    sys.exit(app.exec())
