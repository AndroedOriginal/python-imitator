import re

def operation_steps(line):
    line = line.strip("if while for :")
    steps = re.split(r'\s+', line)
    return steps

def calculate(steps, index, line):
    steps_str = ''.join(steps)
    if re.fullmatch(r'[0-9+\-*/().\s]+', steps_str):
        return eval(steps_str)
    else:
        return f"\033[41mDangerous input!\033[0m\n{index} line \033[31m{line}\033[0m"

def operate_the_code(code):
    all_commands = ("if", "while", "for", "print", "def")
    results = []
    for line in code:
        steps = operation_steps(line)
        index = code.index(line)
        segment = []
        conditions = ["<", ">", "==", "!=", ":"]
        steps.append(":")
        if line.startswith("if"):
            for el in steps:
                if not el in conditions:
                    segment.append(el)
                else:
                    result = calculate(segment, index, line)
                    results.append(result)
                    results.append(el)
                    segment = []
            
            #print(segment)
            #print(f"#{results}")

            result = ' '.join(map(str, results))
            result = result.strip(":")
            if eval(result):
                print("#True")
                return True
            else:
                print("#False")
                return False

def terminal():
    while True:
        command = input("@Python-Imitator:~# ")
        if command.startswith("vim ") or command.startswith("python3 ") or command == "ls" or command == "help":
            result = command_result(command)
            return result

def get_code():
    while True:
        command = input("\033[34m~ \033[0m")
        if command == ":wq!":
            return code
        code.append(command)

def command_result(command):
    if command.startswith("vim "):
       name = command.strip("vim ")
       return name, "vim"
    if command.startswith("python3 "):
       name = command.strip("python3 ")
       return name, "python3"
    if command == "ls":
        return None, "ls"
    if command == "help":
        print("\nvim <name> # create a new project")
        print("python3 <name> # run project\n")
        return None, "help"
    
def open_code(code):
    for line in code:
        print("\033[34m~\033[0m", line)
    print("\n--INSERT--")

code = []

while True:
    name, command = terminal()
    if len(name) != 0:
        if command == "vim":
            if len(code) == 0:
                code = get_code()
            else:
                open_code(code)
        if command == "python3":
            operate_the_code(code)
    else:
        print("\033[41mE32: No file name\033[0m")
