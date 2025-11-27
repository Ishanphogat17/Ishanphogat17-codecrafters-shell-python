import sys
import os

BUILTINS = ['echo', 'type','error']
DIRS = os.environ['PATH'].split(os.pathsep)
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
            elif message in DIRS:
                for dir in DIRS:
                    if os.access(f"{dir}/{message}", os.X_OK):
                        print(f"{message} is a {dir}/{message}")
                        return
            else:
                print(f"{message}: not found")
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
