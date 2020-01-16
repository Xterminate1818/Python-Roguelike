import weakref
import pygame as pg
import time


class MovementComponent:
    collision = []
    _instances = set()

    def __init__(self, rect):
        self.rect = rect
        self.dx = 0
        self.dy = 0
        self._instances.add(weakref.ref(self))

    def move(self):
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        return self.rect

    @staticmethod
    def move_all():
        for i in MovementComponent.get_instances():
            i.move()

    def get_pos(self):
        return [self.rect.x, self.rect.y]

    def get_rect(self):
        return self.rect

    def check_collision(self):
        collisions = []
        for c in self.collision:
            if self.rect.colliderect(c):
                collisions.append(c)
        return collisions

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


class PhysicsMovement(MovementComponent):
    def __init__(self, rect, speed):
        self.speed = speed
        super().__init__(rect)
        self._instances.add(weakref.ref(self))
        MovementComponent._instances.add(weakref.ref(self))

    def move(self):
        if self.dx > 1:
            self.dx = 1
        if self.dx < -1:
            self.dx = -1
        if self.dy > 1:
            self.dy = 1
        if self.dy < -1:
            self.dy = -1
        if abs(self.dx) + abs(self.dy) > 1:
            self.dx *= .707
            self.dy *= .707
        self.rect.centerx += self.dx * self.speed
        collisions = self.check_collision()
        for c in collisions:
            if self.dx > 0:
                self.rect.right = c.left
            if self.dx < 0:
                self.rect.left = c.right
        self.rect.centery += self.dy * self.speed
        collisions = self.check_collision()
        for c in collisions:
            if self.dy > 0:
                self.rect.bottom = c.top
            if self.dy < 0:
                self.rect.top = c.bottom


class ProjectileMovement(MovementComponent):
    def __init__(self, rect, vector, speed):
        self.speed = speed
        self.vec = list(vector)
        self.vec[0] *= speed
        self.vec[1] *= speed
        super().__init__(rect)
        self._instances.add(weakref.ref(self))
        MovementComponent._instances.add(weakref.ref(self))

    def move(self):
        self.rect.x += self.vec[0]
        self.rect.y += self.vec[1]
        if len(self.check_collision()) > 0:
            return 'hit'
        else:
            return self.rect


#############################################
class HealthComponent:
    _instances = set()

    def __init__(self, health, hitbox, damageCD):
        self.maxHealth = health
        self.health = health
        self.hitbox = hitbox
        self.damageCD = damageCD
        self.lastDamage = time.time()
        self._instances.add(weakref.ref(self))

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

    def damage_rect(self, rect, amount):
        for i in HealthComponent.get_instances():
            if i != self and rect.colliderect(i.hitbox) and time.time() - i.lastDamage > i.damageCD:
                i.health -= amount
                i.lastDamage = time.time()

    def suicide(self):
        self.health = 0

    def heal_self(self, amount):
        self.heal(self, amount)

    @staticmethod
    def heal(target, amount):
        target.health += amount
        if target.health > target.maxHealth:
            target.health = target.maxHealth

    @staticmethod
    def kill(target):
        target.health = 0


class DamageComponent:



#############################################
class Item:
    def __init__(self, name, image):
        self.name = name
        self.image = image

    def use(self):
        pass

    def drop(self):
        pass
