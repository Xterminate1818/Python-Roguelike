import pygame
app = pygame.display.set_mode((100, 100))
CATONKEYBOARD = pygame.USEREVENT+1
my_event = pygame.event.Event(CATONKEYBOARD, message="Bad cat!")
pygame.event.post(my_event)
for event in pygame.event.get():
    if event.type == CATONKEYBOARD:
        print(event.message)