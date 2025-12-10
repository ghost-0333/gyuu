"""ユーティリティ関数"""

import os


def get_file_size(filepath: str) -> int:
    """ファイルサイズを取得"""
    return os.path.getsize(filepath)


def format_size(size: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"
