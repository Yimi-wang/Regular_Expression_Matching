import sys
import time
import Thompson_DFA
import Thompson_NFA
import egrep
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python egrep.py MODE PATTERN FILE')
        sys.exit(1)
    mode = int(sys.argv[1])
    pattern = sys.argv[2]
    file = sys.argv[3]
    if mode == 0:
        egrep.egrep(pattern,file)
    if mode == 1:
        Thompson_NFA.main(pattern,file)             
    if mode == 2:
        Thompson_DFA.main(pattern,file)

