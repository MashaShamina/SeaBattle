import pygame
import sys
import os
import random

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
pygame.font.init()
cell_size = 50
FPS = 50
lvl = 1
time = 300
pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
level = {1: "Начинающий",
         2: "Продолжающий",
         3: "Эксперт"}
points = 0
clickcoordinates = 0
game_status = 0
running = True
clock = pygame.time.Clock()
# группы спрайтов
all_sprites = pygame.sprite.Group()
ship_group = pygame.sprite.Group()
clickcoordinate = pygame.sprite.Group()


def load_image(name, colorkey=-1):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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


class Pictures(pygame.sprite.Sprite):
    image1 = load_image("Начинающий.png")
    image2 = load_image("Продолжающий.png")
    image3 = load_image("Эксперт.png")

    def __init__(self, _x, _y, index, *group):
        super().__init__(*group)
        self.index = index
        if self.index == 1:
            self.image = Pictures.image1
        elif self.index == 2:
            self.image = Pictures.image2
        if self.index == 3:
            self.image = Pictures.image3
        self.rect = self.image.get_rect()
        self.rect.x = _x
        self.rect.y = _y

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            global lvl
            lvl = self.index


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('Морской бой.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    allsprites = pygame.sprite.Group()
    pic1 = Pictures(100, 650, 1, allsprites)
    pic2 = Pictures(500, 650, 2, allsprites)
    pic3 = Pictures(900, 650, 3, allsprites)

    while True:
        allsprites.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                allsprites.update(event)
                print("Старт!!!")
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def regulations():
    intro_text = ["ПРАВИЛА ИГРЫ", "",
                  "Компьютер расставляет корабли",
                  "случайным образом. Ваша задача -",
                  "набрать наибольшее количество",
                  "очков за определённое время,",
                  "которое зависит от вашего уровня",
                  "На начинающем уровне - 5 минут,",
                  "на продолжающем - 2,5 минуты, на",
                  "эксперте - минута. По умолчанию",
                  "стоит начинающий уровень. За",
                  "корабль, состоящий из 4 клеток,",
                  "даётся 4 очка, за корабль из 3",
                  "клеток - 3 очка, из 2 - 2 очка,",
                  "из одной клетки - очко.", "",
                  "Удачи!"]
    font = pygame.font.Font(None, 30)
    text_coord = 0
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 830
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 300
        self.top = 10

    # настройка внешнего вида
    def set_view(self, left, top):
        self.left = left
        self.top = top

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255), (
                    x * cell_size + self.left, y * cell_size + self.top, cell_size,
                    cell_size), 1)
                if self.board[y][x] == 2:
                    pygame.draw.line(screen, 'red', (x * cell_size + self.left, y * cell_size + self.top),
                                     (x * cell_size + self.left + cell_size, y * cell_size + self.top + cell_size),
                                     width=5)
                    pygame.draw.line(screen, 'red', (x * cell_size + self.left + cell_size, y * cell_size + self.top),
                                     (x * cell_size + self.left, y * cell_size + self.top + cell_size), width=5)
                elif self.board[y][x] == 1:
                    pygame.draw.circle(screen, 'white', (
                        x * cell_size + self.left + cell_size / 2, y * cell_size + self.top + cell_size / 2),
                                       5, width=5)
                else:
                    pygame.draw.rect(screen, 'white', (
                        x * cell_size + self.left, y * cell_size + self.top, cell_size,
                        cell_size), 1)

    def get_cell(self, mouse_pos):
        for y in range(self.height):
            for x in range(self.width):
                if mouse_pos[0] < self.left or mouse_pos[1] < self.top or \
                        mouse_pos[0] > self.left + self.width * cell_size or \
                        mouse_pos[1] > self.top + self.height * cell_size:
                    cell_coords = None
                if x * cell_size + self.left <= mouse_pos[0] and \
                        mouse_pos[0] <= x * cell_size + self.left + cell_size and \
                        y * cell_size + self.top <= mouse_pos[1] and \
                        mouse_pos[1] <= y * cell_size + self.top + cell_size:
                    cell_coords = (x, y)
                    # rect = pygame.Rect(x * cell_size + self.left, y * cell_size + self.top, cell_size, cell_size)
                    # clickcoordinate.add(rect)
                    break
        return cell_coords

    def on_click(self, cell_coords, state):
        global clickcoordinates
        clickcoordinates = cell_coords
        if cell_coords is not None:
            for i in range(self.height):
                for j in range(self.width):
                    if j == cell_coords[0] and i == cell_coords[1] and state > self.board[i][j]:
                        self.board[i][j] = state

    def get_click(self, mouse_pos, state):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell, state)


def picture_with_ships():
    fon_ships = pygame.transform.scale(load_image('Корабли.png'), (400, 200))
    screen.blit(fon_ships, (360, 550))


def change_time():
    global time
    if lvl == 1:
        time = 300
    if lvl == 2:
        time = 150
    if lvl == 3:
        time = 60


def level_time_points():
    intro_text = ["Уровень:", "Время:", "Очки:"]
    font = pygame.font.Font(None, 30)
    text_coord = 0
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        if line == "Уровень:":
            q = font.render(level[lvl], True, pygame.Color('white'))
            screen.blit(q, (110, 10))
        if line == "Время:":
            q = font.render(str(time), True, pygame.Color('white'))
            screen.blit(q, (110, 40))
        if line == "Очки:":
            q = font.render(str(points), True, pygame.Color('white'))
            screen.blit(q, (110, 70))


class ShipsWithWater(pygame.sprite.Sprite):
    def __init__(self, rectWithWater, *group):
        super().__init__(*group)
        self.rect = rectWithWater


class Ships(pygame.sprite.Sprite):
    def __init__(self, size, *group):
        super().__init__(*group)
        self.size = size
        shipwater = pygame.sprite.Group()
        # Сгенерим координаты корабля и буферной зоны
        rectWithWaters = self.generateShip()
        # Создаем корабль с буферной зоной, где нельзя ставить корабль
        sh = ShipsWithWater(rectWithWaters, shipwater)
        while pygame.sprite.spritecollideany(sh, ship_group):
            sh.kill()
            shipwater.empty()
            rectWithWaters = self.generateShip()
            sh = ShipsWithWater(rectWithWaters, shipwater)
        # правильные корабли, которые прошли проверку
        self.add(ship_group)
        print(self.x, self.y, self.size, self.direction)

    def generateShip(self):
        self.x = random.randrange(10)
        self.y = random.randrange(10)
        self.direction = random.randrange(2)
        if self.direction == 0:
            if self.x + (self.size - 1) > 9:
                self.x -= self.size - 1
            self.rect = pygame.Rect(cell_size * self.x, cell_size * self.y, cell_size * self.size, cell_size)
            rectWithWater = pygame.Rect(cell_size * (self.x - 1), cell_size * (self.y - 1),
                                        cell_size * (self.size + 2), cell_size * 3)
        else:
            if self.y + (self.size - 1) > 9:
                self.y -= self.size - 1
            self.rect = pygame.Rect(cell_size * self.x, cell_size * self.y, cell_size, cell_size * self.size)
            rectWithWater = pygame.Rect(
                cell_size * (self.x - 1), cell_size * (self.y - 1), cell_size * 3,
                cell_size * (self.size + 2))
        return rectWithWater

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN:
            # В переменную b передаём кортеж с координатой нажатия, чтобы в переменной a "привести к общему языку" /
            # координаты для удобства работы
            d = args[0].pos
            q = (d[0] - 300, d[1] - 10)
            if self.rect.collidepoint(q):
                board.get_click(d, 2)
                global points
                points += 1
            else:
                board.get_click(d, 1)


class Carrier(Ships):
    def __init__(self, *group):
        super().__init__(4, *group)


class Submarine(Ships):
    def __init__(self, *group):
        super().__init__(3, *group)


class Cruiser(Ships):
    def __init__(self, *group):
        super().__init__(3, *group)


class Destroyer(Ships):
    def __init__(self, *group):
        super().__init__(2, *group)


class Vedette(Ships):
    for i in range(5):
        def __init__(self, *group):
            super().__init__(1, *group)


def result():
    f = open('result.txt', 'w')
    f.write('Ваш уровень: ' + level[lvl] + ' ' + 'Ваши очки: ' + str(points))


def initT():
    pygame.display.set_caption('Морской бой')
    start_screen()
    global running
    running = True
    screen.fill((0, 183, 217))
    change_time()
    all_sprites.empty()
    ship_group.empty()
    clickcoordinate.empty()
    # Создадим четырёхпалубный корабль
    Carrier(all_sprites)
    Submarine(all_sprites)
    Cruiser(all_sprites)
    for _ in range(3):
        Destroyer(all_sprites)
    for _ in range(4):
        Vedette(all_sprites)
    global game_status
    game_status = 0
    global points
    points = 0
    print(game_status)
    print(running)


if __name__ == '__main__':
    initT()
    board = Board(10, 10)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if time > 0:
                if event.type == pygame.USEREVENT + 1:
                    time -= 1
            else:
                game_status = 1
                time = 1000000000000000
            if points == 20:
                game_status = 2
                points += time
                time = 1000000000000000
            if game_status == 0:
                screen.fill((0, 183, 217))
                level_time_points()
                board.render(screen)
                regulations()
                picture_with_ships()
            elif game_status == 1:
                screen.fill((0, 0, 0))
                pygame.draw.line(screen, 'red', (0, 0), (width, height), width=5)
                pygame.draw.line(screen, 'red', (width, 0), (0, height), width=5)
                font = pygame.font.Font(None, 250)
                text = font.render("GAME OVER", True, 'red')
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 2 - text.get_height() // 2
                text_w = text.get_width()
                text_h = text.get_height()
                screen.blit(text, (text_x, text_y))
                pygame.draw.rect(screen, 'red', (text_x - 10, text_y - 10,
                                                 text_w + 20, text_h + 20), 1)
                pygame.draw.rect(screen, (255, 0, 0), (350, 520, 520, 160), 0)
                font1 = pygame.font.Font(None, 80)
                b = font1.render("НАЧАТЬ СНАЧАЛА", True, 'white')
                screen.blit(b, (350, 570))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x >= 350 and x <= 870 and y >= 520 and y <= 680:
                        game_status = -1
            elif game_status == 2:
                screen.fill((0, 183, 217))
                font = pygame.font.Font(None, 250)
                text = font.render("YOU WIN!", True, 'white')
                text_x = width // 2 - text.get_width() // 2
                text_y = height // 2 - text.get_height() // 2
                text_w = text.get_width()
                text_h = text.get_height()
                font = pygame.font.Font(None, 150)
                q = font.render('Ваши очки: ' + str(points), True, pygame.Color('white'))
                screen.blit(text, (text_x, text_y - 150))
                screen.blit(q, (text_x + 50, 360))
                font1 = pygame.font.Font(None, 50)
                a = font1.render("Ваш результат сохранился в txt файл", True, 'white')
                screen.blit(a, (text_x + 100, 460))
                result()
                pygame.draw.rect(screen, (255, 0, 0), (350, 520, 520, 160), 0)
                font1 = pygame.font.Font(None, 80)
                b = font1.render("НАЧАТЬ СНАЧАЛА", True, 'white')
                screen.blit(b, (350, 570))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x >= 350 and x <= 870 and y >= 520 and y <= 680:
                        game_status = -1
            elif game_status == -1:
                initT()
                board = Board(10, 10)
            ship_group.update(event)
            pygame.display.flip()
    pygame.quit()
