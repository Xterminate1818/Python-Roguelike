import weakref
import pygame as pg
import time
import math
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from Common import vector
import queue


class Movement:
    collision = []

    def __init__(self, speed):
        self.speed = speed
        self.dx = 0
        self.dy = 0

    def check_collision(self, rect):
        collisions = []
        for c in self.collision:
            if rect.colliderect(c):
                collisions.append(c)
        return collisions

    def move(self, rect, **kwargs):
        dx = self.dx
        dy = self.dy
        limit = 1
        for key, value in kwargs.items():
            if key == 'dx':
                dx = value
            if key == 'dy':
                dy = value
            if key == 'limit':
                limit = value

        collision = False
        if dx > limit:
            dx = limit
        if dx < -limit:
            dx = -limit
        if dy > limit:
            dy = limit
        if dy < -limit:
            dy = -limit
        if abs(dx) + abs(dy) > limit:
            dx *= .707
            dy *= .707
        rect.centerx += dx * self.speed
        collisions = self.check_collision(rect)
        for c in collisions:
            collision = True
            if dx > 0:
                rect.right = c.left
            if dx < 0:
                rect.left = c.right
        rect.centery += dy * self.speed
        collisions = self.check_collision(rect)
        for c in collisions:
            collision = True
            if dy > 0:
                rect.bottom = c.top
            if dy < 0:
                rect.top = c.bottom
        return rect, collision


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

    def tick(self):
        pass


class GraphicsManager:
    def __init__(self, surface):
        self.surf = surface
        self.bg = queue.Queue(0)
        self.fg = queue.Queue(0)
        self.offset = [0, 0]

    def push_bg(self, image, location):
        self.bg.put([image, location])

    def push_fg(self, image, location):
        self.fg.put([image, location])

    def draw(self):
        while not self.bg.empty():
            surf, dest = self.bg.get_nowait()
            newDest = (dest[0] + self.offset[0], dest[1] + self.offset[1])
            self.surf.blit(surf, newDest)
        while not self.fg.empty():
            surf, dest = self.fg.get_nowait()
            newDest = (dest[0] + self.offset[0], dest[1] + self.offset[1])
            self.surf.blit(surf, newDest)
        pg.display.flip()


class Image(Attribute):
    surf = None
    _instances = set()

    def __init__(self, image, layer, manager):
        self.image = image
        self.rect = image.get_rect()
        self.layer = layer
        self.manager = manager
        self._instances.add(weakref.ref(self))

    def get_height(self):
        return self.image.get_height()

    def get_width(self):
        return self.image.get_width()

    def blit(self):
        if self.layer == 'bg':
            self.manager.push_bg(self.image, self.rect)
        elif self.layer == 'fg':
            self.manager.push_fg(self.image, self.rect)
        else:
            print('incorrect layer value')

    def clone(self):
        return Image(self.image, self.layer, self.manager)

    def __getitem__(self, x):
        if x == 0:
            return self.image
        if x == 1:
            return self.rect
        else:
            raise IndexError

    @classmethod
    def blit_all(cls):
        for img in cls.instances():
            img.blit()

    @classmethod
    def instances(cls):
        dead = set()
        for ref in cls.healthComp:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls.healthComp -= dead


class Health(Attribute):
    def __init__(self, health, hitbox, damageCD, *args):
        self.maxHealth = health
        self.health = health
        self.hitbox = hitbox
        self.damageCD = damageCD
        self.lastDamage = time.time()
        self.immune = args
        Attribute.healthComp.add(weakref.ref(self))

    def heal_self(self, amount):
        self.heal(self, amount)

    @staticmethod
    def heal(target, amount):
        target.health += amount
        if target.health > target.maxHealth:
            target.health = target.maxHealth


class Damage(Attribute):
    def __init__(self, damage, damageCD, type):
        self.damageCD = damageCD
        self.damage = damage
        self.type = type
        self.lastDamage = time.time()
        Attribute.damageComp.add(weakref.ref(self))

    def rect(self, rect):
        if time.time() - self.lastDamage >= self.damageCD:
            self.lastDamage = time.time()
            for i in Attribute.health():
                if rect.colliderect(i.hitbox) and self.type not in i.immune:
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


class RangedAttack(Damage):
    def __init__(self, image, manager, **kwargs):
        self.lastAttack = time.time()
        self.image = Image(image, 'fg', manager)
        speed = 10
        self.cd = 0.3
        damage = 1
        type = None
        for key, value in kwargs.items():
            if key == 'damage':
                damage = value
            if key == 'cd':
                self.cd = value
            if key == 'speed':
                speed = value
            if key == 'type':
                type = value
        super().__init__(damage, 0, type)
        self.movement = Movement(speed)
        self.list = []

    def fire(self, loc, dest):
        if time.time() - self.lastAttack > self.cd:
            vec = vector(loc, dest)
            rect = pg.Rect(loc[0], loc[1], self.image.get_width(), self.image.get_height())
            rect.center = loc
            image = self.image.clone()
            image.rect = rect
            position = [float(rect.centerx), float(rect.centery)]
            self.list.append([image, vec, position])
            self.lastAttack = time.time()

    def tick(self):
        for p in self.list:
            p[2][0] += p[1][0] * self.movement.speed
            p[2][1] += p[1][1] * self.movement.speed
            p[0].rect.center = p[2]
            if len(self.movement.check_collision(p[0].rect)) > 0:
                self.list.remove(p)
            else:
                p[0].blit()


#############################################
class Item:
    def __init__(self, name, image):
        self.name = name
        self.image = image

    def use(self):
        pass

    def drop(self):
        pass
