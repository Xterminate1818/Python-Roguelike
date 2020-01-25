from Common import *
from Entity import *
from LevelEditor import *
from UI import *
import pygame as pg
from pygame.locals import *
import time

pg.init()

# Main Menu
menuTitle = UI((disWidth / 2, disHeight * .2), (600, 200), 'The Dungeon', None, bg=blue, fg=white)
menuStart = UI((disWidth / 2, disHeight * .55), (400, 100), 'Start Game', 'menuStart', bg=white, fg=black)
menuQuit = UI((disWidth / 2, disHeight * .75), (400, 100), 'Quit Game', 'menuQuit', bg=white, fg=black)

# Pause Menu
pausedResume = UI((disWidth / 2, disHeight * .5), (400, 100), 'Resume', 'pausedResume', bg=white, fg=black)
pausedReturn = UI((disWidth / 2, disHeight * .7), (400, 100), 'Return to Title', 'pausedReturn', bg=white, fg=black)

menu = [
    menuTitle,
    menuStart,
    menuQuit
]

paused = [
    pausedResume,
    pausedReturn
]

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

fps = 60
app = pg.display.set_mode((disWidth, disHeight))
Image.surf = app

# Room init
for r in roomDirectoryList:
    Room.add_instance(r)
currentRoom = Room.get_random()
Movement.collision = currentRoom.collision
isPaused = False
isMainMenu = True
activate(menu)
# Init clock
clock = pg.time.Clock()
start_time = time.time()
appTime = time.time() - start_time
graphics = GraphicsManager(app)
# Init display
pg.display.set_caption("Game Project")
Entity.kill_all()
# Init player
p = Player(currentRoom.spawnPoint, graphics)

# Game Loop
while True:
    while isMainMenu:
        app.fill(black)
        UI.draw()
        pg.display.flip()
        clock.tick(fps / 2)
        for e in pg.event.get():
            if e.type == QUIT:
                pg.quit()
                sys.exit()
            if e.type == UIEvent:
                if e.id == 'menuStart':
                    deactivate(menu)
                    isMainMenu = False
                if e.id == 'menuQuit':
                    pg.quit()
                    sys.exit()
            if e.type == MOUSEBUTTONDOWN:
                mouseLoc = pg.mouse.get_pos()
                UI.click(mouseLoc)
    while isPaused:
        app.fill(black)
        UI.draw()
        pg.display.flip()
        clock.tick(fps / 2)
        for e in pg.event.get():
            if e.type == QUIT:
                pg.quit()
                sys.exit()
            if e.type == UIEvent:
                if e.id == 'pausedResume':
                    deactivate(paused)
                    isPaused = False
                if e.id == 'pausedReturn':
                    deactivate(paused)
                    activate(menu)
                    isMainMenu = True
                    isPaused = False
            if e.type == KEYUP:
                if e.key == K_ESCAPE:
                    deactivate(paused)
                    isPaused = False
            if e.type == MOUSEBUTTONDOWN:
                mouseLoc = pg.mouse.get_pos()
                UI.click(mouseLoc)
    appTime = time.time() - start_time
    app.fill(black)
    # Mouse logic
    mouseLoc = pg.mouse.get_pos()
    for e in pg.event.get():
        if e.type == QUIT:
            pg.quit()
            sys.exit()
        if e.type == KEYDOWN:
            if e.key == K_w:
                p.dy += -1
            if e.key == K_s:
                p.dy += 1
            if e.key == K_a:
                p.dx += -1
            if e.key == K_d:
                p.dx += 1
        if e.type == KEYUP:
            if e.key == K_w:
                p.dy -= -1
            if e.key == K_s:
                p.dy -= 1
            if e.key == K_a:
                p.dx -= -1
            if e.key == K_d:
                p.dx -= 1
            if e.key == K_ESCAPE:
                activate(paused)
                isPaused = True
    if pg.mouse.get_pressed()[0]:
        p.attack(mouseLoc)
    if p.hitbox.colliderect(currentRoom.exitRect) and currentRoom.exitOpen:
        currentRoom = Room.get_random()
        p.hitbox.x, p.hitbox.y = currentRoom.spawnPoint
        Movement.collision = currentRoom.collision
    offset = (disWidth / 2 - p.rect.centerx, disHeight / 2 - p.rect.centery)
    currentRoom.exitOpen = True
    currentRoom.draw()
    Entity.tick_all()
    graphics.draw()
    clock.tick(fps)
