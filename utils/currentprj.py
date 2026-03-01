
class UpdHistory:
    WORKFLOW = "workflow" # semua ,mulari dari timeline ,seteffect,setlayer,preview
    ASSETBAR = "assetbar" # assetbar saja
    EFFXSET = "effxset" # effect setting saja
    EMPETY = "empety"
    LAYER = "layer"
    LAYERSETANDTMLN = "layersetandtmln" # layersettings and timeline
    LYSFXSTTMLN = "lysfxsttmln" # timeline and effectset and layerset
    ###############
    LISTHISTORY = [WORKFLOW,ASSETBAR,EFFXSET,EMPETY,LAYER,LAYERSETANDTMLN,LYSFXSTTMLN]

class CurrentPrj:
    # history current
    index_history: int = 0
    fl_updhistory: str = UpdHistory.EMPETY
    # project current
    namefile:str | None = None
    folderfile:str | None = None
    pathfile:str | None = None

class CurrentThread:
    MAINPROC = None
    
class UndoRedo:
  """CONDITION UNDO AND REDO"""
  same_redo = 0
  same_undo = 0
