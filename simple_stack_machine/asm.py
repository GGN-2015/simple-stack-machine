from typing import Optional
import sys

try:
    from .ins_code import INSTURCTION_MAP, VAL_RANGE, DEASM_INSTURCTION_MAP
except:
    from ins_code import INSTURCTION_MAP, VAL_RANGE, DEASM_INSTURCTION_MAP

class ProgramFile:
    def __init__(self) -> None:
        self._clear()

    def _clear(self):
        self.initial_memory = {}
        self.memory = {}
        self.pc = 0
        self.sp = 0
        self.init_sp = 0 # 初始 sp
        self.ap = 0
        self.finish = False
        self.debug = False

    def _chk_nxt_pos(self, position_now:int, line_id:int):
        if position_now >= VAL_RANGE:
            raise ValueError(f"{line_id}: position_now out of bound.")

    def check_pos(self, position_now:int):
        if self.initial_memory.get(position_now) is not None:
            raise ValueError(f"{position_now} refilled.")
    
    # 获取内存中的整数
    def _get_integer(self, pos:int, siz:int=8) -> int:
        data_list = []
        for i in range(siz):
            data_list.append(self.memory.get((pos + i) % VAL_RANGE, 0)  % 256)
        data_val = 0
        for i in range(siz - 1, -1, -1):
            data_val = ((data_val << 8) | data_list[i])
        return data_val
    
    # 赋值到内存中
    def _set_integer(self, val:int, pos:int, siz:int=8) -> None:
        data_list = []
        for i in range(siz):
            data_list.append((val >> (8 * i)) & 255)
        for i in range(siz):
            self.memory[pos + i] = data_list[i]

    # 从 self.initial_memory 拷贝到 self.memory
    def _load_memory(self):
        self.memory = {}
        for item in self.initial_memory:
            self.memory[item] = self.initial_memory[item]

    # 系统调用
    def _syscal(self):
        data_1 = self._get_integer(8)
        data_2 = self._get_integer(16)
        data_3 = self._get_integer(24)
        data_4 = self._get_integer(32)
        data_5 = self._get_integer(40)
        data_6 = self._get_integer(48)
        data_7 = self._get_integer(56)

        if data_1 == 1: # 输入一个字符
            try:
                chr_val = ord(sys.stdin.read(1)) % 256
            except:
                chr_val = 255
            self._set_integer(chr_val, 8)

        elif data_1 == 2: # 输出一个字符串
            pos_now = data_2
            while True:
                if self.memory.get(pos_now, 0) == 0:
                    break
                print(chr(self.memory[pos_now]), end="")
                pos_now += 1

        elif data_1 == 3: # 打开调试模式
            self.debug = (data_2 != 0)

        # 未知的系统调用编号
        else:
            raise ValueError(f"syscal {data_1} unknow.")

        # 系统调用结束的时候
        # 把初始位置清零
        self._set_integer(0, 0)

    # 输出调试信息
    def _debug_show(self, cmd:str):
        print(f"0x{self.pc:016x}: ", end="")

        # 输出当前命令
        if cmd == "PUSHIMM":
            print(f"PUSHIMM 0x{self._get_integer(self.pc + 1):016x}")
        else:
            print(cmd)

        # 输出栈空间
        print(f"stack (0x{self.init_sp:016x} .. 0x{self.sp:016x}):")
        for i in range(self.init_sp, self.sp, 8):
            print(f"    0x{self._get_integer(i):016x}")

    # 运行程序
    def run(self, debug_mode:bool=False) -> int:
        self.debug = debug_mode

        if self.finish is True:
            raise ValueError("you can not run program twice.")
        self._load_memory()
        self.finish = True
        self.pc = self._get_integer(8) # 初始化 pc
        self.sp = self._get_integer(16) # 初始化 sp
        self.init_sp = self.sp
        self.ap = 0

        while True:
            
            cmd_val = self.memory[self.pc]
            if DEASM_INSTURCTION_MAP.get(cmd_val) is None:
                raise ValueError(f"{cmd_val} is not a command.")
            
            # 找到对应的命令名称
            cmd = DEASM_INSTURCTION_MAP[cmd_val]

            # 输出调试信息
            if self.debug:
                self._debug_show(cmd)
                input("(enter to continue)\n")

            if cmd == "NOP":
                self.pc += 1

            elif cmd == "HALT":
                self.sp -= 8
                ans = self._get_integer(self.sp)
                if self.debug:
                    print(f"program end with result 0x{ans:016x}")
                return ans
            
            elif cmd == "POP":
                self.sp -= 8
                self.pc += 1

            elif cmd == "POPAP":
                self.sp -= 8
                self.ap = self._get_integer(self.sp)
                self.pc += 1

            elif cmd == "PUSHIMM":
                for i in range(8):
                    self.memory[self.sp + i] = (
                        self.memory[self.pc + 1 + i]
                    )
                self.sp += 8
                self.pc += 9

            elif cmd == "POPSP":
                self.sp -= 8
                self.sp = self._get_integer(self.sp)
                self.pc += 1

            elif cmd == "PUSHSP":
                self._set_integer(self.sp, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "PUSHPC":
                self._set_integer(self.pc, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "RET":
                self.sp -= 8
                self.pc = self._get_integer(self.sp)

            elif cmd == "LOAD":
                for i in range(8):
                    self.memory[self.sp + i] = (
                        self.memory[self.ap + i]
                    )
                self.sp += 8
                self.pc += 1

            elif cmd == "SAVE":
                self.sp -= 8
                for i in range(8):
                    self.memory[self.ap + i] = (
                        self.memory[self.sp + i]
                    )
                self.pc += 1

            elif cmd == "SYSCAL":
                self._set_integer(1, 0)
                self._syscal()
                self.pc += 1

            elif cmd == "ADD":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 + val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "SUB":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 - val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "MUL":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 * val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "DIV":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 // val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "MOD":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 % val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "NEG":
                self.sp -= 8
                val = self._get_integer(self.sp)
                ans = (~val) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "NOT":
                self.sp -= 8
                val = self._get_integer(self.sp)
                ans = (not val) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "AND":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 & val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "OR":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 & val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "XOR":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 & val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "RSH":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = ((val_1 % VAL_RANGE) >> val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "LSH":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 << val_2) % VAL_RANGE
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "JMP":
                self.sp -= 8
                self.pc = self._get_integer(self.sp)

            elif cmd == "BR":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                if val_1 != 0:
                    self.pc = val_2 - 1
                self.pc += 1

            elif cmd == "LEQ":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 <= val_2)
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "LT":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 < val_2)
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "EQU":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (val_1 == val_2)
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "DUP":
                self.sp -= 8
                offset = self._get_integer(self.sp)
                for i in range(8):
                    val_now = self.memory.get(
                            (self.sp - (8 * offset) - 8 + i) % VAL_RANGE, 0)
                    self.memory[self.sp + i] = (
                        val_now
                    )
                self.sp += 8
                self.pc += 1

            elif cmd == "POPS":
                self.sp -= 8
                val_pos = self.sp
                self.sp -= 8
                offset = self._get_integer(self.sp)
                for i in range(8):
                    self.memory[self.sp - 8 * offset - 8 + i] = (
                        self.memory[val_pos + i])
                self.pc += 1

            elif cmd == "EXCH":
                for i in range(8):
                    t = self.memory[self.sp - 16 + i]
                    self.memory[self.sp - 16 + i] = self.memory[self.sp -8 + i]
                    self.memory[self.sp - 8 + i] = t

            else:
                raise ValueError(f"{cmd} is not a valid command.")



    def read_program(self, filepath:str):
        position_now = 0
        segment_begin_now = 0

        late_insert:dict[tuple[int, int], str] = {} # 记录延迟插入位置
        token_value:dict[str, int] = {} # 记录标识符的值

        for line_id, line in enumerate(list(open(filepath, "r"))):
            # 去除注释
            line = line.strip()
            line = line.split("//", maxsplit=1)[0].strip()
            if line == "":
                continue
            
            # 处理四种东西
            #   位置调整符号
            #   指令
            #   64bit 数据
            #   跳转标识符
            for part in line.split():
                
                # 识别到字符型立即数
                if part.startswith("#"):
                    val = eval(part[1:])
                    self.check_pos(position_now)
                    self.initial_memory[position_now] = val % 256
                    position_now += 1
                    self._chk_nxt_pos(position_now, line_id)

                # 识别到指令
                elif INSTURCTION_MAP.get(part) is not None:
                    self.check_pos(position_now)
                    self.initial_memory[position_now] = (
                        INSTURCTION_MAP[part]
                    )
                    position_now += 1
                    self._chk_nxt_pos(position_now, line_id)

                # 识别到冒号
                # 分别考虑跳转标识符和位置调整符
                elif part.endswith(":"):

                    if len(part) == 1:
                        raise ValueError(f"{line_id}: colon detected.")
                    
                    # 得到了一个位置调整符
                    if part[0].isdigit():
                        data_val = eval(part[:-1])

                        # 保证当前段长度是八的整数倍
                        while (position_now - segment_begin_now) % 8 != 0:
                            self.check_pos(position_now)
                            self.initial_memory[position_now] = 0
                            position_now += 1

                        position_now = int(data_val)
                        segment_begin_now = position_now
                        self._chk_nxt_pos(position_now, line_id)

                    # 得到了一个跳转标识符
                    else:
                        jmp_label = part[:-1]
                        token_value[jmp_label] = position_now

                else:
                    # 理解成 64bit 数据
                    if part[0].isdigit():
                        data_val = eval(part)
                        for i in range(8):
                            chr_now = (data_val >> (i * 8)) & ((1 << 8) - 1)
                            self.check_pos(position_now)
                            self.initial_memory[position_now] = chr_now
                            position_now += 1
                            self._chk_nxt_pos(position_now, line_id)

                    # 理解成一个标识符使用
                    # 标识符需要在全局扫描结束后赋值
                    else:
                        late_insert[(position_now, line_id)] = part
                        position_now += 8
                        self._chk_nxt_pos(position_now, line_id)

        # 为标识符填写值
        for pos, line_id in late_insert:
            token = late_insert[(pos, line_id)]
            if token_value.get(token) is None:
                raise ValueError(f"{line_id}: token {token} undefined.")
            data_val = token_value[token]
            pos_now = pos
            for i in range(8):
                chr_now = (data_val >> (i * 8)) & ((1 << 8) - 1)
                self.check_pos(position_now)
                self.initial_memory[pos_now] = chr_now
                pos_now += 1
                self._chk_nxt_pos(pos_now, line_id)
    
    # 用于计算反汇编
    # 并计算所有的跳转指令目标点
    def _debug_show_raw(self, program_segment:list[int]=[], pos_set:Optional[set[int]]=None) -> set[int]:
        show_text = pos_set is not None
        need_calc_set = not show_text

        # 需要输出的对象
        output_item = []

        # 需要计算 pos_set
        if pos_set is None:
            pos_set = set()

        # 计算代码段起始位置
        if program_segment == []:
            ans = 0
            for i in range(15, 7, -1):
                ans = (
                    (ans << 8) | self.initial_memory.get(i, 0))
            program_segment = [ans]
        assert isinstance(program_segment, list)

        # 第多少个程序段
        ps_id = 1

        # 开始反汇编
        pos_val_pairt = sorted(list(self.initial_memory.items()))
        vis = {}
        for begin_pos, _ in pos_val_pairt:
            if vis.get(begin_pos) is not None:
                continue
            
            # 为了输出缩进记录行首位置
            line_front = True
            output_item.append(f"\n0x{begin_pos:016x}:")
            is_program = (begin_pos in program_segment)

            if not is_program:
                output_item.append("\n")
            else:
                output_item.append(f" // program segment part {ps_id}\n")
                ps_id += 1

            index = 0
            while self.initial_memory.get(begin_pos + index) is not None:
                if line_front:
                    output_item.append("    ")
                    line_front = False
                
                if not is_program:
                    arr = []
                    for i in range(8):
                        arr.append(f"{self.initial_memory.get(begin_pos + index + i, 0):02x}")
                        vis[begin_pos + index + i] = True
                    output_item.append(f"0x{"".join(arr[::-1])} ")
                    index += 8
                    if begin_pos + index == 16:
                        output_item.append("// initial pc\n")
                    elif begin_pos + index == 24:
                        output_item.append("// initial sp\n")
                    line_front = True
                else:
                    val = self.initial_memory[begin_pos + index]
                    vis[begin_pos + index] = True

                    if (begin_pos + index) in pos_set:
                        output_item.append(f"\n0x{begin_pos + index:016x}:")
                        output_item.append(f" // program segment part {ps_id}\n")
                        ps_id += 1
                        output_item.append(f"    ")

                    # 遇到了命令
                    if DEASM_INSTURCTION_MAP.get(val) is not None:
                        cmd = DEASM_INSTURCTION_MAP[val]
                        output_item.append(f"{cmd}")

                        if cmd == "PUSHIMM":
                            arr = []
                            for i in range(8):
                                pos_now = begin_pos + index + 1 + i
                                vis[pos_now] = True
                                arr.append(f"{self.initial_memory.get(pos_now, 0):02x}")
                            output_item.append((" 0x" + ("".join(arr[::-1]))) + "\n")
                            index += 9

                        else:
                            index += 1
                            output_item.append("\n")
                        line_front = True
                        
                    # 遇到了未知命令
                    else:
                        output_item.append(f"#0x{val:02x} // unknown cmd\n")
                        line_front = True
                        index += 1
        
        # 显示可视化版本的反汇编
        if show_text:
            print("".join(output_item))

        # 计算能够推测出来的分界点集合
        if need_calc_set:
            non_empty_pos = [
                item.strip()
                for item in output_item
                if item.strip() != "" and not item.strip().startswith("//")]
            print(output_item)
            print(non_empty_pos)
            for i in range(2, len(non_empty_pos)):
                if non_empty_pos[i].strip() == "BR" or non_empty_pos[i].strip() == "JMP":
                    if non_empty_pos[i-2] == "PUSHIMM":
                        pos_set.add(eval(non_empty_pos[i-1]))

        return pos_set
    
    # 输出反汇编
    def de_asm(self, program_segment:list[int]=[]):
        pos_set = self._debug_show_raw(program_segment, None)
        self._debug_show_raw(program_segment, pos_set)

if __name__ == "__main__":
    pf = ProgramFile()
    pf.read_program("sample_asm/sum.asm")
    pf.run(False)
