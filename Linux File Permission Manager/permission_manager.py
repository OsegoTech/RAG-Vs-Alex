#!/usr/bin/env python3
"""Linux File Permission Manager - View and modify file/directory permissions."""

import os
import stat
import sys
import argparse
import re


# Symbolic permission bits
PERM_BITS = {
    'r': {'u': stat.S_IRUSR, 'g': stat.S_IRGRP, 'o': stat.S_IROTH},
    'w': {'u': stat.S_IWUSR, 'g': stat.S_IWGRP, 'o': stat.S_IWOTH},
    'x': {'u': stat.S_IXUSR, 'g': stat.S_IXGRP, 'o': stat.S_IXOTH},
}


def get_symbolic_mode(mode: int) -> str:
    """Convert a numeric mode integer to rwxrwxrwx string."""
    bits = [
        ('r', stat.S_IRUSR), ('w', stat.S_IWUSR), ('x', stat.S_IXUSR),
        ('r', stat.S_IRGRP), ('w', stat.S_IWGRP), ('x', stat.S_IXGRP),
        ('r', stat.S_IROTH), ('w', stat.S_IWOTH), ('x', stat.S_IXOTH),
    ]
    return ''.join(c if mode & b else '-' for c, b in bits)


def get_file_type_char(mode: int) -> str:
    if stat.S_ISDIR(mode):
        return 'd'
    if stat.S_ISLNK(mode):
        return 'l'
    if stat.S_ISBLK(mode):
        return 'b'
    if stat.S_ISCHR(mode):
        return 'c'
    if stat.S_ISFIFO(mode):
        return 'p'
    if stat.S_ISSOCK(mode):
        return 's'
    return '-'


def view_permissions(path: str) -> None:
    """Display the current permissions of a file or directory."""
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    file_stat = os.stat(path)
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

    # Human-readable breakdown
    print()
    print("  User  : " + _explain_bits(mode, 'u'))
    print("  Group : " + _explain_bits(mode, 'g'))
    print("  Others: " + _explain_bits(mode, 'o'))


def _explain_bits(mode: int, who: str) -> str:
    parts = []
    if mode & PERM_BITS['r'][who]:
        parts.append('read')
    if mode & PERM_BITS['w'][who]:
        parts.append('write')
    if mode & PERM_BITS['x'][who]:
        parts.append('execute')
    return ', '.join(parts) if parts else 'no permissions'


def apply_numeric_mode(path: str, mode_str: str) -> None:
    """Apply a numeric (octal) permission mode, e.g. '755'."""
    try:
        new_mode = int(mode_str, 8)
    except ValueError:
        print(f"Error: '{mode_str}' is not a valid octal permission (e.g. 755, 644).", file=sys.stderr)
        sys.exit(1)

    if new_mode < 0 or new_mode > 0o7777:
        print("Error: Octal permission must be between 000 and 7777.", file=sys.stderr)
        sys.exit(1)

    os.chmod(path, new_mode)
    print(f"Permissions of '{path}' set to {oct(new_mode)}.")


# Regex for symbolic mode: [ugoa]*[+\-=][rwx]+
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

    # 'a' or empty means all three
    if who_str == '' or who_str == 'a':
        targets = ['u', 'g', 'o']
    else:
        targets = list(who_str)
        # deduplicate while preserving order
        seen = set()
        targets = [t for t in targets if not (t in seen or seen.add(t))]

    current_mode = stat.S_IMODE(os.stat(path).st_mode)
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
            # Clear all bits for this entity first
            all_bits = PERM_BITS['r'][who] | PERM_BITS['w'][who] | PERM_BITS['x'][who]
            new_mode &= ~all_bits
            new_mode |= mask

    os.chmod(path, new_mode)
    print(f"Permissions of '{path}' changed: {oct(current_mode)} -> {oct(new_mode)}.")


def change_permissions(path: str, mode_str: str) -> None:
    """Detect whether mode_str is numeric or symbolic and apply it."""
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Numeric if all digits (treat as octal)
    if re.fullmatch(r'[0-7]{1,4}', mode_str):
        apply_numeric_mode(path, mode_str)
    else:
        apply_symbolic_mode(path, mode_str)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='permission_manager',
        description='Linux File Permission Manager — view and modify file permissions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  View permissions:
    %(prog)s view myfile.txt
    %(prog)s view /etc/hosts

  Change with numeric (octal) mode:
    %(prog)s chmod myfile.txt 755
    %(prog)s chmod secret.txt 600

  Change with symbolic mode:
    %(prog)s chmod myfile.txt u+x       # add execute for owner
    %(prog)s chmod myfile.txt go-w      # remove write from group and others
    %(prog)s chmod myfile.txt a=r       # set read-only for everyone
    %(prog)s chmod myfile.txt u+rw,g=r  # multiple specs (comma-separated)

Symbolic mode format:
  [who][op][perms]
    who  : u (user/owner), g (group), o (others), a (all) — default: a
    op   : + (add), - (remove), = (set exactly)
    perms: r (read), w (write), x (execute)
""",
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
            'Permission mode. Numeric (octal) e.g. 755, 644, or '
            'symbolic e.g. u+x, go-w, a=r. '
            'Comma-separate multiple symbolic specs: u+x,g-w'
        ),
    )

    return parser


def main() -> None:
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'view':
        view_permissions(args.path)

    elif args.command == 'chmod':
        # Support comma-separated symbolic specs like u+x,g-w
        specs = [s.strip() for s in args.mode.split(',')]
        for spec in specs:
            change_permissions(args.path, spec)
        # Show updated permissions after change
        print()
        view_permissions(args.path)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
