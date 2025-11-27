import sys
import os

BUILTINS = ['echo', 'type','error']
DIRS = os.environ['PATH'].split(os.pathsep)
#print(DIRS)
def main():
    # TODO: Uncomment the code below to pass the first stage
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break
        if command.startswith('echo '):
            message = command[5:]
            #print(f"{command}: command not found")
            print(message)

        elif command.startswith('type '):
            message = command[5:]
            if message in BUILTINS:
                print(f"{message} is a shell builtin")
            else:
                found = False
                pathext = os.environ.get('PATHEXT', '').split(os.pathsep)
                for dir in DIRS:
                    # Check exact match first (for files that already have extension)
                    full_path = f"{dir}/{message}"
                    if os.access(full_path, os.X_OK):
                        print(f"{message} is a {full_path}")
                        found = True
                        break
                    
                    # Check with extensions
                    for ext in pathext:
                        full_path_ext = f"{dir}/{message}{ext}"
                        if os.access(full_path_ext, os.X_OK):
                            print(f"{message} is a {full_path_ext}")
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    print(f"{message}: not found")
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
