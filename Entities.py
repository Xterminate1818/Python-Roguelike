from init import *


class Entity:
    _instances = set()

    def __init__(self, rect, image, collision):
        self.rect = rect
        self.image = image
        self.collision = collision

    def draw(self):
        app.blit(self.image, self.rect)

    def move(self, dx, dy):
        self.rect.centerx += dx
        self.rect.centery += dy

    def teleport(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def check_collision(self):
        collisions = []
        for c in self.collision:
            if self.rect.colliderect(c):
                collisions.append(c)
        return collisions

    def tick(self):
        pass

    def tick_all(self):
        for e in Entity.get_instances():
            e.tick()

    def kill(self):
        del self

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
    collision = []

    def __init__(self, pos, vec, image, speed):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos
        super().__init__(self.rect, self.image, Projectile.collision)
        self.vector = vec
        self.speed = speed

    def tick(self):
        self.rect.centerx += self.vector[0] * self.speed
        self.rect.centery += self.vector[1] * self.speed
        self.draw()
        if len(self.check_collision()) > 0:
            self.kill()

    @staticmethod
    def add(p):
        Projectile._instances += p


class Player(Entity):
    _instances = set()
    collision = []

    def __init__(self, rect):
        self.image = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        super().__init__(rect, self.image, Player.collision)
        self.initTime = time.time()
        self.speed = 10
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

    def move(self, dx, dy):
        self.rect.centerx += int(dx)
        collisions = self.check_collision()
        for c in collisions:
            if dx > 0:
                self.rect.right = c.left
            if dx < 0:
                self.rect.left = c.right
        self.rect.centery += int(dy)
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
        self.draw()

    def attack(self, destination):
        if self.attackAvailable:
            self.lastAttack = time.time()
            vec = vector(self.attackSource, destination)
            Projectile.add(Projectile(self.attackSource, vec, fireSpell, 25))


class Enemy(Entity):
    _instances = set()
    collision = []

    def __init__(self, pos, image):
        self.image = image
        self.rect = image.get_rect
        self.rect.centerx, self.rect.centery = pos
        super().__init__(self.rect, self.image, Enemy.collision)
