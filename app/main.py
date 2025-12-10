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
                 current.append(char)
                 i += 1
             elif in_double_quotes:
                 # In double quotes, backslash escapes specific chars, but for this level
                 # we might just treat it as literal or simple escape. 
                 # Given the test failure "hello's", we just need quote separation.
                 # Let's simple-handle: if next is special, escape it?
                 # Actually, shell behavior: \ inside "" only escapes $ ` " \ and newline.
                 # Example failure suggests simple quote handling first.
                 # Let's append literal backslash unless we strictly need escape logic.
                 # But wait, `shlex` handles this. The user used `shlex` for cat. 
                 # Can we just use `shlex`?
                 # `shlex.split` handles quotes effectively.
                 # If allowed, replacing naive loop with `shlex.split` is best.
                 # The user imported `shlex`.
                 # Let's try manual first to be safe with specific "echo" behavior if needed, 
                 # but correct logic is:
                 current.append(char)
                 i += 2
             else:
                 # Outside quotes, backslash escapes next char including space
                 if i + 1 < len(args):
                     current.append(args[i+1])
                     i += 2
                 else:
                     current.append(char)
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
    """Handles the echo command with proper quote parsing."""
    arguments = parse_arguments(args)
    print(' '.join(arguments))
    
def handle_type(args):
    """Handles the type command."""
    target = args
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

        if command == "exit":
            break
        
        if command.startswith('echo '):
            handle_echo(command[5:])
        elif command.startswith('type '):
            handle_type(command[5:])
        elif command == 'pwd':
            pwd()
        elif command.startswith('cat '):
            args = shlex.split(command[4:])
            handle_cat(args)
        elif command.startswith("cd "):
            path = command[3:].strip()
            if not path:  # Empty path
                path = os.path.expanduser("~")
            
            handle_cd(path)
        else:
            parts = command.split()
            exe_name = parts[0]
            exe_args = parts[1:]
            handle_external(exe_name, exe_args)

if __name__ == "__main__":
    main()
