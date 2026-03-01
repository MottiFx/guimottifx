import math

class ConfigTimeLine:
    LAYERHEIGHT:int = 40
    LAYERWIDTH:int = 50 
    GAP:int = 50
    ZOOM:float = 1.
    ###################
    DURATION:float = 120
    CURRENTPOS:float = 0.0
    FPS:float = 30.0
    ###################
    PREVIEW:bool = False

class ConfigFrame:
    SETUPFRAME = False
    LOSSLES = 1.5

class ConfigAudio:
    CHANNELS = 2
    SAMPLE_RATE = 44100
    TYPE_AUDIO = "stereo"

class ConfigRender:
    status = False
    message = None

class ConfigThreadRender:
    MAINFUNC = None

def scale():
    conf = ConfigTimeLine
    return conf.LAYERWIDTH * conf.ZOOM

def timeline_width():
    conf  = ConfigTimeLine
    return int(conf.DURATION * scale())

def timeline_height(total_layer):
    conf = ConfigTimeLine
    calculate = conf.GAP + (conf.GAP * total_layer)
    calculate += conf.LAYERHEIGHT
    return calculate

def format_hms_frames(seconds: float,fps:float) -> str:
    if seconds < 0:
        seconds = 0.0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    minimizeframe = seconds - int(seconds)
    frm = int(math.floor(minimizeframe * fps))
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{frm:02d}"

class ScrollTimeLine:
    X = 0
    Y = 0
