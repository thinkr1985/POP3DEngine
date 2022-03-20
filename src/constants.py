import os
import psutil

MODULE = os.path.dirname(__file__)

ICONS_PATH = os.path.join(MODULE, 'icons')

DEFAULT_SHADER = os.path.join(MODULE, 'default_shaders', 'lambert')

CONSTANT_SHADER = os.path.join(MODULE, 'default_shaders', 'constant')

DEFAULT_TEXTURES = os.path.join(MODULE, 'default_textures')

LOGO = os.path.join(MODULE, 'icons', 'pop3d_logo.png')

STRIDE = 48

PID = os.getpid()

PS_PROCESS = psutil.Process(PID)
