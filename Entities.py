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
        self.health = HealthComponent(1, self.rect, 999)
        self.movement = ProjectileMovement(self.rect, self.vector, self.speed)
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self, room):
        self.rect = self.movement.move()
        self.health.hitbox = self.rect
        self.health.damage_rect(self.rect, 999)
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

        # Health, hitbox, damage CD
        self.health = HealthComponent(5, self.rect, 1)
        self.movement = PhysicsMovement(self.rect, self.speed)

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
        self.attackAvailable = True if time.time() - self.lastAttack > self.attackCD else False
        self.abilityAvailable = True if time.time() - self.lastAbility > self.abilityCD else False
        self.specialAvailable = True if time.time() - self.lastSpecial > self.specialCD else False
        self.attackSource = [self.rect.x + self.attackOffset[0], self.rect.y + self.attackOffset[1]]
        Enemy.target = self.rect
        self.movement.dx = self.dx
        self.movement.dy = self.dy
        self.health.hitbox = self.rect
        self.movement.rect = self.rect
        self.draw()
        if self.health.health <= 0:
            self.kill()

    def attack(self, destination):
        if self.attackAvailable:
            self.lastAttack = time.time()
            vec = vector(self.attackSource, destination)
            Projectile.add(Projectile(self.attackSource, vec, fireSpell, 10))

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
        self.speed = 4
        self.movement = PhysicsMovement(self.rect, self.speed)
        self.health = HealthComponent(3, self.rect, 0)

        self.attackCD = 1
        self.lastAttack = time.time()
        self.canAttack = True

        self.range = 10
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
        self.movement.dx = self.dx
        self.movement.dy = self.dy
        self.movement.rect = self.rect
        self.health.hitbox = self.rect

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