import numpy as np
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

DEFAULT_SHAPES_DIR = os.path.join(MODULE, 'default_shapes')

LOGO = os.path.join(MODULE, 'icons', 'pop3d_logo.png')

STRIDE = 48

PID = os.getpid()

PS_PROCESS = psutil.Process(PID)

NUM_LIGHT_LIMITS = 1

ATMOSPHERE_DIFFUSE_COLOR = np.array([0.05, 0, 0.7], dtype=np.float32)

ATMOSPHERE_DIFFUSE_INTENSITY = 0.1
