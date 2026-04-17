import os
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
    "git" # Git commands
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

def is_any_unsafe(cmds):
    """
    check if any bash command is unsafe.
    """
    for cmd in cmds:
        if is_unsafe(cmd):
            return True
    return False

def is_unsafe(cmd):
    """
    check if a bash command is unsafe.
    """
    if sys.platform.startswith("win"):
        if any(c in cmd for c in unsafe_commands_windows):
            return True
    else:
        if any(c in cmd for c in unsafe_commands_unix):
            return True
    return False

if __name__ == "__main__":
    cmd = input("Enter a command: ")
    if is_unsafe(cmd):
        print("Unsafe command detected!")
    else:
        print("Command is safe to execute.")