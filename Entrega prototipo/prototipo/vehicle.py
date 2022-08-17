class Vehicle:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.destination = (0,0)

    def __init__(self, x, y, dx, dy, destination):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.destination = destination

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def changeSpeed(self, dx, dy):
        self.dx = dx
        self.dy = dy
