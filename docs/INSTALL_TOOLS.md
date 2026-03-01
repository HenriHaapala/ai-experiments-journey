# External Tools Installation Guide

This document provides instructions for installing external security and linting tools required for pre-commit hooks.

## ✅ Already Installed

- **Ruff** (Python linting/formatting) - Installed via pip
- **Semgrep** (SAST scanning) - Installed via pip
- **Biome** (Frontend linting) - Installed via npm

## ⏸️ Optional: Gitleaks (Secrets Detection)

Gitleaks is currently configured in the pre-commit hooks but requires manual installation with admin privileges.

### Installation Options

#### Option 1: Chocolatey (Requires Admin)
```powershell
# Run PowerShell as Administrator
choco install gitleaks -y
```

#### Option 2: Scoop (No Admin Required)
```powershell
scoop bucket add extras
scoop install gitleaks
```

#### Option 3: Manual Download
1. Download from: https://github.com/gitleaks/gitleaks/releases/latest
2. Download `gitleaks_X.X.X_windows_x64.zip`
3. Extract to a folder (e.g., `C:\tools\gitleaks`)
4. Add to PATH environment variable

### Verification

```bash
# Check if Gitleaks is installed
gitleaks version
```

## Current Status

**Pre-commit hooks will work without Gitleaks**, but the secrets detection step will be skipped. To enable full security scanning:

1. Install Gitleaks using one of the methods above
2. The pre-commit hook will automatically detect it and start scanning for secrets

## Tool Locations

- **Ruff**: `%APPDATA%\Roaming\Python\Python314\Scripts\ruff.exe`
- **Semgrep**: `%APPDATA%\Roaming\Python\Python314\Scripts\semgrep.exe`
- **Biome**: `node_modules/.bin/biome.exe` (local to project)
- **Lefthook**: `node_modules/.bin/lefthook.exe` (local to project)

## Troubleshooting

### Scripts Not in PATH

If you see warnings like "The script X.exe is installed in '...\Scripts' which is not on PATH":

**Option 1: Add to PATH (Recommended)**
```powershell
# Add this directory to your PATH:
C:\Users\YOUR_USERNAME\AppData\Roaming\Python\Python314\Scripts
```

**Option 2: Use `python -m` prefix**
```bash
python -m ruff check .
# Note: semgrep deprecated python -m usage, use direct command
```

### Pre-Commit Hooks Not Running

```bash
# Reinstall hooks
npm run hooks:install

# Check hook status
lefthook run pre-commit --verbose
```

### Permission Errors

If Chocolatey installation fails:
- Run PowerShell/Command Prompt as Administrator
- Or use Scoop (no admin required)
- Or download binaries manually

## Next Steps

After installing tools, test the pre-commit hooks:

```bash
# Make a small change
echo "# Test" >> README.md

# Stage and commit (hooks will run automatically)
git add README.md
git commit -m "Test pre-commit hooks"
```

You should see output from:
1. Secrets check (if Gitleaks installed)
2. Biome (frontend linting)
3. Ruff (Python linting/formatting)

---

For more details, see:
- [TESTING_SETUP.md](TESTING_SETUP.md) - Testing infrastructure documentation
- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Security tools documentation
