// Program: Subroutine for outputting strings

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

// Output string
// Return the number of characters successfully output
puts:
    // stack: [str_pos, 0, ret_addr]

    // Copy pointer to system call parameter
    PUSHIMM 2
    DUP
    PUSHIMM 16
    POPAP
    SAVE

    // Initiate system call No.2
    // Output string
    PUSHIMM 8
    POPAP
    PUSHIMM 2
    SAVE
    SYSCAL

    // Get the number of characters successfully output
    PUSHIMM 8
    POPAP
    LOAD
    // stack: [str_pos, 0, ret_addr, char_cnt]

    PUSHIMM 1
    POPS
    // stack: [str_pos, char_cnt, ret_addr]
    // Function return
    JMP

// Start of main program
_main:

    // Generate local variable table
    PUSHIMM hello_world_str
    PUSHIMM 0
    // stack: [str_pos, 0]

    // Generate function call
    PUSHIMM puts
    CALL

    HALT

// Data segment
// Lines starting with a pound sign describe a byte of information
0x0000000200000000:
hello_world_str:
    #0x68 #0x65 #0x6c #0x6c #0x6f #0x20 #0x77 #0x6f 
    #0x72 #0x6c #0x64 #0x21 #0x0a #0x00 #0x00 #0x00

// Stack segment
0x0000000200000010: