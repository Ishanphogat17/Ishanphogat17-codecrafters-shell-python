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

def handle_echo(args):
    """Handles the echo command with proper quote parsing."""
    arguments = []
    current = []
    in_quotes = False
    i = 0
    
    while i < len(args):
        if args[i] == "'":
            if not in_quotes:
                # Start of quoted section
                in_quotes = True
                i += 1
            else:
                # Inside quotes, check if it's an empty quote pair
                if i + 1 < len(args) and args[i + 1] == "'":
                    # Skip empty quotes
                    i += 2
                else:
                    # End of quoted section
                    in_quotes = False
                    i += 1
        elif args[i].isspace() and not in_quotes:
            # End of current argument
            if current:
                arguments.append(''.join(current))
                current = []
            # Skip all spaces between arguments
            while i < len(args) and args[i].isspace():
                i += 1
        else:
            current.append(args[i])
            i += 1
    
    # Don't forget the last argument
    if current:
        arguments.append(''.join(current))
    
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
