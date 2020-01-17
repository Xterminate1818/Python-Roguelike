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

    @classmethod
    def test_collide(cls, rect):
        col = False
        for i in cls.get_instances():
            if rect.colliderect(i.rect):
                col = True
        return col


class Projectile(Entity):
    _instances = set()
    clsList = []

    def __init__(self, pos, vec, image, speed, ignore):
        self.image = image
        super().__init__(pos, self.image)
        self.vector = vec
        self.speed = speed
        self.damage = Damage(1, 0, ignore)
        self.movement = ProjectileMovement(self.rect, self.vector, self.speed)
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self, room):
        self.rect = self.movement.move()
        if self.rect is not None:
            self.damage.rect(self.rect)
        if not self.movement.alive or Enemy.test_collide(self.rect):
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
        self.lookingRight = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        self.lookingLeft = pg.transform.flip(self.lookingRight, True, False)
        super().__init__(pos, self.lookingRight)
        self.initTime = time.time()

        self.health = Health(5, self.rect, 1)
        self.movement = PhysicsMovement(self.rect, self.speed)
        self.idleRight = Animation(playerIdleRight, 8)
        self.idleLeft = Animation(playerIdleLeft, 8)
        self.movingRight = Animation(playerRunningRight, 8)
        self.movingLeft = Animation(playerRunningLeft, 8)

        self.facing = 'right'

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

        if self.dx > 0:
            self.facing = 'right'
        elif self.dx < 0:
            self.facing = 'left'

        if self.dx == 0 and self.dy == 0:
            if self.facing == 'right':
                frame = self.idleRight.next()
            else:
                frame = self.idleLeft.next()
        else:
            print('run')
            if self.facing == 'right':
                frame = self.movingRight.next()
            else:
                frame = self.movingLeft.next()
        self.movement.dx = self.dx
        self.movement.dy = self.dy
        self.health.hitbox = self.rect
        self.movement.rect = self.rect
        if frame is not None:
            app.blit(frame, self.rect)
        if self.health.health <= 0:
            self.kill()

    def attack(self, destination):
        if self.attackAvailable:
            self.lastAttack = time.time()
            vec = vector(self.attackSource, destination)
            Projectile.add(Projectile(self.attackSource, vec, fireSpell, 10, [self.health]))

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
    target = pg.Rect(0, 0, 0, 0)

    def __init__(self, pos):
        self.image = evilEye
        super().__init__(pos, self.image)

        self.gridX = math.floor(pos[0]/tileGrid)
        self.gridY = math.floor(pos[1]/tileGrid)
        self.targetX = math.floor(Enemy.target.centerx / tileGrid)
        self.targetY = math.floor(Enemy.target.centery / tileGrid)
        self.path = PathFinding(Enemy.pathMap, (self.gridX, self.gridY), (self.targetX, self.targetY))
        self.speed = 4

        self.movement = PhysicsMovement(self.rect, self.speed)
        self.health = Health(3, self.rect, 0)
        self.damage = Damage(1, .7, [self.health])

        self.attackCD = 1
        self.lastAttack = time.time()
        self.canAttack = True

        self.range = 10
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self, room):
        self.canAttack = True if time.time() - self.lastAttack > self.attackCD else False

        self.gridX = math.floor(self.rect.x / tileGrid)
        self.gridY = math.floor(self.rect.y / tileGrid)
        self.path.loc = [self.gridX, self.gridY]
        self.targetX = math.floor(Enemy.target.x / tileGrid)
        self.targetY = math.floor(Enemy.target.y / tileGrid)
        self.path.target = [self.targetX, self.targetY]
        destination = self.path.next_location()
        destination[0] *= tileGrid
        destination[1] *= tileGrid

        self.dx, self.dy = vector((self.rect.x, self.rect.y), destination)
        self.movement.dx = self.dx
        self.movement.dy = self.dy
        self.movement.rect = self.rect
        self.health.hitbox = self.rect
        self.damage.rect(self.rect)
        self.draw()
        if self.health.health <= 0:
            self.kill()

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
