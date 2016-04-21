import mission

class MatchedNumber:
    def __init__(self, rect, n):
        self.rect = rect
        self.n = n

class LodNumber:
    def __init__(self, y):
        self.numbers = {}
        self.y = y

    def append(self, mn):
        self.numbers[mn.rect.x] = mn

    def valid(self, mn, prev):
        if prev:
            if prev.n == 1:
                return 11 <= mn.rect.x-prev.rect.x <= 14
            else:
                return 17 <= mn.rect.x-prev.rect.x <= 21
        else:
            return True

    def value(self):
        ary = sorted(self.numbers.values(), key=lambda e:e.rect.x)
        n = 0
        prev = None
        for mn in ary:
            n = n*10 + mn.n
            if not self.valid(mn, prev):
                n = 0
            prev = mn

        return n

class LodInfo:
    def __init__(self, frame, mission, image):
        self.frame = frame
        self.mission = mission
        self.image = image
        self.y_numbers = {}
        self.crit = False
        self.miss = False
        self.number = None
        self.analyze()

    def strip(self):
        self.image = None

    def store_number(self, m):
        for i in range(-1,2):
            ry = m.rect.y+i
            if not ry in self.y_numbers:
                self.y_numbers[ry] = LodNumber(m.rect.y)

            self.y_numbers[ry].append(m)

    def analyze(self):
        self.mission.execute(self.image)
        m = self.mission

        self.miss = bool(m.result["miss"])

        for n in range(10):
            for rect in m.result["gold/num_%d" % n]:
                self.store_number(MatchedNumber(rect, n))

            for rect in m.result["white/num_%d" % n]:
                self.store_number(MatchedNumber(rect, n))

        if not self.y_numbers:
            return

        self.number = max(self.y_numbers.values(), key=lambda e:e.value())
        self.crit = any(19 <= self.number.y-rect.y <= 21 for rect in m.result["crit"])

    def info_str(self):
        damage = 0
        if self.number:
            damage = self.number.value()

        return "frame,%d,damage,%d,critical,%s,miss,%s" % (self.frame, damage, self.crit, self.miss)
