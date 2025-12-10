#!/usr/bin/env python3
"""
gyuu GUI - デスクトップアプリ版
pywebviewを使ってWeb UIをネイティブウィンドウで表示
"""

import webview
import os
import base64
from pathlib import Path

# グローバルでwindowを保持
windows = []


def get_html_path():
    """HTMLファイルのパスを取得"""
    # スクリプトのディレクトリを基準にする
    script_dir = Path(__file__).parent
    html_path = script_dir / 'index.html'
    
    if html_path.exists():
        return str(html_path)
    
    raise FileNotFoundError("index.html が見つかりません")


class Api:
    """JavaScriptから呼び出せるAPI"""
    
    def save_file(self, filename, data_url):
        """ファイル保存ダイアログを表示して保存"""
        try:
            if not windows:
                return {'success': False, 'reason': 'Window not ready'}
            
            window = windows[0]
            
            header, encoded = data_url.split(',', 1)
            data = base64.b64decode(encoded)
            
            # 拡張子を取得
            ext = filename.split('.')[-1] if '.' in filename else 'png'
            
            # 保存ダイアログを表示
            save_path = window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=filename,
                file_types=(f'画像ファイル (*.{ext})', f'すべてのファイル (*.*)')
            )
            
            if save_path:
                if isinstance(save_path, (list, tuple)):
                    save_path = save_path[0]
                
                with open(save_path, 'wb') as f:
                    f.write(data)
                return {'success': True, 'path': save_path}
            
            return {'success': False, 'reason': 'cancelled'}
        
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def save_all_files(self, files):
        """フォルダを選択して全ファイルを保存"""
        try:
            if not windows:
                return {'success': False, 'reason': 'Window not ready'}
            
            window = windows[0]
            
            # フォルダ選択ダイアログ
            folder = window.create_file_dialog(webview.FOLDER_DIALOG)
            
            if folder:
                if isinstance(folder, (list, tuple)):
                    folder = folder[0]
                
                saved = []
                for file_info in files:
                    filename = file_info['filename']
                    data_url = file_info['dataUrl']
                    
                    header, encoded = data_url.split(',', 1)
                    data = base64.b64decode(encoded)
                    
                    filepath = os.path.join(folder, filename)
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    saved.append(filepath)
                
                return {'success': True, 'count': len(saved), 'folder': folder}
            
            return {'success': False, 'reason': 'cancelled'}
        
        except Exception as e:
            return {'success': False, 'reason': str(e)}


def main():
    global windows
    
    html_path = get_html_path()
    
    # APIインスタンスを作成
    api = Api()
    
    # ウィンドウを作成
    window = webview.create_window(
        title='🗜️ gyuu - 画像圧縮ツール',
        url=html_path,
        width=900,
        height=700,
        min_size=(600, 400),
        resizable=True,
        text_select=False,
        js_api=api
    )
    
    # グローバルに保存
    windows.append(window)
    
    # アプリを起動
    webview.start(debug=False)


if __name__ == '__main__':
    main()
