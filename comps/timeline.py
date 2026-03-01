from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from procmottifx.systems.infile.history import make_history
from procmottifx.systems.parsing.cacheframe import run_removch
from procmottifx.systems.projects.addproject import create_effect
from procmottifx.systems.projects.delproject import del_layer
from procmottifx.systems.projects.getproject import get_projectfile
from procmottifx.systems.projects.updproject import upd_layer
from procmottifx.systems.protos import schema_pb2 as sch
from guimottifx.utils.configediting import ConfigFrame, ConfigTimeLine, ScrollTimeLine, scale, timeline_height, timeline_width
from guimottifx.utils.currentprj import CurrentPrj, UpdHistory
from guimottifx.utils.signal import UTILSASSETBAR, UTILSFRAMESET, UTILSLAYER, UTILSLAYERSETTINGS, UTILSPREVIEW, UTILSRENDER, UTILSSETUP, UTILSTIMELINE
import numpy as np 

iconlayer = [
    {"type": sch.TypLyr.TYP_LYR_IMAGE, "icon": "\ue3f4"},
    {"type": sch.TypLyr.TYP_LYR_VIDEO, "icon": "\ueb87"},
    # {"type": sch.TypLyr.TYP_LYR_GROUP, "color":"#f2ff3a","icon": "\uf720"},
    {"type": sch.TypLyr.TYP_LYR_AUDIO, "icon": "\ueb82"},
    {"type": sch.TypLyr.TYP_LYR_ADJUSMENT, "icon": "\uf866"},
    {"type": sch.TypLyr.TYP_LYR_FRAMES, "icon": "\uf49a"},
]

KEYNAMELAYER = 0 # untuk memberi tahu jika ini layer
KEYLAYER = 1 # key layer yang berisi uid ,semua dengan key yg sama tapi beda val
TARGET_UIDX = None # target layer
SIDEKEY = 2 # strip key yang kuning untuk stretch layer
SELECT_STRIP = None # strip yang dipilih
UPDATED = False

class LayerPaint(QGraphicsRectItem):
    def __init__(self,start_x,order_y,duration_width,layer_height,color,label,icon,uidx):
        super().__init__()
        self.setRect(0,0,duration_width,layer_height)
        self.setPos(start_x,order_y)
        self.setData(KEYLAYER,uidx)
        self.setData(KEYNAMELAYER,"layer")

        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(QColor(color)))
        self.setToolTip(label)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)

        # setup
        self.leftHighlight = QGraphicsRectItem()
        self.rightHighlight = QGraphicsRectItem()
        self.iconLayer = QGraphicsTextItem()
        self.labelLayer = QGraphicsTextItem()
        self.leftHighlight.setParentItem(self)
        self.rightHighlight.setParentItem(self)
        self.labelLayer.setParentItem(self)
        self.iconLayer.setParentItem(self)

        self.leftHighlight.setData(SIDEKEY,"left")
        self.rightHighlight.setData(SIDEKEY,"right")
        
        self.labelLayer.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.iconLayer.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.leftHighlight.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.rightHighlight.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

        self.labelLayer.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.iconLayer.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)


        # hide active bar
        self.leftHighlight.hide()
        self.rightHighlight.hide()

        # set pos
        self.leftHighlight.setPos(0,0)
        # duration_width = end_time
        self.rightHighlight.setPos(duration_width-5.5,0)

        # set size
        self.leftHighlight.setRect(0,0,5.5,layer_height)
        self.rightHighlight.setRect(0,0,5.5,layer_height)

        # set color
        self.leftHighlight.setPen(Qt.PenStyle.NoPen)
        self.rightHighlight.setPen(Qt.PenStyle.NoPen)
        self.leftHighlight.setBrush(QColor("yellow"))
        self.rightHighlight.setBrush(QColor("yellow"))
        
        # set mouse
        self.leftHighlight.setCursor(Qt.CursorShape.SizeHorCursor)
        self.rightHighlight.setCursor(Qt.CursorShape.SizeHorCursor)

        # set zValue
        self.leftHighlight.setZValue(1)
        self.rightHighlight.setZValue(1)

        # set pos text
        self.labelLayer.setPos(28,5)
        self.iconLayer.setPos(5.5,2)
        
        # setup text
        self.iconLayer.setPlainText(icon)
        self.labelLayer.setDefaultTextColor("white")
        # self.labelLayer.setFont(QFont("",14))
        self.labelLayer.setPlainText(label)
        self.iconLayer.setDefaultTextColor("white")
        self.iconLayer.setFont(QFont("Material Symbols Outlined",14,800))

class BackLayer(QGraphicsRectItem):
    def __init__(self,order_y,width,height):
        super().__init__()
        self.setPos(0,order_y)
        self.setRect(0,0,width,height)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setZValue(-1)

        self.setPen(QColor("#4B4B4B"))
        self.setBrush(Qt.BrushStyle.NoBrush)


class TimeLinePos(QGraphicsLineItem):
    def __init__(self,pos_time):
        super().__init__()
        sizelinepos = 10
        self.setPos(pos_time,0)
        self.setLine(0,0,0,sizelinepos)
        self.setPen(QPen(QColor("#4B4B4B"),2))
        self.setZValue(9)

class HeadPos(QGraphicsLineItem):
    def __init__(self,pos_time,timeline_height):
        super().__init__()
        self.setPos(pos_time,0)
        self.setLine(0,0,0,timeline_height)
        self.setPen(QPen(QColor("#9cff2b"),2))
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setZValue(10)

class TimeLine(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mainScene = QGraphicsScene()
        self.setScene(self.mainScene)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.setObjectName("graphics_content")
        self.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform,True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.horizontalScrollBar().valueChanged.connect(self.getLastScroll)
        self.verticalScrollBar().valueChanged.connect(self.getLastScroll)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        esc_shortcut = QShortcut(QKeySequence("`"),self)
        esc_shortcut.activated.connect(self.addLayer)

        cut_start = QShortcut(QKeySequence("alt+["),self)
        cut_end = QShortcut(QKeySequence("alt+]"),self)
        cut_start.activated.connect(self.cutLeft)
        cut_end.activated.connect(self.cutRight)

        zoom_in = QShortcut(QKeySequence("ctrl+="),self)
        zoom_out = QShortcut(QKeySequence("ctrl+-"),self)
        zoom_in.activated.connect(self.zoomIn)
        zoom_out.activated.connect(self.zoomOut)

        sc_del_layer = QShortcut(QKeySequence("delete"),self)
        sc_del_layer.activated.connect(self.deleteLayer)

        UTILSASSETBAR.asset_and_timeline_1.connect(self.refreshLayer)
        UTILSPREVIEW.preview_cut_left.connect(self.cutLeft)
        UTILSPREVIEW.preview_cut_right.connect(self.cutRight)
        UTILSPREVIEW.preview_pos.connect(self.updHeadPos)
        UTILSTIMELINE.timeline_and_assetbar_1.connect(self.addEffectLayer)
        UTILSLAYERSETTINGS.layerset_and_timeline_1.connect(self.refreshLayer)
        UTILSSETUP.RESETGUI.connect(self.showTimeLine)
        UTILSPREVIEW.preview_play.connect(self.pauseTimeLine)
        UTILSRENDER.RENDERSTART.connect(self.pauseTimeLine)

    def pauseTimeLine(self):
        if self.isEnabled():
            self.setEnabled(False)
        else: self.setEnabled(True)

    def showTimeLine(self):
        ConfigTimeLine.CURRENTPOS = 0
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        self.refreshLayer()

    def mousePressEvent(self,e:QMouseEvent):
        self.customFocusLayer(e)
        # self.headPosSet(e)

        return super().mousePressEvent(e)
    
    def mouseReleaseEvent(self, event):
        self.histroyUpdate(UpdHistory.LAYERSETANDTMLN)
        if not UPDATED and ConfigFrame.SETUPFRAME:
            UTILSLAYER.pos_layer.emit()
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, e:QMouseEvent):
        self.headPosSet(e) # harus paling atas karena dia yang set currentpos
        self.stretchLayer(e)
        self.MoveAndReorderLayer(e)
        return super().mouseMoveEvent(e)

    def setSizeView(self):
        projf,_ = get_projectfile()
        tmheight = len(projf.layers) - 1
        _sizemain = timeline_height(tmheight)
        _defaultsize = self.mainScene.itemsBoundingRect()
        if _sizemain < _defaultsize.height():
            self.setSceneRect(0,0,timeline_width(),_defaultsize.height())
        else:
            self.setSceneRect(0,0,timeline_width(),_sizemain)

    
    def histroyUpdate(self,updh):
        global UPDATED
        if UPDATED:
            make_history(updh)
            UPDATED = False

    def addTimeLinePos(self):
        """Add TimelinePos"""
        conf = ConfigTimeLine
        for i in np.arange(conf.DURATION):
            sec = scale() * i
            linepos = TimeLinePos(sec)
            if i % 5 == 0: # jika habis dibagi 5 berarti berada di kelipatan 5
                linepos.setLine(0,0,0,20)
            self.mainScene.addItem(linepos)

    def addLayer(self):
        """Add Layer"""
        conf = ConfigTimeLine
        sc = scale()
        projf,_ = get_projectfile()
        for data in projf.layers:
            start_time = data.start * sc
            order_y = conf.GAP + (conf.GAP * data.order) 
            height = conf.LAYERHEIGHT
            end = data.end
            duration_width = (end - data.start) * sc # = end_time
            color = data.colors if not data.visible else "#545454"
            label = data.name if not data.visible else f"{data.name}_visible"
            for ic in iconlayer:
                if ic["type"] == data.typlyr:
                    icon = ic["icon"] if not data.visible else "\uf653"
                    break
            uid = data.uid
            backlayer = BackLayer(order_y,timeline_width(),height)
            layer = LayerPaint(start_time,order_y,duration_width,height,color,label,icon,uid)

            self.mainScene.addItem(backlayer)
            self.mainScene.addItem(layer)
    
    def addHeadPos(self):
        """Add HeadPos"""
        sc = scale()
        pos = ConfigTimeLine.CURRENTPOS # posisi detiknya

        projf,_ = get_projectfile()
        tlayer = len(projf.layers)
        timeline_h = self.viewport().height() * (timeline_height(tlayer) if tlayer != 0 else 1)
        calculate_pos = pos * sc
        self.headpos = HeadPos(calculate_pos,timeline_h)

        self.mainScene.addItem(self.headpos)

    def updHeadPos(self):
        """Update HeadPos"""
        # print(format_hms_ms(ConfigTimeLine.CURRENTPOS))
        UTILSTIMELINE.timeline_and_preview_1.emit()
        # dikali lagi agar sesuai settingan 1 detik 50px == scale()
        calculate = ConfigTimeLine.CURRENTPOS * scale()
        self.headpos.setPos(calculate,0)

    def headPosSet(self, e:QMouseEvent):
        """Drag HeadPos"""
        if e.buttons() != Qt.MouseButton.LeftButton:
            return
        
        # posisi mouse viewport, jika width 300 dan scroll berada di 200 maka pos mouse hanya 200 hingga 300 atau 0 hingga 100
        pos = e.position()
        mx = pos.x()

        mx += ScrollTimeLine.X
        calculate = mx / scale()

        conf = ConfigTimeLine
        # pasin dengan frames dari fps
        calculate = round(calculate * conf.FPS) / conf.FPS
        
        ConfigTimeLine.CURRENTPOS = max(0.,min(conf.DURATION,calculate))

        self.updHeadPos()
        self.updScrollPos(e)

    def getLastScroll(self):
        """Get current scroll in timeline"""
        ScrollTimeLine.X = self.horizontalScrollBar().value()
        ScrollTimeLine.Y = self.verticalScrollBar().value()

    def updScrollPos(self,e: QMouseEvent):
        """Update scroll positions"""

        # posisi mouse viewport, jika width 300 dan scroll berada di 200 maka pos mouse hanya 200 hingga 300 atau 0 hingga 100
        pos  = e.position()
        mx,my = pos.x(),pos.y()

        viewport = self.viewport()
        width = viewport.width()
        height = viewport.height()

        space_before_endorstartsize = 70
        step_add_scroll = 20

        scroll_x = ScrollTimeLine.X
        scroll_y = ScrollTimeLine.Y

        if mx > width - space_before_endorstartsize: # kanan
            scroll_x += step_add_scroll
        elif mx < space_before_endorstartsize: # kiri
            scroll_x = max(0,scroll_x - step_add_scroll)
        if my > height - space_before_endorstartsize: # bawah
            scroll_y += step_add_scroll
        elif my < space_before_endorstartsize: # atas
            scroll_y = max(0,scroll_y - step_add_scroll)

        self.horizontalScrollBar().setValue(scroll_x)
        self.verticalScrollBar().setValue(scroll_y)
        
    def customFocusLayer(self,e:QMouseEvent):
        """Custom event focus layer"""
        global TARGET_UIDX,SELECT_STRIP

        if e.button() != Qt.MouseButton.LeftButton:
            return
        

        item = self.itemAt(e.pos())

        # jika yang diklik adalah selain layer
        if item and not isinstance(item,LayerPaint) and not isinstance(item,BackLayer) and not isinstance(item,HeadPos):
            checkstrip = item.data(SIDEKEY)
            if checkstrip:
                SELECT_STRIP = checkstrip 
                # print(SELECT_STRIP)
            else: SELECT_STRIP = None
            # cari siapa yang jadi parent itemnya atau containernya
            item = item.parentItem()
        else: SELECT_STRIP = None

        is_item_layer = True if isinstance(item,LayerPaint) else False
        uid_select = item.data(KEYLAYER) if is_item_layer else None

        if uid_select:
            if uid_select == TARGET_UIDX: return
            else: self.unfocusLayer()
            TARGET_UIDX = uid_select
            projf,_ = get_projectfile()
            layer = next(ly for ly in projf.layers if ly.uid == uid_select)
            # print(TARGET_UIDX)
            UTILSFRAMESET.fxset.emit(layer)
            item.leftHighlight.show()
            item.rightHighlight.show()
        else: self.unfocusLayer()

    def unfocusLayer(self):
        """Unfocus Layer"""
        global TARGET_UIDX,UPDATED

        if TARGET_UIDX is None:
            return

        items = self.items()
        item  = next((im for im in items if im.data(KEYLAYER) == TARGET_UIDX and isinstance(im,LayerPaint)),None)

        if item:
            # print("unfocus")
            item.leftHighlight.hide()
            item.rightHighlight.hide()
            TARGET_UIDX = None
            UPDATED = False
        # else: print("not")

    def stretchLayer(self,e: QMouseEvent): # NOSONAR
        """Stretch layer""" 
        global UPDATED
        if e.buttons() != Qt.MouseButton.LeftButton:
            return
        
        if not TARGET_UIDX: return
        
        projf,_ = get_projectfile()
        items = self.items()
        item = next((im for im in items if im.data(KEYLAYER) == TARGET_UIDX and isinstance(im,LayerPaint)),None)
        getlayer = next((d for d in projf.layers if d.uid == TARGET_UIDX),None)
        sc = scale()
        updata = {}

        time_pos = round(ConfigTimeLine.CURRENTPOS * ConfigTimeLine.FPS) / ConfigTimeLine.FPS

        if item and getlayer:
            updata["uid_l"] = TARGET_UIDX
            rect = item.rect()
            if SELECT_STRIP == "left":
                realstart = getlayer.realend - (getlayer.end - time_pos)
                if (getlayer.end - time_pos) < 0.1 or realstart < 0:
                    # print("cant")
                    return
                print(time_pos)
                print(realstart)
                updata["start"] = time_pos
                updata["realstart"] = realstart
                end = getlayer.end
                new_pos_start = time_pos * sc
                calculate_endwith = (end - time_pos) * sc
                rect.setWidth(calculate_endwith)
                item.setX(new_pos_start)
                item.setRect(rect)
                lastpos = time_pos if time_pos < getlayer.start else getlayer.start
                newpos = getlayer.start if time_pos < getlayer.start else time_pos
                run_removch(lastpos,newpos)
                item.rightHighlight.setX(calculate_endwith-5.5)
                upd_layer(updata)
                UPDATED = True
            elif SELECT_STRIP == "right":
                realend = getlayer.realstart + (time_pos - getlayer.start)
                if (time_pos - getlayer.start) < 0.1 or realend > getlayer.duration:
                    # print("cant")
                    return
                print(realend)
                updata["end"] = time_pos
                updata["realend"] = realend
                start  = getlayer.start
                calculate_endwith = (time_pos - start) * sc
                rect.setWidth(calculate_endwith)
                item.setRect(rect)
                item.rightHighlight.setX(calculate_endwith-5.5)
                lastpos = time_pos if time_pos < getlayer.end else getlayer.end
                newpos = getlayer.end if time_pos < getlayer.end else time_pos
                run_removch(lastpos,newpos)
                upd_layer(updata)
                UPDATED = True
            else: return
        else: UPDATED = False

    def cutLayer(self, condition):
        """Cut layer"""
        global TARGET_UIDX,UPDATED

        if not TARGET_UIDX: return

        items = self.items()
        item = next((im for im in items if im.data(KEYLAYER) == TARGET_UIDX and isinstance(im,LayerPaint)),None)
        projf,_ = get_projectfile()
        getlayer = next((d for d in projf.layers if d.uid == TARGET_UIDX),None)
        sc = scale()
        
        conf = ConfigTimeLine
        timepos = round(conf.CURRENTPOS * conf.FPS) / conf.FPS

        if item and getlayer:
            rect = item.rect()
            if condition == "cut_left":
                cut_start = timepos
                cut_realstart = getlayer.realstart + (timepos - getlayer.start)
                if (getlayer.end - cut_start) < 0.1:
                    # print("cant")
                    return
                run_removch(getlayer.start,cut_start)
                upd_layer({"uid_l": TARGET_UIDX,"start": cut_start,"realstart":cut_realstart})
                UPDATED = True
                self.histroyUpdate(UpdHistory.LAYER)
                end = getlayer.end
                new_pos_start = cut_start * sc
                calculate_endwidth =  (end - cut_start) * sc
                item.setX(new_pos_start)
                rect.setWidth(calculate_endwidth)
                item.setRect(rect)
                item.rightHighlight.setX(calculate_endwidth-5.5)
            elif condition == "cut_right":
                cut_end = timepos
                cut_realend = getlayer.realend - (getlayer.end - timepos)
                if (cut_end - getlayer.start) < 0.1:
                    # print("cant")
                    return
                run_removch(cut_end,getlayer.end)
                upd_layer({"uid_l": TARGET_UIDX,"end": cut_end,"realend":cut_realend})
                UPDATED = True
                self.histroyUpdate(UpdHistory.LAYER)
                calculate_endwidth = (cut_end - getlayer.start) * sc
                rect.setWidth(calculate_endwidth)
                item.setRect(rect)
                item.rightHighlight.setX(calculate_endwidth-5.5)
            else: UPDATED = False

    def cutLeft(self):
        """Cut Left Layer"""
        self.cutLayer("cut_left")
    def cutRight(self):
        """Cut right layer"""
        self.cutLayer("cut_right")

    def MoveAndReorderLayer(self,e:QMouseEvent):
        """Move and reorder layer"""
        global UPDATED
        if e.buttons() != Qt.MouseButton.LeftButton:
            return
        if SELECT_STRIP : return
        if not TARGET_UIDX: return
        items = self.items()
        projf,_  = get_projectfile()
        item = next((im for im in items if im.data(KEYLAYER) == TARGET_UIDX and isinstance(im,LayerPaint)),None)
        getlayer = next((d for d in projf.layers if d.uid == TARGET_UIDX),None)
        if not item or not getlayer:
            UPDATED = False
            return

        sc = scale()
        conf = ConfigTimeLine
        pos = e.position()

        mx,my = pos.x(),pos.y()
        mx += ScrollTimeLine.X
        mx /= sc
        my += ScrollTimeLine.Y

        # for move
        total_duration = getlayer.end - getlayer.start
        postime = mx - (total_duration / 2)
        timepos = round(postime * ConfigTimeLine.FPS) / ConfigTimeLine.FPS
        start = max(0.,timepos)
        end = min(ConfigTimeLine.DURATION,start + total_duration)
        
        updata = {"uid_l": TARGET_UIDX, "start": start,"end": end}
        # print(f"start: {getlayer.start}, end: {getlayer.end}")

        # for order
        new_order = int((my-conf.GAP)/conf.GAP) 
        new_order = max(0,min(len(projf.layers)-1,new_order))

        lastpos = start if start < getlayer.start else getlayer.start
        newpos = getlayer.end if start < getlayer.start else end

        if new_order != getlayer.order:
            old_order = getlayer.order
            other_layer = next((d for d in projf.layers if d.order == new_order),None)
            if other_layer:
                # compare_data = d
                # print(f"select: {getlayer.order}, compare: {compare_data["order"]}")
                upd_layer({"uid_l": other_layer.uid,"order": old_order})
                UPDATED = True
                reorder_item = next((item for item in items if item.data(KEYLAYER) == other_layer.uid),None)
                if reorder_item: 
                    run_removch(lastpos, newpos)
                    reorder_layer_compare = conf.GAP + (conf.GAP * old_order)
                    reorder_item.setY(reorder_layer_compare)


            updata["order"] = new_order
            reorder_layer_select = conf.GAP + (conf.GAP * new_order)
            item.setY(reorder_layer_select)


        run_removch(lastpos, newpos)
        upd_layer(updata)
        calculate_pos_x = start  * sc 
        item.setX(calculate_pos_x)
        UPDATED = True

    def refreshLayer(self):
        """Delete item layer"""
        global TARGET_UIDX,SELECT_STRIP
        self.mainScene.clear()
        TARGET_UIDX = None
        SELECT_STRIP = None
        self.setSizeView()
        self.addTimeLinePos()
        self.addLayer()
        self.addHeadPos()

    def zoomIn(self):
        maxin = ConfigTimeLine.ZOOM
        ConfigTimeLine.ZOOM = min(8.0,ConfigTimeLine.ZOOM * 1.25)
        if ConfigTimeLine.ZOOM != maxin:
            self.refreshLayer()

    def zoomOut(self):
        maxout = ConfigTimeLine.ZOOM
        ConfigTimeLine.ZOOM = max(0.125,ConfigTimeLine.ZOOM / 1.25)
        if ConfigTimeLine.ZOOM != maxout:
            self.refreshLayer()

    def deleteLayer(self):
        global UPDATED
        if not TARGET_UIDX: return
        if not CurrentPrj.pathfile: return
        projf,_ = get_projectfile()
        chs_lyr = next((lyr for lyr in projf.layers if lyr.uid == TARGET_UIDX),None)
        if not chs_lyr: return

        lastpos = chs_lyr.start
        newpos = chs_lyr.end

        run_removch(lastpos,newpos)
        del_layer({"uid_l": TARGET_UIDX})
        UPDATED = True
        self.histroyUpdate(UpdHistory.LYSFXSTTMLN)
        self.refreshLayer()
        UTILSFRAMESET.delcont.emit()
        UTILSLAYER.pos_layer.emit()

    def addEffectLayer(self,prodata):
        if not TARGET_UIDX: return
        projf,_ = get_projectfile()
        sel_lyr = next((lyr for lyr in projf.layers if lyr.uid == TARGET_UIDX),None)
        if not sel_lyr: return
        last_pos = sel_lyr.start
        new_pos = sel_lyr.end
        data = {
            "uid_layer": TARGET_UIDX,
            "typfx": prodata["typfx"]
        }
        func = prodata["func"]()
        prog = func.add_data()
        run_removch(lastpos=last_pos,newpos=new_pos)
        create_effect(data=data,progs=prog)
        projf,_ = get_projectfile()
        sel_lyr = next((lyr for lyr in projf.layers if lyr.uid == TARGET_UIDX),None)
        if not sel_lyr: return
        UTILSFRAMESET.fxset.emit(sel_lyr)
        UTILSLAYER.pos_layer.emit()


