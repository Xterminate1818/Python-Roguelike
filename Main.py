from init import *


# Room logic
class Room:
    def __init__(self):
        self.room_list = []
        for dir in roomDirectoryList:
            loaded_level = mpu.io.read(dir)
            self.room_list.append(loaded_level)
        self.current_room = random.choice(self.room_list)
        self.tileMap = self.current_room['tileMap']
        self.propMap = self.current_room['propMap']
        self.enemyMap = self.current_room['enemyMap']
        self.pathMap = emptyPathMap
        self.spawnPoint = self.current_room['spawn']
        self.exitPoint = self.current_room['exit']
        self.exitRect = pg.Rect(self.exitPoint[0] * tileGrid, self.exitPoint[1] * tileGrid, tileGrid, tileGrid)
        self.exit_open = False
        self.entity_collision = []
        self.spell_collision = []
        self.hazard_rects = []
        self.random()

    def random(self):
        _room = random.choice(self.room_list)
        if len(self.room_list) > 1:
            while _room == self.current_room:
                _room = random.choice(self.room_list)
        self.current_room = _room
        self.tileMap = self.current_room['tileMap']
        self.propMap = self.current_room['propMap']
        self.enemyMap = self.current_room['enemyMap']
        self.spawnPoint = self.current_room['spawn']
        self.exitPoint = self.current_room['exit']
        self.exitRect = pg.Rect(self.exitPoint[0] * tileGrid, self.exitPoint[1] * tileGrid, tileGrid, tileGrid)
        self.exit_open = False
        self.entity_collision = []
        self.spell_collision = []
        for y, row in enumerate(self.tileMap):
            for x, col in enumerate(row):
                if col is None:
                    self.pathMap[y][x] = 0
                else:
                    try:
                        self.pathMap[y][x] = tileData[col][1]
                        self.entity_collision.append(pg.Rect(x * tileGrid, y * tileGrid, tileGrid, tileGrid))
                        self.spell_collision.append(pg.Rect(x * tileGrid, y * tileGrid, tileGrid, tileGrid))
                    except KeyError:
                        pass
        self.hazard_rects = []
        for y, row in enumerate(self.propMap):
            for x, col in enumerate(row):
                if col in hazardTiles:
                    self.hazard_rects.append([pg.Rect((x * tileGrid) + 15, (y * tileGrid) + 15,
                                                      tileGrid - 30, tileGrid - 30), col])
                    self.pathMap[y][x] = 0

    def get_spawn(self):
        _x = self.spawnPoint[0] * tileGrid
        _y = self.spawnPoint[1] * tileGrid
        return _x, _y

    def draw(self):
        for y, row in enumerate(self.tileMap):
            for x, col in enumerate(row):
                try:
                    app.blit(tileData[col][0], (x * tileGrid, y * tileGrid))
                except KeyError:
                    pass
        for y, row in enumerate(self.propMap):
            for x, col in enumerate(row):
                try:
                    app.blit(propData[col], (x * tileGrid, y * tileGrid))
                except KeyError:
                    pass
        for t in self.hazard_rects:
            pg.draw.rect(app, black, t[0])
        if len(Enemy.instances) == 0:
            app.blit(ladder, self.exitRect)
            self.exit_open = True
        else:
            self.exit_open = False


r = Room()


class Enemy:
    instances = []
    collision = r.entity_collision
    types = {
        # image, health, speed
        'evil_eye': [evilEye, 5, 4]
    }

    def __init__(self, type, gridx, gridy):
        self.image = Enemy.types[type][0]
        self.type = type
        self.speed = 4
        self.health = 5
        self.vector = [0, 0]
        self.x = gridx * tileGrid
        self.y = gridy * tileGrid
        self.path = []
        self.width, self.height = self.image.get_size()
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.destination = [0, 0]
        self.moveCD = 1
        self.lastMove = appTime

    def draw(self):
        app.blit(self.image, (self.rect.x, self.rect.y))

    def pathfind(self, target):
        # A* algorithm
        grid = Grid(matrix=r.pathMap)
        start = grid.node(math.floor(self.rect.centerx / tileGrid), math.floor(self.rect.centery / tileGrid))
        end = grid.node(math.floor(target.rect.x / tileGrid), math.floor(target.rect.y / tileGrid))
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
        if len(path) > 1:
            self.destination = [path[1][0] * tileGrid, path[1][1] * tileGrid]
        elif len(path) != 0:
            self.destination = [path[0][0] * tileGrid, path[0][1] * tileGrid]

    def move(self):
        radians = math.atan2(self.destination[1] - self.rect.y, self.destination[0] - self.rect.x)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        self.rect = phys_move(self.rect, [dx, dy], [])

    def update(self):
        Enemy.collision = r.entity_collision
        self.x = self.rect.x
        self.y = self.rect.y
        if self.health <= 0:
            Enemy.instances.remove(self)
        if [self.rect.x, self.rect.y] == self.destination or self.path == []:
            self.pathfind(p)

    @staticmethod
    def level_spawn():
        for y, row in enumerate(r.enemyMap):
            for x, col in enumerate(row):
                if col in Enemy.types:
                    Enemy.spawn(str(col), x, y)

    @staticmethod
    def draw_all():
        for z in Enemy.instances:
            z.draw()

    @staticmethod
    def update_all():
        for z in Enemy.instances:
            z.update()

    @staticmethod
    def move_all():
        for z in Enemy.instances:
            z.move()

    @staticmethod
    def spawn(type, gridx, gridy):
        Enemy.instances.append(Enemy(type, gridx, gridy))


# Game init
if __name__ == "__main__":
    # Init clock
    clock = pg.time.Clock()
    start_time = time.time()
    appTime = time.time() - start_time
    # Init display
    pg.display.set_caption("Game Project")
    # Init player
    p = Player(r.spawnPoint)
    # Mouse variables
    mousePressed = False
    mouseReleased = False
    mouseHeld = False
    mouseLast = False
    # Spawn enemies
    Enemy.level_spawn()


    def draw_scene():
        r.draw()
        Player.draw_all()
        Enemy.draw_all()
        Particle.draw_all()
        Spell.draw_all()


    def move_entities():
        Player.move_all()
        Enemy.move_all()
        Spell.move_all()


    def update_scene():
        Player.update_all()
        Enemy.update_all()
        Particle.update_all()


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
                    p.up = True
                if e.key == K_s:
                    p.down = True
                if e.key == K_a:
                    p.left = True
                if e.key == K_d:
                    p.right = True
                # Pause
                if e.key == K_ESCAPE:
                    isPaused = not isPaused
                if e.key == K_SPACE:
                    r.random()
                    p.rect.x, p.rect.y = r.get_spawn()
                    Enemy.level_spawn()

            if e.type == KEYUP:
                if e.key == K_w:
                    p.up = False
                if e.key == K_s:
                    p.down = False
                if e.key == K_a:
                    p.left = False
                if e.key == K_d:
                    p.right = False
                if e.key == K_z:
                    Enemy.spawn('evil_eye', mouseGridLoc[0], mouseGridLoc[1])
                if e.key == K_p:
                    for e in Enemy.instances:
                        print(e.destination)
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

        if not isPaused:
            update_scene()

        if p.rect.colliderect(r.exitRect) and r.exit_open:
            r.random()
            p.rect.x, p.rect.y = r.get_spawn()
            Enemy.level_spawn()

        draw_scene()
        move_entities()
        pg.display.update()
        clock.tick(fps)
