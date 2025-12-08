import sys
import os
import subprocess

BUILTINS = ['echo', 'type', 'exit', 'pwd']
def pwd(args):
    print(os.getcwd(args))

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
    """Handles the echo command."""
    print(args)

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
        if command == "pwd":
            pwd()
            continue
            
        if command.startswith('echo '):
            handle_echo(command[5:])
        elif command.startswith('type '):
            handle_type(command[5:])
        else:
            parts = command.split()
            exe_name = parts[0]
            exe_args = parts[1:]
            handle_external(exe_name, exe_args)

if __name__ == "__main__":
    main()
