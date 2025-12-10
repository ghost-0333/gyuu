# 🗜️ gyuu

画像をぎゅーっと圧縮します。

## プロジェクト構造

```gyuu/
├── Gyuu.app/            # macOSアプリ（ダブルクリックで起動）
├── gyuu.py              # CLIエントリーポイント
├── requirements.txt     # 依存パッケージ
├── README.md
├── gyuu/                # CLIパッケージ
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── compressor.py
│   ├── formats.py
│   └── utils.py
└── gui/                 # GUIパッケージ
    ├── gui_app.py       # GUIアプリ
    ├── index.html
    ├── style.css
    └── app.js
```

## インストール

```bash
# 仮想環境に入る
source .venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 仮想環境から抜ける
deactivate
```

## 使い方

### GUI（ウィンドウ）

#### 方法1: アプリをダブルクリック

`Gyuu.app` をダブルクリックするだけ！

#### 方法2: コマンドで起動**

```bash
source .venv/bin/activate
python gui/gui_app.py
```

画像をドラッグ&ドロップして圧縮できます。

### CLI（コマンドライン）

```bash
# 画像を圧縮（元ファイルを上書き）
python gyuu.py image.png
# または
python -m gyuu image.png

# 別ファイルに出力
python gyuu.py image.png -o compressed.png

# ディレクトリ内の画像を一括圧縮
python gyuu.py images/ -o output/
```

### オプション

| オプション | 説明 |
|-----------|------|
| `-o, --output` | 出力ファイルまたはディレクトリ |
| `-q, --quality` | 圧縮品質 (1-100, デフォルト: 80) |
| `-f, --format` | 出力フォーマット (png, jpg, webp) |
| `--max-width` | 最大幅（リサイズ） |
| `--max-height` | 最大高さ（リサイズ） |
| `-r, --recursive` | サブディレクトリも処理 |

### 使用例

```bash
# 品質60%で圧縮
python gyuu.py image.png -q 60

# WebP形式に変換
python gyuu.py image.png -f webp

# 最大幅1920pxにリサイズしながら圧縮
python gyuu.py image.png --max-width 1920

# ディレクトリを再帰的に処理
python gyuu.py images/ -o output/ -r

# 複数オプションの組み合わせ
python gyuu.py photos/ -o compressed/ -q 70 -f webp --max-width 1920 -r
```

## 対応フォーマット

- PNG
- JPEG
- WebP
- GIF
- BMP

## 圧縮アルゴリズム

- **PNG**: 色数を256色に削減（量子化）+ 最適化
- **JPEG**: 品質ベースの圧縮 + 最適化
- **WebP**: 品質ベースの圧縮（method=6で高圧縮）

## ライセンス

MIT
