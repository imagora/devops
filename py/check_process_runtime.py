import re
import subprocess

PROCESS_NAME = ""
SHELL_ALL_PROCESS = "ps axu | grep %s | grep -v grep | awk '{print $2}'"
SHELL_GET_RUNTIME = "ps -o etime %s"


def main():
    pids = subprocess.check_output(SHELL_ALL_PROCESS % PROCESS_NAME, stderr=subprocess.STDOUT, shell=True).decode().split('\n')
    for pid in pids:
        run_time = subprocess.check_output(SHELL_GET_RUNTIME % pid, stderr=subprocess.STDOUT, shell=True).decode()
        params = re.findall('\s+ELAPSED\s+([0-9]+)?\-?([0-9]+)?:?([0-9]+)?:?([0-9]+)', run_time)
        if len(params) == 0:
            print("Cannot parse param: ", run_time)
            continue

        ts = 0
        params = params.pop()
        params = [int(i) for i in params if len(i) > 0]
        if len(params) == 4:
            ts = params[0] * 24 * 3600 + params[1] * 3600 + params[2] * 60 + params[3]
        if len(params) == 3:
            ts = params[0] * 3600 + params[1] * 60 + params[2]
        if len(params) == 2:
            ts = params[0] * 60 + params[1]
        if len(params) == 1:
            ts = params[1]

        if ts > 12 * 3600:
            print('Process %s run for %d' % (pid, ts))


if __name__ == '__main__':
    main()
