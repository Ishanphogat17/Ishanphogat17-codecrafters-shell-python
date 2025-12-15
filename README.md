# Python Shell Implementation

This project implements a custom shell in Python, designed to mimic core functionalities of standard Unix shells like Bash or Zsh. It supports built-in commands, external program execution, piping, redirection, and persistent command history.

## Features

### 1. Built-in Commands
The shell supports the following built-in commands:
- **`echo [args...]`**: Prints arguments to the standard output.
- **`exit [n]`**: Exits the shell (optionally with a status code).
- **`type [name]`**: Displays information about command type (builtin or external path).
- **`pwd`**: Prints the current working directory.
- **`cd [path]`**: Changes the current working directory. Supports `~` expansion.
- **`history [n | -a/-r/-w file]`**: Manages command history.

### 2. Command History
The shell provides robust history management using `readline`:
- **Persistence**: History is automatically saved to `~/.python_shell_history` or the file specified by the `HISTFILE` environment variable.
- **Auto-load/save**: History is loaded on startup and saved on exit.
- **Commands**:
  - `history`: List full history.
  - `history <n>`: List the last `<n>` commands.
  - `history -a <file>`: Append new session commands to `<file>`.
  - `history -r <file>`: Reload history from `<file>`.
  - `history -w <file>`: Write current history to `<file>`.

### 3. Redirection
Supports standard I/O redirection operators:
- `>`: Overwrite standard output to a file.
- `>>` or `1>>`: Append standard output to a file.
- `2>`: Overwrite standard error to a file.
- `2>>`: Append standard error to a file.

### 4. Piping
Basic support for chaining commands using pipes (`|`):
- Connects the stdout of one command to the stdin of the next.
- Works with both built-ins and external programs.

### 5. Autocomplete
- Tab completion is enabled for:
  - Built-in commands.
  - Executable files found in the system `PATH`.

## Setup & specific behaviors
- **Windows Support**: Includes fallbacks for `readline` functions like `append_history_file` which are not natively available on Windows.
- **Robustness**: Gracefully handles invalid `HISTFILE` paths by falling back to defaults.

## Usage
Run the shell by executing the `main.py` script:
```bash
python app/main.py
```
Or with a custom history file:
```bash
HISTFILE=my_history.txt python app/main.py
```
