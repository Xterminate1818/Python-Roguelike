from Common import *
import pygame as pg
import math
from tkinter import *
from tkinter import filedialog, messagebox
import mpu
from pygame.locals import *
import weakref
pg.init()


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


tile_list = []
for t in tileData:
    if tileData[t][1] != -1:
        tile_list.append(t)

prop_list = [None]
for p in propData:
    prop_list.append(p)

enemy_list = [None]
for e in enemyData:
    enemy_list.append(e)

# Tkinter window
root = Tk()
root.title("Editor")
root.geometry('500x500')
sizeLabel = Label(root, text='Generate Room:', font=("Times New Roman", 30))
xSizeLabel = Label(root, text='X size', font=("Times New Roman", 20))
xSizeEntry = Entry(root)
ySizeLabel = Label(root, text='Y size', font=("Times New Roman", 20))
ySizeEntry = Entry(root)
sizeLabel.place(relx=.5, rely=.2, anchor='center')
xSizeLabel.place(relx=.3, rely=.35, anchor='center')
xSizeEntry.place(relx=.3, rely=.45, anchor='center')
ySizeLabel.place(relx=.7, rely=.35, anchor='center')
ySizeEntry.place(relx=.7, rely=.45, anchor='center')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.mainloop()

