import sys
from rust import RustDemangler

def main():
    inp_str = sys.argv[1]
    robj = RustDemangler()

if __name__ == '__main__':
    main(sys.argv[1])