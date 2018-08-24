import sys
import subprocess

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
print(sys.path)
print()
print(reqs)

