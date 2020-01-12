
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


# Collision Detection between a rect and tiles
def collide(rect, tiles):
    collisions = []
    for t in tiles:
        if rect.colliderect(t):
            collisions.append(t)
    return collisions


# Move rect to position, snaps to collision
def phys_move(rect, vector, tiles):  # Movement in list format [10, 10]
    rect.centerx += int(vector[0])
    collisions = collide(rect, tiles)
    for tile in collisions:
        if vector[0] > 0:
            rect.right = tile.left
        if vector[0] < 0:
            rect.left = tile.right
    rect.centery += int(vector[1])
    collisions = collide(rect, tiles)
    for tile in collisions:
        if vector[1] > 0:
            rect.bottom = tile.top
        if vector[1] < 0:
            rect.top = tile.bottom
    return rect


class Text:
    instances = []

    def __init__(self, string, _color, size, x, y):
        self.string = string
        self.color = _color
        self.size = size
        self.font_obj = pg.font.Font(fontName, self.size)
        self.surf = self.font_obj.render(self.string, True, self.color)
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y

    def draw(self):
        app.blit(self.surf, self.rect)

    @staticmethod
    def draw_all():
        for t in Text.instances:
            t.draw()

    @staticmethod
    def add(text):
        Text.instances.append(text)


class Particle:
    instances = []
    collision = r.entity_collision

    def __init__(self, x, y, size, vector, _color, duration):
        self.width = size
        self.height = size
        self.rect = pg.Rect(0, 0, self.width, self.height)
        self.rect.centerx = x
        self.rect.centery = y
        self.color = _color
        self.vector = vector
        self.duration = duration
        self.created = appTime
        self.isIndefinite = False
        if self.duration < 0:
            self.isIndefinite = True

    def draw(self):
        pg.draw.rect(app, self.color, self.rect)

    def update(self):
        Particle.collision = r.entity_collision
        self.rect.centerx += int(self.vector[0])
        self.rect.centery += int(self.vector[1])
        if len(collide(self.rect, Particle.collision)) > 0:
            Particle.instances.remove(self)
        if appTime - self.created >= self.duration and not self.isIndefinite:
            try:
                Particle.instances.remove(self)
            except ValueError:
                pass
        self.draw()

    @staticmethod
    def draw_all():
        for _p in Particle.instances:
            _p.draw()

    @staticmethod
    def update_all():
        for _p in Particle.instances:
            _p.update()

    @staticmethod
    def random_spawn(x, y, size, _color, duration, amount, intensity):
        for n in range(amount):
            dx = random.randint(-intensity, intensity)
            dy = random.randint(-intensity, intensity)
            while dx == 0 and dy == 0:
                dx = random.randint(-intensity, intensity)
                dy = random.randint(-intensity, intensity)
            test_rect = pg.Rect(x + dx, y + dy, size, size)
            for c in Particle.collision:
                if test_rect.colliderect(c):
                    dx = random.randint(-intensity, intensity)
                    dy = random.randint(-intensity, intensity)
                    test_rect = pg.Rect(x + dx, y + dy, size, size)
            Particle.instances.append(Particle(x, y, size, [dx, dy], _color, duration))

    @staticmethod
    def spawn(x, y, size, vector, _color, duration, amount, intensity):
        for n in range(amount):
            dx = vector[0] + random.randint(-intensity, intensity)
            dy = vector[1] + random.randint(-intensity, intensity)
            while dx == 0 and dy == 0:
                dx = random.randint(-intensity, intensity)
                dy = random.randint(-intensity, intensity)
            Particle.instances.append(Particle(x, y, size, [dx, dy], _color, duration))


class Player:
    collision = r.entity_collision
    instances = []

    def __init__(self, pos):
        self.image = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        self.x = tileGrid * pos[0]
        self.y = tileGrid * pos[1]
        self.up = self.down = self.left = self.right = False
        self.width = tileGrid
        self.height = tileGrid
        self.rect = pg.Rect(self.x + 20, self.y, self.width - 20, self.height)
        self.staffOffset = [54, -6]
        self.acceleration = 1
        self.speed = 6
        self.spell = flare
        self.lastSpell = appTime
        self.chargingSpell = False
        self.chargingStart = 0
        self.chargingTime = 0
        self.user_controlled = True
        self.vector = [0, 0]
        self.viewRadian = 0
        self.viewDegrees = 0
        self.maxHealth = 5
        self.health = self.maxHealth
        self.damageCD = 0.7
        self.lastDamage = appTime
        if self not in Player.instances:
            Player.instances.append(self)

    def draw(self):
        app.blit(self.image, (self.rect.x, self.rect.y))
        for n in range(self.maxHealth):
            app.blit(heartEmpty, (n * tileGrid, 0))
        for n in (range(self.health)):
            app.blit(heartFull, (n * tileGrid, 0))
        print(self.health)

    @staticmethod
    def draw_all():
        for _p in Player.instances:
            _p.draw()

    def move(self):
        # Moves
        self.vector = [0, 0]
        if self.up:
            self.vector[1] -= self.speed
        if self.down:
            self.vector[1] += self.speed
        if self.left:
            self.vector[0] -= self.speed
        if self.right:
            self.vector[0] += self.speed
        if abs(self.vector[0]) + abs(self.vector[1]) > self.speed:
            self.vector[0] *= 0.707
            self.vector[1] *= 0.707
        self.rect = phys_move(self.rect, self.vector, Player.collision)

    @staticmethod
    def move_all():
        for _p in Player.instances:
            _p.move()

    def tp(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self):
        Player.collision = r.entity_collision
        self.x = self.rect[0]
        self.y = self.rect[1]
        self.viewRadian = -math.atan2(mouseLoc[1] - self.rect.centery, mouseLoc[0] - self.rect.centerx)
        self.viewDegrees = math.degrees(self.viewRadian)
        if self.maxHealth > 10:
            self.maxHealth = 10
        for h in r.hazard_rects:
            if self.rect.colliderect(h[0]) and appTime - self.lastDamage > self.damageCD:
                self.lastDamage = appTime
                self.health -= 1
                break
        for e in Enemy.instances:
            if self.rect.colliderect(e.rect) and appTime - self.lastDamage > self.damageCD:
                self.lastDamage = appTime
                self.health -= 1
                break
        # Casts spell
        if mouseHeld:
            self.cast_spell(mouseLoc)

    @staticmethod
    def update_all():
        for p in Player.instances:
            p.update()

    def cast_spell(self, mouse):
        if appTime - self.lastSpell > self.spell.rate and mouseHeld:
            self.spell.cast(self.rect.x + self.staffOffset[0], self.rect.y + self.staffOffset[1], mouse)
            self.lastSpell = appTime


class Spell:
    types = []
    collision = r.spell_collision

    def __init__(self, image, speed, rate, damage, range):
        self.image = image
        self.speed = speed
        self.rate = rate
        self.damage = damage
        self.range = range * tileGrid
        self.width, self.height = self.image.get_size()
        # [rect, vector]
        self.instances = []
        self.charging = []
        Spell.types.append(self)

    def cast(self, x, y, destination):
        radians = math.atan2(destination[1] - y, destination[0] - x)
        start = [x, y]
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        vector = [dx, dy]
        rect = pg.Rect(x, y, self.width, self.height)
        rect.centerx = x
        rect.centery = y
        self.instances.append([rect, vector, start])

    def move(self):
        Spell.collision = r.spell_collision
        for n in self.instances:
            n[0].centerx += int(n[1][0])
            n[0].centery += int(n[1][1])
            if not n[0].colliderect(playArea):
                self.instances.remove(n)
            for c in Spell.collision:
                if n[0].colliderect(c) and n in self.instances:
                    self.instances.remove(n)
            for e in Enemy.instances:
                if n[0].colliderect(e.rect) and n in self.instances:
                    self.instances.remove(n)
                    e.health -= self.damage
            if math.hypot(n[0].centerx - n[2][0], n[0].centery - n[2][1]) > self.range and n in self.instances:
                self.instances.remove(n)

    def draw(self):
        for n in self.instances:
            app.blit(self.image, (n[0].centerx, n[0].centery))

    @staticmethod
    def move_all():
        for s in Spell.types:
            s.move()

    @staticmethod
    def draw_all():
        for s in Spell.types:
            s.draw()


# image, speed, rate, damage, range
flare = Spell(flareSpell, 20, 0.4, 1, 5)


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
