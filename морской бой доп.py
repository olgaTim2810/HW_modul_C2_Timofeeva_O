from random import randint

#Класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x},{self.y})'

#Классы исключений
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):   #Исключение неправильного корабля: выход за границы или занятость точек
    pass

#Класс корабля (с полями нос корабля, его длина, ориентация)
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []          #в списке ship_dots будут хранится все координаты коробля
        for i in range(self.l): #задаем координаты корабля, начиная с его "носа"
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:     #проверяем ориентацию корабля
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))   #добавляем в рассматриваемый корабль заданные координаты

        return ship_dots

#Проверка попадания в корабль
    def shooten(self, shot):
        return shot in self.dots

#Класс "игровое поле" (с полями "скрыть поле" и размер)
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  #количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]  #размер поля

        self.busy = []  #хранение точек занятых кораблями и точек попавших в корабли
        self.ships = []  #список кораблей

#Вывод корабля на доску
    def __str__(self):
        res = ""  #описание всей доски
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):  #Проходимся по строкам и индексам поля/доски
            res += f"\n{i + 1} | " + " | ".join(row) + " |" #вывод номера строки и ее оформление

        if self.hid:                     #Параметр сокрытия кораблей на доске: если hid == True, то
            res = res.replace("■", "O")  #заменяем "квадратики" корабля на пустоту "0" (если мы хотим скрыть корабль на доске)
        return res

#Проверка расположения корабля за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

#Контур корабля и добавление его на доску
    def contour(self, ship, verb=False):
    #окружение точки, в которой мы находимся: создадим список со сдвинутыми/соседними точками, вокруг данной точки
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:  #для каждой точки из списка точек корабля
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
               # self.field[cur.x][cur.y] = '+'                       #не даем кораблям располагаться близко друг к другу
                if not (self.out(cur)) and cur not in self.busy:      #если точка не выходит за границы и не занята,то:
                    if verb:                                    #параметр verb говорит нужно ли ставить точки вокруг корабля, по умолчанию verb=False
                        self.field[cur.x][cur.y] = "."                #ставим на месте этой точки - '.'
                    self.busy.append(cur)                             #добавляем точку в список занятых точек

#Метод проверяющий, что каждая точка корабля не выходит за границы и не занята
    def add_ship(self, ship):
        for d in ship.dots:  # Пройдемся по точкам корабля
            if self.out(d) or d in self.busy: #Выбрасываем исключение, если точки корабля выходят за границы или заняты
                raise BoardWrongShipException()
        for d in ship.dots:      #Все точки корабля обозначим квадратиками и впишим каждую такую точку в список занятых
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship) #составляем список собственных кораблей
        self.contour(ship)      #обводим их по контуру

#Стрельба по доске
    def shot(self, d):                 #Выстрел по точкам корабля
        if self.out(d):                #если точка за пределами доски
            raise BoardOutException()  #выбрасываем исключение

        if d in self.busy:             #если точка занята
            raise BoardUsedException() #выбрасываем исключение

        self.busy.append(d)            #делаем точку занятой, если она не была занята

        for ship in self.ships:        #проход в цикле по кораблям, для проверки принадлежности точки к какому-то кораблю
            if ship.shooten(d):        #if d in ship.dots:  если в корабль попали:
                ship.lives -= 1        #уменьшаем количество жизней корабля и помечаем пораженную точку "X"
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:    #если у корабля кончились жизни, увеличиваем счетчик пораженных кораблей на 1
                    self.count += 1
                    self.contour(ship, verb=True)  #Точками "." обозначим контур корабля
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):   #до начала игры в списке busy хранились точки соседствующие с кораблями
        self.busy = []  #обнулим список хранения точек соседствующих с кораблями, т.к. список будет использоваться для хранения выстрелов игрока

    def defeat(self):
        return len(self.ships)   #повтор хода, при попадании в цель

#класс Игрока
class Player:
    def __init__(self, board, enemy):               #введем две доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()     #привызове метода ask будет выводиться ошибка, т.к. этот метод нужен для потомков данного класса

    def move(self):                                 #в бесконечном цикле выполняем выстрел
        while True:
            try:
                target = self.ask()                 #цель: координаты выстрела
                repeat = self.enemy.shot(target)    #повтор: выполнение выстрела, если игрок попал в цель
                return repeat
            except BoardException as e:
                print(e)

#Класс игрок-комп
class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

#Класс игрок-пользователь
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

#Класс игры
class Game:
    def __init__(self, size=6):   #сосдадим конструктор с размерами доски, случайными досками для игрока и компьютера
        self.size = size
        pl = self.random_board()  #случайные доски для игрока и компьютера
        co = self.random_board()
        co.hid = True            #скроем доску компьютера от игрока

        self.ai = AI(co, pl)      #создание игроков
        self.us = User(pl, co)

    def try_board(self):                   #метод создающий корабли на доске
        lens = [3, 2, 2, 1, 1, 1, 1]       #список с длиной кораблей
        board = Board(size=self.size)      #создание доски
        attempts = 0
        for l in lens:                     #установка кораблей на доску
            while True:
                attempts += 1              #увеличиваем количество попыток поставить корабли на доску
                if attempts > 2000:        #кол-во попыток поставить корабли, если >2000, то пишим None
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))   #случайным образом устанавливаем корабль на доску
                try:
                    board.add_ship(ship)         #Если все корабли установились правильно, то цикл закончен
                    break
                except BoardWrongShipException:   #Если выскочило исключение (корабли неверно расположились на доске), то операция выполняется заново
                    pass
        board.begin()           #подготовить доску к игре
        return board
#метод гарантированно генерирующий случайную доску
    def random_board(self):
        board = None                              #рассматриваем пустую доску
        while board is None:                      #в бесконечном цикле пытаемся создать корабли на доске
            board = self.try_board()
        return board

#Приветствие
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def merge_boards(first, second):
        first_lines = first.split("\n")
        second_lines = second.split("\n")

        result = ""
        for i in range(len(first_lines)):
            result_line = f"{first_lines[i]:27}   *   {second_lines[i]} \n"
            result += result_line

        return result

#Игровой цикл
    def loop(self):
        num = 0       #номер хода
        while True:   #вывод досок пользователя и компьютера по очереди
            print("-" * 20)
            print()
            user_board = "   Доска пользователя:\n" + str(self.us.board)
            ai_board = "   Доска компьютера:\n" + str(self.ai.board)
            print(Game.merge_boards(user_board, ai_board))

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()      #выстрел игрока
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()      #выстрел компьютера
            if repeat:                       #метод repeat отвечает за повтор хода, если необходимо повторить ход, то меняем номер хода,
                num -= 1                     #чтобы переменная num осталась такой же и ход остался у того же игрока

            if self.ai.board.count == len(self.ai.board.ships):     #если пользователь поразил 7 кораблей компьютера, то он выиграл
                print("-" * 20)
                print(self.ai.board)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                print(self.us.board)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()