from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from screeninfo import get_monitors

monitor = get_monitors()[0]
w,h = int(monitor.width/5), int(monitor.height/3)
x,y = int((monitor.width - w)/2),int((monitor.height-h)/2)

