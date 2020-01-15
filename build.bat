pyinstaller Main.py -w --onefile
@RD /S /Q "__pycache__"
@RD /S /Q "build"
@RD /S /Q "Main.spec"
