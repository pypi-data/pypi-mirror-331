"""
Free LLM Toolbox - A Python package for easy interaction with various LLMs and Vision models
"""
from .language_model import LanguageModel
from .vision_utils import ImageAnalyzerAgent

# Définir un alias pour LanguageModel
LLM_answer_v3 = LanguageModel

__version__ = "0.1.2"  # Version mise à jour

__all__ = [
    "LanguageModel",
    "ImageAnalyzerAgent",
    "LLM_answer_v3",
]