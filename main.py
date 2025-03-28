import re

def if_function(line):
    line = line.strip("if :")
    conditions = ("and", "or", "not")
    steps = re.split(r'\s+', line)
    print(steps)

def operate_the_code(code):
    all_commands = ("if", "while", "for", "print", "def")
    for line in code:
        if line.startswith("if"):
            if_function(line)

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
        print()
        print("vim <name> #create a new project")
        print("python3 <name> #")
        print()
        return None, "help"
    
def open_code(code):
    for line in code:
        print("\033[34m~\033[0m", line)
    print("--INSERT--")

code = []

while True:
    name, command = terminal()
    if command == "vim":
        if len(code) == 0:
            code = get_code()
        else:
            open_code(code)
    if command == "python3":
        operate_the_code(code)