import subprocess

for n in range(0, 3):
    procs = []
    for subtask in range(32 * n, 32 * (n + 1)):
        if subtask >= 95:
            continue
        proc = subprocess.Popen(
            ['C:/Users/PC/AppData/Local/Programs/Python/Python313/python.exe', './brute.py', str(subtask)]
        )
        procs.append(proc)
    for proc in procs:
        proc.wait()