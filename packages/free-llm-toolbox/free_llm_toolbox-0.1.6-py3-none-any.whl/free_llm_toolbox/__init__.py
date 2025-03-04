"""
Free LLM Toolbox - A Python package for easy interaction with various LLMs and Vision models
"""

__version__ = "0.1.6"  # Mettez à jour la version!

__all__ = [
    "LanguageModel",
    "ImageAnalyzerAgent",
    # "LLM_answer_v3" removed as it doesn't exist
]

from .language_model import LanguageModel
from .vision_utils import ImageAnalyzerAgent
# ... autres importations spécifiques ...
