from typing import Optional, Any
import sys
import re
import os

try:
    from .ins_code import INSTURCTION_MAP, VAL_RANGE, DEASM_INSTURCTION_MAP
except:
    from ins_code import INSTURCTION_MAP, VAL_RANGE, DEASM_INSTURCTION_MAP

class ProgramFile:
    def __init__(self) -> None:
        self._clear()

    # Convert interger string to int
    @classmethod
    def safe_val_eval(cls, s:str) -> int:
        pattern = r"0x[\dA-Fa-f]+|\d+|0b\d+"
        if re.fullmatch(pattern, s) is None:
            raise ValueError()
        return eval(s)

    def _clear(self):
        self.initial_memory = {}
        self.memory = {}
        self.pc = 0
        self.sp = 0
        self.init_sp = 0 # Initial sp
        self.ap = 0
        self.finish = False
        self.debug = False
        self.syscal_hook:dict[int, Any] = {}
        self.stdout_arr = ""

        # A certain .iasm file can only be included onve
        self.file_included = set()

        # Enable this switch to prevent the program from outputting content to the standard output stream
        # and only record the program's output through the self.stdout_arr string
        self.ignore_stdout = False 

    # syscal_hook is used to provide a mapping from integers to functions
    # This function func will accept parameters func(self.memory, data)
    # where data is eight integers composed of the 64 bytes from 0 to 63 in memory
    def set_syscal_hook(self, syscal_hook:dict[int, Any]):
        self.syscal_hook = {
            (item % VAL_RANGE) : syscal_hook[item] # Note to ensure all values are positive
            for item in syscal_hook
        }

    def _chk_nxt_pos(self, file_now:str, position_now:int, line_id:int):
        if position_now >= VAL_RANGE:
            raise ValueError(f"{file_now}: {line_id}: position_now out of bound.")

    def check_pos(self, position_now:int):
        if self.initial_memory.get(position_now) is not None:
            raise ValueError(f"{position_now} refilled.")
    
    # Get integer from memory
    def _get_integer(self, pos:int, siz:int=8) -> int:
        data_list = []
        for i in range(siz):
            data_list.append(self.memory.get((pos + i) % VAL_RANGE, 0)  % 256)
        data_val = 0
        for i in range(siz - 1, -1, -1):
            data_val = ((data_val << 8) | data_list[i])
        return data_val
    
    # Assign value to memory
    def _set_integer(self, val:int, pos:int, siz:int=8) -> None:

        data_list = []
        for i in range(siz):
            data_list.append((val >> (8 * i)) & 255)
        for i in range(siz):
            self.memory[pos + i] = data_list[i]

    # Copy from self.initial_memory to self.memory
    def _load_memory(self):
        self.memory = {}
        for item in self.initial_memory:
            self.memory[item] = self.initial_memory[item]

    # System call
    def _syscal(self):
        data = [
            self._get_integer(0),
            self._get_integer(8),
            self._get_integer(16),
            self._get_integer(24),
            self._get_integer(32),
            self._get_integer(40),
            self._get_integer(48),
            self._get_integer(56)
        ]

        # Use user-defined system call
        if self.syscal_hook.get(data[1]) is not None:
            func = self.syscal_hook[data[1]]
            func(self.memory, data)

        elif data[1] == 1: # Input a character
            try:
                chr_val = ord(sys.stdin.read(1)) % 256
            except:
                chr_val = 255
            self._set_integer(chr_val, 8) # Successfully read character information is sent to data[1]

        elif data[1] == 2: # Output a string
            pos_now = data[2]
            chr_cnt = 0
            while True:
                if self.memory.get(pos_now, 0) == 0:
                    break

                # Record the program's standard output
                chr_cnt += 1
                self.stdout_arr += chr(self.memory[pos_now])
                if not self.ignore_stdout:
                    print(chr(self.memory[pos_now]), end="")
                pos_now += 1
            self._set_integer(chr_cnt, 8) # The number of successfully output characters is sent to data[1]

        elif data[1] == 3: # Enable debug mode
            self.debug = (data[2] != 0)

        # Unknown system call number
        else:
            raise ValueError(f"syscal {data[1]} unknow.")

        # When the system call ends
        # Clear the initial position
        self._set_integer(0, 0)

    # Output debug information
    def _debug_show(self, cmd:str):
        print(f"PC: 0x{self.pc:016x}")
        print(f"SP: 0x{self.sp:016x}")
        print(f"AP: 0x{self.ap:016x}")

        # Output system call debug information
        data = [
            self._get_integer(0),
            self._get_integer(8),
            self._get_integer(16),
            self._get_integer(24),
            self._get_integer(32),
            self._get_integer(40),
            self._get_integer(48),
            self._get_integer(56)
        ]
        if self.debug:
            print("SYSCAL ARGS:")
            for i in range(1, len(data)):
                print(f"    0x{data[i]:016x}")
        print()

        # Output current command
        print("    ", end="")
        if cmd == "PUSHIMM":
            print(f"PUSHIMM 0x{self._get_integer(self.pc + 1):016x}")
            
        else:
            print(cmd)
        print()

        # Output stack space
        print(f"stack (0x{self.init_sp:016x} .. 0x{self.sp:016x}):")
        for i in range(self.init_sp, self.sp, 8):
            print(f"    0x{self._get_integer(i):016x}")

    # Get signed value for a unsined value
    @classmethod
    def get_real_val(cls, val:int) -> int:
        if ((val >> 63) & 1) != 0:
            return val - VAL_RANGE
        else:
            return val

    # Run the program
    def run(self, debug_mode:Optional[bool]=None) -> int:
        if isinstance(debug_mode, bool):
            self.debug = debug_mode

        if self.finish is True:
            raise ValueError("you can not run program twice.")
        self._load_memory()
        self.finish = True
        self.pc = self._get_integer(8) # Initialize pc
        self.sp = self._get_integer(16) # Initialize sp
        self.init_sp = self.sp
        self.ap = 0

        while True:
            
            cmd_val = self.memory.get(self.pc, 0)
            if DEASM_INSTURCTION_MAP.get(cmd_val) is None:
                raise ValueError(f"{cmd_val} is not a command.")
            
            # Find the corresponding command name
            cmd = DEASM_INSTURCTION_MAP[cmd_val]

            # Output debug information
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

            elif cmd == "CALL":
                old_pc = self.pc
                self.sp -= 8
                self.pc = self._get_integer(self.sp)
                self._set_integer(old_pc + 1, self.sp)
                self.sp += 8

            elif cmd == "LOAD":
                for i in range(8):
                    self.memory[self.sp + i] = (
                        self.memory.get(self.ap + i, 0)
                    )
                self.sp += 8
                self.pc += 1

            elif cmd == "SAVE":
                self.sp -= 8
                for i in range(8):
                    self.memory[self.ap + i] = (
                        self.memory.get(self.sp + i, 0)
                    )
                self.pc += 1

            elif cmd == "SYSCAL":
                self._set_integer(1, 0)
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
                ans = (-val) % VAL_RANGE
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
                ans = (val_1 | val_2) % VAL_RANGE
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
                ans = (self.get_real_val(val_1) <= self.get_real_val(val_2))
                self._set_integer(ans, self.sp)
                self.sp += 8
                self.pc += 1

            elif cmd == "LT":
                self.sp -= 8
                val_2 = self._get_integer(self.sp)
                self.sp -= 8
                val_1 = self._get_integer(self.sp)
                ans = (self.get_real_val(val_1) < self.get_real_val(val_2))
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
                offset = self._get_integer(self.sp)
                self.sp -= 8
                val_pos = self.sp
                for i in range(8):
                    self.memory[self.sp - 8 * offset - 8 + i] = (
                        self.memory[val_pos + i])
                self.pc += 1

            elif cmd == "EXCH":
                for i in range(8):
                    t = self.memory[self.sp - 16 + i]
                    self.memory[self.sp - 16 + i] = self.memory[self.sp -8 + i]
                    self.memory[self.sp - 8 + i] = t
                self.pc += 1

            else:
                raise ValueError(f"{cmd} is not a valid command.")
            
            # System calls can be triggered by any assignment to position 0
            if self._get_integer(0) != 0:
                self._syscal()

    def get_all_lines(self, asm_filepath:str, encoding:str) -> list[tuple[int, str, str]]:
        ans = []

        # Check file exists
        if not os.path.isfile(asm_filepath):
            raise FileNotFoundError()
        
        # Get absolute filepath
        if not os.path.isabs(asm_filepath):
            asm_filepath = os.path.abspath(asm_filepath)
        rel_path = os.path.relpath(asm_filepath)

        # Do not include one file twice
        if asm_filepath in self.file_included:
            return []
        self.file_included.add(asm_filepath)
        
        # Get folder path
        dirnow = os.path.dirname(asm_filepath)

        for idx, line in enumerate(list(open(asm_filepath, "r", encoding=encoding))):
            line = line.strip()


            # Erase comment
            if line.find("//") != -1:
                line = line.split("//")[0].strip()

            # Skip empty line
            if line == "":
                continue

            # Include file
            if line.startswith("INCLUDE"):
                next_path = eval(line[len("INCLUDE"):], globals=dict(), locals=dict())
                next_path = os.path.join(dirnow, next_path)

                ans += self.get_all_lines(next_path, encoding)
                continue

            # Not INCLUDE command
            ans.append((idx + 1, rel_path, line))

        return ans

    # This function returns a dict[str, int]
    # representing the program positions corresponding to all symbols
    def read_program(self, filepath:str, encoding="utf-8", debug=False) -> dict[str, int]:
        position_now = 0
        segment_begin_now = 0

        # Get current abspath
        asm_filepath = os.path.abspath(filepath)

        late_insert:dict[tuple[int, str, int], str] = {} # Record delayed insertion positions
        token_value:dict[str, int] = {} # Record the values of identifiers

        all_lines = self.get_all_lines(asm_filepath, encoding) # Get all line in a program
        for line_id, file_now, line in all_lines:
            
            # Only PUSHIMM has parameter
            parts = line.split(maxsplit=1)
            if INSTURCTION_MAP.get(parts[0]) is not None:
                if parts[0] != "PUSHIMM" and len(parts) >= 2:
                    raise ValueError(f"{file_now}: {line_id}: command {parts[0]} can not followed by arguments.")

            # Process four types of items
            #   Position adjustment symbols
            #   Instructions
            #   64-bit data
            #   Jump identifiers
            for part in line.split():
                
                # Recognize character-type immediate values
                if part.startswith("#"):
                    val = self.safe_val_eval(part[1:])
                    self.check_pos(position_now)
                    self.initial_memory[position_now] = val % 256
                    position_now += 1
                    self._chk_nxt_pos(file_now, position_now, line_id)

                # Recognize instructions
                elif INSTURCTION_MAP.get(part) is not None:
                    self.check_pos(position_now)
                    self.initial_memory[position_now] = (
                        INSTURCTION_MAP[part]
                    )
                    position_now += 1
                    self._chk_nxt_pos(file_now, position_now, line_id)

                # Recognize colons
                # Consider jump identifiers and position adjusters separately
                elif part.endswith(":"):

                    if len(part) == 1:
                        raise ValueError(f"{line_id}: colon detected.")
                    
                    # Got a position adjuster
                    if part[0].isdigit():
                        data_val = self.safe_val_eval(part[:-1])

                        # Ensure the current segment length is a multiple of eight
                        while (position_now - segment_begin_now) % 8 != 0:
                            self.check_pos(position_now)
                            self.initial_memory[position_now] = 0
                            position_now += 1

                        position_now = int(data_val)
                        segment_begin_now = position_now
                        self._chk_nxt_pos(file_now, position_now, line_id)

                    # Got a jump identifier
                    else:
                        jmp_label = part[:-1]
                        token_value[jmp_label] = position_now

                        if debug:
                            print(f"{jmp_label}: 0x{position_now:016x}")

                else:
                    # Interpret as 64-bit data
                    if part[0].isdigit():
                        data_val = self.safe_val_eval(part)
                        for i in range(8):
                            chr_now = (data_val >> (i * 8)) & ((1 << 8) - 1)
                            self.check_pos(position_now)
                            self.initial_memory[position_now] = chr_now
                            position_now += 1
                            self._chk_nxt_pos(file_now, position_now, line_id)

                    # Interpret as an identifier usage
                    # Identifiers need to be assigned after global scanning is complete
                    else:
                        late_insert[(position_now, file_now, line_id)] = part
                        position_now += 8
                        self._chk_nxt_pos(file_now, position_now, line_id)

        # Fill values for identifiers
        for pos, file_now, line_id in late_insert:
            token = late_insert[(pos, file_now, line_id)]
            if token_value.get(token) is None:
                raise ValueError(f"{line_id}: token {token} undefined.")
            data_val = token_value[token]
            pos_now = pos
            for i in range(8):
                chr_now = (data_val >> (i * 8)) & ((1 << 8) - 1)
                self.check_pos(position_now)
                self.initial_memory[pos_now] = chr_now
                pos_now += 1
                self._chk_nxt_pos(file_now, pos_now, line_id)

        # Return symbol table
        return token_value
    


    # Used to calculate disassembly
    # and calculate the target points of all jump instructions
    def _debug_show_raw(self, program_segment:list[int]=[], pos_set:Optional[set[int]]=None) -> set[int]:
        show_text = pos_set is not None
        need_calc_set = not show_text

        # Objects to be output
        output_item = []

        # Need to calculate pos_set
        if pos_set is None:
            pos_set = set()

        # Calculate the start position of the code segment
        if program_segment == []:
            ans = 0
            for i in range(15, 7, -1):
                ans = (
                    (ans << 8) | self.initial_memory.get(i, 0))
            program_segment = [ans]
        assert isinstance(program_segment, list)

        # Which program segment it is
        ps_id = 1

        # Start disassembly
        pos_val_pairt = sorted(list(self.initial_memory.items()))
        vis = {}
        for begin_pos, _ in pos_val_pairt:
            if vis.get(begin_pos) is not None:
                continue
            
            # Record the line start position for output indentation
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

                    # Encountered a command
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
                        
                    # Encountered an unknown command
                    else:
                        output_item.append(f"#0x{val:02x} // unknown cmd\n")
                        line_front = True
                        index += 1
        
        # Display visual version of disassembly
        if show_text:
            print("".join(output_item))

        # Calculate the set of inferable boundary points
        if need_calc_set:
            non_empty_pos = [
                item.strip()
                for item in output_item
                if item.strip() != "" and not item.strip().startswith("//")]
            for i in range(2, len(non_empty_pos)):
                if non_empty_pos[i].strip() in ["BR", "JMP", "CALL"]:
                    if non_empty_pos[i-2] == "PUSHIMM":
                        pos_set.add(self.safe_val_eval(non_empty_pos[i-1]))

        return pos_set
    
    # Output disassembly
    def de_asm(self, program_segment:list[int]=[]):
        pos_set = self._debug_show_raw(program_segment, None)
        self._debug_show_raw(program_segment, pos_set)

if __name__ == "__main__":
    pf = ProgramFile()
    symbol_map = pf.read_program("sample_asm/putc.asm")
    print(symbol_map)
    # pf.de_asm()
    ret = pf.run(debug_mode=False)
    print(f"program return 0x{ret:016x} ({ret})")
