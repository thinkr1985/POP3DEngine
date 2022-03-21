from logger import get_logger

logger = get_logger(__file__)


class OpenGLVersionCompatibilityError(Exception):
    """Get raised when OpenGL version is less than 4.0.0"""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class EntityCreationError(Exception):
    """Get raised when Entity creation fails."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class VertexShaderCompilationError(Exception):
    """Get raised when Vertex shader compilation fails."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class FragmentShaderCompilationError(Exception):
    """Get raised when Fragment Shader compilation fails."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class ShaderProgramLinkError(Exception):
    """Get raised when Shader linking fails."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class VertexAttributeError(Exception):
    """Get raised when one of the vertex attribute fails though check"""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class ShaderCompilationError(Exception):
    """Get raised when Shader compilation fails."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class UnsupportedShaderType(Exception):
    """Get raised when Shader is not defined in the constant.py's
     SUPPORTED_SHADER_TYPES."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)


class CameraCreationError(Exception):
    """Get raised when failed to create cameras."""
    def __init__(self, message=None):
        super().__init__()
        logger.error(message)
