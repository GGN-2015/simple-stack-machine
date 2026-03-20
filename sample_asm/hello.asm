// 程序：输出 hello world



// 描述 PC 的初始值
0x0000000000000008:
    0x0000000100000000



// 描述 SP 的初始值
0x0000000000000010:
    0x0000000200000010



// 代码段
0x0000000100000000:

    // 2 号系统调用，输出字符串
    PUSHIMM 0x8
    POPAP
    PUSHIMM 0x2
    SAVE
    PUSHIMM 0x10
    POPAP
    PUSHIMM hello_world_str
    SAVE
    SYSCAL
    PUSHIMM 0x0000000000000000
    HALT



// 数据段
0x0000000200000000:
hello_world_str:
    #0x68 #0x65 #0x6c #0x6c #0x6f #0x20 
    #0x77 #0x6f #0x72 #0x6c #0x64 #0x21 #0x0a #0x00



// 堆栈段
0x0000000200000010:
