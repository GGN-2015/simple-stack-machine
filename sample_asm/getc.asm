// Program: Get a character from STDIN

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000010

// Code segment
0x0000000100000000:

    PUSHIMM _main
    JMP

// Attach file content from lib
INCLUDE "std/getc.iasm"

_main:

    PUSHIMM 0
    // stack: [0]

    // Call the getc function
    PUSHIMM getc
    CALL

    // After the function returns, the stack space is
    // stack: [chr_val]
    HALT