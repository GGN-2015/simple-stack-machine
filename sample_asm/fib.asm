// Program: Calculate Fibonacci sequence

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000010

// Code segment
0x0000000100000000:

    // Calculate the nth Fibonacci number
    PUSHIMM 10
    // stack: [n]

    PUSHIMM 0
    // stack: [n, a]

    PUSHIMM 1
    // stack: [n, a, b]

loop_begin:

    EXCH
    // stack: [n, b, a]

    PUSHIMM 1
    DUP
    // stack: [n, b, a, b]

    ADD
    // stack: [n, b, a + b]

    PUSHIMM 2
    DUP
    PUSHIMM 1
    SUB
    // stack: [n, b, a + b, n - 1]

    PUSHIMM 2
    POPS
    // stack: [n - 1, b, a + b]

    PUSHIMM 2
    DUP
    PUSHIMM 0
    EQU
    NOT
    // stack: [n - 1, b, a + b, n - 1 != 0]

    PUSHIMM loop_begin
    BR
    // stack: [0, a, b]

    POP
    // stack: [0, a]

    HALT