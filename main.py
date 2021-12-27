import os
import sys

import pygame

size = width, height = 700, 500
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


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


tile_images = {
    'wall': load_image('wall.jpg'),
    'floor': load_image('floor.png')
}
player_image = load_image('player_down.png')

tile_width = tile_height = 32


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('floor', x, y)
            elif level[y][x] == '*':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
    return new_player, x, y


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


level = load_level('first_level.txt')
player, level_x, level_y = generate_level(level)


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.png'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 80)
    string_rendered = font.render('Поиск', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (265, 165))
    string_rendered = font.render('сокровищ', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (210, 215))
    font = pygame.font.Font(None, 20)
    string_rendered = font.render('Создатель игры:', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (295, 395))
    string_rendered = font.render('Григорьев Илья', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (298, 415))
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
    screen.fill(pygame.Color((84, 55, 64)))
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
