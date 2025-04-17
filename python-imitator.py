import re
import sys
import termios
import tty


def add_or_move_to_end(variables, key, value):
    if key in variables:
        val = variables.pop(key)
        variables[key] = val       
    else:
        variables[key] = value

def calculate_variable(line, full_line, index):
    global debug_mode, debug_text_color
    name = []
    steps = []
    value = 0
    #print("#line:", line)
    for x in line:
        if x not in ("+", "-", "/", "*", "%", "^"):
            name.append(x)
        else:
            name_str = ''.join(name).replace(" ", "")
            if name_str in variables:
                name_value = variables[name_str]
                steps.append(name_value)
                steps.append(x)
            else:
                steps.append(name_str)
                steps.append(x)
            name = []

    #print("#name:", name)

    if name:
        name_str = ''.join(name).replace(" ", "")
        steps.append(name_str)

    result = calculate(steps, index, full_line)
    #print("#result:", result)
    return result

def convert_value(line, index):
    name = []
    for x in line:
        if x != "=":
            name.append(x)
        else:
            break
    name = ''.join(name).replace(" ", "")
    value = line.replace(f"{name} =", "").replace(f"{name} =", "").strip()    
    value_expr = line.split('=')[1].strip()

    if any(key in value for key in variables):
        try:
            value = calculate_variable(value, line, index)
        except:
            print(f"\033[41mDangerous input!\033[0m\n{index+1} line \033[31m{line}\033[0m")
            return variables
    else:
        try:
            value = eval(value_expr, {"__builtins__": None}, {})
        except:
            value = value_expr

    variables[name] = int(value) if str(value).isdigit() else value
    return variables

def safe_eval(expression):
    try:
        return eval(expression, {"__builtins__": None}, variables)
    except Exception:
        return False

def previous_condition(results_of_all_conditions, tabs_count):
    global debug_mode, debug_text_color
    if results_of_all_conditions and tabs_count > 0:
        last_result = next(reversed(results_of_all_conditions))
        if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}last result:", last_result, "\033[0m")
        return last_result
    else:
        if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#last result: True")
        return True

def correct_tabs(line, spaces_in_tab):
    global debug_mode, debug_text_color
    tabs_count = (len(line) - len(line.lstrip())) // spaces_in_tab
    if debug_mode == "default" or debug_mode == "all": print(f"{debug_text_color}#tabs count:", tabs_count, "\033[0m") 
    return tabs_count

def if_function(steps, index, line):
    global debug_mode, debug_text_color
    results = []
    results = segments_function(steps, index, line, results)

    result = ' '.join(map(str, results))
    result = result.strip(":")
    if eval(result):
        if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#if result({index}):", True, "\033[0m")
        return True
    else:
        if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#if result({index}):", False, "\033[0m") 
        return False

def print_function(line):
    global debug_mode, debug_text_color
    result = line.replace("print(", "").replace(")", "").replace('"', "")
    if not '"' in line and result in variables:
        if hasattr(variables[result], '__len__'):
            result = variables[result][0]
        else:
            result = variables[result]
    elif not result in variables and not '"' in line:
        return f"NameError: name '{result}' is not defined"

    return result

def segments_function(steps, index, line, results):
    global debug_mode, debug_text_color
    conditions = ["<", ">", "==", "!=", ":"]
    segment = []
    results = []
    steps.append(":")
    for el in steps:
        if el == ":":
            if segment:
                result = calculate(segment, index, line)
                results.append(result)
            break
        elif el not in conditions:
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
    line = line.replace("if", "").replace("while", "").replace("for", "").replace(":", "")
    steps = re.split(r'\s+', line)
    return steps

def calculate(steps, index, line):
    global debug_mode, debug_text_color
    #print(f"{index}: calculate: {line}")
    for i, step in enumerate(steps):
        if isinstance(step, str) and step in variables:
            val = variables[step]
            if isinstance(val, tuple):
                val = val[0]
            steps[i] = val

    steps = [str(step) for step in steps]
    steps_str = ' '.join(steps)
    if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#calculation steps:", steps_str, "\033[0m") 
    
    try:
        if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#calculation result:", eval(steps_str, {"__builtins__": None}, variables), "\033[0m") 
        return eval(steps_str, {"__builtins__": None}, variables)
    except Exception:
        print(f"\033[41mDangerous input!\033[0m\n{index+1} line \033[31m{line}\033[0m")
        return None

def operate_the_code(code, spaces_in_tab):
    global debug_mode, debug_text_color
    global variables
    results_of_all_conditions = {}
    variables = {}
    while_dictionary = {}
    index = 0
    for_value = 0

    while index <= len(code):
        if index != len(code) or index > len(code):
            line = code[index]
        if debug_mode == "variables" or debug_mode == "all": print(f"{debug_text_color}#variables:", variables, "\033[0m")
        
        steps = operation_steps(line)
        line_index = code.index(line)
        tabs_count = correct_tabs(line, spaces_in_tab)
        line_without_tabs = line.lstrip()

        if debug_mode == "default" or debug_mode == "all": print(f"{debug_text_color}#tabs count: {tabs_count}, #line({index}): {line_without_tabs}\033[0m")

        if previous_condition(results_of_all_conditions, tabs_count) == True:
            if line_without_tabs.startswith("if"):
                result = if_function(steps, line_index, line_without_tabs)
                if result in results_of_all_conditions:
                    del results_of_all_conditions[result]
                results_of_all_conditions[result] = line_index
                if debug_mode == "results" or debug_mode == "all": print(f"{debug_text_color}#results of all conditions:", results_of_all_conditions) 
            
            if line_without_tabs.startswith("print(") and line_without_tabs.endswith(")"):
                result = print_function(line_without_tabs)
                print(result) if debug_mode == False else print(f"{default_text_color}{result}\033[0m") 

            if "=" in line_without_tabs and not line_without_tabs.startswith(("while", "if", "elif")):
                variables = convert_value(line_without_tabs, line_index)
            
            if line_without_tabs.startswith("for"):
                result = line_without_tabs.replace("for ", "").replace(":", "").replace("range", "")

                local_variable_name = []
                for i in range(len(result)):
                    if result[i+1] == "i" and result[i+2] == "n":
                        break
                    local_variable_name.append(result[i])

                local_variable_name = ''.join(local_variable_name).strip()
                local_variable_name.replace("'", "")
                value_start = []
                value_end = []
                result = result.replace(local_variable_name, "").replace("in", "").replace("(", "")

                for i in range(len(result)):
                    if result[i] == ",":
                        break
                    value_start.append(result[i])
                
                value_start = ''.join(value_start).strip()
                result = result.replace(f"{value_start}, ", "")

                for i in range(len(result)):
                    if result[i] == ")":
                        break
                    value_end.append(result[i])

                value_end = ''.join(value_end).strip()
                value_end.replace(")", "")
                value_start = int(value_start)
                if for_value == 0:
                    for_value = value_start
                
                if debug_mode == "results" or debug_mode == "all" or debug_mode == "for": print(f"{debug_text_color}#local variable:\n#Name {local_variable_name} #Value {value_start}, {value_end}, {for_value}\033[0m") 

                for_value = int(for_value)
                value_end = int(value_end)
                variables[local_variable_name] = for_value, (value_end, tabs_count, index)

            if line_without_tabs.startswith("while"):
                result = if_function(steps, line_index, line_without_tabs)

                if result == True:                        
                    while_dictionary[result] = (tabs_count, index)
                else:
                    while_skipping = True
                    while while_skipping and index < len(code):
                        index += 1
                        if index < len(code):
                            next_tabs = correct_tabs(code[index], spaces_in_tab)
                            if next_tabs <= tabs_count:
                                while_skipping = False
                    continue

                if debug_mode == "variables" or debug_mode == "all" or debug_mode == "while": print(f"{debug_text_color}# while dictionary:", while_dictionary,"\033[0m") 
            
            if while_dictionary:
                last_while = next(reversed(while_dictionary))
                if tabs_count == while_dictionary[last_while] or index+1 == len(code):
                    while_line = code[last_while]
                    steps = operation_steps(while_line.lstrip()[6:])
                    result = if_function(steps, last_while, while_line)
                    
                    if not result:
                        del while_dictionary[last_while]
                        index += 1
                        continue
                        
                    index = last_while

        if variables:
            for el in variables:
                if hasattr(variables[el], '__len__'):
                    if variables[el][0] != variables[el][1][0]:
                        if debug_mode == "for" or debug_mode == "all": print(f"{debug_text_color}# {tabs_count} == {variables[el][1][1]}:", tabs_count == variables[el][1][1], "(tabs count)\033[0m") 
                        if debug_mode == "for" or debug_mode == "all": print(f"{debug_text_color}# {index+1} == {len(code)}:",  index+1 == len(code), "(code end)\033[0m") 
                        if index == len(code) or tabs_count == variables[el][1][1] and line_without_tabs != "":
                            if debug_mode == "for" or debug_mode == "all": print(f"{debug_text_color}# index({index}) = {variables[el][1][2]}\033[0m") 
                            index = variables[el][1][2]
                            if True in results_of_all_conditions:
                                del results_of_all_conditions[True]
                            results_of_all_conditions[True] = line_index
                            variables[local_variable_name] = for_value, (value_end, tabs_count, index)
                            for_value += 1
                    else:
                        del variables[local_variable_name]
                        results_of_all_conditions[True] = line_index
                        break

        index += 1

def terminal():
    while True:
        command = input("@Python-Imitator:~# ")
        result = command_result(command)
        return result

def wait_for_i():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            key = sys.stdin.read(1)
            if key == 'i':
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_code():
    while True:
        command = input("\033[34m~ \033[0m")
        if command.startswith(":"):
            if command == ":wq!":
                return code
            else:
                print(f"\033[41mE492: Not an editor command: {command}\033[0m", end='', flush=True)
                wait_for_i()
                print("\033[2K\r", end='')
        else:     
            code.append(command)

def command_result(command):
    global debug_mode
    
    if command.startswith("vim "):
        value = command.replace("vim ", "", 1)
        return value, "vim"
    elif command.startswith("python3 "):
        value = command.replace("python3 ", "", 1)
        return value, "python3"
    elif command.startswith("sit"):
        value = command.replace("sit[", "").replace("]", "").replace("sit", "")
        return value, "sit"
    elif command == "ls":
        return ' ', "ls"
    elif command == "help":
        print("\nvim <name> # create a new project")
        print("python3 <name> # run project")
        print("sit[<value>] # spaces count in 1 tab\n")
        return ' ', "help"
    elif command.startswith("rm"):
        value = command.replace("rm ", "", 1)
        return value, "remove"
    elif command.startswith("debug"):
        value = command.replace("debug", "").replace("[", "").replace("]", "").replace("=", "").strip()
        if "True" in value:
            debug_mode = value.replace("True", "").strip() or "all"
        elif "False" in value:
            debug_mode = False
        else:
            debug_mode = value or "default"
        print(f"Debug mode set to: {debug_mode}")
        return debug_mode, "debug"
    else:
        return f"Command '{command}' not found", None
    
def open_code(code):
    for line in code:
        index = code.index(line) + 1
        print(f"\033[34m{index}\033[0m", line)
    print("\n--INSERT--")


all_codes = {}
code = []
code_name = ''
spaces_in_tab = 1
debug_text_color = "\033[90m"
default_text_color = "\033[94m"
debug_mode = False

while True:
    value, command = terminal()
    print(value, command)
    if command == None:
        print(value)
    code_name = value
    if command == "ls":
        print(f"{" ".join([x for x in all_codes])}")
    if len(value) != 0:
        if command == "vim":
            if not value in all_codes or len(all_codes[value]) == 0:
                code = get_code()
                all_codes[code_name] = code
            else:
                open_code(all_codes[value])
            code = []
        if command == "python3" and value in all_codes:
            operate_the_code(all_codes[value], spaces_in_tab)
            code = []
        if command == "remove" and value in all_codes:
            del all_codes[value]
        if command == "sit":
            if value.strip() == "":
                print(f"Spaces in one tab: [{spaces_in_tab}]")
            elif not value.isdigit() or 0 >= int(value):
                print(f"ValueError: sit[\033[41m{value}\033[0m]\n                {"".join(["^" for x in range(len(value))])}\nThe command sit[] cannot have a value equal to zero, a negative number, or a letter.")
            else:
                spaces_in_tab = int(value)
    else:
        print("\033[41mE32: No file name\033[0m")
