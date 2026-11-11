# Axel 安裝記錄（無 sudo）

## 環境
- OS: Ubuntu 24.04 x86_64
- 工具鏈: g++ 13.3.0, cmake 4.3.4, make

## 安裝流程

### 1. 下載
```bash
/usr/bin/wget -q "https://github.com/axel-download-accelerator/axel/releases/download/v2.17.14/axel-2.17.14.tar.xz" -O /tmp/axel.tar.xz
```

### 2. 編譯
```bash
cd /tmp && tar xf axel.tar.xz
cd axel-2.17.14 && mkdir -p build && cd build
../configure --prefix=$HOME/.local
make -j$(nproc)
make install
```

### 3. 複製到 ~/bin
```bash
cp ~/.local/bin/axel ~/bin/axel
```

### 4. 驗證
```bash
~/bin/axel --version
# Axel 2.17.14 (linux-gnu)
```

## 用途對比

| 工具 | 指令 | 特點 |
|------|------|------|
| aria2c | `aria2c -x16 -s16 -c URL -o file` | 多線程 + 斷點續傳 + metalink，適合 HuggingFace 大檔 |
| axel | `axel -n 16 URL` | 輕量多線程，適合應急快速下載，無續傳 |

## 關鍵差異

- **axel**: 輕量（252KB），用法簡單，無斷點續傳，適合快速替換 wget
- **aria2c**: 功能完整（50MB），支援分段並發、斷點續傳，適合 5GB+ 大檔

## 常用範例
```bash
# axel 16 線程下載
axel -n 16 "https://example.com/large-file.zip" -o /tmp/file.zip

# aria2c 16 線程 + 斷點續傳（推薦 HuggingFace）
aria2c -x16 -s16 -c "https://huggingface.co/..." -d ~/Downloads -o file.safetensors
```
