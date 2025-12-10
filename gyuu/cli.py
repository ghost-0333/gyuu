"""コマンドラインインターフェース"""

import argparse
import sys
from pathlib import Path

from .compressor import compress_image, process_directory
from .utils import format_size


def print_result(result: dict):
    """圧縮結果を表示"""
    if 'error' in result:
        print(f"❌ {result['input']}: {result['error']}")
    else:
        print(f"✅ {result['input']}")
        print(f"   → {result['output']}")
        print(f"   {format_size(result['original_size'])} → {format_size(result['compressed_size'])} ({result['reduction']:.1f}% 削減)")


def print_summary(results: list):
    """サマリーを表示"""
    total_original = 0
    total_compressed = 0
    success_count = 0
    error_count = 0
    
    for result in results:
        if 'error' in result:
            error_count += 1
        else:
            success_count += 1
            total_original += result['original_size']
            total_compressed += result['compressed_size']
    
    if len(results) > 1:
        print("=" * 50)
        print(f"📊 サマリー: {success_count}件成功, {error_count}件失敗")
        if total_original > 0:
            total_reduction = ((total_original - total_compressed) / total_original) * 100
            print(f"   合計: {format_size(total_original)} → {format_size(total_compressed)} ({total_reduction:.1f}% 削減)")


def create_parser() -> argparse.ArgumentParser:
    """引数パーサーを作成"""
    parser = argparse.ArgumentParser(
        description='gyuu - 画像をぎゅーっと圧縮するツール 🗜️',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  gyuu image.png                    # 画像を圧縮（上書き）
  gyuu image.png -o compressed.png  # 別ファイルに出力
  gyuu images/ -o output/           # ディレクトリ内の画像を一括圧縮
  gyuu image.png -q 60              # 品質60%で圧縮
  gyuu image.png -f webp            # WebP形式に変換
  gyuu image.png --max-width 1920   # 最大幅1920pxにリサイズ
        '''
    )
    
    parser.add_argument('input', help='入力ファイルまたはディレクトリ')
    parser.add_argument('-o', '--output', help='出力ファイルまたはディレクトリ')
    parser.add_argument('-q', '--quality', type=int, default=80,
                        help='圧縮品質 (1-100, デフォルト: 80)')
    parser.add_argument('-f', '--format', choices=['png', 'jpg', 'webp'],
                        help='出力フォーマット')
    parser.add_argument('--max-width', type=int, help='最大幅')
    parser.add_argument('--max-height', type=int, help='最大高さ')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='サブディレクトリも処理')
    
    return parser


def main():
    """メインエントリーポイント"""
    parser = create_parser()
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"❌ エラー: '{args.input}' が見つかりません")
        sys.exit(1)
    
    print("🗜️  gyuu - 画像圧縮中...\n")
    
    if input_path.is_dir():
        results = process_directory(
            args.input,
            args.output,
            args.quality,
            args.format,
            args.max_width,
            args.max_height,
            args.recursive
        )
    else:
        results = [compress_image(
            args.input,
            args.output,
            args.quality,
            args.format,
            args.max_width,
            args.max_height
        )]
    
    # 結果を表示
    for result in results:
        print_result(result)
        print()
    
    # サマリー
    print_summary(results)
    
    print("\n✨ 完了!")


if __name__ == '__main__':
    main()
