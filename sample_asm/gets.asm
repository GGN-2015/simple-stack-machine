// Program: Get a character from STDIN

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000020

// Code segment
0x0000000100000000:
    PUSHIMM _main
    JMP

// Attach file content from lib
INCLUDE "std/gets.iasm"
INCLUDE "std/puts.iasm"

_main:

    PUSHIMM my_input_str
    PUSHIMM 0x20
    PUSHIMM 0
    // stack: [my_input_str, max_len, ans_pos (0)]
    
    PUSHIMM gets
    CALL
    // stack: [my_input_str, max_len, chr_cnt]
    
    POP
    POP
    POP
    // stack: []

    PUSHIMM my_input_str
    PUSHIMM 0
    PUSHIMM puts
    CALL 
    // stack: [my_input_str, output_chr_cnt]

    HALT

// Data segment
0x0000000200000000:
my_input_str: