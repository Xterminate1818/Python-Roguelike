import pygame as pg
from init import *


class UIElement:
    _instances = set()

    def __init__(self, rect, image):
        self.rect = rect
        self.image = image
        self._instances.add(weakref.ref(self))

    def draw(self):
        app.blit(self.image, self.rect)

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


class Text(UIElement):
