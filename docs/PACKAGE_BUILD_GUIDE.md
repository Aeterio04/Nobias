# NoBias Package Build and Publish Guide

## Package Information

- **Name**: nobias
- **Version**: 0.0.0
- **License**: MIT
- **Python**: >=3.8

## Package Structure

```
nobias/
├── library/                    # Source code (becomes nobias package)
│   ├── __init__.py
│   ├── py.typed               # PEP 561 type checking marker
│   ├── dataset_audit/         # Dataset auditing module
│   ├── model_audit/           # Model auditing module
│   └── agent_audit/           # Agent auditing module
├── setup.py                   # Package setup (legacy)
├── pyproject.toml            # Modern package configuration
├── MANIFEST.in               # File inclusion rules
├── README.md                 # Package description
└── LICENSE                   # MIT License
```

## Installation Options

### Core Package
```bash
pip install nobias
```
Includes: dataset_audit, model_audit (basic functionality)

### With Agent Audit
```bash
pip install nobias[agent]
```
Adds: groq, openai, anthropic, aiohttp

### With Reports
```bash
pip install nobias[reports]
```
Adds: reportlab, matplotlib

### Full Installation
```bash
pip install nobias[all]
```
Includes all optional dependencies

## Building the Package

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Clean Previous Builds

```bash
# Windows PowerShell
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Linux/Mac
rm -rf dist build *.egg-info
```

### 3. Build the Package

```bash
python -m build
```

This creates:
- `dist/nobias-0.0.0.tar.gz` (source distribution)
- `dist/nobias-0.0.0-py3-none-any.whl` (wheel distribution)

### 4. Verify the Build

```bash
# Check package contents
tar -tzf dist/nobias-0.0.0.tar.gz

# Or for wheel
unzip -l dist/nobias-0.0.0-py3-none-any.whl
```

## Publishing to PyPI

### 1. Create PyPI Account

- Production: https://pypi.org/account/register/
- Test: https://test.pypi.org/account/register/

### 2. Create API Token

1. Go to Account Settings
2. Scroll to API tokens
3. Click "Add API token"
4. Name: "nobias-upload"
5. Scope: "Entire account" or specific project
6. Copy the token (starts with `pypi-`)

### 3. Configure Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

### 4. Test Upload (Recommended)

```bash
python -m twine upload --repository testpypi dist/*
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ nobias
```

### 5. Production Upload

```bash
python -m twine upload dist/*
```

### 6. Verify Upload

Visit: https://pypi.org/project/nobias/

## Post-Publication

### Install and Test

```bash
# Create fresh environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install from PyPI
pip install nobias

# Test imports
python -c "from nobias import audit_dataset; print('✓ Dataset audit')"
python -c "from nobias.model_audit import audit_model; print('✓ Model audit')"
python -c "from nobias.agent_audit import audit_agent; print('✓ Agent audit')"
```

## File Exclusions

The following are automatically excluded from the package:

- `.env` files (via MANIFEST.in)
- `__pycache__` directories
- `.pyc`, `.pyo`, `.pyd` files
- Documentation `.md` files in library/ folder
- Test files
- Git files

## Version Updates

To release a new version:

1. Update version in:
   - `setup.py` (line 23)
   - `pyproject.toml` (line 6)
   - `library/__init__.py` (__version__)

2. Rebuild and republish:
```bash
rm -rf dist build *.egg-info
python -m build
python -m twine upload dist/*
```

## Troubleshooting

### Build Fails

```bash
# Check setup.py syntax
python setup.py check

# Verbose build
python -m build --verbose
```

### Upload Fails

```bash
# Check package with twine
python -m twine check dist/*

# Upload with verbose output
python -m twine upload --verbose dist/*
```

### Import Errors After Install

```bash
# Check installed files
pip show -f nobias

# Reinstall
pip uninstall nobias
pip install nobias --no-cache-dir
```

## Package Metadata

- **Homepage**: https://github.com/nobias/nobias
- **Documentation**: https://github.com/nobias/nobias/blob/main/docs
- **Bug Tracker**: https://github.com/nobias/nobias/issues
- **Keywords**: bias, fairness, machine-learning, ai, llm, audit, ethics

## Dependencies

### Core (Required)
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- scikit-learn >= 1.3.0
- python-dotenv >= 1.0.0

### Optional Extras
- **agent**: LLM API clients
- **reports**: PDF and visualization
- **embeddings**: Semantic similarity
- **langgraph**: LangGraph integration
- **server**: FastAPI server
- **all**: Everything

## Support

For issues with the package:
1. Check GitHub Issues: https://github.com/nobias/nobias/issues
2. Review documentation: docs/
3. Email: contact@nobias.dev
