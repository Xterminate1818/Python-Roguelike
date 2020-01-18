import pygame as pg
from init import *


def render_text(text, _color, size):
    fontObj = pg.font.Font(fontName, size)
    image = fontObj.render(text, True, _color)
    return fontObj, image


class UIElement:
    _buttons = set()
    activated = set()

    def __init__(self, rect, image):
        self.rect = rect
        self.image = image

    def draw(self):
        app.blit(self.image, self.rect)

    def activate(self):
        if self not in self.activated:
            self.activated.add(weakref.ref(self))

    def deactivate(self):
        if self in self.activated:
            self.activated.remove(self)

    def toggle(self):
        if self in self.activated:
            self.activated.remove(self)
        else:
            self.activated.add(weakref.ref(self))

    @classmethod
    def get_buttons(cls):
        dead = set()
        for ref in cls._buttons:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._buttons -= dead

    @classmethod
    def get_active(cls):
        dead = set()
        for ref in cls.activated:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls.activated -= dead

    @classmethod
    def click(cls, pos):
        for b in cls.get_buttons():
            if pos.collidepoint(b.rect):
                b.activate()

    @classmethod
    def hover_cursor(cls, pos):
        for b in cls.get_buttons():
            b.hover()


class Text(UIElement):
    def __init__(self, pos, text, _color, size):
        self.fontObj, self.image = render_text(text, _color, size)
        self.rect = pg.Rect(pos[0], pos[1], self.image.get_width(), self.image.get_height())
        super().__init__(self.rect, self.image)

    def get_width(self):
        return self.rect[2]

    def get_height(self):
        return self.rect[3]


class Button(UIElement):
    def __init__(self, rect, **kwargs):
        width = rect[2]
        height = rect[3]
        self.textSize = int(min(width, height) * 0.6)

        self.bg = black
        self.fg = red
        self.highlight = black
        self.text = ''
        self.backing = pg.Surface((width, height))
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == 'bg':
                    self.bg = value
                if key == 'fg':
                    self.fg = value
                if key == 'text':
                    self.text = Text((self.rect.centerx, self.rect.centery), value, self.fg, self.textSize)
                if key == 'highlight':
                    self.highlight = value
                if key == 'size':
                    self.textSize = value
        self.backing.fill(self.bg)
        self.text = Text(self.rect, self.text, self.fg, self.textSize)
        self.surface = pg.Surface(max(self.text.get_width, self.rect.width),
                                  max(self.text.get_height(), self.rect.height))
        textX = (self.backing.get_width() // 2) - (self.text.get_width() // 2)
        textY = (self.backing.get_height() // 2) - (self.text.get_height() // 2)
        self.surface.blit(self.backing, (0, 0))
        self.surface.blit(self.text, (textX, textY))
        super().__init__(rect, self.surface)
        UIElement._buttons.add(weakref.ref(self))

    def activate(self):
        pass

    def draw(self):
        app.blit(self.surface, self.rect)
        self.text.draw()

    def move(self, pos):
        self.rect.x, self.rect.y = pos
        self.text.rect.x, self.text.rect.y = pos


# Main Menu

