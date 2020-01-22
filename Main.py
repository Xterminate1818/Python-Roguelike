from init import *
from Entities import *
from LevelEditor import *
from UI import *
# Game init
if __name__ == "__main__":
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
    # Init display
    pg.display.set_caption("Game Project")
    Entity.kill_all()
    # Init player
    p = Player(currentRoom.spawnPoint)

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
                if e.key == K_ESCAPE:
                    activate(paused)
                    isPaused = True
        if pg.mouse.get_pressed()[0]:
            p.attack(mouseLoc)
        if p.hitbox.colliderect(currentRoom.exitRect) and currentRoom.exitOpen:
            currentRoom = Room.get_random()
            p.hitbox.x, p.hitbox.y = currentRoom.spawnPoint
            Movement.collision = currentRoom.collision
        currentRoom.exitOpen = True
        currentRoom.draw()
        Entity.tick_all(currentRoom)
        pg.display.update()
        clock.tick(fps)
