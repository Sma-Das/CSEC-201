; ---------------------------------
; 32-bit implementation of Caeser's Cipher
; @author Sma Das
; ---------------------------------

section .data
    ; Basic constants for system calls
    SYS_EXIT equ 1
    SYS_READ equ 3
    SYS_WRITE equ 4

    EXIT_SUCCESS equ 0
    EXIT_FAIL equ 1

    ; File descriptors
    STDOUT equ 1
    STDIN equ 0

    ; Messages
    prmptIN db "Input : ", 0x0
    prmptINlen equ $ - prmptIN

    prmptERR db "Error", 0xA, 0x0
    prmptERRlen equ $ - prmptERR

    prmptOUT db "Output : ", 0x0
    prmptOUTlen equ $ - prmptOUT

    ; buffer size for input string
    BUFFER equ 256

    ; shift amount
    SHIFT equ 3
    ALPHABET equ 26

section .bss
    ; Reserve space for the string
    userIN resb BUFFER
    userINlen resb 4 ;reserve 4 bytes for the string length


section .text
    global _start:

; --------------------------
; str_length(char* string) -> int
; IN: ebx -> char* string
; OUT: eax -> int [length]
; --------------------------
str_length:
    ; preserve values
    push ebx 
    push ecx 
    ; set count to 0
    xor ecx, ecx

check_null:
    ; If null character, terminate loop
    cmp byte [ebx], 0
    jz return_length
    ; Increment loop
    inc ebx
    inc ecx
    jmp check_null

return_length:
    ; move return value into eax
    mov eax, ecx
    ; restore registers
    pop ecx
    pop ebx
    ret

; ----------------------------------------------------
; shift_sentence(char* string, int length)
; IN: ebx -> char* string | sentence you want to shift
; IN: ecx -> int length | length of the string
; ----------------------------------------------------
shift_sentence:
    ; preserve values
    push ebx
    push ecx
    dec ecx ; don't want to shift newline

shift:
    cmp ecx, 0
    jz exit_shift
    
    call is_valid ; check for valid letter
    add byte [ebx], SHIFT
    call shift_over ; check the new shift is in the valid ascii range

    inc ebx
    dec ecx
    jmp shift

exit_shift:
    pop ecx
    pop ebx
    ret

; ---------------------------
; is_valid(char letter)
; IN: ebx -> char letter
; TERMINATE ON INVALID LETTER
; ---------------------------
is_valid:
    cmp byte [ebx], 'A'
    jl quit_fail ; if letter < 'A'
    cmp byte [ebx], 'z'
    jg quit_fail ; elif letter > 'z'
    cmp byte [ebx], 'Z'
    jle valid ; if letter <= 'Z'
    cmp byte [ebx], 'a'
    jl quit_fail ; if letter < 'a'
valid:
    ret

; ----------------------
; shift_over
; IN: ebx -> char letter
; ----------------------
shift_over:
    cmp byte [ebx], 'Z'
    jle return_shift

    cmp byte [ebx], 'a'
    jl shift_down

    cmp byte [ebx], 'z'
    jg shift_down

    jmp return_shift
shift_down:
    sub byte [ebx], ALPHABET
return_shift:
    ret


_start:
    ; Prompt user for input
    mov edx, prmptINlen
    mov ecx, prmptIN
    mov ebx, STDOUT
    mov eax, SYS_WRITE
    int 0x80

    ; Read input
    mov ecx, userIN
    mov ebx, STDIN
    mov eax, SYS_READ
    int 0x80

    push eax ; save the length of the buffer
    mov ebx, userIN ; set ebx to the pointer of the string input
    call str_length
    mov [userINlen], eax ; store the length of the string

    ; shift letters
    mov ecx, [userINlen]
    mov ebx, userIN
    call shift_sentence

    ; Print output dialog
    mov edx, prmptOUTlen
    mov ecx, prmptOUT
    mov ebx, STDOUT
    mov eax, SYS_WRITE
    int 0x80

    ; print shifted sentence
    pop edx ; get the buffer length from eax earlier
    mov ecx, userIN
    mov ebx, STDOUT
    mov eax, SYS_WRITE
    int 0x80

quit_success:
    ; Quit with successful termination
    mov ebx, EXIT_SUCCESS
    jmp quit

quit_fail:
    ; Write error
    mov edx, prmptERRlen
    mov ecx, prmptERR
    mov ebx, STDOUT
    mov eax, SYS_WRITE
    int 0x80

    mov ebx, EXIT_FAIL
    jmp quit

quit:
    ; Exit program
    mov eax, SYS_EXIT
    int 0x80

