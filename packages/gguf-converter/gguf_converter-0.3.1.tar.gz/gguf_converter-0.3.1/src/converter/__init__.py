"""
Advanced model conversion module with architecture-aware optimizations
"""

import importlib
import logging
import sys
from types import ModuleType
from typing import Type, Dict, Any, Optional

# Configure package logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ----- Version Compatibility -----
_MIN_TORCH_VERSION = (2, 0, 1)
_MIN_TRANSFORMERS_VERSION = (4, 31, 0)

# ----- Lazy Loading Setup -----
class _LazyLoader(ModuleType):
    """Lazy loader for heavy dependencies to improve startup performance"""
    
    def __init__(self, local_name, parent_module_globals, name):
        self._local_name = local_name
        self._parent_module_globals = parent_module_globals
        self._module = None
        super().__init__(name)

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self.__name__)
            self._parent_module_globals[self._local_name] = self._module
            logger.debug(f"Lazy-loaded module: {self.__name__}")
        return self._module

    def __getattr__(self, name):
        module = self._load()
        return getattr(module, name)

    def __dir__(self):
        module = self._load()
        return dir(module)

# Lazy-load heavy dependencies
sys.modules[__name__ + ".quantize"] = _LazyLoader(
    "quantize", globals(), __name__ + ".quantize"
)
sys.modules[__name__ + ".gguf_writer"] = _LazyLoader(
    "gguf_writer", globals(), __name__ + ".gguf_writer"
)

# ----- Core Exports with Type Hints -----
from .model_loader import ModelLoader as ModelLoader
from .architecture_maps import (
    get_architecture_optimizer as get_architecture_optimizer,
    register_architecture as register_architecture
)

# ----- Optimization Registry -----
_ARCHITECTURE_OPTIMIZERS: Dict[str, Type[Any]] = {}

def register_architecture(name: str, optimizer_class: Type[Any]):
    """Register custom architecture optimizations (decorator compatible)"""
    _ARCHITECTURE_OPTIMIZERS[name] = optimizer_class
    logger.info(f"Registered architecture optimizer: {name} -> {optimizer_class.__name__}")
    return optimizer_class

def get_architecture_optimizer(model_type: str) -> Optional[Type[Any]]:
    """Get architecture-specific optimizer with fallback handling"""
    optimizer = _ARCHITECTURE_OPTIMIZERS.get(model_type)
    if not optimizer:
        logger.debug(f"No optimizer registered for architecture: {model_type}")
        try:
            module = importlib.import_module(f".architecture_maps.{model_type}", __name__)
            optimizer = getattr(module, f"{model_type.capitalize()}Optimizer", None)
            if optimizer:
                _ARCHITECTURE_OPTIMIZERS[model_type] = optimizer
        except ImportError:
            pass
    return optimizer

# ----- Runtime Configuration -----
class ConverterConfig:
    """Global converter configuration with environment awareness"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """Initialize configuration from environment variables"""
        self.enable_jit_optimizations = True
        self.force_cpu = False
        self.experimental_quantization = False
        self._load_environment()
        
    def _load_environment(self):
        import os
        if os.getenv("GGUF_FORCE_CPU"):
            self.force_cpu = True
        if os.getenv("GGUF_DISABLE_JIT"):
            self.enable_jit_optimizations = False
        if os.getenv("GGUF_EXPERIMENTAL_QUANT"):
            self.experimental_quantization = True

# ----- Public Interface -----
__all__ = [
    "ModelLoader",
    "Quantizer",
    "GGUFWriter",
    "ConverterConfig",
    "get_architecture_optimizer",
    "register_architecture",
    "conversion_handler",
]

# ----- Error Handling -----
class ConversionError(RuntimeError):
    """Base class for conversion-related errors"""
    
    def __init__(self, message: str, module: str = None):
        full_msg = f"[{module}] {message}" if module else message
        super().__init__(full_msg)
        self.module = module

class ArchitectureNotSupportedError(ConversionError):
    """Error raised when encountering unsupported model architectures"""

# ----- Decorators -----
def conversion_handler(*, priority: int = 0):
    """Decorator factory for registering custom conversion handlers"""
    
    def decorator(func):
        func._conversion_priority = priority
        return func
    
    return decorator

# ----- Version Check -----
def _check_dependencies():
    """Verify critical dependency versions"""
    from packaging import version
    
    try:
        import torch
        if version.parse(torch.__version__) < version.parse(".".join(map(str, _MIN_TORCH_VERSION))):
            raise ImportError(f"Torch version >= {_MIN_TORCH_VERSION} required")
        
        import transformers
        if version.parse(transformers.__version__) < version.parse(".".join(map(str, _MIN_TRANSFORMERS_VERSION))):
            raise ImportError(f"Transformers version >= {_MIN_TRANSFORMERS_VERSION} required")
            
    except ImportError as e:
        logger.critical(f"Dependency check failed: {str(e)}")
        raise

# Perform dependency check on first import
_check_dependencies()

# ----- JIT Compilation Setup -----
if ConverterConfig().enable_jit_optimizations:
    try:
        from torch.utils._mode_utils import no_dispatch
        logger.debug("JIT optimizations enabled")
    except ImportError:
        logger.warning("JIT optimizations unavailable in current environment")