import sys
with open('app_new.py', 'rb') as f:
    lines = f.readlines()
    print("ENCODING CHECK:")
    print(lines[100])
    with open('out2.txt', 'wb') as fout:
        fout.write(lines[100])
