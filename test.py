class Matrix:

    def __init__(self, xsize, ysize):
        self.grid = []
        _col = []
        for n in range(ysize):
            self.grid.append([])
        for y in range(len(self.grid)):
            for n in range(xsize):
                self.grid[y].append(None)

        del _col

    def print(self):
        print(self.grid)

    def set(self, x, y, content):
        self.grid[y][x] = content
        print('set')


test = Matrix(2, 2)
test.set(0, 0, True)
test.print()

