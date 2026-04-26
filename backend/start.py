import subprocess, sys, os

def check_library():
    try:
        import unbiased
        print("unbiased library found")
    except ImportError:
        print("Installing unbiased...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "unbiased==0.0.0"])

def check_dependencies():
    deps = ["fastapi", "uvicorn", "pandas", "python-multipart", "openpyxl"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def create_data_dir():
    os.makedirs("data", exist_ok=True)
    os.makedirs("samples", exist_ok=True)

if __name__ == "__main__":
    print("Starting Nobias Backend...")
    check_dependencies()
    check_library()
    create_data_dir()
    print("Starting server on http://127.0.0.1:8000")
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
