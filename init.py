import math
import os
import random
import sys
import time
import gc
import weakref

import mpu
import pygame as pg
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pygame.locals import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

random.seed()
pg.init()
pg.font.init()


def vector(pos1, pos2):
    radians = math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
    dx = math.cos(radians)
    dy = math.sin(radians)
    return dx, dy


black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

fps = 60
dis_width = 1024
dis_height = 640
app = pg.display.set_mode((dis_width, dis_height))
playArea = pg.Rect(0, 0, dis_width, dis_height)
tileGrid = 64

gridWidth = int(dis_width / tileGrid)
gridHeight = int(dis_height / tileGrid)

fontName = "m3x6.ttf"
roomsDirectory = 'levels'

roomDirectoryList = []
# r=root, d=directories, f = files
for r, d, f in os.walk(roomsDirectory):
    for file in f:
        if '.json' in file:
            roomDirectoryList.append(os.path.join(r, file))

# Props:
chest = pg.image.load('textures/sprites/Props/chest_rare.bmp')

ladder = pg.image.load('textures/sprites/Props/ladder.bmp')

spikeRegular = pg.image.load('textures/sprites/Props/spike_regular.bmp')
spikePoison = pg.image.load('textures/sprites/Props/spike_poison.bmp')
spikeCold = pg.image.load('textures/sprites/Props/spike_cold.bmp')

# Dungeon tile set
floorTile = pg.image.load('textures/tiles/Dungeon/floor.bmp')
drop = pg.image.load('textures/tiles/Dungeon/drop.bmp')
void = pg.image.load('textures/tiles/Dungeon/void.bmp')

fourWalls = pg.image.load('textures/tiles/Dungeon/4walls.bmp')
fourSplit = pg.image.load('textures/tiles/Dungeon/4split.bmp')

southWall = pg.image.load('textures/tiles/Dungeon/1wall.bmp')
northWall = pg.transform.flip(southWall, False, True)
eastWall = pg.transform.rotate(northWall, 90)
westWall = pg.transform.flip(eastWall, True, False)

doubleVertWalls = pg.image.load('textures/tiles/Dungeon/doublewalls.bmp')
doubleHorWalls = pg.transform.rotate(doubleVertWalls, 90)

doubleCorner1 = pg.image.load('textures/tiles/Dungeon/doublecorner.bmp')
doubleCorner2 = pg.transform.flip(doubleCorner1, True, False)
doubleCorner3 = pg.transform.flip(doubleCorner1, False, True)
doubleCorner4 = pg.transform.flip(doubleCorner2, False, True)

extCorner1 = pg.image.load('textures/tiles/Dungeon/extcorner.bmp')
extCorner2 = pg.transform.flip(extCorner1, True, False)
extCorner3 = pg.transform.flip(extCorner1, False, True)
extCorner4 = pg.transform.flip(extCorner2, False, True)

extDoubleCorner1 = pg.image.load('textures/tiles/Dungeon/extdoublecorner.bmp')
extDoubleCorner2 = pg.transform.rotate(extDoubleCorner1, 90)
extDoubleCorner3 = pg.transform.rotate(extDoubleCorner2, 90)
extDoubleCorner4 = pg.transform.rotate(extDoubleCorner3, 90)

intCorner1 = pg.image.load('textures/tiles/Dungeon/intcorner.bmp')
intCorner2 = pg.transform.flip(intCorner1, True, False)
intCorner3 = pg.transform.flip(intCorner1, False, True)
intCorner4 = pg.transform.flip(intCorner2, False, True)

rSplit1 = pg.image.load('textures/tiles/Dungeon/rsplit.bmp')
rSplit2 = pg.transform.flip(rSplit1, True, False)
rSplit3 = pg.transform.flip(rSplit1, False, True)
rSplit4 = pg.transform.flip(rSplit2, False, True)
rSplit5 = pg.transform.rotate(rSplit1, 90)
rSplit6 = pg.transform.flip(rSplit5, True, False)
rSplit7 = pg.transform.flip(rSplit5, False, True)
rSplit8 = pg.transform.flip(rSplit7, True, False)


tSplit1 = pg.image.load('textures/tiles/Dungeon/tsplit.bmp')
tSplit2 = pg.transform.rotate(tSplit1, 90)
tSplit3 = pg.transform.rotate(tSplit2, 90)
tSplit4 = pg.transform.rotate(tSplit3, 90)

upU = pg.image.load('textures/tiles/Dungeon/u.bmp')
downU = pg.transform.flip(upU, False, True)
rightU = pg.transform.rotate(upU, 90)
leftU = pg.transform.flip(rightU, True, False)
########################################################################################################################

isPaused = False

# Sprite imports
fireSpell = pg.image.load("textures/projectiles/flare.bmp").convert_alpha()
evilEye = pg.image.load("textures/sprites/Enemies/eye.bmp").convert_alpha()

# Animations

# Player
playerIdleRight = [pg.image.load("textures/sprites/player/idle/f0.bmp"), pg.image.load("textures/sprites/player/idle/f1.bmp"), pg.image.load("textures/sprites/player/idle/f2.bmp"), pg.image.load("textures/sprites/player/idle/f3.bmp")]
playerIdleLeft = []
for index, item in enumerate(playerIdleRight):
    playerIdleLeft.insert(index, pg.transform.flip(item, True, False))

playerRunningRight = [pg.image.load("textures/sprites/player/run/f0.bmp"), pg.image.load("textures/sprites/player/run/f1.bmp"), pg.image.load("textures/sprites/player/run/f2.bmp"), pg.image.load("textures/sprites/player/run/f3.bmp")]
playerRunningLeft = []
for index, item in enumerate(playerIdleRight):
    playerRunningLeft.insert(index, pg.transform.flip(item, True, False))

# UI imports
heartFull = pg.image.load("textures/ui/full heart.bmp")
heartHalf = pg.image.load("textures/ui/half heart.bmp")
heartEmpty = pg.image.load("textures/ui/heart container.bmp")

tileData = {
    'floor': [floorTile, 1],
    'drop': [drop, 0],
    'void': [void, -1],
    'fourWalls': [fourWalls, -1],
    'fourSplit': [fourSplit, -1],
    'southWall': [southWall, -1],
    'northWall': [northWall, -1],
    'eastWall': [eastWall, -1],
    'westWall': [westWall, -1],
    'doubleVertWalls': [doubleVertWalls, -1],
    'doubleHorWalls': [doubleHorWalls, -1],
    'doubleCorner1': [doubleCorner1, -1],
    'doubleCorner2': [doubleCorner2, -1],
    'doubleCorner3': [doubleCorner3, -1],
    'doubleCorner4': [doubleCorner4, -1],
    'extCorner1': [extCorner1, -1],
    'extCorner2': [extCorner2, -1],
    'extCorner3': [extCorner3, -1],
    'extCorner4': [extCorner4, -1],
    'extDoubleCorner1': [extDoubleCorner1, -1],
    'extDoubleCorner2': [extDoubleCorner2, -1],
    'extDoubleCorner3': [extDoubleCorner3, -1],
    'extDoubleCorner4': [extDoubleCorner4, -1],
    'intCorner1': [intCorner1, -1],
    'intCorner2': [intCorner2, -1],
    'intCorner3': [intCorner3, -1],
    'intCorner4': [intCorner4, -1],
    'rSplit1': [rSplit1, -1],
    'rSplit2': [rSplit2, -1],
    'rSplit3': [rSplit3, -1],
    'rSplit4': [rSplit4, -1],
    'rSplit5': [rSplit5, -1],
    'rSplit6': [rSplit6, -1],
    'rSplit7': [rSplit7, -1],
    'rSplit8': [rSplit8, -1],
    'tSplit1': [tSplit1, -1],
    'tSplit2': [tSplit2, -1],
    'tSplit3': [tSplit3, -1],
    'tSplit4': [tSplit4, -1],
    'upU': [upU, -1],
    'downU': [downU, -1],
    'rightU': [rightU, -1],
    'leftU': [leftU, -1]
}
propData = {
    'spike': spikeRegular,
    'chest': chest,
}
enemyData = {
    'evil_eye': evilEye
}

hazardTiles = ['spike', 'cold spike', 'poison spike']