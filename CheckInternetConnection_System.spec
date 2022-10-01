# -*- mode: python -*-

block_cipher = None

a = Analysis(['dlgMain.py'],
             pathex=['/home/alexander/Projects/Python/Virtualenvironments/poetry_venvs/py3.10.6_forTests_MostBloated/.venv/lib/python3.10/site-packages/PyQt5', '/home/alexander/Projects/Python/CheckInternetConnection'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CheckInternetConnection',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , version='version.txt' , icon='CheckInternetConnection.ico' )
