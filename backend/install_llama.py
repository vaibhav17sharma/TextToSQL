#!/usr/bin/env python3
import subprocess
import sys
import os

def check_cuda_available():
    """Check if CUDA is available on the system"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        try:
            # Check nvidia-smi command
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

def install_llama_cpp():
    """Install appropriate version of llama-cpp-python"""
    if check_cuda_available():
        print("🚀 CUDA detected, installing GPU-accelerated llama-cpp-python...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python==0.2.20", 
                "--force-reinstall", 
                "--no-cache-dir",
                "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121"
            ])
            print("✅ GPU-accelerated llama-cpp-python installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️ GPU installation failed, falling back to CPU version...")
            install_cpu_version()
    else:
        print("💻 No CUDA detected, installing CPU-only llama-cpp-python...")
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