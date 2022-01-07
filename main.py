import os
import sys
import threading

import pygame

size = width, height = 700, 500
screen = pygame.display.set_mode(size)
player = None
FPS = 5
list_level = ['first_level.txt', 'second_level.txt', 'third_level.txt']
first_quest = [('Сколько полос на флаге США?', (190, 70), 30), ('13', (100, 70), 30), ('12', (580, 70), 30), 1]
second_quest = [('Сколько километров в одной миле?', (170, 135), 30), ('1.56', (85, 135), 30),
                ('1.61', (580, 135), 30), 2]
third_quest = [('Сколько длилась столетняя война?', (170, 200), 30), ('104', (90, 200), 30), ('116', (580, 200), 30), 2]
fourth_quest = [('Сколько струн у альта?', (235, 263), 30), ('3', (115, 263), 30), ('4', (580, 263), 30), 2]
fifth_quest = [('Сколько элементов в периодической таблице?', (162, 327), 24), ('118', (90, 327), 30),
               ('116', (580, 327), 30), 1]
sixth_quest = [('Сколько часовых поясов в России?', (170, 392), 30), ('10', (105, 392), 30), ('11', (580, 392), 30), 2]
list_questions_answers = [first_quest, second_quest, third_quest, fourth_quest, fifth_quest, sixth_quest]


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
arrow_group = pygame.sprite.Group()
list_potions = []
list_thorns = []
list_doors = []
list_arrows = []
stair = None
prize = None
end = False
action = True

texture_images = {
    'wall': load_image('wall4.jpg'),
    'floor': load_image('floor2.png'),
    'potion_speed': load_image('potion_speed2.png'),
    'potion_wellness': load_image('potion_wellness.png'),
    'thorns': load_image('thorns.jpg'),
    'stair': load_image('stair.jpg'),
    'hatch': load_image('hatch.jpg'),
    'door_closed': load_image('door_closed.jpg'),
    'door_open': load_image('door_open.jpg'),
    'left_crossbow': load_image('left_crossbow.png'),
    'right_crossbow': load_image('right_crossbow.png'),
    'left_arrow': load_image('left_arrow.jpg'),
    'right_arrow': load_image('right_arrow.jpg'),
    'prize': load_image('treasures.png')
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
    def __init__(self, name, pos_x, pos_y):
        super().__init__(potion_group, all_sprites)
        self.image = texture_images['potion_speed' if name == 'speed' else 'potion_wellness']
        self.rect = self.image.get_rect().move(
            (tile_width * pos_x) + 4, tile_height * pos_y)
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
        self.image = texture_images['door_closed']
        self.rect = self.image.get_rect().move(
            (tile_width * pos_x) + 2, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def open_door(self):
        self.image = texture_images['door_open']


class Arrow(pygame.sprite.Sprite):
    def __init__(self, orient, pos_x, pos_y):
        super().__init__(arrow_group, all_sprites)
        self.orient = 'r' if orient == 'right_arrow' else 'l'
        self.image = texture_images[orient]
        self.start_coord = (tile_width * pos_x, (tile_height * pos_y) + 10)
        self.rect = self.image.get_rect().move(self.start_coord)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.orient == 'l':
            self.rect.x -= 15
        else:
            self.rect.x += 15
        if (self.orient == 'l' and self.rect.x < 26) or (self.orient == 'r' and self.rect.x > 644):
            self.rect = self.image.get_rect().move(self.start_coord)


class Textures(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type in 'floor':
            super().__init__(floor_group, all_sprites)
        else:
            super().__init__(texture_group, all_sprites)
        self.image = texture_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Prize(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(stair_group, all_sprites)
        self.image = texture_images['prize']
        self.rect = self.image.get_rect().move(
            (tile_width * pos_x) - 3, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


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
    global stair, prize
    new_player, x, y = None, None, None
    line_doors = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Textures('floor', x, y)
            if level[y][x] == '*':
                Textures('wall', x, y)
            elif level[y][x] == '@':
                Textures('floor', x, y)
                new_player = Player(load_image('player_right.png'), 4, 1, x * 35, y * 32)
            elif level[y][x] in ('s', 'w'):
                name = 'speed' if level[y][x] == 's' else 'wellness'
                Textures('floor', x, y)
                list_potions.append((name, Potion(name, x, y)))
            elif level[y][x] == 't':
                Textures('floor', x, y)
                list_thorns.append(Thorn(load_image('thorns.jpg'), 4, 1, x * 32, y * 32))
            elif level[y][x] == 'u':
                Textures('floor', x, y)
                stair = Stair(x, y)
            elif level[y][x] == 'h':
                Textures('floor', x, y)
                Textures('hatch', x, y)
            elif level[y][x] == 'd':
                Textures('floor', x + 2, y)
                line_doors.append(Door(x, y))
                if len(line_doors) == 2:
                    list_doors.append(line_doors)
                    line_doors = []
            elif level[y][x] == 'l':
                Textures('floor', x, y)
                Textures('left_crossbow', x, y)
            elif level[y][x] == 'r':
                Textures('floor', x, y)
                Textures('right_crossbow', x, y)
            elif level[y][x] == '1':
                Textures('floor', x, y)
                list_arrows.append(Arrow('left_arrow', x, y))
            elif level[y][x] == '2':
                Textures('floor', x, y)
                list_arrows.append(Arrow('right_arrow', x, y))
            elif level[y][x] == 'p':
                Textures('floor', x, y)
                prize = Prize(x, y)
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
cur_level = 1
player, level_x, level_y = generate_level(level)
cur_mod = 'r'
step = 4
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
    screen.blit(string_rendered, (75, 390))
    string_rendered = font.render('Красный флакон - зелье здоровья', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (75, 410))
    string_rendered = font.render('Создатель игры:', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (515, 390))
    string_rendered = font.render('Григорьев Илья', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (518, 410))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def end_screen():
    fon = pygame.transform.scale(load_image('end_screen.png'), size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 80)
    string_rendered = font.render('Поздравляю', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (170, 190))
    string_rendered = font.render('Вас с победой!', 1, pygame.Color('chocolate1'))
    screen.blit(string_rendered, (140, 250))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()


def check_mask(arr, group=None, mode=None, access=True):
    for i in range(len(arr)):
        if mode == 'potion':
            if pygame.sprite.collide_mask(player, arr[i][1]):
                group.remove(arr[i][1])
                return i, arr[i][0]
        elif pygame.sprite.collide_mask(player, arr[i]) and access:
            if mode == 'door':
                return i + 1
            elif mode == 'arrow':
                arr[i].rect = arr[i].image.get_rect().move(arr[i].start_coord)
            elif mode == 'thorn':
                return arr[i]
            else:
                group.remove(arr[i])
            return True
    return False


def back():
    global step
    step = 4


def clear_sprites(group):
    for i in group:
        i.kill()


pygame.init()
start_screen()
clock = pygame.time.Clock()
streams = []
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
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
    if keys[pygame.K_RIGHT]:
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
    if keys[pygame.K_UP]:
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
    if keys[pygame.K_DOWN]:
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
    potion = check_mask(list_potions, potion_group, 'potion')
    if not (isinstance(potion, bool)):
        ind, name = potion
        del list_potions[ind]
        if name == 'speed':
            step = 8
            Timer = threading.Timer(15, back)
            Timer.start()
            streams.append(Timer)
            if len(streams) > 1:
                streams[0].cancel()
                del streams[0]
        else:
            health = 100
            player.health = 100
    thorn = check_mask(list_thorns, mode='thorn')
    if not (isinstance(thorn, bool)):
        if (thorn.cur_frame % 4) == 1:
            health -= 1
            player.health = health
    if check_mask(list_arrows, arrow_group, 'arrow', action):
        health -= 3
        player.health = health
    for i in range(len(list_doors)):
        ans = check_mask(list_doors[i], door_group, 'door')
        if ans:
            if list_questions_answers[i][-1] not in (ans, None):
                health -= 5
                player.health = health
            list_doors[i][ans - 1].open_door()
            list_questions_answers[i][-1] = None
    screen.fill(pygame.Color((84, 55, 64)))
    if stair:
        if pygame.sprite.collide_mask(player, stair):
            cur_level += 1
            player.kill()
            for i in (potion_group, thorn_group, stair_group, texture_group, floor_group, door_group):
                clear_sprites(i)
            list_potions = []
            list_thorns = []
            level = load_level(list_level[cur_level])
            player, level_x, level_y = generate_level(level)
            player.health = health
    if prize:
        if pygame.sprite.collide_mask(player, prize):
            player.kill()
            for i in (potion_group, thorn_group, stair_group, texture_group, floor_group, all_sprites):
                clear_sprites(i)
            list_potions = []
            list_thorns = []
            end = True
            break
    if health <= 0:
        all_sprites.remove(player)
        player_group.remove(player)
        player.kill()
        action = False
    floor_group.draw(screen)
    texture_group.draw(screen)
    potion_group.draw(screen)
    thorn_group.draw(screen)
    door_group.draw(screen)
    player_group.draw(screen)
    stair_group.draw(screen)
    arrow_group.draw(screen)
    player.screen = screen
    all_sprites.update()
    if action:
        font = pygame.font.Font(None, 15)
        string_rendered = font.render(str(player.health), 1, pygame.Color('black'))
        if health == 100:
            screen.blit(string_rendered, (player.rect.x + 5, player.rect.y - 13))
        elif len(str(health)) == 2:
            screen.blit(string_rendered, (player.rect.x + 8, player.rect.y - 13))
        else:
            screen.blit(string_rendered, (player.rect.x + 12, player.rect.y - 13))
    elif not action:
        pygame.draw.rect(screen, pygame.Color('black'), (120, 200, 460, 110), 0)
        font = pygame.font.Font(None, 80)
        string_rendered = font.render('Вы проиграли!', 1, pygame.Color('chocolate1'))
        screen.blit(string_rendered, (145, 225))
    if cur_level == 1:
        for i in list_questions_answers:
            quest_ans, correct = i[:-1], i[-1]
            for j in quest_ans:
                text, coord, size = j
                font = pygame.font.Font(None, size)
                string_rendered = font.render(text, 1, pygame.Color('black'))
                screen.blit(string_rendered, coord)
    pygame.display.flip()
    pygame.event.pump()
    clock.tick(FPS)
if end:
    end_screen()
