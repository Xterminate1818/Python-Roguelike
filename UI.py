import pygame as pg
from init import *


def render_text(text, _color, size):
    fontObj = pg.font.Font(fontName, size)
    image = fontObj.render(text, True, _color)
    return fontObj, image


class Text:
    def __init__(self, text, _color, size):
        self.fontObj, self.image = render_text(text, _color, size)

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


class UI:
    _instances = set()
    _active = set()

    def __init__(self, pos, area, text, **kwargs):
        self.pos = pos
        self.surface = pg.Surface(area)
        self.rect = pg.Rect(pos[0], pos[1], area[0], area[1])
        self.bg = black
        self.fg = white
        self.textSize = int(max(area[0], area[1]) * .8)
        for key, value in kwargs.items():
            if key == 'size':
                self.textSize = value
            if key == 'fg':
                self.fg = value
            if key == 'bg':
                self.bg = value
        self.text = Text(text, self.fg, self.textSize)
        textX = (area[0] / 2) - (self.text.get_width() / 2)
        textY = (area[1] / 2) - (self.text.get_height() / 2)
        self.surface.fill(self.bg)
        self.surface.blit(self.text, (textX, textY))
        self._instances.add(weakref.ref(self))

    def move(self, pos):
        self.rect.center = pos

    def edit(self, **kwargs):
        text = None
        for key, value in kwargs.items():
            if key == 'text':
                text = value
            if key == 'size':
                self.textSize = value
            if key == 'fg':
                self.fg = value
            if key == 'bg':
                self.bg = value
        self.surface.fill(self.bg)
        if text is not None:
            self.text = Text(text, self.fg, self.textSize)
        textX = (self.rect.width / 2) - (self.text.get_width() / 2)
        textY = (self.rect.height / 2) - (self.text.get_height() / 2)
        self.surface.blit(self.text, (textX, textY))

    def activate(self):
        self._active.add(weakref.ref(self))

    def deactivate(self):
        if weakref.ref(self) in self._active:
            self._active.remove(weakref.ref(self))

    @classmethod
    def draw(cls):
        for ui in cls._active:
            app.blit(ui.surface, ui.rect)


def quit_game():
    pg.quit()
    sys.exit()


# Main Menu
