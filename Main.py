import init
from init import app
import Entities as Entity
import LevelEditor as Level
from UI import *
import pygame as pg
from pygame.locals import *
import time
# Game init
if __name__ == "__main__":
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    fps = 60
    app = pg.display.set_mode((init.disWidth, init.disHeight))
    # Room init
    for r in Level.roomDirectoryList:
        Level.Room.add_instance(r)
    currentRoom = Level.Room.get_random()
    Entity.Movement.collision = currentRoom.collision
    isPaused = False
    isMainMenu = True
    activate(menu)
    # Init clock
    clock = pg.time.Clock()
    start_time = time.time()
    appTime = time.time() - start_time
    # Init display
    pg.display.set_caption("Game Project")
    Entity.Entity.kill_all()
    # Init player
    p = Entity.Player(currentRoom.spawnPoint)

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
                        quit_game()
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
                if e.key == K_LEFT:
                    offset[0] += 100
                if e.key == K_RIGHT:
                    offset[0] -= 100
                if e.key == K_UP:
                    offset[1] += 100
                if e.key == K_DOWN:
                    offset[1] -= 100
                if e.key == K_ESCAPE:
                    activate(paused)
                    isPaused = True
        if pg.mouse.get_pressed()[0]:
            p.attack(mouseLoc)
        if p.hitbox.colliderect(currentRoom.exitRect) and currentRoom.exitOpen:
            currentRoom = Level.Room.get_random()
            p.hitbox.x, p.hitbox.y = currentRoom.spawnPoint
            Entity.Movement.collision = currentRoom.collision
        init.offset = (disWidth / 2 - p.rect.centerx, disHeight / 2 - p.rect.centery)
        print(disWidth / 2 - p.rect.centerx, disHeight / 2 - p.rect.centery)
        currentRoom.exitOpen = True
        currentRoom.draw()
        Entity.Entity.tick_all(currentRoom)
        pg.display.update()
        clock.tick(fps)
