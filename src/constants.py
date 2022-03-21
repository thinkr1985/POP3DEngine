import os
import psutil
from OpenGL.GL import *

MODULE = os.path.dirname(__file__)

ICONS_PATH = os.path.join(MODULE, 'icons')

SHADER_SRC = os.path.join(MODULE, 'default_shaders')

SUPPORTED_SHADER_TYPES = {
    'fragment': GL_FRAGMENT_SHADER,
    'vertex': GL_VERTEX_SHADER,
    'geometry': GL_GEOMETRY_SHADER,
    'compute': GL_COMPUTE_SHADER}

DEFAULT_TEXTURES = os.path.join(MODULE, 'default_textures')

LOGO = os.path.join(MODULE, 'icons', 'pop3d_logo.png')

STRIDE = 48

PID = os.getpid()

PS_PROCESS = psutil.Process(PID)
