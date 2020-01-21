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

    def __init__(self, pos, area, text, id, **kwargs):
        self.event = pg.event.Event(UIEvent, id=id)
        self.pos = pos
        self.surface = pg.Surface(area)
        self.rect = pg.Rect(pos[0], pos[1], area[0], area[1])
        self.rect.center = pos
        self.bg = black
        self.fg = white
        self.textSize = int(min(area[0], area[1]) * .9)
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
        self.surface.blit(self.text.image, (textX, textY))
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
        self._active.add(self)

    def deactivate(self):
        if self in self._active:
            self._active.remove(self)

    def draw_self(self):
        app.blit(self.surface, self.rect)

    @classmethod
    def draw(cls):
        for ui in cls._active:
            ui.draw_self()

    @classmethod
    def click(cls, location):
        for ui in UI._active:
            if ui.rect.collidepoint(location):
                pg.event.post(ui.event)


def quit_game():
    pg.quit()
    sys.exit()


# Main Menu
menuTitle = UI((disWidth / 2, disHeight * .2), (600, 200), 'The Dungeon', None, bg=blue, fg=white)
menuStart = UI((disWidth / 2, disHeight * .55), (400, 100), 'Start Game', 'menuStart', bg=white, fg=black)
menuQuit = UI((disWidth / 2, disHeight * .75), (400, 100), 'Quit Game', 'menuQuit', bg=white, fg=black)

# Pause Menu
pausedResume = UI((disWidth / 2, disHeight * .5), (400, 100), 'Resume', 'pausedResume', bg=white, fg=black)
pausedReturn = UI((disWidth / 2, disHeight * .7), (400, 100), 'Return to Title', 'pausedReturn', bg=white, fg=black)

menu = [
    menuTitle,
    menuStart,
    menuQuit
]

paused = [
    pausedResume,
    pausedReturn
]


def activate(ui, *args):
    if type(ui) is not list:
        ui = [ui]
    for obj in ui:
        obj.activate()
    for obj in args:
        obj.activate()


def deactivate(ui, *args):
    if type(ui) is not list:
        ui = [ui]
    for obj in ui:
        obj.deactivate()
    for obj in args:
        obj.deactivate()
