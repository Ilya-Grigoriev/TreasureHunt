import os
import sys

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
wall_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
list_potions = []


class Potion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(potion_group, all_sprites)
        self.image = texture_images['potion_speed']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Textures(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'floor':
            super().__init__(floor_group, all_sprites)
        # elif tile_type == 'potion_speed':
        #     super().__init__(potion_group, all_sprites)
        else:
            super().__init__(wall_group, all_sprites)
        self.image = texture_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


texture_images = {
    'wall': load_image('wall4.jpg'),
    'floor': load_image('floor2.png'),
    'potion_speed': load_image('potion_speed2.png')
}

# player_image = load_image('player_down.png')

tile_width = tile_height = 32


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

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
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Textures('floor', x, y)
            if level[y][x] == '*':
                Textures('wall', x, y)
            elif level[y][x] == '@':
                Textures('floor', x, y)
                new_player = Player(load_image('player_right.png'), 4, 1, 35, 193)
            elif level[y][x] == 's':
                Textures('floor', x, y)
                potion = Potion(x, y)
                list_potions.append(potion)
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
clock = pygame.time.Clock()
cur_mod = 'r'
step = 4
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.rect.x -= step
                for i in list_potions:
                    if pygame.sprite.collide_mask(player, i):
                        potion_group.remove(i)
                        step = 8
                        break
                if not pygame.sprite.spritecollideany(player, wall_group):
                    if cur_mod != 'l':
                        player_2 = Player(load_image('player_left.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'l'
                else:
                    player.rect.x += step
            if event.key == pygame.K_RIGHT:
                player.rect.x += step
                for i in list_potions:
                    if pygame.sprite.collide_mask(player, i):
                        potion_group.remove(i)
                        step = 8
                        break
                if not pygame.sprite.spritecollideany(player, wall_group):
                    if cur_mod != 'r':
                        player_2 = Player(load_image('player_right.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'r'
                else:
                    player.rect.x -= step
            if event.key == pygame.K_UP:
                # print(pygame.sprite.spritecollide(player, tiles_group, False))
                player.rect.y -= step
                for i in list_potions:
                    if pygame.sprite.collide_mask(player, i):
                        potion_group.remove(i)
                        step = 8
                        break
                if not pygame.sprite.spritecollideany(player, wall_group):
                    if cur_mod != 'u':
                        player_2 = Player(load_image('player_up.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'u'
                else:
                    player.rect.y += step
            if event.key == pygame.K_DOWN:
                player.rect.y += step
                for i in list_potions:
                    if pygame.sprite.collide_mask(player, i):
                        potion_group.remove(i)
                        step = 8
                        break
                if not pygame.sprite.spritecollideany(player, wall_group):
                    if cur_mod != 'd':
                        player_2 = Player(load_image('player_down.png'), 4, 1, player.rect.x, player.rect.y)
                        player.kill()
                        player = player_2
                        cur_mod = 'd'
                else:
                    player.rect.y -= step
    screen.fill(pygame.Color((84, 55, 64)))
    wall_group.draw(screen)
    floor_group.draw(screen)
    potion_group.draw(screen)
    player_group.draw(screen)
    all_sprites.update()
    clock.tick(FPS)
    pygame.display.flip()
