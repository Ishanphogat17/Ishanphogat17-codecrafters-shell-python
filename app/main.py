import sys
import os
import subprocess
import shlex
import readline
import atexit

HISTORY_FILE = os.path.expanduser("~/.python_shell_history")

BUILTINS = ['echo', 'type', 'exit', 'pwd', 'history']

def handle_history(args):
    """Handles the history command."""
    if args and args[0] == '-r':
        target_file = HISTORY_FILE
        if len(args) > 1:
            target_file = args[1]
            
        try:
            readline.read_history_file(target_file)
            return
        except FileNotFoundError:
            print(f"history: {target_file}: No such file or directory")
            return

    elif args and args[0] == '-w':
        target_file = HISTORY_FILE
        if len(args) > 1:
            target_file = args[1]
            
        try:
            readline.write_history_file(target_file)
            return
        except FileNotFoundError:
            print(f"history: {target_file}: No such file or directory")
            return

    length = readline.get_current_history_length()
    start_index = 1
    
    if args:
        try:
            n = int(args[0])
            start_index = max(1, length - n + 1)
        except ValueError:
            print(f"history: {args[0]}: numeric argument required")
            return

    for i in range(start_index, length + 1):
        # readline history is 1-indexed
        item = readline.get_history_item(i)
        print(f"{i:>5}  {item}")

def setup_history():
    """Setup history file and load history from it."""
    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, 'w').close()
    readline.read_history_file(HISTORY_FILE)
    atexit.register(save_history)

def save_history():
    """Save history to history file."""
    readline.write_history_file(HISTORY_FILE)

def execute_with_pipes(command_string):
    """Execute a command string that may contain pipes"""
    if '|' not in command_string:
        # No pipes, execute normally
        subprocess.run(command_string, shell=True)
        return
    
    # Split by pipes
    commands = []
    for cmd in command_string.split('|'):
        if cmd.strip():
            commands.append(cmd.strip())
    
    # Create pipeline
    processes = []
    
    # Create all processes
    for i, cmd in enumerate(commands):
        if i == 0:
            # First command
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        elif i == len(commands) - 1:
            # Last command
            p = subprocess.Popen(cmd, shell=True, 
                               stdin=processes[-1].stdout,
                               stdout=None)  # Output to terminal
        else:
            # Middle command
            p = subprocess.Popen(cmd, shell=True,
                               stdin=processes[-1].stdout,
                               stdout=subprocess.PIPE)
        
        processes.append(p)
        if i > 0:
            # Close previous stdout in current process
            processes[i-1].stdout.close()
    
    # Wait for all processes
    for p in processes:
        p.wait()


def get_path_executables():
    """Scans directories in PATH for executable files."""
    executables = set()
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    pathext = os.environ.get('PATHEXT', '').split(os.pathsep) if os.name == 'nt' else ['']

    for directory in path_dirs:
        if not os.path.isdir(directory):
            continue
        try:
            for filename in os.listdir(directory):

                full_path = os.path.join(directory, filename)
                if os.name == 'nt':
                    # Check if file has an executable extension
                    base, ext = os.path.splitext(filename)
                    if ext.upper() in [e.upper() for e in pathext if e]:
                         executables.add(base) # Add base name for autocomplete
                    elif not ext and filename in executables: # Already added via another extension
                         pass
                    
                    # Also checking specific extensions for strict correctness might be too slow or complex
                    # simpler: just add everything that matches PATHEXT logic
                     
                elif os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                     executables.add(filename)
        except OSError:
            continue
            
    return executables

def completer(text, state):

    # List of commands to autocomplete
    commands = []
    for cmd in BUILTINS:
        commands.append(cmd)
    
    path_execs = list(get_path_executables()) 
    # Add a space to path executables too for consistency
    for cmd in path_execs:
        commands.append(cmd)
    
    all_commands = sorted(list(set(commands))) # Deduplicate and sort
    
    # Filter commands that start with the current text
    matches = []
    for cmd in all_commands:
        if cmd.startswith(text):
            matches.append(cmd)
    
    # Return the match corresponding to the current state
    if state < len(matches):
        # If there is only one match, append a space so the user can type arguments immediately
        if len(matches) == 1:
            return matches[state] + ' '
        return matches[state]
    return None


def setup_autocomplete():
    """Initialize readline with our completer function."""
    # Set the completer function
    readline.set_completer(completer)
    
    # Set the delimiter characters (characters that separate words)
    readline.set_completer_delims(' \t\n')
    
    # Enable tab completion
    readline.parse_and_bind('tab: complete')

def stdout_stderr(args):
    """Handle stdout and stderr redirection with >, 2>, and >> operators"""
    
    try:
        # Check for stdout redirection (1>)
        if "2>>" in args:  # If you want to support stderr append
            cmd_part, file_part = args.split("2>>", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "a") as f: 
                f.write(result.stderr)
            if result.stdout:
                print(result.stdout, end='')
        
        elif "1>>" in args:  # NEW: Handle 1>> (stdout append)
            cmd_part, file_part = args.split("1>>", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "a") as f:
                f.write(result.stdout)
            if result.stderr:
                print(result.stderr, end='')
    
        elif "2>" in args:
            cmd_part, file_part = args.split("2>", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "w") as f: 
                f.write(result.stderr)
            if result.stdout:
                print(result.stdout, end='')
        
        # Check for stdout append redirection (>>)
        elif ">>" in args:
            cmd_part, file_part = args.split(">>", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "a") as f:
                f.write(result.stdout)
            if result.stderr:
                print(result.stderr, end='')
        
        elif "1>" in args:
            cmd_part, file_part = args.split("1>", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "w") as f:
                f.write(result.stdout)
            if result.stderr:
                print(result.stderr, end='')
        
        # Check for stdout overwrite redirection (>)
        elif ">" in args:
            cmd_part, file_part = args.split(">", 1)
            result = subprocess.run(cmd_part.strip(), shell=True, capture_output=True, text=True)
            with open(file_part.strip(), "w") as f:
                f.write(result.stdout)
            if result.stderr:
                print(result.stderr, end='')
        
        # No redirection - FIXED: using args instead of cmd
        else:
            subprocess.run(args, shell=True)
            
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except Exception as e:
        print(f"Error: {e}")
        
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
    setup_history()
    setup_autocomplete()
    while True:
        try:
            command = input("$ ")
        except EOFError:
            break
            
        if not command:
            continue

        if any(op in command for op in ['2>', '>>', '>','1>']):
            stdout_stderr(command)
            continue  

        if '|' in command:
            execute_with_pipes(command)
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
        elif exe_name == 'history':
            handle_history(args)
        else:
            handle_external(exe_name, args)

if __name__ == "__main__":
    main()
