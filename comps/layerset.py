from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from procmottifx.systems.infile.history import make_history
from procmottifx.systems.parsing.cacheframe import run_removch
from procmottifx.systems.projects.getproject import get_projectfile
from procmottifx.systems.projects.updproject import upd_layer
from guimottifx.utils.currentprj import CurrentPrj, UpdHistory
from guimottifx.utils.signal import UTILSASSETBAR, UTILSLAYER, UTILSLAYERSETTINGS, UTILSPREVIEW, UTILSRENDER, UTILSSETUP

class LayerSettings(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("frame_content")
        main_lyout = QVBoxLayout()
        main_lyout.setContentsMargins(0,15,0,15)
        main_lyout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(main_lyout)
        main_lyout.setSpacing(15) 
        self.dlg = QColorDialog()
        
        self.boxselected = "●"
        self.boxnotselected = ""

        main_lyout.addWidget(self.mainBar(),0)
        main_lyout.addWidget(self.mainContent(),1)
        UTILSASSETBAR.asset_and_layerset_1.connect(self.refreshContent)
        UTILSSETUP.RESETGUI.connect(self.refreshContent)
        UTILSLAYER.pos_layer.connect(self.refreshContent)
        UTILSPREVIEW.preview_play.connect(self.pauseLys)
        UTILSRENDER.RENDERSTART.connect(self.pauseLys)

    def pauseLys(self):
        if self.isEnabled():
            self.setEnabled(False)
        else: self.setEnabled(True)

    def mainBar(self):
        frame = QFrame()
        frame.setFixedHeight(20)
        qhboxlyt = QHBoxLayout()
        qhboxlyt.setContentsMargins(15,0,15,0)
        frame.setLayout(qhboxlyt)

        label0 = QLabel("#")
        label1 = QLabel("Name Layer")
        label2 = QLabel("\ue23a")
        label3 = QLabel("\ue76e")

        label0.setObjectName("lyslbl")
        label1.setObjectName("lyslbl")
        label1.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        label2.setObjectName("lysicon")
        label3.setObjectName("lysicon")

        qhboxlyt.addWidget(label0,0)
        qhboxlyt.addSpacing(5)
        qhboxlyt.addWidget(label1,1)
        qhboxlyt.addWidget(label2,0)
        qhboxlyt.addSpacing(10)
        qhboxlyt.addWidget(label3,0)

        return frame

    def mainContent(self):
        scrollarea = QScrollArea()
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollarea.setWidgetResizable(True)
        scrollarea.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        self.scrollContent = QVBoxLayout()
        self.scrollContent.setContentsMargins(0,0,0,0)
        self.scrollContent.setSpacing(10)
        self.scrollContent.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(self.scrollContent)

        scrollarea.setWidget(widget)

        return scrollarea

    def addContent(self,layers):
        for lyr in layers:
            _idx_lbl = QLabel(f"{lyr.order}")
            _name_lbl = QLabel(lyr.name)
            _btn_color = QPushButton("")
            _btn_visible = QPushButton()

            # classes object
            _idx_lbl.setObjectName("txtlys")
            _name_lbl.setObjectName("txtlys")
            _name_lbl.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
            _btn_color.setStyleSheet(f"background-color:{lyr.colors};")
            _btn_color.setFixedSize(18,18)
            _btn_color.clicked.connect(
                lambda _,u=lyr.uid,w=_btn_color,v=lyr.visible:self.changeColor(u,v,w)
                )
            _btn_visible.setStyleSheet(f"background-color:white;color:black;")
            _btn_visible.setFixedSize(18,18)
            _btn_visible.clicked.connect(
                lambda _,u=lyr.uid,w=_btn_visible,v=lyr.visible,lp=lyr.start,np=lyr.end:self.changeVisible(u,v,w,lp,np)
                )
            if lyr.visible:
                _btn_visible.setText(self.boxselected)
            else: _btn_visible.setText(self.boxnotselected)

            _container = QFrame()
            _hlayout = QHBoxLayout()
            
            _hlayout.setContentsMargins(15,0,15,0)
            _hlayout.addWidget(_idx_lbl,0)
            _hlayout.addSpacing(5)
            _hlayout.addWidget(_name_lbl,1)
            _hlayout.addWidget(_btn_color,0)
            _hlayout.addSpacing(10)
            _hlayout.addWidget(_btn_visible,0)

            _container.setObjectName("contlys")
            _container.setFixedHeight(40)
            _container.setLayout(_hlayout)

            self.scrollContent.addWidget(_container)

    def refreshContent(self):
        projf,_ = get_projectfile()
        layers = projf.layers
        layers.sort(key=lambda lyr: lyr.order)
        while self.scrollContent.count():
            ch = self.scrollContent.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()

        self.addContent(layers)

    def changeColor(self,uidl,visible,wdg:QPushButton):
        if visible: return
        value = None
        self.dlg.exec()
        if self.dlg.selectedColor().isValid():
            value = self.dlg.selectedColor().name()
            wdg.setStyleSheet(f"background-color:{value}")
        else: return

        data = {
            "uid_l": uidl,
            "color": value
        }

        upd_layer(data)
        make_history(UpdHistory.LAYERSETANDTMLN)
        # self.refreshContent()
        UTILSLAYERSETTINGS.layerset_and_timeline_1.emit()

    def changeVisible(self,uidl,visible,wdg:QPushButton,lastpos,newpos):
        value = None
        if visible:
            value = False
            wdg.setText(self.boxnotselected)
        else:
            value = True
            wdg.setText(self.boxselected)

        data = {
            "uid_l": uidl,
            "visible": value
        }

        run_removch(lastpos,newpos)
        upd_layer(data)
        make_history(UpdHistory.LAYERSETANDTMLN)
        UTILSLAYERSETTINGS.layerset_and_timeline_1.emit()
        UTILSLAYERSETTINGS.layerset_pos_frame.emit()

