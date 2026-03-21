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

// Read a character
getc:
    // stack: [0, ret_addr]

    PUSHIMM 8 // Address 8 is used to store the system call type
    POPAP
    PUSHIMM 1 // System call number 1 means reading a character from standard input
    SAVE
    SYSCAL

    // After the system call is executed, the ASCII code of the character 
    // will be stored in the 64-bit variable at address 8
    PUSHIMM 8
    POPAP
    LOAD // Put this value onto the stack
    // stack: [0, ret_addr, chr_val]

    PUSHIMM 1
    POPS
    // stack: [chr_val, ret_addr]

    // Function return
    JMP

_main:

    PUSHIMM 0
    // stack: [0]

    // Call the getc function
    PUSHIMM getc
    CALL

    // After the function returns, the stack space is
    // stack: [chr_val]
    HALT