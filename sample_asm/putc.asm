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

putc:
    // stack: [chr_val, 0, ret_addr]

    PUSHIMM 2
    DUP
    // stack: [chr_val, 0, ret_addr, chr_val]

    PUSHIMM 0
    // stack: [chr_val, 0, ret_addr, chr_val, 0]

    // Get a pointer to the string
    PUSHSP
    // stack: [chr_val, 0, ret_addr, chr_val, 0, sp_val]
    PUSHIMM 16
    SUB
    // stack: [chr_val, 0, ret_addr, chr_val, 0, str_ptr]

    // Copy pointer to system call parameter
    // The initial position of the string
    PUSHIMM 16
    POPAP
    SAVE
    // stack: [chr_val, 0, ret_addr, chr_val, 0]

    // Initiate system call No.2
    // Output string
    PUSHIMM 8
    POPAP
    PUSHIMM 2
    SAVE
    SYSCAL

    // Get the number of characters successfully output
    // 0 or 1
    PUSHIMM 8
    POPAP
    LOAD
    // stack: [chr_val, 0, ret_addr, chr_val, 0, char_cnt]

    PUSHIMM 3
    POPS
    // stack: [chr_val, char_cnt, ret_addr, chr_val, 0]

    POP
    POP
    // stack: [chr_val, char_cnt, ret_addr]

    // Function return
    JMP

_main:

    // Push character A onto the stack
    PUSHIMM 65
    PUSHIMM 0 // Function return value
    // stack: [65, 0]

    PUSHIMM putc
    CALL
    // stack: [65, 1]

    HALT