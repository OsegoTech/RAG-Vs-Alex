#!/usr/bin/env python3
"""Linux File Permission Manager - View and modify file/directory permissions."""

import os
import stat
import sys
import argparse
import re

# ---------------------------------------------------------------------------
# Permission bit mapping
# ---------------------------------------------------------------------------

PERM_BITS = {
    'r': {'u': stat.S_IRUSR, 'g': stat.S_IRGRP, 'o': stat.S_IROTH},
    'w': {'u': stat.S_IWUSR, 'g': stat.S_IWGRP, 'o': stat.S_IWOTH},
    'x': {'u': stat.S_IXUSR, 'g': stat.S_IXGRP, 'o': stat.S_IXOTH},
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_symbolic_mode(mode: int) -> str:
    """Convert a numeric mode integer to rwxrwxrwx string."""
    bits = [
        ('r', stat.S_IRUSR), ('w', stat.S_IWUSR), ('x', stat.S_IXUSR),
        ('r', stat.S_IRGRP), ('w', stat.S_IWGRP), ('x', stat.S_IXGRP),
        ('r', stat.S_IROTH), ('w', stat.S_IWOTH), ('x', stat.S_IXOTH),
    ]
    return ''.join(c if mode & b else '-' for c, b in bits)


def get_file_type_char(mode: int) -> str:
    if stat.S_ISDIR(mode):  return 'd'
    if stat.S_ISLNK(mode):  return 'l'
    if stat.S_ISBLK(mode):  return 'b'
    if stat.S_ISCHR(mode):  return 'c'
    if stat.S_ISFIFO(mode): return 'p'
    if stat.S_ISSOCK(mode): return 's'
    return '-'


def _explain_bits(mode: int, who: str) -> str:
    parts = []
    if mode & PERM_BITS['r'][who]: parts.append('read')
    if mode & PERM_BITS['w'][who]: parts.append('write')
    if mode & PERM_BITS['x'][who]: parts.append('execute')
    return ', '.join(parts) if parts else 'no permissions'


def _stat(path: str):
    """Wrapper around os.stat() with informative error messages."""
    try:
        return os.stat(path)
    except FileNotFoundError:
        print(f"Error: '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied — cannot access '{path}'.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Core commands
# ---------------------------------------------------------------------------

def view_permissions(path: str) -> None:
    """Display the current permissions of a file or directory."""
    file_stat = _stat(path)
    mode = file_stat.st_mode
    octal_perm = oct(stat.S_IMODE(mode))
    symbolic = get_file_type_char(mode) + get_symbolic_mode(mode)

    owner_uid = file_stat.st_uid
    group_gid = file_stat.st_gid

    try:
        import pwd, grp
        owner = pwd.getpwuid(owner_uid).pw_name
        group = grp.getgrgid(group_gid).gr_name
    except (KeyError, ImportError):
        owner = str(owner_uid)
        group = str(group_gid)

    print(f"File   : {path}")
    print(f"Type   : {'directory' if stat.S_ISDIR(mode) else 'file'}")
    print(f"Mode   : {symbolic}  ({octal_perm})")
    print(f"Owner  : {owner} (uid={owner_uid})")
    print(f"Group  : {group} (gid={group_gid})")
    print()
    print("  User  : " + _explain_bits(mode, 'u'))
    print("  Group : " + _explain_bits(mode, 'g'))
    print("  Others: " + _explain_bits(mode, 'o'))


def apply_numeric_mode(path: str, mode_str: str) -> None:
    """Apply a numeric (octal) permission mode, e.g. '755'."""
    try:
        new_mode = int(mode_str, 8)
    except ValueError:
        print(f"Error: '{mode_str}' is not a valid octal permission (e.g. 755, 644).",
              file=sys.stderr)
        sys.exit(1)

    if not (0 <= new_mode <= 0o7777):
        print("Error: Octal permission must be between 000 and 7777.", file=sys.stderr)
        sys.exit(1)

    _chmod(path, new_mode)
    print(f"Permissions of '{path}' set to {oct(new_mode)}.")


SYMBOLIC_RE = re.compile(r'^([ugoa]*)([+\-=])([rwx]+)$')


def apply_symbolic_mode(path: str, mode_str: str) -> None:
    """Apply a symbolic permission change, e.g. 'u+x', 'go-w', 'a=r'."""
    match = SYMBOLIC_RE.match(mode_str)
    if not match:
        print(
            f"Error: '{mode_str}' is not a valid symbolic mode.\n"
            "  Format: [ugoa][+/-/=][rwx]  (e.g. u+x, go-w, a=r, o+rx)",
            file=sys.stderr,
        )
        sys.exit(1)

    who_str, op, perms = match.groups()

    if who_str in ('', 'a'):
        targets = ['u', 'g', 'o']
    else:
        seen = set()
        targets = [t for t in who_str if not (t in seen or seen.add(t))]

    current_mode = stat.S_IMODE(_stat(path).st_mode)
    new_mode = current_mode

    for who in targets:
        mask = 0
        for perm in perms:
            mask |= PERM_BITS[perm][who]

        if op == '+':
            new_mode |= mask
        elif op == '-':
            new_mode &= ~mask
        elif op == '=':
            all_bits = PERM_BITS['r'][who] | PERM_BITS['w'][who] | PERM_BITS['x'][who]
            new_mode = (new_mode & ~all_bits) | mask

    _chmod(path, new_mode)
    print(f"Permissions of '{path}' changed: {oct(current_mode)} -> {oct(new_mode)}.")


def _chmod(path: str, mode: int) -> None:
    """Wrapper around os.chmod() with informative error messages."""
    try:
        os.chmod(path, mode)
    except PermissionError:
        print(
            f"Error: Permission denied — cannot change permissions of '{path}'.\n"
            "  Try running with sudo.",
            file=sys.stderr,
        )
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def change_permissions(path: str, mode_str: str) -> None:
    """Route to numeric or symbolic handler based on mode_str format."""
    # Stat the file early so errors are reported before any change attempt
    _stat(path)

    if re.fullmatch(r'[0-7]{1,4}', mode_str):
        # Valid octal string
        apply_numeric_mode(path, mode_str)
    elif re.fullmatch(r'[0-9]{1,4}', mode_str):
        # Looks like a number but contains 8 or 9 — invalid octal
        print(
            f"Error: '{mode_str}' is not a valid octal mode. "
            "Octal digits are 0-7 only (e.g. 755, 644, 600).",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        apply_symbolic_mode(path, mode_str)

# ---------------------------------------------------------------------------
# Help command
# ---------------------------------------------------------------------------

HELP_TEXT = """
Linux File Permission Manager
==============================

COMMANDS
  view  <path>           Show current permissions of a file or directory.
  chmod <path> <mode>    Change permissions using numeric or symbolic mode.
  help                   Show this help message.

NUMERIC MODE (octal)
  Three or four octal digits representing user/group/others permissions.
  Each digit is the sum of: 4 (read) + 2 (write) + 1 (execute).

  Common examples:
    755  →  rwxr-xr-x  (owner: all;  group/others: read+execute)
    644  →  rw-r--r--  (owner: r/w;  group/others: read only)
    600  →  rw-------  (owner: r/w;  no access for group/others)
    777  →  rwxrwxrwx  (full access for everyone — use with care)

SYMBOLIC MODE
  Format: [who][operator][permissions]

  who        u = user/owner   g = group   o = others   a = all (default)
  operator   + = add          - = remove  = = set exactly
  perms      r = read         w = write   x = execute

  Examples:
    u+x        add execute permission for the owner
    go-w       remove write from group and others
    a=r        set read-only for everyone
    u+rw,g=r   add read/write for owner AND set group to read-only

EXAMPLES
  python3 permission_manager.py view myfile.txt
  python3 permission_manager.py view /var/log

  python3 permission_manager.py chmod myfile.txt 755
  python3 permission_manager.py chmod secret.key 600
  python3 permission_manager.py chmod script.sh u+x
  python3 permission_manager.py chmod data.csv go-w
  python3 permission_manager.py chmod report.txt u+rw,g=r,o-rwx
"""


def show_help() -> None:
    print(HELP_TEXT)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='permission_manager',
        description='Linux File Permission Manager — view and modify file permissions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )

    subparsers = parser.add_subparsers(dest='command', metavar='command')

    # view
    view_p = subparsers.add_parser('view', help='View permissions of a file or directory.')
    view_p.add_argument('path', help='Path to the file or directory.')

    # chmod
    chmod_p = subparsers.add_parser('chmod', help='Change permissions of a file or directory.')
    chmod_p.add_argument('path', help='Path to the file or directory.')
    chmod_p.add_argument(
        'mode',
        help=(
            'Numeric (octal) mode e.g. 755, 644  OR  '
            'symbolic mode e.g. u+x, go-w, a=r.  '
            'Comma-separate multiple symbolic specs: u+x,g-w'
        ),
    )

    # help
    subparsers.add_parser('help', help='Show detailed usage information.')

    return parser


def main() -> None:
    parser = build_parser()

    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'view':
        view_permissions(args.path)

    elif args.command == 'chmod':
        specs = [s.strip() for s in args.mode.split(',')]
        for spec in specs:
            change_permissions(args.path, spec)
        print()
        view_permissions(args.path)

    elif args.command == 'help':
        show_help()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
