import sys
import json
import subprocess


RUN_SHELL = 'ffprobe -of json -show_frames %s'


class FrameStat:
    def __init__(self):
        self.gop = 0
        self.framerate = 0
        self.last_dts = 0

    def stat_frame(self, frame):
        try:
            if frame['media_type'] != 'video':
                return

            # calc gop
            if frame['key_frame'] == 1 and self.gop != 0:
                print('gop: %d' % self.gop)
                self.gop = 0
            self.gop += 1

            # calc fps
            if self.last_dts == 0:
                self.last_dts = float(frame['pkt_pts_time'])

            if float(frame['pkt_pts_time']) - self.last_dts > 1:
                print('framerate: %d' % self.framerate)
                self.framerate = 0
                self.last_dts = float(frame['pkt_pts_time'])

            self.framerate += 1
        except Exception as e:
            print(repr(e))


def run_ffprobe(url):
    subp = subprocess.Popen(RUN_SHELL % url, stdout=subprocess.PIPE, shell=True)
    frame = ''
    is_start = False
    while True:
        out = subp.stdout.readline().decode().strip()
        if out == '' and subp.poll() is not None:
            print('cannot pull stream, please check the url')
            break

        if not is_start:
            if out == '{':
                continue
            if out == '"frames": [':
                is_start = True
                continue

        if out == '{':
            frame = out
            continue

        if out == '},':
            frame += out[0]
            yield frame

        frame += out


def main():
    if len(sys.argv) != 2:
        print('run param: check_rtmp_config.py rtmp://xxxx')
        return

    url = sys.argv[1]
    stat = FrameStat()
    for frame in run_ffprobe(url):
        frame_json = json.loads(frame)
        stat.stat_frame(frame_json)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print('Stop ffprobe ...')
