import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break
        if command.startswith('echo '):
            message = command[5:]
            print(message)
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
