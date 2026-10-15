# Press F8 to start typing the text that is in the clipboard
# Press F9 to stop typing
#
# Uses keyboard.write() instead of pyautogui.write() for full Unicode support.

import platform
import subprocess
import threading
import time

import keyboard
import pyperclip

IS_WINDOWS = platform.system() == "Windows"

CHUNK_SIZE = 20       # characters per burst
CHAR_INTERVAL = 0.05  # seconds between characters
START_DELAY = 3.0     # seconds after F8 before typing begins (time to switch focus)

stop_typing = False
monitor_thread = None


def type_chunk(chunk: str) -> None:
    if IS_WINDOWS:
        for ch in chunk:
            keyboard.write(ch)
            time.sleep(CHAR_INTERVAL)
    else:
        delay_ms = int(CHAR_INTERVAL * 1000)
        subprocess.run(
            ["xdotool", "type", "--clearmodifiers", f"--delay={delay_ms}", "--", chunk],
            check=False,
        )


def type_text(text: str) -> None:
    global stop_typing
    lines = text.split("\n")
    for line_idx, line in enumerate(lines):
        for i in range(0, max(len(line), 1), CHUNK_SIZE):
            if stop_typing:
                print("[*] Typing stopped.")
                return
            chunk = line[i : i + CHUNK_SIZE]
            if chunk:
                type_chunk(chunk)
        if stop_typing:
            print("[*] Typing stopped.")
            return
        if line_idx < len(lines) - 1:
            if IS_WINDOWS:
                keyboard.press_and_release("enter")
                time.sleep(CHAR_INTERVAL)
            else:
                subprocess.run(["xdotool", "key", "Return"], check=False)
    print("[*] Typing complete.")


def monitor_stop_key() -> None:
    global stop_typing
    keyboard.wait("F9")
    stop_typing = True


def on_f8() -> None:
    global stop_typing, monitor_thread

    # Reset state
    stop_typing = False

    content = pyperclip.paste()
    if not content:
        print("[!] Clipboard is empty.")
        return

    print(f"[*] Starting in {START_DELAY}s � switch to target window now...")
    time.sleep(START_DELAY)

    # Start F9 monitor only if not already running
    if monitor_thread is None or not monitor_thread.is_alive():
        monitor_thread = threading.Thread(target=monitor_stop_key, daemon=True)
        monitor_thread.start()

    typing_thread = threading.Thread(target=type_text, args=(content,), daemon=True)
    typing_thread.start()


print("[*] Clipboard typer ready.  F8 = start  |  F9 = stop  |  Ctrl+C = quit")
keyboard.add_hotkey("F8", on_f8)
keyboard.wait()  # block until Ctrl+C or process termination
