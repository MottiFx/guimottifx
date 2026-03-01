from typing import Any
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class UtilsAssetBar(QObject):
    asset_and_timeline_1 = Signal() 
    asset_and_layerset_1 = Signal()
UTILSASSETBAR = UtilsAssetBar()

class UtilsTimeLine(QObject):
    timeline_and_preview_1 = Signal()
    timeline_and_assetbar_1 = Signal(Any)
UTILSTIMELINE = UtilsTimeLine()

class UtilsPreview(QObject):
    preview_cut_left = Signal()
    preview_cut_right = Signal()
    preview_redo = Signal()
    preview_udo = Signal()
    setup_frame = Signal(bytes,int,int)
    preview_pos = Signal()
    change_frame = Signal(bytes,int,int)
    pos_frame = Signal()
    audio_play = Signal()
    audio_pause = Signal()
    preview_play = Signal()
    # pausecache = Signal()
UTILSPREVIEW = UtilsPreview()

class UtilsLayer(QObject):
    layer_frame = Signal()
    setup_frame = Signal()
    pos_layer = Signal()
    audio_layer = Signal()
UTILSLAYER = UtilsLayer()

class UtilsFrameSet(QObject):
    fxset = Signal(Any)
    delcont = Signal()
UTILSFRAMESET = UtilsFrameSet()

class UtilsRender(QObject):
    PROGTEXT = Signal(str)
    RENDERSTART = Signal()
UTILSRENDER = UtilsRender()

class UtilsLayerSettings(QObject):
    layerset_and_timeline_1 = Signal()
    layerset_pos_frame = Signal()
UTILSLAYERSETTINGS = UtilsLayerSettings()

class UtilsSetup(QObject):
    RESETGUI = Signal()
UTILSSETUP = UtilsSetup()
