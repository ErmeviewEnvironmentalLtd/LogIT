# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Dist\\src\\logit\\LogIT.py'],
             #pathex=[
			#	'C:\\Users\\Duncan\\Documents\\Technical\\programing\\Logit\\LogIt\\Dist',
			#	'C:\\Users\\Duncan\\Documents\\Technical\\programing\\Logit\\LogIt\\Dist\\src\\logit',
			 #],
			 pathex=[
				'Dist',
				'Dist\\src\\logit',
			 ],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5'],
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
          name='LogIT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
		  #icon='C:\\Users\\Duncan\\Documents\\Technical\\programing\\Logit\\Gui\\images\\Logit_Logo__ICO.ico'
		  icon='icons\\Logit_Logo__ICO.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='LogIT')
