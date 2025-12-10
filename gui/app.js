// 状態管理
const state = {
    files: new Map() // id -> { original, compressed, blob, ... }
};

// 要素取得
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const results = document.getElementById('results');
const summary = document.getElementById('summary');
const qualitySlider = document.getElementById('quality');
const qualityValue = document.getElementById('quality-value');

// 品質スライダー
qualitySlider.addEventListener('input', (e) => {
    qualityValue.textContent = `${e.target.value}%`;
});

// ドラッグ&ドロップ
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// ファイル処理
async function handleFiles(files) {
    for (const file of files) {
        if (!file.type.startsWith('image/')) continue;
        
        const id = Date.now() + Math.random();
        await processImage(file, id);
    }
    updateSummary();
}

// 画像読み込み
function loadImage(file) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = URL.createObjectURL(file);
    });
}

// PNG用の色数削減（量子化）
function quantizeImageData(imageData, colorCount) {
    const data = imageData.data;
    const step = Math.max(1, Math.floor(256 / Math.cbrt(colorCount)));
    
    for (let i = 0; i < data.length; i += 4) {
        // RGB各チャンネルを量子化
        data[i] = Math.round(data[i] / step) * step;     // R
        data[i + 1] = Math.round(data[i + 1] / step) * step; // G
        data[i + 2] = Math.round(data[i + 2] / step) * step; // B
        // アルファは維持
    }
}

// 画像圧縮処理
async function processImage(file, id) {
    // カードを作成
    const card = createResultCard(id, file.name, file.size);
    results.appendChild(card);

    try {
        // 設定を取得
        const quality = parseInt(qualitySlider.value) / 100;
        const format = document.getElementById('format').value;
        const maxWidth = parseInt(document.getElementById('max-width').value) || null;
        const maxHeight = parseInt(document.getElementById('max-height').value) || null;

        // 画像を読み込み
        const img = await loadImage(file);
        
        // リサイズ計算
        let width = img.width;
        let height = img.height;

        if (maxWidth && width > maxWidth) {
            height = Math.round(height * (maxWidth / width));
            width = maxWidth;
        }
        if (maxHeight && height > maxHeight) {
            width = Math.round(width * (maxHeight / height));
            height = maxHeight;
        }

        // Canvas で圧縮
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        // 出力フォーマット決定
        let mimeType = file.type;
        let ext = file.name.split('.').pop();
        
        if (format !== 'auto') {
            mimeType = `image/${format}`;
            ext = format === 'jpeg' ? 'jpg' : format;
        }

        // Blob に変換（PNGは量子化で圧縮）
        let blob;
        if (mimeType === 'image/png') {
            // PNGは色数を削減して圧縮
            const imageData = ctx.getImageData(0, 0, width, height);
            quantizeImageData(imageData, Math.max(16, Math.floor(quality * 256)));
            ctx.putImageData(imageData, 0, 0);
            blob = await new Promise(resolve => canvas.toBlob(resolve, mimeType));
        } else {
            blob = await new Promise(resolve => canvas.toBlob(resolve, mimeType, quality));
        }
        
        // 圧縮後のサイズが大きくなった場合は元のファイルを使用
        if (blob.size >= file.size && format === 'auto') {
            blob = file;
        }

        // 状態を保存
        const fileName = file.name.replace(/\.[^.]+$/, `.${ext}`);
        state.files.set(id, {
            originalName: file.name,
            fileName: fileName,
            originalSize: file.size,
            compressedSize: blob.size,
            blob: blob,
            dataUrl: canvas.toDataURL(mimeType, quality)
        });

        // カードを更新
        updateResultCard(id);

    } catch (error) {
        console.error('圧縮エラー:', error);
        card.innerHTML = `<p style="color: red;">エラー: ${error.message}</p>`;
    }
}

// 結果カード作成
function createResultCard(id, name, size) {
    const card = document.createElement('div');
    card.className = 'result-card processing';
    card.id = `card-${id}`;
    card.innerHTML = `
        <div class="preview-container">
            <div class="spinner"></div>
        </div>
        <div class="result-info">
            <h4>${escapeHtml(name)}</h4>
            <p>圧縮中...</p>
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: 50%"></div>
            </div>
        </div>
        <div class="result-actions"></div>
    `;
    return card;
}

// 結果カード更新
function updateResultCard(id) {
    const data = state.files.get(id);
    const card = document.getElementById(`card-${id}`);
    if (!card || !data) return;

    const reduction = ((data.originalSize - data.compressedSize) / data.originalSize * 100);
    const reductionText = reduction >= 0 
        ? `-${reduction.toFixed(1)}%` 
        : `+${Math.abs(reduction).toFixed(1)}%`;
    const reductionClass = reduction >= 0 ? 'reduction-badge' : 'reduction-badge-negative';

    card.className = 'result-card';
    card.innerHTML = `
        <div class="preview-container">
            <img src="${data.dataUrl}" alt="プレビュー">
        </div>
        <div class="result-info">
            <h4>${escapeHtml(data.fileName)}</h4>
            <div class="size-comparison">
                <span class="size-badge size-original">${formatSize(data.originalSize)}</span>
                <span class="size-arrow">→</span>
                <span class="size-badge size-compressed">${formatSize(data.compressedSize)}</span>
                <span class="${reductionClass}">${reductionText}</span>
            </div>
        </div>
        <div class="result-actions">
            <button class="btn btn-download" onclick="downloadFile('${id}')">
                ⬇️ ダウンロード
            </button>
            <button class="btn btn-remove" onclick="removeFile('${id}')">
                🗑️ 削除
            </button>
        </div>
    `;
}

// ファイルダウンロード
async function downloadFile(id) {
    // idを数値に変換して検索
    const numId = typeof id === 'string' ? parseFloat(id) : id;
    const data = state.files.get(numId);
    if (!data) {
        console.error('ファイルが見つかりません:', id);
        return;
    }

    // pywebview APIが利用可能か確認
    if (window.pywebview && window.pywebview.api) {
        try {
            const result = await window.pywebview.api.save_file(data.fileName, data.dataUrl);
            if (result.success) {
                console.log('保存完了:', result.path);
            } else if (result.reason !== 'cancelled') {
                alert('保存エラー: ' + result.reason);
            }
        } catch (e) {
            console.error('保存エラー:', e);
            // フォールバック
            fallbackDownload(data);
        }
    } else {
        // ブラウザ用フォールバック
        fallbackDownload(data);
    }
}

// ブラウザ用ダウンロード（フォールバック）
function fallbackDownload(data) {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(data.blob);
    link.download = data.fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

// ファイル削除
function removeFile(id) {
    const numId = typeof id === 'string' ? parseFloat(id) : id;
    state.files.delete(numId);
    const card = document.getElementById(`card-${id}`);
    if (card) card.remove();
    updateSummary();
}

// すべてダウンロード
document.getElementById('downloadAll').addEventListener('click', async () => {
    if (state.files.size === 0) return;

    // pywebview APIが利用可能か確認
    if (window.pywebview && window.pywebview.api) {
        // フォルダ選択で一括保存
        const files = [];
        for (const data of state.files.values()) {
            files.push({
                filename: data.fileName,
                dataUrl: data.dataUrl
            });
        }
        
        try {
            const result = await window.pywebview.api.save_all_files(files);
            if (result.success) {
                alert(`${result.count}個のファイルを保存しました\n${result.folder}`);
            } else if (result.reason !== 'cancelled') {
                alert('保存エラー: ' + result.reason);
            }
        } catch (e) {
            console.error('保存エラー:', e);
        }
    } else {
        // ブラウザ用フォールバック
        for (const [id] of state.files) {
            downloadFile(id);
            await new Promise(r => setTimeout(r, 100));
        }
    }
});

// サマリー更新
function updateSummary() {
    if (state.files.size === 0) {
        summary.style.display = 'none';
        return;
    }

    let totalOriginal = 0;
    let totalCompressed = 0;

    for (const data of state.files.values()) {
        totalOriginal += data.originalSize;
        totalCompressed += data.compressedSize;
    }

    const reduction = totalOriginal > 0 
        ? ((totalOriginal - totalCompressed) / totalOriginal * 100).toFixed(1)
        : 0;

    document.getElementById('total-files').textContent = state.files.size;
    document.getElementById('total-original').textContent = formatSize(totalOriginal);
    document.getElementById('total-compressed').textContent = formatSize(totalCompressed);
    document.getElementById('total-reduction').textContent = `-${reduction}%`;

    summary.style.display = 'block';
}

// ユーティリティ
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
