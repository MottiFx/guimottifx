from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from procmottifx.systems.infile.history import make_history
from procmottifx.systems.parsing.cacheframe import run_removch
from procmottifx.systems.projects.delproject import del_effect
from procmottifx.systems.projects.getproject import get_effect, get_projectfile
from procmottifx.systems.projects.updproject import upd_effect, upd_value
from procmottifx.systems.protos import schema_pb2 as sch
from libmottifx.compact.effect import LISTAUDFX, LISTEFFECT
from guimottifx.utils.configediting import ConfigTimeLine
from guimottifx.utils.currentprj import UpdHistory
from guimottifx.utils.signal import UTILSFRAMESET, UTILSLAYER, UTILSPREVIEW, UTILSRENDER, UTILSSETUP

SETTINGKEY = "alamak"
TARGETSETTING = None
TARGETUIDFX = None

class FrameSettings(QFrame):
    def __init__(self,data,luid):
        super().__init__()

        main_lyout = QVBoxLayout()
        main_lyout.setContentsMargins(0,0,0,0)
        main_lyout.setSpacing(8)
        self.setLayout(main_lyout)
        self.setProperty(SETTINGKEY,data.uid)
        self.closeIcon = "\uf72a"
        self.openIcon = "\uf729"
        # custom color 16 
        self.dlg = QColorDialog(self)

        _COMBINEFX = LISTEFFECT + LISTAUDFX

        self.expand = data.hide

        nmfx = next(a["name"] for a in _COMBINEFX if a["typfx"] == data.typfx)
        ttl = self.titleEffect(nmfx)
        ttl.enterEvent = lambda _: self.enterSettings(data.uid)
        ttl.leaveEvent = lambda _: self.leaveSettings()

        self.fxfrm = QFrame()
        fxlyt = QVBoxLayout()
        self.fxfrm.setLayout(fxlyt)
        fxlyt.setContentsMargins(0,0,0,0)
        fxlyt.setSpacing(5)
        self.fxfrm.setHidden(self.expand)
        ttl.mousePressEvent = self.openSet
        
        for fxv in data.variables:
            vfx = next(a["func"] for a in _COMBINEFX if a["typfx"] == data.typfx)
            funcfx = vfx()
            minf = next(a["min"] for a in funcfx.get_type() if a["key"] == fxv.name)
            maxf = next(a["max"] for a in funcfx.get_type() if a["key"] == fxv.name)
            listval = next((funcfx.getlist() for a in dir(vfx) if "getlist" in a),None)
            hframe = QFrame()
            hlyo = QHBoxLayout()
            hframe.setLayout(hlyo)
            hlyo.setContentsMargins(15,5,15,5)
            hlyo.setSpacing(10)
            hlyo.addWidget(self.labelVal(fxv.name),3)
            hlyo.addWidget(self.iptEffect(fxv.name,fxv.value,fxv.typvar,minf,maxf,listval,fxv.uid,luid,data.uid),1)
            fxlyt.addWidget(hframe)

        main_lyout.addWidget(ttl)
        main_lyout.addWidget(self.fxfrm)

    def pauseSetting(self):
        if self.isEnabled():
            self.setEnabled(False)
        else: self.setEnabled(True)
    
    def openSet(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton: return

        if self.expand: self.expand = False
        else: self.expand = True

        self.fxfrm.setHidden(self.expand)

    def titleEffect(self,title):
        frm = QFrame()
        frm.setObjectName("bgtlfx")
        txt = QLabel()
        txt.setText(title)
        txt.setObjectName("titlefx")
        lyt = QHBoxLayout()
        lyt.setContentsMargins(15,5,15,5)
        frm.setLayout(lyt)
        lyt.addWidget(txt)
        # TODO: ADD ICON (CLOSE OR OPEN) IN THIS LINE
        return frm
    
    def labelVal(self,keyfx):
        lblval = QLabel()
        lblval.setObjectName("lblfx")
        lblval.setText(keyfx)
        return lblval
         
    def iptEffect(self,kyfx,defval,type,minf,maxf,listval,uidv,luid,uidfx): # NOSONAR
        """
        Docstring for iptEffect

        :param uidv: uid variable
        :param luid: uid layer
        :param uidfx: uid effect
        """
        if type == sch.TypVar.TYP_VAR_FLOAT:
            wdg = QDoubleSpinBox()
            if minf != "unl": wdg.setMinimum(float(minf))
            if maxf != "unl": wdg.setMaximum(float(maxf))
            if float(defval) <= 0.1: wdg.setDecimals(4)
            wdg.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            wdg.setValue(float(defval))
            wdg.setObjectName("iptfx")
            wdg.valueChanged.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
        elif type == sch.TypVar.TYP_VAR_INT:
            wdg = QSpinBox()
            if minf != "unl": wdg.setMinimum(int(minf))
            if maxf != "unl": wdg.setMaximum(int(maxf))
            wdg.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            wdg.setValue(int(defval))
            wdg.setObjectName("iptfx")
            wdg.valueChanged.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
        elif type == sch.TypVar.TYP_VAR_STR:
            wdg = QLineEdit()
            wdg.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            wdg.setText(defval)
            wdg.setObjectName("iptfx")
            wdg.valueChanged.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
        elif type == sch.TypVar.TYP_VAR_OPTION:
            wdg = QComboBox()
            for lvl in listval:
                wdg.addItem(lvl.upper())
            wdg.setCurrentText(defval.upper())
            wdg.currentIndexChanged.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
            wdg.setObjectName("iptfx")
        elif type in [sch.TypVar.TYP_VAR_TUPLE,sch.TypVar.TYP_VAR_MINUS]:
            vald = QDoubleValidator(bottom=-1000,top=1000,decimals=2)
            if  type == sch.TypVar.TYP_VAR_TUPLE and kyfx != "scale":
                wdg = QFrame()
                hlyout = QHBoxLayout()
                hlyout.setContentsMargins(0,0,0,0)
                hlyout.setSpacing(10)
                wdg.setLayout(hlyout)
                lblx = QLabel()
                lblx.setText("x")
                lblx.setObjectName("lblfx")
                tupval = eval(defval)
                ipt1 = QLineEdit()
                ipt2 = QLineEdit()
                ipt1.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
                ipt2.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
                ipt1.setValidator(vald)
                ipt2.setValidator(vald)
                ipt1.setText(str(tupval[0]))
                ipt2.setText(str(tupval[1]))
                ipt1.setObjectName("iptfx")
                ipt2.setObjectName("iptfx")
                ipt1.textChanged.connect(lambda: self.changedIPT(type,kyfx,(ipt1,ipt2),uidv,luid,uidfx))
                ipt2.textChanged.connect(lambda: self.changedIPT(type,kyfx,(ipt1,ipt2),uidv,luid,uidfx))
                hlyout.addWidget(ipt1)
                hlyout.addWidget(lblx)
                hlyout.addWidget(ipt2)
            else:
                wdg = QLineEdit()
                tupval = eval(defval)
                wdg.setValidator(vald)
                wdg.setText(str(tupval[0] if kyfx == "scale" else tupval))
                wdg.setObjectName("iptfx")
                wdg.textChanged.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
        elif type in [sch.TypVar.TYP_VAR_BOOL,sch.TypVar.TYP_VAR_COLOR]:
            wdg = QPushButton()
            wdg.setText(defval)
            wdg.setObjectName("iptfx")
            wdg.clicked.connect(lambda: self.changedIPT(type,kyfx,(wdg,),uidv,luid,uidfx))
            
        return wdg
    
    def changedIPT(self,typfx,kyfx,iptfx:tuple,uidv,luid,uidfx): #NOSONAR
        global ndktau
        if typfx in [sch.TypVar.TYP_VAR_FLOAT, sch.TypVar.TYP_VAR_INT]:
            val = iptfx[0].value()
            ndktau = str(val)
        elif typfx == sch.TypVar.TYP_VAR_STR:
            val = iptfx[0].text()
            ndktau = val.lower()
        elif typfx == sch.TypVar.TYP_VAR_BOOL:
            val = eval(iptfx[0].text())
            print(f"gh: {val}")
            if val: 
                ndktau = "False"
                iptfx[0].setText(ndktau)
            else: 
                ndktau = "True"
                iptfx[0].setText(ndktau)
        elif typfx in [sch.TypVar.TYP_VAR_TUPLE,sch.TypVar.TYP_VAR_MINUS]:
            if not iptfx[0].text(): return
            if kyfx == "scale":
                val = iptfx[0].text()
                val = str((float(val),float(val)))
                ndktau = val
            elif typfx == sch.TypVar.TYP_VAR_MINUS:
                val = iptfx[0].text()
                ndktau = val
            else:
                ndktau = str((float(iptfx[0].text()),float(iptfx[1].text())))
        elif typfx == sch.TypVar.TYP_VAR_COLOR:
            self.dlg.exec()
            if self.dlg.selectedColor().isValid():
                ndktau = self.dlg.selectedColor().name()
                iptfx[0].setText(ndktau)
            else:  return
        elif typfx == sch.TypVar.TYP_VAR_OPTION:
            ndktau = iptfx[0].currentText().lower()
        data = {
            "uid_l": luid,
            "uid_e": uidfx,
            "uid_vrb": uidv,
            "value": ndktau,
        }
        print(data)
        projf,_ = get_projectfile()
        sel_lyr = next((lyr for lyr in projf.layers if lyr.uid == luid),None)
        if not sel_lyr: return
        last_pos = sel_lyr.start
        new_pos = sel_lyr.end
        run_removch(lastpos=last_pos,newpos=new_pos)
        upd_value(data)
        make_history(UpdHistory.EFFXSET)
        UTILSLAYER.pos_layer.emit()  

    def enterSettings(self,uidfx):
        global TARGETUIDFX
        TARGETUIDFX = uidfx
        print(TARGETUIDFX)
        
    def leaveSettings(self):
        global TARGETUIDFX
        TARGETUIDFX = None
        print(TARGETUIDFX)

class EffectSet(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idlayer = None
        self.lyr = None
        self.setObjectName("frame_content")
        main_lyout = QVBoxLayout()
        main_lyout.setContentsMargins(0,0,0,0)
        main_lyout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # main_lyout.setSpacing(20)
        self.setLayout(main_lyout)
        main_lyout.addWidget(self.addListSet(),1)
        UTILSSETUP.RESETGUI.connect(self.showFxSetting)
        UTILSFRAMESET.fxset.connect(self.setIdLayer)
        UTILSFRAMESET.fxset.connect(self.refreshSettings)
        UTILSFRAMESET.delcont.connect(self.deleteAllContent)
        UTILSPREVIEW.preview_play.connect(self.pauseFxSetting)
        UTILSRENDER.RENDERSTART.connect(self.pauseFxSetting)

        del_sc = QShortcut(QKeySequence("alt+delete"),self)
        del_sc.activated.connect(self.deleteFx)

    def pauseFxSetting(self):
        if self.isEnabled(): self.setEnabled(False)
        else: self.setEnabled(True)

    def showFxSetting(self):
        self.idlayer = None
        self.lyr = None
        self.deleteAllContent()

    def addListSet(self):
        scrollarea = QScrollArea()
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setWidgetResizable(True)
        scrollarea.setFrameShape(QFrame.NoFrame)

        widget = QWidget()
        scrollarea.setWidget(widget)
        self.scrollist = QVBoxLayout()
        widget.setLayout(self.scrollist)
        self.scrollist.setContentsMargins(0,0,0,0)
        self.scrollist.setSpacing(5)
        self.scrollist.setAlignment(Qt.AlignmentFlag.AlignTop)

        return scrollarea

    def setIdLayer(self,lid): 
        self.lyr = lid
        self.idlayer = lid.uid
    
    def deleteFx(self):
        print(self.idlayer)
        if not TARGETUIDFX or not self.idlayer: return
        data = {
            "uid_l":self.idlayer,
            "uid_e":TARGETUIDFX
        }
        lastpos = self.lyr.start
        newpos = self.lyr.end
        del_effect(data)
        run_removch(lastpos,newpos)
        projf,_ = get_projectfile()
        lyr = next(ly for ly in projf.layers if ly.uid == self.idlayer)
        self.idlayer = lyr.uid
        self.lyr = lyr        
        make_history(UpdHistory.EFFXSET)
        self.refreshSettings(self.lyr)
        UTILSLAYER.pos_layer.emit()  

    def deleteAllContent(self):
        global TARGETUIDFX
        TARGETUIDFX = None
        while self.scrollist.count():
            ch = self.scrollist.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()
                
    def UndoOrRedoContent(self):
        lastpos = self.lyr.start
        newpos = self.lyr.end
        run_removch(lastpos,newpos)
        projf,_ = get_projectfile()
        lyr = next(ly for ly in projf.layers if ly.uid == self.idlayer)
        self.idlayer = lyr.uid
        self.lyr = lyr        
        self.refreshSettings(self.lyr)
        UTILSLAYER.pos_layer.emit()  
    
    def refreshSettings(self,lg):
        self.deleteAllContent()
        self.addSettings(lg)

    def addSettings(self,l):
        lg = get_effect(l)
        for ls in lg:
            fs = FrameSettings(ls,l.uid)
            self.scrollist.addWidget(fs)
