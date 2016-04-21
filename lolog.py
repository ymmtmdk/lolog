import image_matcher
import mission
import lodinfo
import cv2
import sys
import math
import functools

from datetime import datetime, date, time

from multiprocessing import Pool
import cProfile

class Rogue:
    def __init__(self, mission_name, video_name, start, length, cropping_rect, gui):
        self.mission = mission.Mission(mission_name)
        self.video_name = video_name
        self.gui = gui
        self.start = start
        self.length = length
        self.cropping_rect = cropping_rect
        self.work()

    def show(self, ld_info, image):
        copy = image.src.copy()
        for lod_number in ld_info.y_numbers.values():
            for mn in lod_number.numbers.values():
                cv2.rectangle(image.src, mn.rect.tl(), mn.rect.br(), (255, 0, 0), 1)

        for rect in self.mission.result["crit"]:
            cv2.rectangle(image.src, rect.tl(), rect.br(), (255, 0, 0), 1)
        for rect in self.mission.result["miss"]:
            cv2.rectangle(image.src, rect.tl(), rect.br(), (255, 0, 0), 1)

        cv2.imshow('image', image.src)

        key = cv2.waitKey() & 255
        if ord('q') == key:
            sys.exit(0)
        if ord('s') == key:
            cv2.imwrite("learning/img_%s,.png" % (ld_info.info_str()), copy)

    def work(self):
        cap = cv2.VideoCapture(self.video_name)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start)
        res = []
        for frame_offset in range(self.length):
            _, image = cap.read()
            image = image_matcher.Image(image).crop(self.cropping_rect)
            ld_info = lodinfo.LodInfo(self.start+frame_offset, self.mission, image)
            if ld_info.number:
                print("frame: %d %d" % (self.start+frame_offset, ld_info.number.value()))
            if self.gui:
                self.show(ld_info, image)

            ld_info.strip()
            res.append(ld_info)
        self.infos = res

class Scout:
    class DummyJob:
        def __init__(self, data):
            self.data = data
        def get(self):
            return self.data

    def __init__(self, video_name, start, length, offset_x, offset_y, width, height, processes, gui):
        self.video_name = video_name
        self.start = start

        cap = cv2.VideoCapture(self.video_name)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.length = min(self.frame_count-start, length)

        x = offset_x or 0
        y = offset_y or 0
        w = width or int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) - x
        h = height or int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) - y
        self.cropping_rect = image_matcher.Rect(x, y, w, h)

        self.processes = processes
        if gui:
            self.processes = 1
        self.gui = gui

        self.mission_name = "res/mission.json"

        self.count(self.work())

    def covered_frames(self):
        block_size = math.ceil(self.length/self.processes)
        res = []
        for beg in range(self.start, self.start+self.length, block_size):
            size = min(self.frame_count-beg, block_size)
            res.append((beg, size))
        return res

    def work(self):
        pool = Pool(self.processes)
        jobs = []
        for tpl in self.covered_frames():
            args = [self.mission_name, self.video_name, *tpl, self.cropping_rect, self.gui]
            if self.processes > 1:
                j = pool.apply_async(Rogue, args)
            else:
                j = self.DummyJob(Rogue(*args))
            jobs.append(j)

        return functools.reduce(lambda r,job: r+job.get().infos, jobs, [])

    def count(self, infos):
        def _wait(n):
            return int(n * self.fps / 60)

        blank = 0
        mx = 0
        wait = 0

        dt = datetime.now()
        with open(dt.strftime("log/%Y_%m_%d_%H_%M_%S.csv"), "w") as log:
            def puts(info):
                print(info.info_str())
                log.write(info.info_str() + "\n")

            for info in infos:
                if wait > 0:
                    wait -= 1
                    blank = 0
                    mx = None
                    continue

                if info.number or info.miss:
                    if (info.crit and info.number.value() > 9) or info.miss:
                        puts(info)
                        wait = _wait(10)
                    elif (not mx) or info.number.value() > mx.number.value():
                        blank = 0
                        mx = info
                    else:
                        blank += 1
                else:
                    if mx and mx.number.value() > 9 and blank >= _wait(5):
                        puts(mx)
                        wait = _wait(5)
                    blank += 1

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--start", type="int", default=0, help="set the start time offset")
    parser.add_option("-l", "--length", type="int", default=99999999, help="set the length")
    parser.add_option("-X", "--offset_x", type="int", help="horizontal offset of the crop")
    parser.add_option("-Y", "--offset_y", type="int", help="vertical offset of the crop")
    parser.add_option("--crop_size", help="width and height of the crop")
    parser.add_option("-p", "--processes", type="int", default=cv2.getNumberOfCPUs(), help="num of processes")
    parser.add_option("--gui", action="store_true", help="use the GUI")
    parser.add_option("--profile", action="store_true", help="enable profiling")

    (op, args) = parser.parse_args()

    crop_size = [None, None]
    if op.crop_size:
        crop_size = [int(e) for e in op.crop_size.split('x')]

    if op.profile:
        import cProfile
        cProfile.run('Scout(args[0], op.start, op.length, op.offset_x, op.offset_y, *crop_size, op.processes, op.gui)')
    else:
        Scout(args[0], op.start, op.length, op.offset_x, op.offset_y, *crop_size, op.processes, op.gui)
