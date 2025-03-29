import re

def convert_value(line):
    name = []
    for x in line:
        if not x == "=":
            name.append(x)
        else:
            break
    name = ''.join(name).replace(" ", "")
    value = line.replace(name, "").replace("=", "").replace(" ", "")

    variables[name] = value
    return variables

def safe_eval(expression):
    try:
        return eval(expression, {"__builtins__": None}, variables)
    except Exception:
        return False

def previous_condition(results_of_all_conditions, tabs_count):
    if results_of_all_conditions and tabs_count > 0:
        smallest_result = next(reversed(results_of_all_conditions))
    else:
        return True

    return smallest_result

def correct_tabs(line):
    tabs_count = (len(line) - len(line.lstrip())) / 4
    return tabs_count

def if_function(steps, index, line):
    results = []
    results = segments_function(steps, index, line, results)

    result = ' '.join(map(str, results))
    result = result.strip(":")
    if eval(result):
        #print("#True")
        return True
    else:
        #print("#False")
        return False
    return None

def print_function(line):
    result = line.replace("print(", "").replace(")", "").replace('"', "")
    if not '"' in line and result in variables:
        result = variables[result]

    return result

def segments_function(steps, index, line, results):
    conditions = ["<", ">", "==", "!=", ":"]
    segment = []
    results = []
    steps.append(":")
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
    return results

def operation_steps(line):
    line = line.strip("if while for :")
    steps = re.split(r'\s+', line)
    return steps

def calculate(steps, index, line):
    for step in steps:
        if step in variables:
            steps[steps.index(step)] = variables[step]
    steps_str = ''.join(steps)
    if safe_eval(steps_str):
        return eval(steps_str)
    else:
        return f"\033[41mDangerous input!\033[0m\n{index+1} line \033[31m{line}\033[0m"

def operate_the_code(code):
    global variables
    all_commands = ("if", "while", "for", "print", "def")
    results_of_all_conditions = {}
    variables = {}

    for line in code:
        steps = operation_steps(line)
        line_index = code.index(line)
        tabs_count = correct_tabs(line)
        line_without_tabs = line.lstrip()

        if previous_condition(results_of_all_conditions, tabs_count):
            if line_without_tabs.startswith("if"):
                result = if_function(steps, line_index, line_without_tabs)
                results_of_all_conditions[result] = line_index
            
            if line_without_tabs.startswith("print(") and line_without_tabs.endswith(")"):
                result = print_function(line_without_tabs)
                print(result)

            if "=" in line_without_tabs and not line_without_tabs.startswith(("while", "if", "elif")):
                variables = convert_value(line_without_tabs)

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
        name = command.replace("vim ", "", 1)
        return name, "vim"
    if command.startswith("python3 "):
        name = command.replace("python3 ", "", 1)
        return name, "python3"
    if command == "ls":
        return '', "ls"
    if command == "help":
        print("\nvim <name> # create a new project")
        print("python3 <name> # run project\n")
        return '', "help"
    
def open_code(code):
    for line in code:
        index = code.index(line) + 1
        print(f"\033[34m{index}\033[0m", line)
    print("\n--INSERT--")

code = []
code_name = ''

while True:
    name, command = terminal()
    #print(name, command)
    if code_name == '':
        code_name = name
    if command == "ls":
        print(code_name)
    if len(name) != 0 or command != "ls" or command != "help":
        if command == "vim":
            if len(code) == 0 or name != code_name:
                code = get_code()
            else:
                open_code(code)
        if command == "python3" and name == code_name:
            operate_the_code(code)
    else:
        print("\033[41mE32: No file name\033[0m")