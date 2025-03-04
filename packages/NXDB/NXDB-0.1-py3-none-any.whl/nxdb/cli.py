import sys
import os
import zlib

def cmd_help():
    print('create [filename] - create a new database')

def require_args(count):
    if len(sys.argv) < count:
        cmd_help()
        sys.exit()

def cmd_create():
    require_args(3)
    filename = sys.argv[2] + '.nxdb'
    if os.path.exists(filename):
        print(f"{filename} already exists")
        sys.exit(1)
    else:
        with open(filename, mode='wb') as file:
            text = zlib.compress('[]'.encode())
            file.write(text)
            file.close()
            print(f"Saved to {filename}")
cmds = {
    'help': cmd_help,
    'create': cmd_create
}

def main():
    require_args(2)
    cmd = sys.argv[1]
    if not cmd or not cmd in cmds:
        cmd_help()
        sys.exit()
    cmds[cmd]()
