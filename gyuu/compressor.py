"""画像圧縮のメインロジック"""

import io
from pathlib import Path
from PIL import Image, ImageOps

from .formats import (
    compress_png,
    compress_jpeg,
    compress_webp,
    compress_default,
    SUPPORTED_EXTENSIONS,
)
from .utils import get_file_size


def resize_image(
    image: Image.Image,
    max_width: int = None,
    max_height: int = None
) -> Image.Image:
    """画像をリサイズ"""
    if not max_width and not max_height:
        return image
    
    orig_width, orig_height = image.size
    new_width, new_height = orig_width, orig_height
    
    if max_width and orig_width > max_width:
        ratio = max_width / orig_width
        new_width = max_width
        new_height = int(orig_height * ratio)
    
    if max_height and new_height > max_height:
        ratio = max_height / new_height
        new_height = max_height
        new_width = int(new_width * ratio)
    
    if (new_width, new_height) != (orig_width, orig_height):
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image


def determine_format(input_path: Path, output_format: str = None) -> str:
    """出力フォーマットを決定"""
    if output_format:
        return output_format.lower()
    
    fmt = input_path.suffix.lower().lstrip('.')
    if fmt == 'jpeg':
        fmt = 'jpg'
    return fmt


def compress_by_format(image: Image.Image, fmt: str, quality: int) -> bytes:
    """フォーマットに応じて圧縮"""
    if fmt == 'png':
        return compress_png(image, quality)
    elif fmt in ('jpg', 'jpeg'):
        return compress_jpeg(image, quality)
    elif fmt == 'webp':
        return compress_webp(image, quality)
    else:
        return compress_default(image)


def compress_image(
    input_path: str,
    output_path: str = None,
    quality: int = 80,
    output_format: str = None,
    max_width: int = None,
    max_height: int = None
) -> dict:
    """
    画像を圧縮する
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス（Noneの場合は入力ファイルを上書き）
        quality: 圧縮品質 (1-100)
        output_format: 出力フォーマット (png, jpg, webp)
        max_width: 最大幅
        max_height: 最大高さ
    
    Returns:
        圧縮結果の情報
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {input_path}")
    
    original_size = get_file_size(input_path)
    
    # 画像を開く
    with Image.open(input_path) as img:
        # EXIFの回転情報を適用
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
        
        # リサイズ
        img = resize_image(img, max_width, max_height)
        
        # 出力フォーマットを決定
        fmt = determine_format(input_path, output_format)
        
        # 出力パスを決定
        if output_path is None:
            out_path = input_path
        else:
            out_path = Path(output_path)
        
        # フォーマットに応じた拡張子の変更
        if output_format:
            ext = '.jpg' if fmt == 'jpg' else f'.{fmt}'
            out_path = out_path.with_suffix(ext)
        
        # 圧縮
        compressed_data = compress_by_format(img, fmt, quality)
    
    # ファイルに書き込み
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(compressed_data)
    
    compressed_size = len(compressed_data)
    reduction = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
    
    return {
        'input': str(input_path),
        'output': str(out_path),
        'original_size': original_size,
        'compressed_size': compressed_size,
        'reduction': reduction
    }


def process_directory(
    input_dir: str,
    output_dir: str = None,
    quality: int = 80,
    output_format: str = None,
    max_width: int = None,
    max_height: int = None,
    recursive: bool = False
) -> list:
    """ディレクトリ内の画像を一括圧縮"""
    input_dir = Path(input_dir)
    results = []
    
    if recursive:
        files = input_dir.rglob('*')
    else:
        files = input_dir.glob('*')
    
    for filepath in files:
        if filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
            if output_dir:
                rel_path = filepath.relative_to(input_dir)
                out_path = Path(output_dir) / rel_path
            else:
                out_path = None
            
            try:
                result = compress_image(
                    str(filepath),
                    str(out_path) if out_path else None,
                    quality,
                    output_format,
                    max_width,
                    max_height
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'input': str(filepath),
                    'error': str(e)
                })
    
    return results
