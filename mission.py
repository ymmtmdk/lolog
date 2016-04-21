import image_matcher
import json

class Task:
    def __init__(self, fullname, threshold, filter = (), cond = None):
        self.fullname = fullname
        self.filter = tuple(filter)
        self.threshold = threshold
        self.cond = cond
        self.tmpl = image_matcher.Template(self.tmplfile(), self.maskfile(), self.threshold, self.filter)

    def dir(self):
        return 'res/' + '/'.join(self.fullname.split('/')[:-1])

    def name(self):
        return self.fullname.split('/')[-1]

    def tmplfile(self):
        return self.dir() + '/' + self.name() + '.png'

    def maskfile(self):
        return self.dir() + '/mask_' + self.name() + '.png'

    def match(self, image, offset = None):
        result = image.get(self.filter).match(self.tmpl, self.filter)

        if offset:
            for rect in result:
                rect.shift(offset)

        return result

class Mission:
    def __init__(self, filename):
        self.filename = filename
        self.tasks = {}
        self.result = {}
        with open(self.filename) as f:
            for dic in json.loads(f.read()):
                self.tasks[dic["fullname"]] = Task(**dic)

    def execute(self, image):
        image = image_matcher.FilteredImage(image)

        self.result.clear()

        for name in sorted(self.tasks.keys()):
            self.run_task(image, self.tasks[name])

    def run_task(self, image, task):
        if task.fullname in self.result:
            return self.result[task.fullname]

        res = self.result[task.fullname] = []

        if task.cond:
            for rect in self.run_task(image, self.tasks[task.cond]):
                large_rect = image_matcher.Rect(rect.x-2, rect.y-2, rect.w+4, rect.h+4)
                img = image.crop(large_rect)
                res.extend(task.match(img, large_rect))
        else:
            res.extend(task.match(image))

        return res
