import sys
import os
import subprocess

BUILTINS = ['echo', 'type', 'exit']

def main():
    # Parse PATH environment variable
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    
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
            message = command[5:]
            print(message)

        elif command.startswith('type '):
            target = command[5:]
            if target in BUILTINS:
                print(f"{target} is a shell builtin")
            else:
                found = False
                pathext = os.environ.get('PATHEXT', '').split(os.pathsep)
                
                for directory in path_dirs:
                    # Check exact match first
                    full_path = os.path.join(directory, target)
                    if os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                        print(f"{target} is {full_path}")
                        found = True
                        break
                    
                    # Check with extensions
                    for ext in pathext:
                        if not ext: continue
                        full_path_ext = full_path + ext
                        if os.access(full_path_ext, os.X_OK) and not os.path.isdir(full_path_ext):
                            print(f"{target} is {full_path_ext}")
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    print(f"{target}: not found")
        else:
            parts = command.split()
            exe_name = parts[0]
            exe_args = parts[1:]
            
            found_executable = None
            pathext = os.environ.get('PATHEXT', '').split(os.pathsep)
            
            for directory in path_dirs:
                # Check exact match first
                full_path = os.path.join(directory, exe_name)
                if os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                    found_executable = full_path
                    break
                
                # Check with extensions
                for ext in pathext:
                    if not ext: continue
                    full_path_ext = full_path + ext
                    if os.access(full_path_ext, os.X_OK) and not os.path.isdir(full_path_ext):
                        found_executable = full_path_ext
                        break
                if found_executable:
                    break
            
            if found_executable:
                try:
                    # Execute the program with arguments
                    subprocess.run([found_executable] + exe_args)
                except Exception as e:
                    print(f"{exe_name}: execution failed: {e}")
            else:
                print(f"{exe_name}: command not found")


 
if __name__ == "__main__":
    main()
