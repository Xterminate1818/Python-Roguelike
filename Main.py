from init import *
from Entities import *
from LevelEditor import *

# Game init
if __name__ == "__main__":
    # Room init
    for r in roomDirectoryList:
        Room.add_instance(r)
    currentRoom = Room.get_random()
    # Init clock
    clock = pg.time.Clock()
    start_time = time.time()
    appTime = time.time() - start_time
    # Init display
    pg.display.set_caption("Game Project")
    Entity.kill_all()
    # Init player
    p = Player(currentRoom.spawnPoint)
    Entity.collision = currentRoom.collision
    # Enemies
    Enemy.matrix_spawn(currentRoom.enemyMap)
    # Mouse variables
    mousePressed = False
    mouseReleased = False
    mouseHeld = False
    mouseLast = False

    # Game Loop
    while True:
        appTime = time.time() - start_time
        app.fill(black)
        # Mouse logic
        mouseLoc = pg.mouse.get_pos()
        mouseGridLoc = [math.floor(mouseLoc[0] / tileGrid), math.floor(mouseLoc[1] / tileGrid)]
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
            mousePressed = False
            mouseReleased = False
            mouseHeld = False
            if pg.mouse.get_pressed()[0] == 1:
                mouseHeld = True
            if pg.mouse.get_pressed()[0] == 1 and not mouseLast:
                mousePressed = True
            if pg.mouse.get_pressed()[0] == 0 and mouseLast:
                mouseReleased = True
            mouseLast = pg.mouse.get_pressed()

        if p.rect.colliderect(currentRoom.exitRect) and currentRoom.exitOpen:
            currentRoom = Room.get_random()
            p.rect.x, p.rect.y = currentRoom.spawnPoint

        currentRoom.draw()
        Entity.tick_all()
        pg.display.update()
        clock.tick(fps)
