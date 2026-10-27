# -*- coding: utf-8 -*-
import sys, os
p = r"D:\Desktop\相册\二维IP制作_20261012\手办设计"
print(sys.getfilesystemencoding(), sys.getdefaultencoding())
print(len(p), os.path.exists(p))
print(repr(os.listdir(p))[:200])
