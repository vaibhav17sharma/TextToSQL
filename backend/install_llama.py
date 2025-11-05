#!/usr/bin/env python3
import subprocess
import sys
import os

def check_cuda_available():
    """Check if CUDA is available on the system"""
    # Check environment variables first
    if os.environ.get('NVIDIA_VISIBLE_DEVICES') == 'all':
        print("🌍 NVIDIA_VISIBLE_DEVICES=all detected")
        return True
    
    try:
        # Check nvidia-smi command
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ nvidia-smi available")
            return True
        else:
            print("❌ nvidia-smi failed")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ nvidia-smi not found or timeout")
        return False

def install_llama_cpp():
    """Install appropriate version of llama-cpp-python"""
    if check_cuda_available():
        print("🚀 CUDA detected, installing prebuilt GPU wheel...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python==0.2.20", 
                "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121",
                "--force-reinstall", 
                "--no-cache-dir"
            ])
            print("✅ GPU wheel installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️ GPU wheel failed, installing CPU version...")
            install_cpu_version()
    else:
        print("💻 No CUDA detected, installing CPU version...")
        install_cpu_version()

def install_cpu_version():
    """Install CPU-only version"""
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "llama-cpp-python==0.2.20", 
        "--force-reinstall", 
        "--no-cache-dir"
    ])
    print("✅ CPU-only llama-cpp-python installed successfully")

if __name__ == "__main__":
    install_llama_cpp()