# aria2 從源碼編譯（無 sudo）

## 適用情境

需要安裝多線程下載工具，但系統無 sudo 權限。

## 環境

- OS: Ubuntu 24.04 x86_64
- 工具鏈: g++ (Ubuntu 13.3.0), cmake 4.3.4, make
- 下載: /usr/bin/wget（可用）
- Snap curl 有問題（sandbox 限制），不可用

## 編譯流程

### 1. 下載源碼

```bash
cd /tmp
/usr/bin/wget -q "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0.tar.xz" -O aria2.tar.xz
tar xf aria2.tar.xz
```

### 2. 配置（啟用 OpenSSL）

```bash
cd aria2-1.37.0
mkdir -p build && cd build
../configure --prefix=$HOME/.local --with-openssl --disable-bittorrent --disable-metalink --disable-tests
```

**確認 `OpenSSL: yes`**（必須有，否則 HTTPS 續傳失敗）

### 3. 編譯並安裝

```bash
make -j$(nproc)
make install
```

### 4. 複製到 ~/bin

```bash
mkdir -p ~/bin
cp ~/.local/bin/aria2c ~/bin/
```

## 驗證

```bash
~/.local/bin/aria2c --version
```

## 使用方式

```bash
# 16 線程 + 16 分割下載，斷點續傳
~/.local/bin/aria2c -x16 -s16 -c \
  "https://huggingface.co/xxx/resolve/main/model.safetensors" \
  -o model.safetensors

# 範例：Qwen Image diffusion model
cd ~/ComfyUI/models/diffusion_models
~/.local/bin/aria2c -x16 -s16 -c \
  "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors" \
  -o qwen_image_fp8_e4m3fn.safetensors
```

## 參數說明

| 參數 | 意義 |
|------|------|
| `-x16` | 每個檔案 16 個連線 |
| `-s16` | 16 個分割下載 |
| `-c` | 斷點續傳（resume） |
| `-o` | 輸出檔名 |

## 常見問題

**Q: aria2c 一直 403 或被阻擋？**  
A: HuggingFace 有同 IP 單一連線限制，`-x16` 足以加速但不要開太多。qwen_2.5_vl 等超大檔建議 `-x8 -s8` 避免觸發。

**Q: OpenSSL 沒找到？**  
A: 先確認 `pkg-config --list-all | grep ssl` 有輸出，再加 `--with-openssl`。
