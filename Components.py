import weakref
import pygame as pg
import time
import math
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


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
        self.alive = True
        super().__init__(rect)
        self._instances.add(weakref.ref(self))
        MovementComponent._instances.add(weakref.ref(self))

    def move(self):
        self.rect.x += self.vec[0]
        self.rect.y += self.vec[1]
        if len(self.check_collision()) > 0:
            self.alive = False
        else:
            return self.rect


##############################################
class Attribute:
    healthComp = set()
    damageComp = set()
    animationComp = set()

    @classmethod
    def health(cls):
        dead = set()
        for ref in cls.healthComp:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls.healthComp -= dead

    @classmethod
    def damage(cls):
        dead = set()
        for ref in cls.damageComp:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls.damageComp -= dead


class Health(Attribute):

    def __init__(self, health, hitbox, damageCD):
        self.maxHealth = health
        self.health = health
        self.hitbox = hitbox
        self.damageCD = damageCD
        self.lastDamage = time.time()
        Attribute.healthComp.add(weakref.ref(self))

    def heal_self(self, amount):
        self.heal(self, amount)

    @staticmethod
    def heal(target, amount):
        target.health += amount
        if target.health > target.maxHealth:
            target.health = target.maxHealth


class Damage(Attribute):
    def __init__(self, damage, damageCD, ignore):
        self.damageCD = damageCD
        self.damage = damage
        self.ignore = list(ignore)
        self.lastDamage = time.time()
        Attribute.damageComp.add(weakref.ref(self))

    def rect(self, rect):
        if time.time() - self.lastDamage >= self.damageCD:
            self.lastDamage = time.time()
            for i in Attribute.health():
                if rect.colliderect(i.hitbox) and i not in self.ignore:
                    i.health -= self.damage

    def target(self, target):
        target.health -= self.damage


class Animation(Attribute):
    def __init__(self, animation, framerate):
        self.list = animation
        self.fr = 1 / framerate
        self.lastFrame = time.time()
        self.currentFrame = 0
        self.length = len(self.list) - 1

    def next(self):
        if time.time() - self.lastFrame >= self.fr:
            ret = self.list[self.currentFrame]
            self.currentFrame += 1
            if self.currentFrame > self.length:
                self.currentFrame = 0
            self.lastFrame = time.time()
            return ret
        else:
            return self.list[self.currentFrame]


class PathFinding(Attribute):
    def __init__(self, pathmap, loc, target):
        self.destination = None
        self.pathMap = pathmap
        self.path = [self.destination]
        self.target = target
        self.loc = loc
        self.ignore = None

    def pathfind(self):
        grid = Grid(matrix=self.pathMap.grid)
        start = grid.node(self.loc[0], self.loc[1])
        end = grid.node(math.floor(self.target[0]), math.floor(self.target[1]))
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
        self.path = path
        if len(self.path) > 1:
            self.destination = self.path[1]
        elif len(self.path) != 0:
            self.destination = path[0]

    def next_location(self):
        if self.pathMap is not None:
            self.pathfind()
        return list(self.destination)


#############################################
class Item:
    def __init__(self, name, image):
        self.name = name
        self.image = image

    def use(self):
        pass

    def drop(self):
        pass
