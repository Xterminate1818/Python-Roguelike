from Common import *
import pygame as pg
import math
import time
from tkinter import *
from tkinter import filedialog, messagebox
import mpu
from pygame.locals import *
import weakref
from opensimplex import OpenSimplex
pg.init()

room = [[]]
random.seed(time.time())


class Room:
    _instances = set()
    clsList = []

    def __init__(self, _file, manager):
        self.manager = manager
        self.file = mpu.io.read(_file)
        self.dict = dict(self.file)

        self.tileMap = Matrix(gridWidth, gridHeight)
        self.tileMap.replace(self.dict['tileMap'])
        self.propMap = Matrix(gridWidth, gridHeight)
        self.propMap.replace(self.dict['propMap'])
        self.enemyMap = Matrix(gridWidth, gridHeight)
        self.enemyMap.replace(self.dict['enemyMap'])
        self.pathMap = Matrix(gridWidth, gridHeight)
        self.pathMap.fill(1)

        if len(self.tileMap) != len(self.propMap) != len(self.enemyMap):
            raise ValueError('Map sizes are not uniform (y dimension)')
        if len(self.tileMap[0]) != len(self.propMap[0]) != len(self.enemyMap[0]):
            raise ValueError('Map sizes are not uniform (x dimension)')

        self.width = len(self.tileMap)
        self.height = len(self.tileMap[0])

        self.spawnPoint = self.dict['spawn']
        self.spawnPoint[0] *= tileGrid
        self.spawnPoint[1] *= tileGrid

        self.exitPoint = self.dict['exit']
        self.exitPoint[0] *= tileGrid
        self.exitPoint[1] *= tileGrid
        self.exitRect = pg.Rect(self.exitPoint[0], self.exitPoint[1], tileGrid, tileGrid)
        self.exitOpen = False

        self.collision = []
        for y, row in enumerate(self.tileMap.grid):
            for x, col in enumerate(row):
                if tileData[col][1] < 1:
                    self.collision.append(pg.Rect(x * tileGrid, y * tileGrid, tileGrid, tileGrid))
                    self.pathMap.set(x, y, 0)
        self._instances.add(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @staticmethod
    def get_random():
        instances = []
        for i in Room.get_instances():
            instances.append(i)
        return random.choice(instances)

    @classmethod
    def add_instance(cls, file, manager):
        cls.clsList.append(Room(file, manager))

    def draw(self):
        for y, row in enumerate(self.tileMap):
            for x, col in enumerate(row):
                self.manager.push_bg(tileData[col][0], [x * tileGrid, y * tileGrid])
        if self.exitOpen:
            self.manager.push_bg(stairs, self.exitRect)


def generate_map():
    global xSizeEntry, ySizeEntry, iterationsEntry, room
    xSize = int("".join(num for num in xSizeEntry.get() if num.isdigit()))
    ySize = int("".join(num for num in ySizeEntry.get() if num.isdigit()))
    iter = int("".join(num for num in iterationsEntry.get() if num.isdigit()))
    simplex = OpenSimplex(seed=random.getrandbits(100))
    room = [[]]
    room = [[int(round((simplex.noise2d(x / iter, y / iter) + 1) / 2)) for x in range(xSize)] for y in range(ySize)]
    del simplex
    app.fill((255, 255, 255))
    for y, row in enumerate(room):
        for x, col in enumerate(row):
            if col == 1:
                relx = round(500 / len(row))
                rely = round(500 / len(room))
                pg.draw.rect(app, (0, 0, 0), (x * relx, y * rely, relx, rely))
    pg.display.flip()


# Pygame window
app = pg.display.set_mode((500, 500))
pg.display.set_caption("Preview")
app.fill((255, 255, 255))


# Tkinter window
root = Tk()
root.resizable(False, False)
root.title("Level Setup")
sizeLabel = Label(root, text='Generate Room:', font=("Times New Roman", 20))
sizeLabel.grid(row=0, column=0, columnspan=2)
xSizeLabel = Label(root, text='Width:', font=("Times New Roman", 20))
xSizeLabel.grid(row=1, column=0)
xSizeEntry = Entry(root)
xSizeEntry.grid(row=1, column=1)
ySizeLabel = Label(root, text='Height:', font=("Times New Roman", 20))
ySizeLabel.grid(row=2, column=0)
ySizeEntry = Entry(root)
ySizeEntry.grid(row=2, column=1)
iterationLabel = Label(root, text='Iterations:', font=("Times New Roman", 20))
iterationLabel.grid(row=3, column=0)
iterationsEntry = Entry(root)
iterationsEntry.grid(row=3, column=1)
generateButton = Button(root, text='Generate Level', relief='groove', font=("Times New Roman", 16), command=generate_map)
generateButton.grid(row=4, column=0, columnspan=2, pady=10)


while True:
    try:
        root.update()
        if len(xSizeEntry.get()) == 0 or len(ySizeEntry.get()) == 0 or len(iterationsEntry.get()) == 0:
            generateButton.config(state=DISABLED)
        else:
            generateButton.config(state=NORMAL)
    except TclError:
        exit()
    for e in pg.event.get():
        if e.type == QUIT:
            pg.quit()
            root.destroy()
            sys.exit()
    pg.display.flip()

