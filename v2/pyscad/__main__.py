import sys

template = """
import pyscad as ps

def build():
    obj = ps.CustomObject()
    obj.x = ps.Cube(10, 10, 10)
    return obj

def main():
    obj = build()
    obj.autorender()

if __name__ == '__main__':
    main()
"""

def main():
    fname = sys.argv[1]
    if not fname.endswith('.py'):
        fname = fname + '.py'
    with open(fname, 'w') as f:
        f.write(template)
    
    print(f'New PySCAD script written to {fname}')


if __name__ == '__main__':
    main()
