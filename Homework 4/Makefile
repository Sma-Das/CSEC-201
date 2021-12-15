all: caeser_decrypt caeser_encrypt

caeser_decrypt: cdecrypt.o
	ld -m elf_i386 -o caeser_decrypt cdecrypt.o
cdecrypt.o: cdecrypt.asm
	nasm -f elf32 cdecrypt.asm

caeser_encrypt: cencrypt.o
	ld -m elf_i386 -o caeser_encrypt cencrypt.o
cencrypt.o: cencrypt.asm
	nasm -f elf32 cencrypt.asm
