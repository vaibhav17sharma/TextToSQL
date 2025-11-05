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
        print("🚀 CUDA detected, building with CUDA support...")
        try:
            # Set environment for CUDA build
            env = os.environ.copy()
            env['CMAKE_ARGS'] = '-DLLAMA_CUBLAS=ON'
            env['FORCE_CMAKE'] = '1'
            
            # Uninstall existing version first
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "llama-cpp-python", "-y"], 
                         capture_output=True)
            
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python==0.2.20", 
                "--force-reinstall", 
                "--no-cache-dir",
                "--no-binary=llama-cpp-python"  # Force compilation
            ], env=env)
            print("✅ CUDA-enabled llama-cpp-python built successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ CUDA build failed: {e}")
            print("Installing CPU version...")
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