// Program: Output hello world

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000010

// Code segment
0x0000000100000000:

    // Call function func_call
    PUSHIMM func_call
    CALL

    // Push an immediate value here
    // Prevent stack underflow
    PUSHIMM 0x0000000000000000
    HALT

func_call:

    // System call No.2, output string
    PUSHIMM 0x8
    POPAP
    PUSHIMM 0x2
    SAVE
    PUSHIMM 0x10
    POPAP
    PUSHIMM hello_world_str
    SAVE
    SYSCAL

    // Function return
    JMP

// Data segment
// Lines starting with a pound sign describe a byte of information
0x0000000200000000:
hello_world_str:
    #0x68 #0x65 #0x6c #0x6c #0x6f #0x20 #0x77 #0x6f 
    #0x72 #0x6c #0x64 #0x21 #0x0a #0x00 #0x00 #0x00

// Stack segment
0x0000000200000010: