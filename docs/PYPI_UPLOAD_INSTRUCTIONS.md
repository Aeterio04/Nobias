# PyPI Upload Instructions for nobias 0.0.0

## Package Built Successfully ✅

The package has been built and validated:
- `dist/nobias-0.0.0.tar.gz` (source distribution)
- `dist/nobias-0.0.0-py3-none-any.whl` (wheel distribution)

Both files passed twine validation checks.

## Upload to PyPI

### Option 1: Upload to Test PyPI (Recommended First)

Test your package on Test PyPI before uploading to production:

```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your Test PyPI API token (starts with `pypi-`)

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ nobias
```

### Option 2: Upload to Production PyPI

Once you've tested on Test PyPI, upload to production:

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## Getting API Tokens

### For Test PyPI:
1. Go to https://test.pypi.org/account/register/
2. Verify your email
3. Go to Account Settings → API tokens
4. Click "Add API token"
5. Name: "nobias-upload"
6. Scope: "Entire account" (or specific to nobias project)
7. Copy the token (you'll only see it once!)

### For Production PyPI:
1. Go to https://pypi.org/account/register/
2. Verify your email
3. Go to Account Settings → API tokens
4. Click "Add API token"
5. Name: "nobias-upload"
6. Scope: "Entire account" (or specific to nobias project)
7. Copy the token (you'll only see it once!)

## Alternative: Using .pypirc File

Create `~/.pypirc` (or `%USERPROFILE%\.pypirc` on Windows):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

Then upload without being prompted:
```bash
# Test PyPI
python -m twine upload --repository testpypi dist/*

# Production PyPI
python -m twine upload dist/*
```

## After Upload

### Verify on PyPI
- Test PyPI: https://test.pypi.org/project/nobias/
- Production PyPI: https://pypi.org/project/nobias/

### Test Installation

```bash
# Create fresh environment
python -m venv test_nobias
test_nobias\Scripts\activate  # Windows
# or: source test_nobias/bin/activate  # Linux/Mac

# Install from PyPI
pip install nobias

# Test imports
python -c "from nobias import audit_dataset; print('✓ Dataset audit works')"
python -c "from nobias.model_audit import audit_model; print('✓ Model audit works')"
python -c "from nobias.agent_audit import audit_agent; print('✓ Agent audit works')"
```

### Install with extras

```bash
# With agent support
pip install nobias[agent]

# With all features
pip install nobias[all]
```

## Package Contents

The package includes:
- ✅ All three audit modules (dataset, model, agent)
- ✅ All Python source files
- ✅ names.json data file for persona generation
- ✅ README.md and LICENSE
- ❌ No .env files (excluded)
- ❌ No .md documentation from library/ (excluded)
- ❌ No test files (excluded)
- ❌ No __pycache__ (excluded)

## Troubleshooting

### Upload fails with 403 error
- Check your API token is correct
- Ensure token has proper scope
- For first upload, token must have "Entire account" scope

### Package already exists
- You cannot re-upload the same version
- Increment version number in setup.py, pyproject.toml, and library/__init__.py
- Rebuild: `python -m build`
- Upload new version

### Import errors after install
- Check installed files: `pip show -f nobias`
- Try reinstalling: `pip uninstall nobias && pip install nobias --no-cache-dir`

## Next Steps

After successful upload:
1. Update GitHub repository with release tag
2. Create GitHub release with changelog
3. Update documentation with installation instructions
4. Announce on relevant channels

## Version 0.0.0 Notes

This is the initial alpha release. Future versions should:
- Increment to 0.0.1, 0.0.2, etc. for bug fixes
- Increment to 0.1.0 for new features
- Increment to 1.0.0 for stable production release
