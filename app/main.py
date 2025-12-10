import sys
import os
import subprocess
import shlex

BUILTINS = ['echo', 'type', 'exit', 'pwd']

def handle_cat(args):
    """Handles the cat command."""
    files = args
    for filename in files:
        if not filename: continue
        try:
            with open(filename, 'r') as f:
                sys.stdout.write(f.read())
        except FileNotFoundError:
            print(f"cat: {filename}: No such file or directory")

def pwd():
    print(os.getcwd())

def handle_cd(path):
    expanded_path = os.path.expanduser(path)
    try:
        os.chdir(expanded_path)
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")

def find_in_path(executable_name):
    """
    Searches for an executable in the directories listed in the PATH environment variable.
    Returns the full path if found, otherwise None.
    """
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    pathext = os.environ.get('PATHEXT', '').split(os.pathsep)

    for directory in path_dirs:
        # Check exact match first
        full_path = os.path.join(directory, executable_name)
        if os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
            return full_path
        
        # Check with extensions
        for ext in pathext:
            if not ext: continue
            full_path_ext = full_path + ext
            if os.access(full_path_ext, os.X_OK) and not os.path.isdir(full_path_ext):
                return full_path_ext
    return None

def parse_arguments(args):
    """Parses shell arguments handling mixed quotes and whitespace."""
    arguments = []
    current = []
    in_single_quotes = False
    in_double_quotes = False
    i = 0
    
    while i < len(args):
        char = args[i]
        
        if char == "'":
            if in_double_quotes:
                # Inside double quotes, single quote is literal
                current.append(char)
                i += 1
            elif in_single_quotes:
                # Closing single quote
                in_single_quotes = False
                i += 1
            else:
                # Opening single quote
                in_single_quotes = True
                i += 1
        elif char == '"':
            if in_single_quotes:
                # Inside single quotes, double quote is literal
                current.append(char)
                i += 1
            elif in_double_quotes:
                # Closing double quote
                in_double_quotes = False
                i += 1
            else:
                # Opening double quote
                in_double_quotes = True
                i += 1
        elif char == '\\': # Handle backslash escapes
            if in_single_quotes:
                current.append('\\')
                i += 1
            elif in_double_quotes:
                # Inside double quotes, backslash needs to handle \" and \\ and maybe \n but mostly literal otherwise
                if i + 1 < len(args):
                    next_char = args[i+1]
                    if next_char == '"' or next_char == '\\':
                         current.append(next_char)
                         i += 2
                    else:
                        current.append('\\')
                        i += 1
                else:
                    current.append('\\')
                    i += 1
            else:
                # Outside quotes, backslash escapes next char including space
                if i + 1 < len(args):
                    current.append(args[i+1])
                    i += 2
                else:
                    current.append('\\')
                    i += 1
        elif char.isspace():
            if in_single_quotes or in_double_quotes:
                current.append(char)
                i += 1
            else:
                # Argument separator
                if current:
                    arguments.append(''.join(current))
                    current = []
                # Skip whitespace
                while i < len(args) and args[i].isspace():
                    i += 1
        else:
            current.append(char)
            i += 1
            
    if current:
        arguments.append(''.join(current))
        
    return arguments

def handle_echo(args):
    """Handles the echo command."""
    print(' '.join(args))
    
def handle_type(args):
    """Handles the type command."""
    if not args: return
    target = args[0]
    if target in BUILTINS:
        print(f"{target} is a shell builtin")
    else:
        found_path = find_in_path(target)
        if found_path:
            print(f"{target} is {found_path}")
        else:
            print(f"{target}: not found")

def handle_external(command_name, args):
    """Handles execution of external programs."""
    found_path = find_in_path(command_name)
    
    if found_path:
        try:
            # Execute the program with arguments
            # We use the basename for argv[0] as per requirements
            executable_name = os.path.basename(found_path)
            subprocess.run([executable_name] + args, executable=found_path)
        except Exception as e:
            print(f"{command_name}: execution failed: {e}")
    else:
        print(f"{command_name}: command not found")

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command = input()
        except EOFError:
            break
            
        if not command:
            continue
            
        parts = parse_arguments(command)
        if not parts:
            continue
            
        exe_name = parts[0]
        args = parts[1:]

        if exe_name == "exit":
            break
        
        elif exe_name == 'echo':
            handle_echo(args)
        elif exe_name == 'type':
            handle_type(args)
        elif exe_name == 'pwd':
            pwd()
        elif exe_name == 'cat':
            handle_cat(args)
        elif exe_name == 'cd':
            path = args[0] if args else os.path.expanduser("~")
            handle_cd(path)
        else:
            handle_external(exe_name, args)

if __name__ == "__main__":
    main()
