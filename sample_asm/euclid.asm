// Program: Euclidean algorithm (division method)

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000010

// Code segment
0x0000000100000000:

    // Jump directly to the start of the main program
    PUSHIMM _main
    JMP

// Attach file content from lib
INCLUDE "std/gcd.iasm"

// Start of main program
_main:
    PUSHIMM 1081
    PUSHIMM 2231
    PUSHIMM 0
    // stack: [a, b, 0]

    // Recursively call gcd function
    PUSHIMM gcd
    CALL

    // After function returns
    // stack: [..., a, b, ans]
    HALT