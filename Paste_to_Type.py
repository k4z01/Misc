# Press F8 to start typing the text that is in the clipboard
# Press F9 to stop typing


import pyautogui
import time
import pyperclip
import keyboard
import threading

stop_typing = False  # Flag to signal typing stop

def type_text(text, chunk_size=20, interval=0.1):
    global stop_typing
    for i in range(0, len(text), chunk_size):
        if stop_typing:
            print("Typing stopped!")
            break
        chunk = text[i:i+chunk_size]
        pyautogui.write(chunk, interval=interval)


def monitor_keypress():
    global stop_typing
    keyboard.wait("F9")
    stop_typing = True

while True:
    keyboard.wait("F8")

    stop_typing = False
    content = pyperclip.paste()  # Get clipboard content

    # Start typing in a thread
    typing_thread = threading.Thread(target=type_text, args=(content,))
    typing_thread.start()

    # Start monitoring any key press in another thread
    monitor_thread = threading.Thread(target=monitor_keypress)
    monitor_thread.start()

    typing_thread.join()  # Wait for typing to finish or be stopped

