import re
import time
def egrep(pattern, file):
     
    with open(file, 'r', encoding='utf-8') as f:
        lines = [line.replace('\n', '') for line in f.readlines()]

    start_time = time.time()
    for i, line in enumerate(lines, start=1):
        if(re.search(pattern, line)):
            print(f'{i}: {line}', end='\n')       

    end_time = time.time()
    print('\nProgram run time:', end_time - start_time, 'seconds')