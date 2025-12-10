"""
gyuu - TinyPNG-like image compression tool
画像をぎゅーっと圧縮するツール
"""

from .compressor import compress_image, process_directory
from .utils import format_size, get_file_size

__version__ = "1.0.0"
__all__ = ["compress_image", "process_directory", "format_size", "get_file_size"]
