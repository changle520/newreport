# -*- mode: python -*-
import sys
import os.path as osp
sys.setrecursionlimit(5000)

SETUP_DIR='C:\\Users\\ipharmacare\\newreport\\'

block_cipher = None


a = Analysis(['main.py',
'C:\\Users\\ipharmacare\\newreport\\check\\checkItems.py',
'C:\\Users\\ipharmacare\\newreport\\common\\calcDDD.py',
'C:\\Users\\ipharmacare\\newreport\\common\\configReader.py',
'C:\\Users\\ipharmacare\\newreport\\common\\connectDB.py',
'C:\\Users\\ipharmacare\\newreport\\common\\convert_unit.py',
'C:\\Users\\ipharmacare\\newreport\\common\\getReportContent.py',
'C:\\Users\\ipharmacare\\newreport\\common\\log.py',
'C:\\Users\\ipharmacare\\newreport\\common\\saveTestResult.py'],
pathex=['C:\\Users\\ipharmacare\\newreport'],
binaries=[],
datas=[(SETUP_DIR+'config','config\\'),(SETUP_DIR+'log','log\\'),(SETUP_DIR+'result','result\\')],
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
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
