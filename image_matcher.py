import numpy
import cv2

class Image:
    def __init__(self, src):
        self.src = src
        self.h, self.w = src.shape[:2]

    def crop(self, rect):
        r = rect
        if r.x == 0 and r.y == 0 and r.w == self.w and r.h == self.h:
            return self

        x1 = max(r.x, 0)
        x2 = min(r.x+r.w, self.w)
        y1 = max(r.y, 0)
        y2 = min(r.y+r.h, self.h)
        img = self.src[y1:y2, x1:x2]
        return Image(img)

    def match(self, target, filter):
        t = target
        result = cv2.matchTemplate(self.src, t.tmpl.get(filter).src, cv2.TM_CCORR_NORMED, mask = t.mask.get(filter).src)
        locs = numpy.where(result > t.threshold)
        locs = zip(*locs[::-1])

        # min,max,minLoc,maxLoc = cv2.minMaxLoc(result)
        # print(t.tmplfile, max, t.threshold, max > t.threshold)
        # max > t.threshold and print(t.tmplfile, max, t.threshold, max > t.threshold)

        m = 1
        if "harf_h" in filter:
            m = 2

        return [MatchedRect(x, y*m, t.w, t.h, result[y][x]) for x, y in locs]

    def filter(self, filter):
        if not filter:
            return self

        src = self.src.copy()
        if "harf_h" in filter:
            src = cv2.resize(src, (self.w,int(self.h/2)))

        if "gray" in filter:
            src = cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)

        return Image(src)

    def from_file(name):
        return Image(cv2.imread(name))

class FilteredImage:
    def __init__(self, image):
        self.image = image
        self.cache = {}

    def get(self, filter):
        if not filter in self.cache:
            self.cache[filter] = self.image.filter(filter)
        return self.cache[filter]

    def crop(self, rect):
        return FilteredImage(self.image.crop(rect))

class Template:
    def __init__(self, tmplfile, maskfile, threshold, filter):
        self.tmplfile = tmplfile
        self.maskfile = maskfile
        self.tmpl = FilteredImage(Image.from_file(tmplfile))
        self.mask = FilteredImage(Image.from_file(maskfile))
        self.threshold = threshold
        self.w, self.h = self.tmpl.image.w, self.tmpl.image.h

class Rect:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w, h

    def tl(self):
        return (self.x, self.y)

    def br(self):
        return (self.x+self.w, self.y+self.h)

    def shift(self, m):
        self.x += m.x
        self.y += m.y

    def __str__(self):
        return "Rect(%d, %d, %d, %d)" % (self.x, self.y, self.w, self.h)

class MatchedRect(Rect):
    def __init__(self, x, y, w, h, value):
        Rect.__init__(self, x, y, w, h)
        self.value = value

    def __str__(self):
        return "MatchedRect(%d, %d, %d, %d, %f)" % (self.x, self.y, self.w, self.h, self.value)
