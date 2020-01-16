from init import *
from Components import *


class Entity:
    _instances = set()

    def __init__(self, pos, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.width = self.rect.width
        self.height = self.rect.height

        self.dx = 0
        self.dy = 0
        self.speed = 5
        self._instances.add(weakref.ref(self))

    def draw(self):
        app.blit(self.image, self.rect)

    def tick(self, room):
        self.draw()

    def kill(self):
        del self

    @classmethod
    def tick_all(cls, room):
        for i in cls.get_instances():
            i.tick(room)

    @classmethod
    def kill_all(cls):
        for e in cls.get_instances():
            e.kill()

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


class Projectile(Entity):
    _instances = set()
    clsList = []

    def __init__(self, pos, vec, image, speed):
        self.image = image
        super().__init__(pos, self.image)
        self.vector = vec
        self.speed = speed
        self.movement = ProjectileMovement(self.rect, self.vector, self.speed)
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self, room):
        self.rect = self.movement.move()
        if self.rect == 'hit':
            Projectile.clsList.remove(self)
            self.kill()
        else:
            self.draw()

    @classmethod
    def add(cls, p):
        Projectile.clsList.append(p)


class Player(Entity):
    _instances = set()

    def __init__(self, pos):
        self.image = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        super().__init__(pos, self.image)
        self.initTime = time.time()

        self.health = HealthComponent(5, self.rect)

        self.attackOffset = [30, 6]
        self.attackSource = [self.rect.x + self.attackOffset[0], self.rect.y + self.attackOffset[1]]

        self.attackCD = 0.5
        self.lastAttack = self.initTime
        self.attackAvailable = True

        self.abilityCD = 3
        self.lastAbility = self.initTime
        self.abilityAvailable = True

        self.specialCD = 5
        self.lastSpecial = self.initTime
        self.specialAvailable = True
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self, room):
        self.damageAvailable = True if time.time() - self.lastDamage > self.damageCD else False
        self.attackAvailable = True if time.time() - self.lastAttack > self.attackCD else False
        self.abilityAvailable = True if time.time() - self.lastAbility > self.abilityCD else False
        self.specialAvailable = True if time.time() - self.lastSpecial > self.specialCD else False
        self.attackSource = [self.rect.x + self.attackOffset[0], self.rect.y + self.attackOffset[1]]
        Enemy.target = self.rect
        self.draw()
        self.move()

    def attack(self, destination):
        if self.attackAvailable:
            self.lastAttack = time.time()
            vec = vector(self.attackSource, destination)
            Projectile.add(Projectile(self.attackSource, vec, fireSpell, 10))
            self.hitBox = pg.Rect(self.rect[0] + 10, self.rect[1] + 10, self.rect[2] - 10, self.rect[3] - 10)

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


class Enemy(Entity):
    _instances = set()
    clsList = []
    pathMap = []
    target = None

    def __init__(self, pos):
        self.image = evilEye
        super().__init__(pos, self.image)

        self.destination = [-1, -1]
        self.ignore = [-1, -1]
        self.speed = 2

        self.attackCD = 1
        self.lastAttack = time.time()
        self.canAttack = True

        self.range = 10
        self.maxHealth = 3
        self.health = self.maxHealth
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def pathfind(self):
        grid_x = math.floor(self.rect.x / tileGrid)
        grid_y = math.floor(self.rect.y / tileGrid)
        grid = Grid(matrix=Enemy.pathMap)
        start = grid.node(grid_x, grid_y)
        end = grid.node(math.floor(Enemy.target.centerx / tileGrid), math.floor(Enemy.target.centery / tileGrid))
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
        if grid_x == path[0][0] and grid_y == path[0][1] and len(path) > 1:
            path.remove(path[0])
        dest = path[0]
        x = dest[0] * tileGrid
        y = dest[1] * tileGrid
        self.destination = [x, y]

    def tick(self, room):
        self.pathMap = room.pathMap.get()
        self.canAttack = True if time.time() - self.lastAttack > self.attackCD else False
        self.draw()
        self.pathfind()
        self.dx, self.dy = vector((self.rect.x, self.rect.y), self.destination)
        self.dx *= self.speed
        self.dy *= self.speed
        self.move()

    def move(self):
        if self.dx > self.speed:
            self.dx = self.speed
        if self.dx < -self.speed:
            self.dx = -self.speed
        if self.dy > self.speed:
            self.dy = self.speed
        if self.dy < -self.speed:
            self.dy = -self.speed
        dx = self.dx
        dy = self.dy
        if abs(dx) + abs(dy) > self.speed:
            dx *= .707
            dy *= .707
        self.rect.centerx += dx
        collisions = self.check_collision()
        for c in collisions:
            if dx > 0:
                self.rect.right = c.left
            if dx < 0:
                self.rect.left = c.right
        self.rect.centery += dy
        collisions = self.check_collision()
        for c in collisions:
            if dy > 0:
                self.rect.bottom = c.top
            if dy < 0:
                self.rect.top = c.bottom

    def kill(self):
        Enemy.clsList.remove(self)
        del self

    @classmethod
    def spawn(cls, pos):
        Enemy.clsList.append(Enemy(pos))

    @staticmethod
    def matrix_spawn(matrix):
        for y, row in enumerate(matrix):
            for x, col in enumerate(row):
                if col in enemyData:
                    Enemy.spawn([x * tileGrid, y * tileGrid])