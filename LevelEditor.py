if __name__ == "__main__":
    from Main import tile_data, prop_data, enemy_data, dis_width, dis_height,  tileGrid, white
    from pygame.locals import *
    import pygame as pg
    import math
    from tkinter import *
    from tkinter import filedialog, messagebox
    import mpu
    spawn_icon = pg.image.load('textures/ui/spawn icon.bmp')
    exit_icon = pg.image.load('textures/ui/exit icon.bmp')
    wall_placeholder = pg.image.load('textures/ui/wall placeholder.bmp')

    tile_list = [None]
    for t in tile_data:
        if 'wall' not in t:
            tile_list.append(t)

    prop_list = [None]
    for p in prop_data:
        prop_list.append(p)

    enemy_list = []
    for e in enemy_data:
        enemy_list.append(e)


    # pygame window
    pg.display.set_caption("Preview")
    app = pg.display.set_mode((dis_width, dis_height))
    clock = pg.time.Clock()

    class Editor:
        def __init__(self):
            self.tile_x = 0
            self.tile_y = 0
            self.tileMap = [
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]
            self.propMap = [
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]
            self.enemyMap = [
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
            ]
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

            palette = ['None']
            for p in tile_data:
                palette.append(p)

        def reinit(self):
            self.levelInfo = {
                'tileMap': self.tileMap,
                'propMap': self.propMap,
                'enemyMap': self.enemyMap,
                'spawn': self.spawn,
                'exit': self.exit
            }

        def clear_room(self):
            ask_ifclear = messagebox.askyesno('Clear', 'Clear all ' + add_type.get() + ' instances?')
            if ask_ifclear == 1:
                if add_type.get() == 'tile' or add_type.get() == 'wall':
                    self.tileMap = [
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]
                elif add_type.get() == 'prop':
                    self.propMap = [
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]
                elif add_type.get() == 'enemy':
                    self.enemyMap = [
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                    ]
                elif add_type.get() == 'spawn':
                    self.spawn = [-1, -1]
                elif add_type.get() == 'exit':
                    self.exit = [-1, -1]

        def fill_room(self, object):
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    if add_type.get() == 'tile' or 'wall':
                        self.tileMap[y][x] = object
                    if add_type.get() == 'prop':
                        self.propMap[y][x] = object
                    if add_type.get() == 'enemy':
                        self.enemyMap[y][x] = object

        def save_room(self):
            self.reinit()
            file_dir = 'levels/'+ level_name_entry.get() + '.json'
            if file_dir == 'levels/.json':
                messagebox.showerror('Error', 'Filename cannot be empty')
            else:
                ask_ifsave = messagebox.askyesno('Save','Save current room as '+level_name_entry.get()+'?')
                if ask_ifsave == 1:
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
                'up' : False,
                'down' : False,
                'left' : False,
                'right' : False,
                'nw' : False,
                'ne' : False,
                'sw' : False,
                'se' : False
            }
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    if self.tileMap[y][x] in tile_data:
                        if tile_data[self.tileMap[y][x]][1] == -1:
                            try:
                                adj['up'] = True if tile_data[self.tileMap[y-1][x]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['up'] = False
                            try:
                                adj['down'] = True if tile_data[self.tileMap[y+1][x]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['down'] = False
                            try:
                                adj['left'] = True if tile_data[self.tileMap[y][x-1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['left'] = False
                            try:
                                adj['right'] = True if tile_data[self.tileMap[y][x+1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['right'] = False
                            try:
                                adj['nw'] = True if tile_data[self.tileMap[y-1][x-1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['nw'] = False
                            try:
                                adj['ne'] = True if tile_data[self.tileMap[y-1][x+1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['ne'] = False
                            try:
                                adj['sw'] = True if tile_data[self.tileMap[y+1][x-1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['sw'] = False
                            try:
                                adj['se'] = True if tile_data[self.tileMap[y+1][x+1]][1] == -1 else False
                            except (IndexError, KeyError):
                                adj['se'] = False
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
                                self.tileMap[y][x] = ''
                            if up and down and right and left and ne and nw and se and sw:
                                self.tileMap[y][x] = 'void'



        def run(self):
            root.update()
            mouseLoc = pg.mouse.get_pos()
            mousePressed = pg.mouse.get_pressed()
            for e in pg.event.get():
                if e.type == QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == KEYUP:
                    if e.key == K_p:
                        self.smart_walls()

            if mousePressed[0] == 1:
                if add_type.get() == 'tile' or add_type.get() == 'wall' and self.selectedTile is not None:
                    tile_x = math.floor(mouseLoc[0] / tileGrid)
                    tile_y = math.floor(mouseLoc[1] / tileGrid)
                    try:
                        self.tileMap[tile_y][tile_x] = self.selectedTile
                    except IndexError:
                        pass
                if add_type.get() == 'prop':
                    prop_x = math.floor(mouseLoc[0] / tileGrid)
                    prop_y = math.floor(mouseLoc[1] / tileGrid)
                    try:
                        self.propMap[prop_y][prop_x] = self.selectedTile
                    except IndexError:
                        pass
                if add_type.get() == 'enemy':
                    enemy_x = math.floor(mouseLoc[0] / tileGrid)
                    enemy_y = math.floor(mouseLoc[1] / tileGrid)
                    try:
                        self.enemyMap[enemy_y][enemy_x] = self.selectedTile
                    except IndexError:
                        pass
                if add_type.get() == 'spawn':
                    spawn_x = math.floor(mouseLoc[0] / tileGrid)
                    spawn_y = math.floor(mouseLoc[1] / tileGrid)
                    self.spawn = [spawn_x, spawn_y]
                if add_type.get() == 'exit':
                    exit_x = math.floor(mouseLoc[0] / tileGrid)
                    exit_y = math.floor(mouseLoc[1] / tileGrid)
                    self.exit = [exit_x, exit_y]
            app.fill(white)
            for y, row in enumerate(self.tileMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(tile_data[col][0], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            for y, row in enumerate(self.propMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(prop_data[col], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            for y, row in enumerate(self.enemyMap):
                for x, col in enumerate(row):
                    try:
                        app.blit(enemy_data[col], (x * tileGrid, y * tileGrid))
                    except KeyError:
                        pass
            if self.spawn != [-1, -1]:
                app.blit(spawn_icon, (self.spawn[0] * tileGrid, self.spawn[1] * tileGrid))
            self.selectedTile = selection.get()
            if self.exit != [-1, -1]:
                app.blit(exit_icon, (self.exit[0] * tileGrid, self.exit[1] * tileGrid))
            pg.display.flip()
            clock.tick(60)
    level_editor = Editor()

    def radio_update():
        if add_type.get() == 'tile':
            selector = OptionMenu(painting_frame, selection, *tile_list)
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'prop':
            selector = OptionMenu(painting_frame, selection, *prop_list)
            selector.grid(row=2, column=0, columnspan=2)
        elif add_type.get() == 'wall':
            selector = OptionMenu(painting_frame, selection, *[wall_placeholder])
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
    fill_button = Button(painting_frame, text="Fill", command=lambda:level_editor.fill_room(selection.get()))
    clear_button = Button(painting_frame, text="Clear", command=level_editor.clear_room)
    add_type = StringVar()
    add_type.set('tile')
    tile_select = Radiobutton(painting_frame, text='Tiles', variable=add_type, value='tile', command=radio_update)
    wall_select = Radiobutton(painting_frame, text='Walls', variable=add_type, value='wall', command=radio_update)
    prop_select = Radiobutton(painting_frame, text='Props', variable=add_type, value='prop', command=radio_update)
    enemy_select = Radiobutton(painting_frame, text='Enemies', variable=add_type, value='enemy', command=radio_update)
    spawn_select = Radiobutton(painting_frame, text='Spawnpoint', variable=add_type, value='spawn', command=radio_update)
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