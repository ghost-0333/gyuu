"""画像フォーマット別の圧縮処理"""

import io
from PIL import Image


def compress_png(image: Image.Image, quality: int) -> bytes:
    """PNG画像を圧縮"""
    # 色数を削減して圧縮
    if image.mode == 'RGBA':
        # アルファチャンネルがある場合
        compressed = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        compressed = compressed.convert('RGBA')
    elif image.mode == 'P':
        # パレット画像はそのまま
        compressed = image
    else:
        # その他はRGBに変換して量子化
        if image.mode != 'RGB':
            image = image.convert('RGB')
        compressed = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        compressed = compressed.convert('RGB')
    
    buffer = io.BytesIO()
    compressed.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


def compress_jpeg(image: Image.Image, quality: int) -> bytes:
    """JPEG画像を圧縮"""
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=quality, optimize=True)
    return buffer.getvalue()


def compress_webp(image: Image.Image, quality: int) -> bytes:
    """WebP画像を圧縮"""
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=quality, method=6)
    return buffer.getvalue()


def compress_default(image: Image.Image) -> bytes:
    """その他のフォーマットを圧縮"""
    buffer = io.BytesIO()
    image.save(buffer, format=image.format, optimize=True)
    return buffer.getvalue()


# サポートする拡張子
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
