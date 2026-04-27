"""
Run this to start the Nobias backend server.
Usage: python start.py
"""
import subprocess, sys, os

def check_library():
    try:
        import unbiased
        print("[OK] unbiased library found")
    except ImportError:
        print("[WARNING] unbiased library not found - using mock implementation")
        print("   To install the real library: pip install unbiased==0.0.0")

def check_dependencies():
    deps = ["fastapi", "uvicorn", "pandas", "numpy", "python_multipart", "openpyxl"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
            print(f"[OK] {dep}")
        except ImportError:
            print(f"[*] Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep.replace("_", "-")])
            print(f"[OK] {dep}")

def create_data_dir():
    os.makedirs("data", exist_ok=True)
    os.makedirs("samples", exist_ok=True)
    print("[OK] data/ and samples/ directories ready")

if __name__ == "__main__":
    print("Starting Nobias Backend...\n")
    check_dependencies()
    check_library()
    create_data_dir()
    print(f"\n[OK] All dependencies ready. Starting server on http://127.0.0.1:8000\n")
    
    # Use subprocess to avoid the "must pass as import string" reload warning
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])
