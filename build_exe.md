# Building TaSched as Windows Executable

This document explains how to package TaSched as a standalone Windows executable (.exe) using PyInstaller.

## Prerequisites

1. Python 3.13 installed
2. All dependencies installed (see requirements.txt)
3. PyInstaller installed

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build the Executable

Run the following command from the project root directory:

```bash
pyinstaller --name="TaSched" ^
    --onefile ^
    --noconsole ^
    --icon="tasched/assets/images/WAEC_Icon.ico" ^
    --add-data="tasched/assets;tasched/assets" ^
    app.py
```

**Command Breakdown:**

- `--name="TaSched"`: Sets the executable name to TaSched.exe
- `--onefile`: Packages everything into a single .exe file
- `--noconsole`: Runs without showing a console window (GUI mode)
- `--icon`: Sets the application icon
- `--add-data`: Includes asset files (images, sounds)
- `app.py`: The main entry point

### 3. Alternative: Using a Spec File

For more advanced builds, you can create a `.spec` file:

```python
# TaSched.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('tasched/assets', 'tasched/assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TaSched',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='tasched/assets/images/WAEC_Icon.ico',
    version='version_info.txt'  # Optional: Add version metadata
)
```

Then build with:

```bash
pyinstaller TaSched.spec
```

## Build Output

After building, you'll find:

- `dist/TaSched.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `TaSched.spec` - Build specification file

## Testing the Executable

1. Navigate to the `dist` folder
2. Run `TaSched.exe`
3. The application should start without requiring Python to be installed

## Distribution

To distribute TaSched:

1. Copy `TaSched.exe` from the `dist` folder
2. The executable is self-contained and can run on any Windows machine
3. No Python installation required on target machines

## Troubleshooting

### Missing DLL Errors

If you encounter missing DLL errors:

```bash
pyinstaller --onefile --noconsole --collect-all pygame app.py
```

### Asset Files Not Found

Ensure the `--add-data` parameter correctly includes all asset directories:

```bash
--add-data="tasched/assets/images;tasched/assets/images" ^
--add-data="tasched/assets/sounds;tasched/assets/sounds"
```

### Large File Size

To reduce executable size:

1. Use UPX compression (already enabled with `upx=True`)
2. Exclude unnecessary modules:

```bash
pyinstaller --exclude-module matplotlib --exclude-module numpy ...
```

## Creating an MSI Installer (Future)

For professional distribution, create an MSI installer using:

- **WiX Toolset**: https://wixtoolset.org/
- **Advanced Installer**: https://www.advancedinstaller.com/
- **Inno Setup**: https://jrsoftware.org/isinfo.php

## Version Information (Optional)

Create `version_info.txt` for Windows version metadata:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'WAEC'),
        StringStruct(u'FileDescription', u'TaSched - Task Scheduler & Countdown Orchestrator'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'TaSched'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 WAEC'),
        StringStruct(u'OriginalFilename', u'TaSched.exe'),
        StringStruct(u'ProductName', u'TaSched'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

## Notes

- The first run may take longer as PyInstaller extracts files
- Antivirus software may flag the executable (false positive)
- Test on a clean Windows machine before distribution
- Keep the original Python source code for updates

## Build Script (Optional)

Create `build.bat` for easy building:

```batch
@echo off
echo Building TaSched...
pyinstaller --name="TaSched" --onefile --noconsole --icon="tasched/assets/images/WAEC_Icon.ico" --add-data="tasched/assets;tasched/assets" app.py
echo Build complete! Executable in dist\TaSched.exe
pause
```
