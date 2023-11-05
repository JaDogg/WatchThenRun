import argparse
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from typing import Optional

import pystray
from PIL import Image
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SHOULD_KEEP_RUNNING = True
ICON: Optional[pystray.Icon] = None

if getattr(sys, 'frozen', False):
    EXE_PATH = sys._MEIPASS
else:
    EXE_PATH = os.path.dirname(__file__)

ICON_PATH = os.path.join(EXE_PATH, 'icon.png')


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_modified(self, event):
        if event.is_directory:
            return
        self.execute_command()

    def execute_command(self):
        subprocess.Popen(self.command, shell=True)


def expand_path(path: str, file_path: str = None) -> str:
    if file_path:
        path = path.replace("@FILE", file_path)
    user_expanded = os.path.expanduser(path)
    env_expanded = os.path.expandvars(user_expanded)
    return os.path.abspath(env_expanded)


def terminate():
    global SHOULD_KEEP_RUNNING, ICON
    SHOULD_KEEP_RUNNING = False
    ICON.stop()


class FileWatcher:
    def __init__(self, file_path, command, sleep_time=0.3):
        self.file_path = expand_path(file_path)
        self.command = expand_path(command, file_path=self.file_path)
        self.sleep_time = sleep_time

    def run(self):
        event_handler = FileChangeHandler(self.command)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.file_path), recursive=False)
        observer.start()

        menu = (pystray.MenuItem("Exit", terminate),)
        icon_image = Image.open(ICON_PATH)
        global ICON
        ICON = pystray.Icon("file_watcher", icon_image, "File Watcher", menu)

        try:
            ICON.run()
            while SHOULD_KEEP_RUNNING:
                time.sleep(self.sleep_time)
        except KeyboardInterrupt:
            pass
        ICON.stop()
        observer.stop()
        observer.join()
        sys.exit(0)


def select_file_and_command():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select File to Watch")
    command = simpledialog.askstring("Command", "Enter Command to Execute", initialvalue="notepad @FILE")
    return file_path, command


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", nargs="?", help="Path of the file to watch")
    parser.add_argument("command", nargs="?", help="Command to execute on file change")
    args = parser.parse_args()

    if not args.file_path or not args.command:
        args.file_path, args.command = select_file_and_command()

    file_watcher = FileWatcher(args.file_path, args.command)
    file_watcher.run()


if __name__ == "__main__":
    main()
