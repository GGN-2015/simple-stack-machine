// Program: Output a specified character

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

INCLUDE "std/putc.iasm"

_main:

    // Push character A onto the stack
    PUSHIMM 0x4241
    PUSHIMM 0 // Function return value
    // stack: [0x4241, 0]
    PUSHIMM putc
    CALL
    // stack: [65, 1]

    PUSHIMM 10
    PUSHIMM 0 // Function return value
    // stack: [65, 1, 10, 0]
    PUSHIMM putc
    CALL
    // stack: [65, 1, 10, 1]

    POP
    POP
    // stack: [65, 1]

    HALT
