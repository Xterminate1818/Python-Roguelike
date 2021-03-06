from Components import *
from Common import *


class Entity:
    _instances = set()

    def __init__(self, pos, image, manager):
        self.image = Image(image, 'fg', manager)
        self.rect = self.image.rect
        self.rect.x, self.rect.y = pos
        self.image.location = self.rect
        self.width = self.rect.width
        self.height = self.rect.height

        self.dx = 0
        self.dy = 0
        self.speed = 5
        self._instances.add(weakref.ref(self))

    def tick(self):
        pass

    def kill(self):
        del self

    @classmethod
    def tick_all(cls):
        for i in cls.get_instances():
            i.tick()

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


class Player(Entity):
    _instances = set()

    def __init__(self, pos, manager):
        self.lookingRight = pg.image.load("textures/sprites/Player/wizard.bmp").convert_alpha()
        self.lookingLeft = pg.transform.flip(self.lookingRight, True, False)
        self.manager = manager
        self.image = self.lookingRight
        super().__init__(pos, self.lookingRight, self.manager)
        self.hitbox = self.rect.inflate(-20, -10)
        self.initTime = time.time()

        self.health = Health(5, self.hitbox, 1, Player)
        self.movement = Movement(self.speed)
        self.attackObj = RangedAttack(fireSpell, self.manager, speed=18)
        self.idleRight = Animation(playerIdleRight, 8)
        self.idleLeft = Animation(playerIdleLeft, 8)
        self.movingRight = Animation(playerRunningRight, 8)
        self.movingLeft = Animation(playerRunningLeft, 8)

        self.facing = 'right'

        self.abilityCD = 3
        self.lastAbility = self.initTime
        self.abilityAvailable = True

        self.specialCD = 5
        self.lastSpecial = self.initTime
        self.specialAvailable = True
        self.specialRange = 10
        self._instances.add(weakref.ref(self))
        Entity._instances.add(weakref.ref(self))

    def tick(self):
        self.abilityAvailable = True if time.time() - self.lastAbility > self.abilityCD else False
        self.specialAvailable = True if time.time() - self.lastSpecial > self.specialCD else False

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
            if self.facing == 'right':
                frame = self.movingRight.next()
            else:
                frame = self.movingLeft.next()
        self.movement.dx = self.dx
        self.movement.dy = self.dy
        self.hitbox, _collided = self.movement.move(self.hitbox)
        self.health.hitbox = self.rect
        self.rect = self.hitbox.inflate(20, 10)
        self.attackObj.tick()
        self.image.image = frame
        self.manager.push_fg(frame, self.rect)
        if self.health.health <= 0:
            self.kill()

    def attack(self, destination):
        self.attackObj.fire(self.hitbox.center, destination)

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

