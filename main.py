import os
import sys
import threading

import pygame

size = width, height = 700, 500
screen = pygame.display.set_mode(size)
player = None
FPS = 5


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
floor_group = pygame.sprite.Group()
texture_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()
thorn_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
stair_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
list_potions = []
list_thorns = []
list_doors = []
stair = None

texture_images = {
    'wall': load_image('wall4.jpg'),
    'floor': load_image('floor2.png'),
    'potion_speed': load_image('potion_speed2.png'),
    'thorns': load_image('thorns.jpg'),
    'stair': load_image('stair.jpg'),
    'hatch': load_image('hatch.jpg'),
    'door': load_image('door_closed.jpg')
}


class Thorn(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(thorn_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.screen = None

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Potion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(potion_group, all_sprites)
        self.image = texture_images['potion_speed']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Stair(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(stair_group, all_sprites)
        self.image = texture_images['stair']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(door_group, all_sprites)
        self.image = texture_images['door']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Textures(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type in 'floor':
            super().__init__(floor_group, all_sprites)
        else:
            super().__init__(texture_group, all_sprites)
        self.image = texture_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# player_image = load_image('player_down.png')

tile_width = tile_height = 32


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.health = 100
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.screen = None

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


def generate_level(level):
    global stair
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Textures('floor', x, y)
            if level[y][x] == '*':
                Textures('wall', x, y)
            elif level[y][x] == '@':
                Textures('floor', x, y)
                new_player = Player(load_image('player_right.png'), 4, 1, x * 35, y * 32)
            elif level[y][x] == 's':
                Textures('floor', x, y)
                potion = Potion(x, y)
                list_potions.append(potion)
            elif level[y][x] == 't':
                Textures('floor', x, y)
                thorn = Thorn(load_image('thorns.jpg'), 4, 1, x * 35, y * 32)
                list_thorns.append(thorn)
            elif level[y][x] == 'u':
                Textures('floor', x, y)
                stair = Stair(x, y)
            elif level[y][x] == 'h':
                Textures('floor', x, y)
                Textures('hatch', x, y)
            elif level[y][x] == 'd':
                Textures('floor', x + 2, y)
                Door(x, y)
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


level = load_level('second_level.txt')
player, level_x, level_y = generate_level(level)
cur_mod = 'r'
step = 8
health = 100


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.png'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 80)
    string_rendered = font.render('Поиск', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (265, 165))
    string_rendered = font.render('сокровищ', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (210, 215))
    font = pygame.font.Font(None, 20)
    string_rendered = font.render('Голубой флакон - зелье скорости на 15 секунд', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (75, 395))
    string_rendered = font.render('Создатель игры:', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (515, 395))
    string_rendered = font.render('Григорьев Илья', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (518, 415))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def check_mask(arr):
    for i in arr:
        if pygame.sprite.collide_mask(player, i):
            potion_group.remove(i)
            return True
    return False


def back():
    global step
    step = 4


pygame.init()
start_screen()
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.rect.x -= step
                if not pygame.sprite.spritecollideany(player, texture_group):
                    if cur_mod != 'l':
                        player_2 = Player(load_image('player_left.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'l'
                        player.health = health
                else:
                    player.rect.x += step
            if event.key == pygame.K_RIGHT:
                player.rect.x += step
                if not pygame.sprite.spritecollideany(player, texture_group):
                    if cur_mod != 'r':
                        player_2 = Player(load_image('player_right.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'r'
                        player.health = health
                else:
                    player.rect.x -= step
            if event.key == pygame.K_UP:
                # print(pygame.sprite.spritecollide(player, tiles_group, False))
                player.rect.y -= step
                if not pygame.sprite.spritecollideany(player, texture_group):
                    if cur_mod != 'u':
                        player_2 = Player(load_image('player_up.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'u'
                        player.health = health
                else:
                    player.rect.y += step
            if event.key == pygame.K_DOWN:
                player.rect.y += step
                if not pygame.sprite.spritecollideany(player, texture_group):
                    if cur_mod != 'd':
                        player_2 = Player(load_image('player_down.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'd'
                        player.health = health
                else:
                    player.rect.y -= step
    if check_mask(list_potions):
        step = 8
        Timer = threading.Timer(15, back)
        Timer.start()
    if check_mask(list_thorns):
        health -= 1
        player.health = health
    screen.fill(pygame.Color((84, 55, 64)))
    if pygame.sprite.collide_mask(player, stair):
        player.kill()
        potion_group.clear(screen, pygame.Surface(size))
        stair_group.clear(screen, pygame.Surface(size))
        texture_group.clear(screen, pygame.Surface(size))
        texture_group.clear(screen, pygame.Surface(size))
        thorn_group.clear(screen, pygame.Surface(size))
        list_potions = []
        list_thorns = []
        level = load_level('second_level.txt')
        player, level_x, level_y = generate_level(level)
    floor_group.draw(screen)
    texture_group.draw(screen)
    potion_group.draw(screen)
    thorn_group.draw(screen)
    player_group.draw(screen)
    stair_group.draw(screen)
    door_group.draw(screen)
    player.screen = screen
    all_sprites.update()
    font = pygame.font.Font(None, 15)
    string_rendered = font.render(str(player.health), 1, pygame.Color('black'))
    screen.blit(string_rendered, (player.rect.x + 5, player.rect.y - 10))
    clock.tick(FPS)
    pygame.display.flip()
