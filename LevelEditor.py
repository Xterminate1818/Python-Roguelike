class Matrix:

    def __init__(self, xsize, ysize):
        self.grid = []
        _col = []
        for n in range(ysize):
            self.grid.append([])
        for y in range(len(self.grid)):
            for n in range(xsize):
                self.grid[y].append(None)

    def print(self):
        print(self.grid)

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = None

    def fill(self, content):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = content

    def set(self, x, y, content):
        self.grid[y][x] = content
        print('set')

    def reset(self):
        self.grid = self.gridOriginal

    def __getitem__(self, y):
        return self.grid[y]


class Room:
    _instances = set()
    current = None

    def __init__(self, file):
        self.file = mpu.io.read(file)
        self.dict = dict(self.file)

        self.tileMap = self.dict['tileMap']
        self.propMap = self.dict['propMap']
        self.enemyMap = self.dict['enemyMap']

        if len(self.tileMap) != len(self.propMap) != len(self.enemyMap):
            raise ValueError('Map sizes are not uniform (y dimension)')
        if len(self.tileMap[0]) != len(self.propMap[0]) != len(self.enemyMap[0]):
            raise ValueError('Map sizes are not uniform (x dimension)')

        self.width = len(self.tileMap)
        self.height = len(self.tileMap[0])

        self.pathMap = Matrix(self.width, self.height, 1)
        self.spawnPoint = self.dict['spawn']
        self.exitPoint = self.dict['exit']
        self.exit_open = False
        self.collision = []
        self._instances.add(weakref.ref(self))

        for y, row in enumerate(self.tileMap):
            for x, col in enumerate(row):
                try:
                    self.pathMap[y][x] = tileData[col][1]
                    self.collision.append(pg.Rect(x * tileGrid, y * tileGrid, tileGrid, tileGrid))
                except KeyError:
                    pass
        if Room.current is None:
            Room.current = self

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


if __name__ == "__main__":
    from init import *
    from pygame.locals import *

    test = Matrix(2, 2)
    test.print()
    test.set(0, 0, False)
    test.print()

    import pygame as pg
    import math
    from tkinter import *
    from tkinter import filedialog, messagebox
    import mpu

    spawn_icon = pg.image.load('textures/ui/spawn icon.bmp')
    exit_icon = pg.image.load('textures/ui/exit icon.bmp')
    wall_placeholder = pg.image.load('textures/ui/wall placeholder.bmp')

    tile_list = []
    for t in tileData:
        if tileData[t][1] != -1:
            tile_list.append(t)

    prop_list = [None]
    for p in propData:
        prop_list.append(p)

    enemy_list = [None]
    for e in enemyData:
        enemy_list.append(e)

    pg.display.set_caption("Preview")
    app = pg.display.set_mode((dis_width, dis_height))
    clock = pg.time.Clock()


    class Editor:
        def __init__(self):
            self.tile_x = 0
            self.tile_y = 0
            self.tileMap = Matrix(gridWidth, gridHeight)
            self.propMap = Matrix(gridWidth, gridHeight)
            self.enemyMap = Matrix(gridWidth, gridHeight)
            self.spawn = [-1, -1]
            self.exit = [-1, -1]
            self.selectedTile = None
            self.levelInfo = {
                'tileMap': self.tileMap,
                'propMap': self.propMap,
                'enemyMap': self.enemyMap,
                'spawn': self.spawn,
                'exit': self.exit
            }

        def clear_room(self):
            askIfClear = messagebox.askyesno('Clear', 'Clear all ' + add_type.get() + ' instances?')
            if askIfClear == 1:
                if add_type.get() == 'tile' or add_type.get() == 'wall':
                    self.tileMap = Matrix(gridWidth, gridHeight, None)
                elif add_type.get() == 'prop':
                    self.propMap = Matrix(gridWidth, gridHeight, None)
                elif add_type.get() == 'enemy':
                    self.enemyMap = Matrix(gridWidth, gridHeight, None)
                elif add_type.get() == 'spawn':
                    self.spawn = [-1, -1]
                elif add_type.get() == 'exit':
                    self.exit = [-1, -1]

        def fill_room(self, obj):
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    if add_type.get() == 'tile' or 'wall':
                        self.tileMap[y][x] = obj
                    if add_type.get() == 'prop':
                        self.propMap[y][x] = obj
                    if add_type.get() == 'enemy':
                        self.enemyMap[y][x] = obj

        def save_room(self):
            file_dir = 'levels/' + level_name_entry.get() + '.json'
            if file_dir == 'levels/.json':
                messagebox.showerror('Error', 'Filename cannot be empty')
            else:
                askIfSave = messagebox.askyesno('Save', 'Save current room as ' + level_name_entry.get() + '?')
                if askIfSave == 1:
                    print('save')
                    mpu.io.write(file_dir, self.levelInfo)

        def load(self):
            root.filename = filedialog.askopenfilename(initialdir='levels', title='Select room to load')
            if root.filename != '':
                loaded_level = mpu.io.read(root.filename)
                self.levelInfo = dict(loaded_level)
                self.tileMap = self.levelInfo["tileMap"]
                self.propMap = self.levelInfo['propMap']
                self.enemyMap = self.levelInfo['enemyMap']
                self.spawn = self.levelInfo['spawn']
                self.exit = self.levelInfo['exit']
                self.reinit()

        def smart_walls(self):
            adj = {
                'up': False,
                'down': False,
                'left': False,
                'right': False,
                'nw': False,
                'ne': False,
                'sw': False,
                'se': False
            }
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    if self.tileMap[y][x] in tileData:
                        if tileData[self.tileMap[y][x]][1] == -1:
                            try:
                                adj['up'] = True if tileData[self.tileMap[y - 1][x]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['up'] = False
                            try:
                                adj['down'] = True if tileData[self.tileMap[y + 1][x]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['down'] = False
                            try:
                                adj['left'] = True if tileData[self.tileMap[y][x - 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['left'] = False
                            try:
                                adj['right'] = True if tileData[self.tileMap[y][x + 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['right'] = False
                            try:
                                adj['nw'] = True if tileData[self.tileMap[y - 1][x - 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['nw'] = False
                            try:
                                adj['ne'] = True if tileData[self.tileMap[y - 1][x + 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['ne'] = False
                            try:
                                adj['sw'] = True if tileData[self.tileMap[y + 1][x - 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['sw'] = False
                            try:
                                adj['se'] = True if tileData[self.tileMap[y + 1][x + 1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['se'] = False
                            if y + 1 > gridHeight - 1:
                                adj['down'] = True
                                adj['se'] = True
                                adj['sw'] = True
                            if y - 1 < 0:
                                adj['up'] = True
                                adj['ne'] = True
                                adj['nw'] = True
                            if x + 1 > gridWidth - 1:
                                adj['right'] = True
                                adj['ne'] = True
                                adj['se'] = True
                            if x - 1 < 0:
                                adj['left'] = True
                                adj['nw'] = True
                                adj['sw'] = True
                            up = adj['up']
                            down = adj['down']
                            left = adj['left']
                            right = adj['right']
                            ne = adj['ne']
                            nw = adj['nw']
                            se = adj['se']
                            sw = adj['sw']
                            if not up and not down and not left and not right and not nw and not ne and not se and not nw:
                                self.tileMap[y][x] = 'fourWalls'
                            if up and down and right and left and not ne and not nw and not se and not sw:
                                self.tileMap[y][x] = 'fourSplit'
                            if up and down and right and left and ne and nw and se and sw:
                                self.tileMap[y][x] = 'void'
                            if not up and down and not right and not left:
                                self.tileMap[y][x] = 'upU'
                            if up and not down and not right and not left:
                                self.tileMap[y][x] = 'downU'
                            if not up and not down and right and not left:
                                self.tileMap[y][x] = 'rightU'
                            if not up and not down and not right and left:
                                self.tileMap[y][x] = 'leftU'
                            if up and not down and left and right:
                                self.tileMap[y][x] = 'southWall'
                            if not up and down and left and right:
                                self.tileMap[y][x] = 'northWall'
                            if up and down and left and not right:
                                self.tileMap[y][x] = 'westWall'
                            if up and down and not left and right:
                                self.tileMap[y][x] = 'eastWall'
                            if up and down and left and right and not se and sw and ne and nw:
                                self.tileMap[y][x] = 'extCorner1'
                            if up and down and left and right and not sw and se and ne and nw:
                                self.tileMap[y][x] = 'extCorner2'
                            if up and down and left and right and not ne and sw and se and nw:
                                self.tileMap[y][x] = 'extCorner3'
                            if up and down and left and right and not nw and ne and se and sw:
                                self.tileMap[y][x] = 'extCorner4'
                            if not up and down and right and not left:
                                self.tileMap[y][x] = 'intCorner1'
                            if not up and down and not right and left:
                                self.tileMap[y][x] = 'intCorner2'
                            if up and not down and right and not left:
                                self.tileMap[y][x] = 'intCorner3'
                            if up and not down and not right and left:
                                self.tileMap[y][x] = 'intCorner4'
                            if up and down and not right and not left:
                                self.tileMap[y][x] = 'doubleVertWalls'
                            if not up and not down and right and left:
                                self.tileMap[y][x] = 'doubleHorWalls'
                            if not up and down and right and not left and not se and not sw and not ne and not nw:
                                self.tileMap[y][x] = 'doubleCorner1'
                            if not up and down and not right and left and not se and not sw and not ne and not nw:
                                self.tileMap[y][x] = 'doubleCorner2'
                            if up and not down and right and not left and not se and not sw and not ne and not nw:
                                self.tileMap[y][x] = 'doubleCorner3'
                            if up and not down and not right and left and not se and not sw and not ne and not nw:
                                self.tileMap[y][x] = 'doubleCorner4'
                            if not up and down and right and left and not se and not sw:
                                self.tileMap[y][x] = 'tSplit1'
                            if up and down and right and not left and not ne and not se:
                                self.tileMap[y][x] = 'tSplit2'
                            if up and not down and right and left and not ne and not nw:
                                self.tileMap[y][x] = 'tSplit3'
                            if up and down and not right and left and not nw and not sw:
                                self.tileMap[y][x] = 'tSplit4'
                            if up and down and right and not left and not ne:
                                self.tileMap[y][x] = 'rSplit1'
                            if up and down and not right and left and not nw:
                                self.tileMap[y][x] = 'rSplit2'
                            if up and down and right and not left and not se:
                                self.tileMap[y][x] = 'rSplit3'
                            if up and down and not right and left and not sw:
                                self.tileMap[y][x] = 'rSplit4'
                            if up and not down and left and right and ne and not nw:
                                self.tileMap[y][x] = 'rSplit5'
                            if up and not down and left and right and nw and not ne:
                                self.tileMap[y][x] = 'rSplit6'
                            if not up and down and left and right and se and not sw:
                                self.tileMap[y][x] = 'rSplit7'
                            if not up and down and left and right and sw and not se:
                                self.tileMap[y][x] = 'rSplit8'
                            if up and down and left and right and not se and not sw and nw and ne:
                                self.tileMap[y][x] = 'extDoubleCorner1'
                            if up and down and left and right and not se and not ne and sw and nw:
                                self.tileMap[y][x] = 'extDoubleCorner2'
                            if up and down and left and right and not nw and not ne and se and sw:
                                self.tileMap[y][x] = 'extDoubleCorner3'
                            if up and down and left and right and se and ne and not sw and not nw:
                                self.tileMap[y][x] = 'extDoubleCorner4'

        def run(self):
            root.update()
            mouseLoc = pg.mouse.get_pos()
            mousePressed = pg.mouse.get_pressed()
            for e in pg.event.get():
                self.smart_walls()
                if e.type == QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == KEYUP:
                    if e.key == K_p:
                        self.tileMap.print()

            if mousePressed[0] == 1:
                tile_x = math.floor(mouseLoc[0] / tileGrid)
                tile_y = math.floor(mouseLoc[1] / tileGrid)
                if add_type.get() == 'tile':
                    self.tileMap.set(tile_x, tile_y, 'floor')
                if add_type.get() == 'spawn':
                    self.spawn = [tile_x, tile_y]
                if add_type.get() == 'exit':
                    exit_x = math.floor(mouseLoc[0] / tileGrid)
                    exit_y = math.floor(mouseLoc[1] / tileGrid)
                    self.exit = [exit_x, exit_y]
            app.fill(white)
            # Display tiles
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(tileData[col][0], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            # Display props
            for y, row in enumerate(self.propMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(propData[col], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            # Display enemies
            for y, row in enumerate(self.enemyMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(enemyData[col], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            if self.spawn != [-1, -1]:
                app.blit(spawn_icon, (self.spawn[0] * tileGrid, self.spawn[1] * tileGrid))
            self.selectedTile = selection.get()
            if self.exit != [-1, -1]:
                app.blit(exit_icon, (self.exit[0] * tileGrid, self.exit[1] * tileGrid))

            self.levelInfo = {
                'tileMap': self.tileMap,
                'propMap': self.propMap,
                'enemyMap': self.enemyMap,
                'spawn': self.spawn,
                'exit': self.exit
            }
            pg.display.flip()
            clock.tick(60)


    level_editor = Editor()


    def radio_update():
        if add_type.get() == 'tile':
            selector = OptionMenu(painting_frame, selection, *tile_list)
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'wall':
            selector = OptionMenu(painting_frame, selection, *['Wall'])
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'prop':
            selector = OptionMenu(painting_frame, selection, *prop_list)
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'enemy':
            selector = OptionMenu(painting_frame, selection, *enemy_list)
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'spawn':
            selector = OptionMenu(painting_frame, selection, *['Spawn Point'])
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'exit':
            selector = OptionMenu(painting_frame, selection, *['Exit Point'])
            selector.grid(row=2, column=0, columnspan=2)


    # Tkinter window
    root = Tk()
    root.title("Editor")

    painting_frame = LabelFrame(root, text='Painting Options', padx=5, pady=5)
    save_frame = LabelFrame(root, text='Save Options')
    selection = StringVar(root)
    selection.set(tile_list[0])  # default value

    selector = OptionMenu(painting_frame, selection, *tile_list)
    fill_button = Button(painting_frame, text="Fill", command=lambda: level_editor.fill_room(selection.get()))
    clear_button = Button(painting_frame, text="Clear", command=level_editor.clear_room)
    add_type = StringVar()
    add_type.set('tile')
    tile_select = Radiobutton(painting_frame, text='Tiles', variable=add_type, value='tile', command=radio_update)
    wall_select = Radiobutton(painting_frame, text='Walls', variable=add_type, value='wall', command=radio_update)
    prop_select = Radiobutton(painting_frame, text='Props', variable=add_type, value='prop', command=radio_update)
    enemy_select = Radiobutton(painting_frame, text='Enemies', variable=add_type, value='enemy', command=radio_update)
    spawn_select = Radiobutton(painting_frame, text='Spawnpoint', variable=add_type, value='spawn',
                               command=radio_update)
    exit_select = Radiobutton(painting_frame, text='Exit', variable=add_type, value='exit', command=radio_update)

    save_button = Button(save_frame, text="Save", command=level_editor.save_room, width=20)
    load_button = Button(save_frame, text="Load", command=level_editor.load, width=20)
    save_name_label = Label(save_frame, text='Room name:')
    level_name_entry = Entry(save_frame)

    painting_frame.grid(row=0, column=0, padx=20, pady=10)
    save_frame.grid(row=1, column=0, padx=20, pady=10)
    selector.grid(row=2, column=0, columnspan=2)
    fill_button.grid(row=3, column=0)
    clear_button.grid(row=3, column=1)
    tile_select.grid(row=4)
    wall_select.grid(row=5)
    prop_select.grid(row=6)
    enemy_select.grid(row=7)
    spawn_select.grid(row=8)
    exit_select.grid(row=9)
    save_button.grid(row=1, column=0, padx=20, columnspan=2)
    load_button.grid(row=0, column=0, padx=20, columnspan=2)
    save_name_label.grid(row=2, column=0)
    level_name_entry.grid(row=2, column=1)

    while True:
        level_editor.run()
