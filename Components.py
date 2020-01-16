class MovementComponent:
    def __init__(self, rect, collision):
        self.rect = rect
        self.collision = collision

    def move(self, dx, dy):
        self.rect.centerx += dx
        self.rect.centery += dy
        return self.rect

    def get_pos(self):
        return self.rect