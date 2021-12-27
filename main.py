import os
import sys

import pygame

size = width, height = 500, 500
screen = pygame.display.set_mode(size)
player = None


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except FileNotFoundError:
        print(f'Файл с именем {filename} не найден')
        terminate()


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.png'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 80)
    string_rendered = font.render('Поиск', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (165, 165))
    string_rendered = font.render('сокровищ', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (110, 215))
    font = pygame.font.Font(None, 20)
    string_rendered = font.render('Создатель игры:', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (195, 395))
    string_rendered = font.render('Григорьев Илья', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (198, 415))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


pygame.init()
start_screen()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    pygame.display.flip()
