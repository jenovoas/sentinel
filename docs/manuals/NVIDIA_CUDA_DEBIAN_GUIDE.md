# 🎮 NVIDIA DRIVER & CUDA GUIDE (Debian 13 Trixie)

**Objective**: Enable GPU Acceleration for Ollama (AI) and Sentinel Core.
**Target Hardware**: NVIDIA GPU (3GB VRAM).
**OS**: Debian 13 (Testing/Trixie).

> [!IMPORTANT]
> This process interacts with the kernel. **Follow specifically.**
> Incorrect driver installation can lead to a black screen.

---

## 1. Preparation
Ensure `contrib` and `non-free` repositories are enabled.

```bash
# Check sources.list
cat /etc/apt/sources.list
# Should look like:
# deb http://deb.debian.org/debian trixie main contrib non-free-firmware non-free
```

If missing, add them and run:
```bash
sudo apt update
sudo apt install linux-headers-$(uname -r) build-essential
```

## 2. Driver Installation (The Debian Way)
Do **NOT** use the `.run` file from Nvidia's website. Use the Debian packages to stay stable.

```bash
# Install Driver and CUDA libraries
sudo apt install nvidia-driver nvidia-cuda-toolkit
```

## 3. Verification
After installation, **REBOOT**.
Then run:
```bash
nvidia-smi
```
- **Success**: You see a table with GPU Name, VRAM usage, and Driver Version.
- **Fail**: "Command not found" or "Communicating with driver failed".

## 4. CUDA Verification for Ollama
Ollama needs the libraries to be discoverable.
```bash
# Check if libraries exist
ls -l /usr/lib/x86_64-linux-gnu/libcuda*
```

---

## 5. Troubleshooting (Black Screen)
If you reboot and get a black screen:
1.  Press `Ctrl + Alt + F2` to get a terminal.
2.  Login.
3.  Purge the drivers:
    ```bash
    sudo apt purge nvidia-*
    sudo apt autoremove
    sudo reboot
    ```
This will restore the Nouveau (Generic) driver.
