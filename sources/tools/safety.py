"""
Best-effort pre-check for agent shell commands.

is_unsafe() catches obvious destructive commands (rm, dd, piping a download
into a shell, ...) before they run. It is NOT a security boundary: obfuscation
such as `$(printf r)m` or variable expansion can bypass it. Real containment is
the Docker privilege drop that runs agent commands as an unprivileged user.
"""

import os
import shlex
import sys

unsafe_commands_unix = [
    "rm",           # File/directory removal
    "dd",           # Low-level disk writing
    "mkfs",         # Filesystem formatting
    "chmod",        # Permission changes
    "chown",        # Ownership changes
    "shutdown",     # System shutdown
    "reboot",       # System reboot
    "halt",         # System halt
    "sysctl",       # Kernel parameter changes
    "kill",         # Process termination
    "pkill",        # Kill by process name
    "killall",      # Kill all matching processes
    "exec",         # Replace process with command
    "tee",          # Write to files with privileges
    "umount",       # Unmount filesystems
    "passwd",       # Password changes
    "useradd",      # Add users
    "userdel",      # Delete users
    "brew",      # Homebrew package manager
    "groupadd",     # Add groups
    "groupdel",     # Delete groups
    "visudo",       # Edit sudoers file
    "screen",       # Terminal session management
    "fdisk",        # Disk partitioning
    "parted",       # Disk partitioning
    "chroot",       # Change root directory
    "route",        # Routing table management
    "--force",     # Force flag for many commands
    "rebase",     # Rebase git repository
    "git",          # Git commands
    "eval",         # Evaluate a string as a command
    "crontab",      # Scheduled jobs (also matches /etc/crontab)
    "-delete",      # find -delete
    "shred",        # Overwrite files
    "truncate",     # Shrink or empty files
    "nc",           # Netcat (reverse shells, exfiltration)
    "ncat",         # Nmap netcat
    "socat",        # Socket relay (reverse shells)
]

unsafe_commands_windows = [
    "del",          # Deletes files
    "erase",        # Alias for del, deletes files
    "rd",           # Removes directories (rmdir alias)
    "rmdir",        # Removes directories
    "format",       # Formats a disk, erasing data
    "diskpart",     # Manages disk partitions, can wipe drives
    "chkdsk /f",    # Fixes filesystem, can alter data
    "fsutil",       # File system utilities, can modify system files
    "xcopy /y",     # Copies files, overwriting without prompt
    "copy /y",      # Copies files, overwriting without prompt
    "move",         # Moves files, can overwrite
    "attrib",       # Changes file attributes, e.g., hiding or exposing files
    "icacls",       # Changes file permissions (modern)
    "takeown",      # Takes ownership of files
    "reg delete",   # Deletes registry keys/values
    "regedit /s",   # Silently imports registry changes
    "shutdown",     # Shuts down or restarts the system
    "schtasks",     # Schedules tasks, can run malicious commands
    "taskkill",     # Kills processes
    "wmic",  # Deletes processes via WMI
    "bcdedit",      # Modifies boot configuration
    "powercfg",     # Changes power settings, can disable protections
    "assoc",        # Changes file associations
    "ftype",        # Changes file type commands
    "cipher /w",    # Wipes free space, erasing data
    "esentutl",     # Database utilities, can corrupt system files
    "subst",        # Substitutes drive paths, can confuse system
    "mklink",       # Creates symbolic links, can redirect access
    "bootcfg"
]

# Windows also checks the unix list: Git for Windows puts rm, git, etc. on PATH.
# Unix skips the windows list: words like format/move/del are not unix commands.
if sys.platform.startswith("win"):
    UNSAFE_COMMANDS = unsafe_commands_unix + unsafe_commands_windows
else:
    UNSAFE_COMMANDS = unsafe_commands_unix

PIPE_INTERPRETERS = {
    "sh", "bash", "zsh", "dash", "ksh", "fish",
    "python", "python3", "perl", "ruby", "node", "php",
}
PIPE_TOKENS = {"|", "|&"}
PAYLOAD_FLAGS = {"-c", "-e", "--command"}
SHELL_PUNCTUATION = "();<>|&`"
SUBSTITUTION_MARKERS = ("$(", "`")
MAX_NESTED_DEPTH = 4

def _tokenize(cmd):
    """
    Split a command into shell words, called by _is_unsafe_at_depth.

    Shell punctuation (`|`, `;`, `&&`, `(`, ...) becomes its own token, so
    `ls;rm x` yields `rm` as a separate word. Quoted text stays one token.
    Unbalanced quotes fall back to a plain whitespace split.

    Args:
        cmd (str): the command line to split.

    Returns:
        list[str]: the tokens.
    """
    lexer = shlex.shlex(cmd, posix=not sys.platform.startswith("win"), punctuation_chars=SHELL_PUNCTUATION)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:
        return cmd.split()

def _matches_denylist(tokens):
    """
    Check tokens against the platform denylist, called by _is_unsafe_at_depth.

    Tokens are basename-normalized so '/bin/rm' and './rm' still match the
    bare 'rm' entry. Multi-token entries (e.g. 'chkdsk /f') match when all
    their parts appear among the tokens regardless of order.

    Args:
        tokens (list[str]): tokens of one command line.

    Returns:
        bool: True if any denylist entry matches.
    """
    norm_tokens = {os.path.basename(t) for t in tokens}
    for entry in UNSAFE_COMMANDS:
        parts = {os.path.basename(p) for p in entry.split()}
        if parts and parts.issubset(norm_tokens):
            return True
    return False

def _pipes_into_interpreter(tokens):
    """
    Detect a pipe into a shell or interpreter (`curl x | sh`), called by _is_unsafe_at_depth.

    Args:
        tokens (list[str]): tokens of one command line.

    Returns:
        bool: True if a token after `|` or `|&` is an interpreter such as sh or python3.
    """
    for previous, token in zip(tokens, tokens[1:]):
        if previous in PIPE_TOKENS and os.path.basename(token) in PIPE_INTERPRETERS:
            return True
    return False

def _is_nested_command(token):
    """
    Tell whether a token may hold a command of its own, called by _is_unsafe_at_depth.

    Quoted payloads such as the argument of `bash -c '...'` or `os.system('...')`
    stay one token; they contain whitespace or shell punctuation. Tokens made
    only of punctuation (`|`, `;`) are not nested commands.

    Args:
        token (str): one token from _tokenize.

    Returns:
        bool: True if the token should be checked again as a command.
    """
    if all(c in SHELL_PUNCTUATION for c in token):
        return False
    return any(c.isspace() or c in SHELL_PUNCTUATION for c in token)

def _nested_payloads(tokens, depth):
    """
    Pick the tokens to re-check as commands, called by _is_unsafe_at_depth.

    At the top level only the code argument of `-c`, `-e` or `--command`,
    and quoted text holding a command substitution (`"$(...)"` or
    backticks, which the shell runs) is re-checked, so
    ordinary quoted text such as `echo "please kill time"` is not flagged.
    Inside such a payload (depth >= 1) every token holding whitespace or
    punctuation is re-checked, which catches `os.system('curl ... | sh')`.

    Args:
        tokens (list[str]): tokens of one command line.
        depth (int): how many payloads deep the tokens are.

    Returns:
        list[str]: tokens to check again as commands.
    """
    if depth > 0:
        return [t for t in tokens if _is_nested_command(t)]
    substitutions = [t for t in tokens if any(m in t for m in SUBSTITUTION_MARKERS)]
    payloads = [
        token for previous, token in zip(tokens, tokens[1:])
        if previous in PAYLOAD_FLAGS and _is_nested_command(token)
    ]
    return substitutions + payloads

def _is_unsafe_at_depth(cmd, depth):
    """
    Check one command line and its code payloads, called by is_unsafe.

    Args:
        cmd (str): the command line to check.
        depth (int): how many payloads deep this call is.

    Returns:
        bool: True if the command or any nested payload looks unsafe.
    """
    tokens = _tokenize(cmd)
    if _matches_denylist(tokens) or _pipes_into_interpreter(tokens):
        return True
    if depth >= MAX_NESTED_DEPTH:
        return False
    return any(_is_unsafe_at_depth(t, depth + 1) for t in _nested_payloads(tokens, depth))

def is_unsafe(cmd):
    """
    Best-effort check whether a shell command looks destructive, called by BashInterpreter.

    Checks the command against the denylist (unix list on unix; unix plus
    windows lists on Windows), flags pipes into a shell or interpreter, and
    re-checks code payloads (e.g. the argument of `bash -c` or `python3 -c`)
    up to MAX_NESTED_DEPTH levels.
    This is NOT a security boundary: obfuscation like `$(printf r)m` or
    variable expansion can bypass it. Real containment is the Docker
    privilege drop.

    Args:
        cmd (str): the command line to check.

    Returns:
        bool: True if the command looks unsafe.
    """
    return _is_unsafe_at_depth(cmd, 0)

if __name__ == "__main__":
    cmd = input("Enter a command: ")
    if is_unsafe(cmd):
        print("Unsafe command detected!")
    else:
        print("Command is safe to execute.")