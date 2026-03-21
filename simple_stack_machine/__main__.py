from . import ProgramFile
import json
import sys
import os

# Check if some flag exists in argv_list
# return argv_list without that flag
def check_and_erase(argv_list:list[str], flag:str) -> tuple[bool, list[str]]:
    found = 0
    for item in argv_list:
        if item.strip() == flag.strip():
            found += 1
    return found >= 1, [
        item
        for item in argv_list
        if item.strip() != flag.strip()
    ]

if __name__ == "__main__":
    argv_list = json.loads(json.dumps(sys.argv[1:]))
    debug_mode, argv_list = check_and_erase(argv_list, "--debug")

    if len(argv_list) != 1:
        print("Usage:")
        print("    python -m simple_stack_machine <filepath.asm>")
        print("    python -m simple_stack_machine --debug <filepath.asm>")
        sys.exit(1)
    
    filepath = argv_list[0]
    if not os.path.isfile(filepath):
        print(f"File \"{filepath}\" not found.")

    pf = ProgramFile()
    pf.read_program(filepath)
    ret_val = pf.run(debug_mode)
    
    sys.exit(ret_val % 256)
