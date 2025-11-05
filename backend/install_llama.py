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
        print("🚀 CUDA detected, trying prebuilt CUDA wheel...")
        try:
            # Uninstall existing version first
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "llama-cpp-python", "-y"], 
                         capture_output=True)
            
            # Try CUDA 12.1 wheel first
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python==0.2.20", 
                "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121",
                "--force-reinstall", 
                "--no-cache-dir"
            ])
            print("✅ CUDA wheel installed successfully")
            
            # Verify CUDA support
            try:
                import llama_cpp
                print(f"🔍 llama-cpp version: {llama_cpp.__version__}")
            except Exception as e:
                print(f"⚠️ Could not verify llama-cpp: {e}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ CUDA wheel failed: {e}")
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
    
    # Verify installation
    try:
        import llama_cpp
        print(f"🔍 llama-cpp version: {llama_cpp.__version__}")
    except Exception as e:
        print(f"⚠️ Could not verify llama-cpp: {e}")

if __name__ == "__main__":
    install_llama_cpp()