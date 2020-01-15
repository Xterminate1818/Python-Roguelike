from init import *


class Entity:
    _instances = set()
    collision = []

    def __init__(self, pos, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.dx = 0
        self.dy = 0
        self.speed = 5
        self._instances.add(weakref.ref(self))

    def draw(self):
        app.blit(self.image, self.rect)

    def move(self):
        dx = self.dx
        dy = self.dy
        if abs(dx) + abs(dy) > self.speed:
            dx *= .707
            dy *= .707
        self.rect.centerx += dx
        self.rect.centery += dy

    def teleport(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def check_collision(self):
        collisions = []
        for c in Entity.collision:
            if self.rect.colliderect(c):
                collisions.append(c)
        return collisions

    def tick(self):
        self.draw()

    def kill(self):
        del self

    @staticmethod
    def tick_all():
        for i in Entity.get_instances():
            i.tick()

    @staticmethod
    def kill_all():
        for e in Entity.get_instances():
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

    def __init__(self, pos, vec, image, speed):
        self.image = image
        super().__init__(pos, self.image)
        self.vector = vec
        self.speed = speed
        self._instances.add(weakref.ref(self))

    def tick(self):
        self.rect.centerx += self.vector[0] * self.speed
        self.rect.centery += self.vector[1] * self.speed
        self.draw()
        if len(self.check_collision()) > 0:
            self.kill()
        self.draw()

    @classmethod
    def add(cls, p):
        Projectile._instances += p


class Player(Entity):
    _instances = set()

    def __init__(self, pos):
        self.image = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        super().__init__(pos, self.image)
        self.initTime = time.time()

        self.speed = 3.5
        self.maxHealth = 5
        self.health = self.maxHealth

        self.attackOffset = [54, -6]
        self.attackSource = [self.rect.x + self.attackOffset[0], self.rect.y + self.attackOffset[1]]

        self.damageCD = 1.5
        self.lastDamage = self.initTime
        self.damageAvailable = True

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

    def move(self):
        if self.dx > 1:
            self.dx = 1
        if self.dx < -1:
            self.dx = -1
        if self.dy > 1:
            self.dy = 1
        if self.dy < -1:
            self.dy = -1
        dx = self.dx
        dy = self.dy
        if abs(dx) + abs(dy) > 1:
            dx *= .707
            dy *= .707
        self.rect.centerx += dx * self.speed
        collisions = self.check_collision()
        for c in collisions:
            if dx > 0:
                self.rect.right = c.left
            if dx < 0:
                self.rect.left = c.right
        self.rect.centery += dy * self.speed
        collisions = self.check_collision()
        for c in collisions:
            if dy > 0:
                self.rect.bottom = c.top
            if dy < 0:
                self.rect.top = c.bottom

    def tick(self):
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
            Projectile.add(Projectile(self.attackSource, vec, fireSpell, 25))
        self.draw()

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
        self.speed = 5

        self.pathCD = 0.2
        self.lastPath = time.time()
        self.canPath = True

        self.attackCD = 1
        self.lastAttack = time.time()
        self.canAttack = True

        self.range = 10
        self.maxHealth = 3
        self.health = self.maxHealth
        self._instances.add(weakref.ref(self))

    def pathfind(self):
        grid = Grid(self.pathMap)
        start = grid.node(math.floor(self.rect.centerx / tileGrid), math.floor(self.rect.centery / tileGrid))
        end = grid.node(math.floor(Enemy.target.rect.x / tileGrid), math.floor(Enemy.target.rect.y / tileGrid))
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
        if len(path) == 0:
            self.destination = [-1, -1]
        elif path[0][0] * tileGrid != self.ignore[0] and path[0][1] * tileGrid != self.ignore[1]:
            self.destination = path[0]
        elif len(path) > 1:
            self.destination = path[1]

    def tick(self):
        if self.rect.x == self.destination:
            self.ignore = self.destination
        self.canPath = True if time.time() - self.lastPath > self.pathCD else False
        self.canAttack = True if time.time() - self.lastAttack > self.attackCD else False
        if Enemy.target is not None:
            if self.canPath:
                self.pathfind()
            if self.canAttack and abs(self.rect.x - Enemy.target.rect.x) <= self.range \
                    and abs(self.rect.y - Enemy.target.rect.y) <= self.range:
                Enemy.target.health -= 1
                self.lastAttack = time.time()
        self.draw()

    @classmethod
    def spawn(cls, pos):
        Enemy.clsList.append(Enemy(pos))

    @staticmethod
    def matrix_spawn(matrix):
        for y, row in enumerate(matrix):
            for x, col in enumerate(row):
                if col in enemyData:
                    Enemy.spawn([x * tileGrid, y * tileGrid])

