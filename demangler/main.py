import sys
from rust import RustDemangler

def main():
    inp_str = input()
    robj = RustDemangler()
    print(robj.demangle(inp_str))

if __name__ == '__main__':
    main()
