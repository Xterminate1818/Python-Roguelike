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
    MovementComponent.collision = currentRoom.collision
    Enemy.pathMap = currentRoom.pathMap.get()

    # Init clock
    clock = pg.time.Clock()
    start_time = time.time()
    appTime = time.time() - start_time
    # Init display
    pg.display.set_caption("Game Project")
    Entity.kill_all()

    # Init player
    p = Player(currentRoom.spawnPoint)

    # Enemies
    Enemy.matrix_spawn(currentRoom.enemyMap)

    mainMenu = True

    # Game Loop
    while True:
        while mainMenu:
            app.fill(black)

        appTime = time.time() - start_time
        app.fill(black)
        Enemy.target = p.rect
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
        if pg.mouse.get_pressed()[0]:
            p.attack(mouseLoc)
        if p.rect.colliderect(currentRoom.exitRect) and currentRoom.exitOpen:
            currentRoom = Room.get_random()
            p.rect.x, p.rect.y = currentRoom.spawnPoint
            MovementComponent.collision = currentRoom.collision

        MovementComponent.move_all()
        currentRoom.draw()
        Entity.tick_all(currentRoom)
        pg.display.update()
        clock.tick(fps)
