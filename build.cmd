@echo off
pyinstaller --onefile --add-data "icon.png:." --windowed --icon=run.ico wtr.py