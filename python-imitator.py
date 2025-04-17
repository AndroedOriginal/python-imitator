import re

def add_or_move_to_end(variables, key, value):
    if key in variables:
        val = variables.pop(key)
        variables[key] = val       
    else:
        variables[key] = value

def calculate_variable(line, full_line, index):
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
    #print("#tabs count:", tabs_count)
    if results_of_all_conditions and tabs_count > 0:
        last_result = next(reversed(results_of_all_conditions))
        #print("last result:", last_result)
        return last_result
    else:
        #print("#Just 'True'")
        return True

def correct_tabs(line, spaces_in_tab):
    tabs_count = (len(line) - len(line.lstrip())) // spaces_in_tab
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

def print_function(line):
    result = line.replace("print(", "").replace(")", "").replace('"', "")
    #print(not '"' in line)
    #print(result in variables)
    #print(variables, result)
    if not '"' in line and result in variables:
        #print("true")
        if hasattr(variables[result], '__len__'):
            result = variables[result][0]
        else:
            result = variables[result]
    elif not result in variables and not '"' in line:
        return f"NameError: name '{result}' is not defined"

    return result

def segments_function(steps, index, line, results):
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
    #print(f"{index}: calculate: {line}")
    for i, step in enumerate(steps):
        if isinstance(step, str) and step in variables:
            val = variables[step]
            if isinstance(val, tuple):
                val = val[0]  # берём только само значение, а не служебные данные
            steps[i] = val

    steps = [str(step) for step in steps]
    steps_str = ' '.join(steps)
    #print(steps_str)
    
    try:
        return eval(steps_str, {"__builtins__": None}, variables)
    except Exception:
        print(f"\033[41mDangerous input!\033[0m\n{index+1} line \033[31m{line}\033[0m")
        return None

def operate_the_code(code, spaces_in_tab):
    global variables
    results_of_all_conditions = {}
    variables = {}
    while_dictionary = {}
    index = 0
    for_value = 0

    while index <= len(code):
        if index != len(code) or index > len(code):
            line = code[index]
        #print("\033[90m#variables:", variables,"\033[0m")
        
        steps = operation_steps(line)
        line_index = code.index(line)
        tabs_count = correct_tabs(line, spaces_in_tab)
        line_without_tabs = line.lstrip()

        #print(f"\033[90m#tabs count: {tabs_count}, #line({index}): {line_without_tabs}\033[0m")

        if previous_condition(results_of_all_conditions, tabs_count) == True:
            if line_without_tabs.startswith("if"):
                result = if_function(steps, line_index, line_without_tabs)
                if result in results_of_all_conditions:
                    del results_of_all_conditions[result]
                results_of_all_conditions[result] = line_index
                #print("\033[90m#results of all conditions:", results_of_all_conditions)
            
            if line_without_tabs.startswith("print(") and line_without_tabs.endswith(")"):
                result = print_function(line_without_tabs)
                print(result)

            if "=" in line_without_tabs and not line_without_tabs.startswith(("while", "if", "elif")):
                variables = convert_value(line_without_tabs, line_index)
            
            if line_without_tabs.startswith("for"):
                result = line_without_tabs.replace("for ", "").replace(":", "").replace("range", "")
                #print(f"\033[90m#result: {result}")

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
                #print(f"\033[90mm#result: {result}\033[0m")

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
                
                #print(f"\033[90m#local variable:\n#Name {local_variable_name} #Value {value_start}, {value_end}, {for_value}\033[0m")

                for_value = int(for_value)
                value_end = int(value_end)
                #print(for_value)
                variables[local_variable_name] = for_value, (value_end, tabs_count, index)
                #print(for_value)

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

                #print("\033[90m#dictionary:", while_dictionary,"\033[0m")
            
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
                        #print(f"\033[90m# {tabs_count} == {variables[el][1][1]}:", tabs_count == variables[el][1][1], "(tabs count)\033[0m")
                        #print(f"\033[90m# {index+1} == {len(code)}:",  index+1 == len(code), "(code end)\033[0m")
                        if index == len(code) or tabs_count == variables[el][1][1] and line_without_tabs != "":
                            #print(f"\033[90m# index({index}) = {variables[el][1][2]}\033[0m")
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
        if command.startswith("vim ") or command.startswith("python3 ") or command.startswith("sit") or command == "ls" or command == "help":
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
        value = command.replace("vim ", "", 1)
        return value, "vim"
    if command.startswith("python3 "):
        value = command.replace("python3 ", "", 1)
        return value, "python3"
    if command.startswith("sit[") and command.endswith("]"):
        value = command.replace("sit[", "").replace("]", "")
        return value, "sit"
    if command == "ls":
        return '', "ls"
    if command == "help":
        print("\nvim <name> # create a new project")
        print("python3 <name> # run project")
        print("sit[<value>] # spaces count in 1 tab\n")
        return '', "help"
    
def open_code(code):
    for line in code:
        index = code.index(line) + 1
        print(f"\033[34m{index}\033[0m", line)
    print("\n--INSERT--")

code = []
code_name = ''
spaces_in_tab = 1

while True:
    value, command = terminal()
    #print(value, command)
    if code_name == '' and command != "sit":
        code_name = value
    if command == "ls":
        print(code_name)
    if len(value) != 0 or command != "ls" or command != "help" or command != "sit":
        if command == "vim":
            if len(code) == 0 or value != code_name:
                code = get_code()
            else:
                open_code(code)
        if command == "python3" and value == code_name:
            operate_the_code(code, spaces_in_tab)
        if command == "sit":
            print(value)
            if 0 >= int(value) or not value.isdigit():
                print(f"ValueError: sit[\033[41m{value}\033[0m]")
                break
            else:
                spaces_in_tab = int(value)
    else:
        print("\033[41mE32: No file name\033[0m")