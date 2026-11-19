from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['cli/main.py'],
    pathex=[SPECPATH],
    datas=[
        ('text.yml', 'data'),
        *collect_data_files('sgx', includes=['generate.sh']),
    ],
)

pyz = PYZ(a.pure)

exe = EXE(pyz, a.scripts, a.binaries, a.datas, name='main')
