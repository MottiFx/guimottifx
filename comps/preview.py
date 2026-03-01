from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtOpenGLWidgets import *

from guimottifx.utils.configediting import ConfigTimeLine, format_hms_frames
from guimottifx.utils.signal import UTILSPREVIEW, UTILSRENDER, UTILSSETUP, UTILSTIMELINE
    

class FrameView(QGraphicsPixmapItem):
    def __init__(self,frame,outw,outh):
        super().__init__()
        self.image = QImage(
            frame,
            outw,
            outh,
            # outw * 4,
            QImage.Format.Format_RGBA8888 # rgb lebih lambat dibanding rba
        )
        self.frameMap = QPixmap()
        self.setPixmap(self.frameMap.fromImage(self.image))

class MainView(QGraphicsView):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mainScene = QGraphicsScene()
        self.setScene(self.mainScene)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainScene.setSceneRect(-2000,-2000,4000,4000)
        self.setObjectName("grap_pre")
        self.scale(1,1) # mencoba scale untuk meperjelas

        self.setRenderHints(QPainter.RenderHint.LosslessImageRendering  | QPainter.RenderHint.SmoothPixmapTransform)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        UTILSSETUP.RESETGUI.connect(self.clearView)
        UTILSPREVIEW.setup_frame.connect(self.setupView)
        UTILSPREVIEW.change_frame.connect(self.changeFrame)
        # TODO: Need update feature zoomIn and zoomOut

    def clearView(self):
        self.mainScene.clear()
    
    def setupView(self,frame,outw,outh):
        self.pixframe = FrameView(frame,outw,outh)
        self.mainScene.addItem(self.pixframe)
        self.centerOn(self.pixframe)

    def changeFrame(self,frame,outw,outh):
        self.image = QImage(
            frame,
            outw,
            outh,
            # outw * 4,
            QImage.Format.Format_RGBA8888 # rgb lebih lambat dibanding rba
        )
        pixmap = self.pixframe.frameMap.fromImage(self.image)
        self.pixframe.setPixmap(pixmap)


class MainBar(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedHeight(45)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(50)
        self.mainLayout.setContentsMargins(0,5,0,10)
        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pauseIcon = "\ue034"
        self.playIcon  = "\ue037"
        self.showIcon  = "\ue8f4"
        self.hideIcon  = "\ue8f5"
        
        self.buttonPlay = QLabel("\ue037")
        self.buttonPlay.setObjectName("icon_preview")
        self.buttonPlay.mousePressEvent = self.playAndpausPreview
        self.buttonPrevious = QLabel("\ue045")
        self.buttonPrevious.setObjectName("icon_preview")
        self.buttonPrevious.mousePressEvent = self.previeousPos
        self.buttonNext = QLabel("\ue044")
        self.buttonNext.setObjectName("icon_preview")
        self.buttonNext.mousePressEvent = self.nextPos
        self.buttonCutLeft = QLabel("\uf73b")
        self.buttonCutLeft.setObjectName("icon_preview")
        self.buttonCutLeft.mousePressEvent = self.cutLeft
        self.buttonCutRight = QLabel("\uf738")
        self.buttonCutRight.setObjectName("icon_preview")
        self.buttonCutRight.mousePressEvent = self.cutRight
        self.buttonCapture = QLabel("\uf7d3")
        self.buttonCapture.setObjectName("icon_preview")
        self.buttonBeat = QLabel("\uf475")
        self.buttonBeat.setObjectName("icon_preview")
        self.buttonUndo = QLabel("\ue166")
        self.buttonUndo.setObjectName("icon_preview")
        self.buttonUndo.mousePressEvent = self.undo
        self.buttonRedo = QLabel("\ue15a")
        self.buttonRedo.setObjectName("icon_preview")
        self.buttonRedo.mousePressEvent = self.redo
        self.timeLabel = QLabel("00:00:00")
        self.timeLabel.setObjectName("label_preview")

        self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.timeLabel)
        # self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.buttonCapture)
        self.mainLayout.addWidget(self.buttonUndo)
        self.mainLayout.addWidget(self.buttonCutLeft)
        self.mainLayout.addWidget(self.buttonPrevious)
        self.mainLayout.addWidget(self.buttonPlay)
        self.mainLayout.addWidget(self.buttonNext)
        self.mainLayout.addWidget(self.buttonCutRight)
        self.mainLayout.addWidget(self.buttonRedo)
        self.mainLayout.addWidget(self.buttonBeat)
        self.mainLayout.addStretch(2)

        space_playpause = QShortcut(QKeySequence("space"),self)
        space_playpause.activated.connect(self._playandpauseutil)

        UTILSTIMELINE.timeline_and_preview_1.connect(self.changeTimeLabel)
        UTILSRENDER.RENDERSTART.connect(self.pauseMainbar)

    def pauseMainbar(self):
        if self.isEnabled(): self.setEnabled(False)
        else: self.setEnabled(True)


    def showEvent(self, event):
        self.changeTimeLabel()
        self.perfps = 1000 / ConfigTimeLine.FPS
        self.timer = QTimer(interval=self.perfps,timerType=Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.timeoutUpdate)
        # self.timer.timerType(Qt.TimerType.PreciseTimer)
        return super().showEvent(event)
    
    def updIconPlayPause(self):
        if ConfigTimeLine.PREVIEW:
            self.buttonPlay.setText(self.playIcon)
        else: 
            self.buttonPlay.setText(self.pauseIcon)

    def changeTimeLabel(self):
        times = format_hms_frames(ConfigTimeLine.CURRENTPOS,ConfigTimeLine.FPS)
        self.timeLabel.setText(times)

    def cutLeft(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        UTILSPREVIEW.preview_cut_left.emit()

    def cutRight(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        UTILSPREVIEW.preview_cut_right.emit()

    def undo(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        UTILSPREVIEW.preview_udo.emit()

    def redo(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        UTILSPREVIEW.preview_redo.emit()

    def _playandpauseutil(self):
        self.updIconPlayPause()

        if not ConfigTimeLine.PREVIEW:
            UTILSPREVIEW.audio_play.emit()
            ConfigTimeLine.PREVIEW = True
            self.buttonCutLeft.setEnabled(False)
            self.buttonCutRight.setEnabled(False)
            self.timer.start()
        else: 
            UTILSPREVIEW.audio_pause.emit()
            ConfigTimeLine.PREVIEW = False
            self.buttonCutLeft.setEnabled(True)
            self.buttonCutRight.setEnabled(True)
            self.timer.stop()
            #! dont always use this ⬇ , it will make your app force close (look in the layerencode, and signal)
            #! jangan sampai salah pakai, karena prosesnya cukup mahal, jadi sekali saja digunakan,di layerencode langsung, karena sebelumnya sekaligus dua
            # UTILSPREVIEW.pausecache.emit()
            # gc.collect()
        UTILSPREVIEW.preview_play.emit()

    def playAndpausPreview(self, e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        self._playandpauseutil()
        
    def nextPos(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton or ConfigTimeLine.PREVIEW:
            return
        currentframe = int(round(ConfigTimeLine.CURRENTPOS * ConfigTimeLine.FPS))
        currentframe += 1
        nowframe = currentframe / ConfigTimeLine.FPS
        ConfigTimeLine.CURRENTPOS = min(ConfigTimeLine.DURATION,nowframe)
        UTILSPREVIEW.preview_pos.emit()
        UTILSPREVIEW.pos_frame.emit()

        
    def previeousPos(self,e:QMouseEvent):
        if e.button() != Qt.MouseButton.LeftButton or ConfigTimeLine.PREVIEW:
            return
        currentframe = int(round(ConfigTimeLine.CURRENTPOS * ConfigTimeLine.FPS))
        currentframe -= 1
        nowframe = currentframe / ConfigTimeLine.FPS
        ConfigTimeLine.CURRENTPOS = max(0.,nowframe)
        UTILSPREVIEW.preview_pos.emit()
        UTILSPREVIEW.pos_frame.emit()

    def timeoutUpdate(self):
        if ConfigTimeLine.CURRENTPOS >= ConfigTimeLine.DURATION:
            ConfigTimeLine.CURRENTPOS = ConfigTimeLine.DURATION
            UTILSPREVIEW.preview_pos.emit()
            self.updIconPlayPause()
            ConfigTimeLine.PREVIEW = False
            self.timer.stop()
            return

        UTILSPREVIEW.pos_frame.emit()

class Preview(QFrame):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("frame_content")
        self.lyout = QVBoxLayout()
        self.setLayout(self.lyout)
        self.lyout.setContentsMargins(0,0,0,0)
        self.lyout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lyout.addWidget(MainView())
        self.lyout.addWidget(MainBar())
