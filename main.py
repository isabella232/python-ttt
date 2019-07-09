import tkinter as tk
import tkinter as ttk
# from tkinter import font as tkfont
from PIL import Image, ImageTk
import random
import copy
import math

# 定数

first_col = "#EE4444"
first_col_light = "#EE9999"
second_col = "#4444EE"
second_col_light = "#9999EE"

C_DELAY = 400


# ユーティリティ {{{

def from_rgb(col):
    return "#%02x%02x%02x" % col


def random_color():
    return (
            random.randrange(256),
            random.randrange(256),
            random.randrange(256)
            )


def my_polygon(canvas, pos, pos_list, *args, rotate=0, **kwargs):
    n = len(pos_list)

    pos_list = copy.deepcopy(pos_list)

    pos_list = list(map(lambda el: (
        pos[0] + (el[0] * math.cos(rotate) - el[1] * math.sin(rotate)),
        pos[1] + (el[0] * math.sin(rotate) + el[1] * math.cos(rotate))
        ), pos_list))
    for i in range(n):
        canvas.create_line(pos_list[i], pos_list[(i + 1) % n], *args, **kwargs)


def writePlayer(canvas, who, x, y, *, small=False):
    names = ["first", "second"]
    marks = ["o", "x"]
    cols = [first_col, second_col]
    if small:
        canvas.create_text(
                x, y,
                text=names[who], font=("Molot", 18))
        canvas.create_text(
                x + 45 if who == 0 else x + 53, y-2,
                text=marks[who], fill=cols[who], font=("Molot", 24))
    else:
        canvas.create_text(
                x, y,
                text=names[who], font=("Molot", 26))
        canvas.create_text(
                x + 65 if who == 0 else x + 77, y,
                text=marks[who], fill=cols[who], font=("Molot", 35))

# }}}


# クラス {{{

class Game:
    def __init__(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def get(self, i, j):
        assert(0 <= i < 3)
        assert(0 <= j < 3)
        return self.board[i][j]

    def set(self, i, j, k):
        assert(0 <= i < 3)
        assert(0 <= j < 3)
        assert(0 <= k <= 2)
        self.board[i][j] = k
        return self.check()

    def check(self):
        board = self.board
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != 0:
                return board[i][0]
        for i in range(3):
            if board[0][i] == board[1][i] == board[2][i] != 0:
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != 0:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != 0:
            return board[0][2]
        if self.countNonZero() == 9:
            return -1
        return 0

    def countNonZero(self):
        cnt = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j]:
                    cnt += 1
        return cnt

    # こういうのはデバッグ用に残しておく
    def output(self):
        print("-------")
        for i in range(3):
            print("|", end="")
            for j in range(3):
                if self.get(i, j) == 0:
                    print(" ", end="")
                elif self.get(i, j) == 1:
                    print("o", end="")
                elif self.get(i, j) == 2:
                    print("x", end="")
                print("|", end="")
            print()
            print("-------")

    def outputWithNumber(self):
        num = 1
        fromNum = []
        print()
        print("-------")
        for i in range(3):
            print("|", end="")
            for j in range(3):
                if game.get(i, j) == 0:
                    print(num, end="")
                    num += 1
                    fromNum.append((i, j))
                elif game.get(i, j) == 1:
                    print("o", end="")
                elif game.get(i, j) == 2:
                    print("x", end="")
                print("|", end="")
            print()
            print("-------")
        return fromNum

    def __hash__(self):
        hs = 0
        for i in range(3):
            for j in range(3):
                hs += self.board[i][j] * (3 ** (i * 3 + j))
        return hs


class GameAI:
    def __init__(self, func, name):
        self.func = func
        self.name = name

    def think(self, me, game: Game):
        return self.func(me, game)


game = Game()


def think1(me, game):
    while(True):
        select = (random.randrange(3), random.randrange(3))
        if game.get(select[0], select[1]) == 0:
            return select

# }}}


# 計算 {{{

# メモ化再帰 : 本質的な計算量改善

memo = {}


def think_dfs(me, you, game):
    if hash(game) in memo:
        return memo[hash(game)]
    if game.check() != 0:
        memo[hash(game)] = (game.check(), [])
        return memo[hash(game)]

    canWin = []
    canReachDraw = []
    some = []

    for i in range(3):
        for j in range(3):
            if game.get(i, j) == 0:
                game2 = copy.deepcopy(game)
                game2.set(i, j, me)
                winner = think_dfs(you, me, game2)[0]
                if me == winner:
                    canWin.append((i, j))
                if winner == -1:
                    canReachDraw.append((i, j))
                some.append((i, j))
    if canWin:
        memo[hash(game)] = (me, canWin)
    elif canReachDraw:
        memo[hash(game)] = (-1, canReachDraw)
    else:
        memo[hash(game)] = (you, some)
    return memo[hash(game)]


# メモを予め埋めておく
think_dfs(1, 2, Game())
think_dfs(2, 1, Game())


def think2(me, game):
    if random.randrange(9) < 3:
        return think3(me, game)
    else:
        return think1(me, game)


def think3(me, game, *, noResign=False):
    (winner, candi) = think_dfs(me, 3 - me, copy.deepcopy(game))
    if winner == 3 - me and not noResign:
        return None
    assert(len(candi) != 0)
    return random.choice(candi)


# }}}


# アプリメイン {{{

class TicTacToe(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.width = 500
        self.height = 500

        self.title("Tic Tac Toe")
        self.geometry(f"{self.width}x{self.height}")

        # メインのフレーム
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # grid_[row/column]configure(index, ...)
        # これは, weightによる重み付けを行ったグリッド表示をする
        # https://effbot.org/tkinterbook/grid.htm#Tkinter.Grid.grid_rowconfigure-method
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        pages = [TitleScene, LevelSelect, Main]  # TODO
        self.frames = {}
        for page in pages:
            page_name = page.__name__
            frame = page(parent=container, controller=self)
            self.frames[page_name] = frame

            # グリッドマネージャーにより, フレームを中央に置く
            # https://effbot.org/tkinterbook/grid.htm
            frame.grid(row=0, column=0, sticky="nsew")
            # nsew と指定することで中央寄せができる

        self.raise_frame("TitleScene")

    def raise_frame(self, page_name):
        assert(page_name in self.frames.keys())

        # フレームの重なりを一番上に持ってくるようなことをする
        # tkraise : https://kite.com/python/docs/Tkinter.Frame.tkraise
        frame = self.frames[page_name]
        frame.refresh()
        frame.tkraise()

# }}}


# シーンの抽象化 {{{

class Scene(ttk.Frame):
    def __init__(self, *args, parent, controller, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.controller = controller
        self.width = controller.width
        self.height = controller.height

    def refresh(self):
        pass

# }}}


# シーン : タイトル {{{

class TitleScene(Scene):
    def __init__(self, parent, controller):
        Scene.__init__(self, parent=parent, controller=controller)

        canvas = self.canvas = ttk.Canvas(
                self,
                width=500, height=500, bg="black")
        canvas.pack()

        # https://stackoverflow.com/questions/29401873/tkinter-pil-image-not-displaying-inside-of-a-function
        # ものすごい罠. 画像は変数に束縛しておかないと, ガベコレで勝手に消えてしまう
        self.title0_img = ImageTk.PhotoImage(Image.open("title1.png"))
        canvas.create_image(0, 0, image=self.title0_img, anchor="nw")

        self.left_logo = MiniLogo(canvas, "left_logo")

        self.right_logo = MiniLogo(canvas, "right_logo")

        self.counter = 0
        self.after(1000//60, self.update)

        canvas.bind("<1>", lambda ev: controller.raise_frame("LevelSelect"))

    def update(self):

        M = 300
        self.counter += 1
        self.counter %= M

        canvas = self.canvas
        y = self.height - 80 + math.sin(math.pi * 2 * self.counter / M) * 20
        canvas.delete("mes")
        canvas.create_text(
                self.width / 2, y,
                text="touch to start",
                fill="white", tags="mes", font=("Molot", 30))

        self.left_logo.pos = (45, y)
        self.right_logo.pos = (self.width - 45, y)

        self.after(1000//60, self.update)

    def refresh(self):
        pass


# }}}


# 小さな回るロゴ {{{

class MiniLogo:
    def __init__(self, canvas, tag):
        self.canvas = canvas
        self.counter = 0
        self.tag = tag
        self.delay = 1000 // 60
        self.pos = (0, 0)
        canvas.after(self.delay, self.rotateOuter)

    def my_after(self, M, M2, now, nxt):
        canvas = self.canvas
        if self.counter < M:
            canvas.after(self.delay, now)
        elif self.counter < M2:
            canvas.after(self.delay, now)
        else:
            self.counter = 0
            canvas.after(self.delay, nxt)

    # 外側で一回転
    def rotateOuter(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        tag = self.tag
        c = min(self.counter / M, 1)

        canvas.delete(tag)

        for i in range(-1, 2):
            for j in range(-1, 2):
                my_polygon(
                        canvas,
                        (self.pos[0] + i * 12, self.pos[1] + j * 12),
                        [(-6, -6), (-6, 6), (6, 6), (6, -6)],
                        rotate=2*math.pi*3/4*c,
                        fill="white",
                        width=2,
                        capstyle="projecting",  # もはやどこにドキュメントが存在するかわからない
                        tags=tag)

        self.my_after(M, M * 3, self.rotateOuter, self.shrink)

    # 小さくなる
    def shrink(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        tag = self.tag
        c = min(self.counter / M, 1)

        canvas.delete(tag)

        for i in range(-1, 2):
            for j in range(-1, 2):
                r = 6 * (1 - c * .4)
                my_polygon(
                        canvas,
                        (self.pos[0] + i * 12, self.pos[1] + j * 12),
                        [(-r, -r), (-r, r), (r, r), (r, -r)],
                        fill="white",
                        width=2,
                        capstyle="projecting",
                        tags=tag)

        self.my_after(M, M * 3, self.shrink, self.gather)

    # 集まる
    def gather(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        tag = self.tag
        c = min(self.counter / M, 1)

        canvas.delete(tag)

        for i in range(-1, 2):
            for j in range(-1, 2):
                r = 6 * .6
                my_polygon(
                        canvas,
                        (
                            self.pos[0] + i * 12 * (1 - c),
                            self.pos[1] + j * 12 * (1 - c)),
                        [(-r, -r), (-r, r), (r, r), (r, -r)],
                        fill="white",
                        width=2,
                        capstyle="projecting",
                        tags=tag)

        self.my_after(M, M * 3, self.gather, self.rotateInner)

    # 内側で回転
    def rotateInner(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        tag = self.tag
        c = min(self.counter / M, 1)

        canvas.delete(tag)

        r = 6 * .6
        my_polygon(
                canvas,
                self.pos,
                [(-r, -r), (-r, r), (r, r), (r, -r)],
                fill="white",
                rotate=-math.pi*2/4*3*c,
                width=2,
                capstyle="projecting",
                tags=tag)

        self.my_after(M, M * 3, self.rotateInner, self.spread)

    # 広がる
    def spread(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        tag = self.tag
        c = min(self.counter / M, 1)

        canvas.delete(tag)

        for i in range(-1, 2):
            for j in range(-1, 2):
                r = 6 * .6
                my_polygon(
                        canvas,
                        (self.pos[0] + i * 12 * c, self.pos[1] + j * 12 * c),
                        [(-r, -r), (-r, r), (r, r), (r, -r)],
                        fill="white",
                        width=2,
                        capstyle="projecting",
                        tags=tag)

        self.my_after(M, M * 3, self.spread, self.expand)

    # 大きくなる
    def expand(self):
        M = 20
        self.counter += 1
        canvas = self.canvas
        c = min(self.counter / M, 1)
        tag = self.tag

        canvas.delete(tag)

        for i in range(-1, 2):
            for j in range(-1, 2):
                r = 6 * (.4 + c * .6)
                my_polygon(
                        canvas,
                        (self.pos[0] + i * 12, self.pos[1] + j * 12),
                        [(-r, -r), (-r, r), (r, r), (r, -r)],
                        fill="white",
                        width=2,
                        capstyle="projecting",
                        tags=tag)

        self.my_after(M, M * 3, self.expand, self.rotateOuter)

# }}}


# シーン : レベルセレクト {{{

class LevelSelect(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)

        self.lv1 = LevelSelector(selection, self)
        self.lv1.place(x=30, y=200)
        self.lv2 = LevelSelector(selection, self)
        self.lv2.place(x=260, y=200)

        start_btn = MyButton(
                self,
                text="start",
                width=240, height=60,
                command=self.start)
        start_btn.place(x=120, y=420)

        card1 = Player(self, text="First", mark="o", col=first_col)
        card1.place(x=30, y=100)

        card2 = Player(self, text="Second", mark="x", col=second_col)
        card2.place(x=260, y=100)

        self.lv1.set(0)
        self.lv2.set(1)

    def start(self, ev):
        self.controller.AI1 = self.lv1.getAI()
        self.controller.AI2 = self.lv2.getAI()
        self.controller.Card1 = self.lv1.getCard()
        self.controller.Card2 = self.lv2.getCard()

        self.controller.raise_frame("Main")

    def refresh(self):
        pass

# }}}


# シーン : ゲーム {{{

class Main(Scene):
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)

        vs = ttk.Canvas(self, width=200, height=100)
        vs.create_text(40, 40, text="v", font=("Molot", 23))
        vs.create_text(60, 50, text="s", font=("Molot", 23))
        vs.place(x=197, y=10)

        cells = self.cells = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                # クロージャを作る
                cell = cells[i][j] = Cell(
                        self,
                        width=100, height=100,
                        command=(lambda i, j: lambda ev: self.clicked(i, j))
                        (i, j))
                cell.place(x=90 + 104*i, y=100 + 104*j)
                cell.setMark("o", first_col)

        self.card = [None, None]

        self.resign_btn = MyButton(
                self, text="resign",
                width=140, height=60,
                command=self.resign)
        self.help_btn = MyButton(
                self, text="help",
                width=140, height=60,
                command=self.help)
        self.quit_btn = MyButton(
                self, text="quit",
                width=140, height=60,
                command=self.quit)

        self.message = None

    def human_interface(self, show):
        if show:
            self.resign_btn.place(x=10, y=420)
            self.help_btn.place(x=170, y=420)
            self.quit_btn.place(x=330, y=420)
        else:
            self.resign_btn.place_forget()
            self.help_btn.place_forget()
            self.quit_btn.place_forget()

    def over(self):
        self.message = ttk.Canvas(self, width=300, height=100)
        self.message.place(x=20, y=410)
        self.gameover = True
        self.refrectGame()
        self.human_interface(False)
        self.quit_btn.place(x=330, y=420)

    def draw(self):
        self.over()
        self.message.create_text(140, 40, text="draw", font=("Molot", 30))

    def resigned(self):
        self.over()
        writePlayer(self.message, self.turn, 60, 25, small=True)
        self.message.create_text(190, 25, text="resigned.", font=("Molot", 18))
        writePlayer(self.message, 1 - self.turn, 130, 60)
        self.message.create_text(260, 60, text="win", font=("Molot", 25))

    def playerWin(self):
        self.over()
        writePlayer(self.message, self.turn, 70, 40)
        self.message.create_text(200, 40, text="win", font=("Molot", 25))

    def refresh(self):
        self.game = Game()

        self.AI = [self.controller.AI1, self.controller.AI2]

        for c in self.card:
            if c:
                c.place_forget()

        if self.message:
            self.message.place_forget()

        Card1 = self.controller.Card1
        Card2 = self.controller.Card2

        self.card = [Card1(self), Card2(self)]

        self.card[0].place(x=20, y=10)
        self.card[1].place(x=270, y=25)

        self.is_human = False
        self.gameover = False
        self.turn = 0
        self.turnSetup()

    def refrectGame(self):
        for i in range(3):
            for j in range(3):
                w = self.game.get(i, j)
                self.cells[i][j].disabled = not self.is_human or self.gameover
                if w == 0:
                    self.cells[i][j].setMark(
                            "o" if self.turn == 0 else "x",
                            first_col_light if self.turn == 0
                            else second_col_light)
                    self.cells[i][j].setDetermined(False)
                elif w == 1:
                    self.cells[i][j].setMark("o", first_col)
                    self.cells[i][j].setDetermined(True)
                elif w == 2:
                    self.cells[i][j].setMark("x", second_col)
                    self.cells[i][j].setDetermined(True)

    def turnSetup(self):
        self.is_human = self.AI[self.turn].name == "human"
        self.opps = 1 - self.turn

        self.refrectGame()

        self.card[self.turn].setActive(True)
        self.card[self.opps].setActive(False)

        self.human_interface(self.is_human)

        if not self.is_human:
            self.after(C_DELAY, self.AI_choose)

    def AI_choose(self):
        sel = self.AI[self.turn].think(self.turn + 1, self.game)
        if sel is None:
            self.resigned()
            return
        self.game.set(sel[0], sel[1], self.turn + 1)
        self.next()

    def clicked(self, i, j):
        if self.game.get(i, j) != 0:
            return
        if not self.is_human or self.gameover:
            return
        self.game.set(i, j, self.turn + 1)
        self.next()

    def resign(self, ev):
        if not self.is_human or self.gameover:
            return
        self.resigned()

    def help(self, ev):
        if not self.is_human or self.gameover:
            return
        sel = think3(self.turn, self.game, noResign=True)
        self.game.set(sel[0], sel[1], self.turn + 1)
        self.next()

    def quit(self, ev):
        if not self.is_human and not self.gameover:
            return
        self.controller.raise_frame("TitleScene")

    def next(self):
        ch = self.game.check()
        if ch == 0:
            self.turn = 1 - self.turn
            self.turnSetup()
        elif ch == -1:
            self.draw()
        elif ch == 1 or ch == 2:
            self.playerWin()

# }}}


# ボタン {{{

class MyButton(ttk.Canvas):
    def __init__(
            self, *args, width, height,
            command=None, text="",
            col1=from_rgb((240, 200, 200)),
            col2=from_rgb((240, 160, 160)),
            col3=from_rgb((240, 60, 60)),
            after_moved=None,
            after_leaved=None,
            fontsize=18, **kwargs):
        ttk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)

        self.disabled = False

        self.width = width
        self.height = height

        self.col1 = col1
        self.col2 = col2
        self.col3 = col3

        self.after_moved = after_moved
        self.after_leaved = after_leaved

        if command:
            self.bind("<1>", command)

        self.bind("<1>", self.pressing, add="+")
        self.bind("<ButtonRelease-1>", self.moved)
        self.bind("<Enter>", self.moved)
        self.bind("<Motion>", self.moved)
        self.bind("<Leave>", self.leaved)

        self.leaved(None)

        self.text = self.create_text(
                width/2, height/2,
                text=text, font=("Molot", fontsize))

    def pressing(self, ev, force=False):
        if self.disabled and not force:
            return
        width, height = self.width, self.height
        self.delete("face")
        self.create_rectangle(
                4, 4, width, height,
                fill=self.col3,
                outline=from_rgb((120, 120, 120)), width=4, tags="face"
                )
        self.lower("face")

    def moved(self, ev, force=False):
        if self.disabled and not force:
            return
        width, height = self.width, self.height
        self.delete("face")
        self.create_rectangle(
                4, 4, width, height,
                fill=self.col2,
                outline=from_rgb((120, 120, 120)), width=4, tags="face"
                )
        self.lower("face")
        if self.after_moved:
            self.after_moved()

    def leaved(self, ev, force=False):
        if self.disabled and not force:
            return
        width, height = self.width, self.height
        self.delete("face")
        self.create_rectangle(
                4, 4, width, height,
                fill=self.col1,
                outline=from_rgb((120, 120, 120)), width=4, tags="face"
                )
        self.lower("face")
        if self.after_leaved:
            self.after_leaved()

# }}}


# セル {{{

class Cell(MyButton):
    def __init__(self, *args, **kwargs):
        self.determined = False
        self.mark = ""
        self.col = "black"

        MyButton.__init__(
                self, *args,
                col1="#EEEEEE",
                col2="#DDDDDD",
                col3="#888888",
                after_moved=self.after_moved,
                after_leaved=self.after_leaved,
                **kwargs)

        self.setDetermined(False)

    def setDetermined(self, determined):
        self.determined = determined

        if determined:
            self.delete("mark")
            self.create_text(
                    50, 50,
                    text=self.mark, font=("Molot", 50),
                    tags="mark",
                    fill=self.col)

            self.col1 = "#EEEEEE"
            self.col2 = "#EEEEEE"
            self.col3 = "#EEEEEE"
            self.leaved(None, force=True)
        else:
            self.col1 = "#EEEEEE"
            self.col2 = "#DDDDDD"
            self.col3 = "#888888"
            self.leaved(None, force=True)

    def setMark(self, mark, col):
        self.mark = mark
        self.col = col

    def after_moved(self):
        if self.determined:
            return
        self.delete("mark")
        self.create_text(
                50, 50,
                text=self.mark, font=("Molot", 50),
                tags="mark",
                fill=self.col)

    def after_leaved(self):
        if self.determined:
            return
        self.delete("mark")

# }}}


# レベルカード {{{

class Lv1(ttk.Canvas):
    def __init__(
            self, *args, **kwargs):
        self.width = width = 200
        self.height = height = 60
        ttk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)

        self.setActive(True)

    def setActive(self, active):
        width = self.width
        height = self.height

        self.delete("all")

        self.create_rectangle(
                4, 4, width, height,
                fill=from_rgb((240, 240, 200)) if active
                else "#AAAAAA",
                outline="black",
                width=4 if active else 1,
                tags="face"
                )
        self.text = self.create_text(
                20 + width/2, height/2,
                text="Lv.1", font=("Molot", 22))
        r = 4
        square = [(-r, -r), (-r, r), (r, r), (r, -r)]

        my_polygon(self, (width/2 - 40, height/2), square)


class Lv2(ttk.Canvas):
    def __init__(
            self, *args, **kwargs):
        self.width = width = 200
        self.height = height = 60
        ttk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)

        self.setActive(True)

    def setActive(self, active):
        width = self.width
        height = self.height

        self.delete("all")

        self.create_rectangle(
                4, 4, width, height,
                fill=from_rgb((240, 200, 160)) if active
                else "#AAAAAA",
                outline="black",
                width=4 if active else 1,
                tags="face"
                )
        self.text = self.create_text(
                20 + width/2, height/2,
                text="Lv.2", font=("Molot", 22))
        r = 4
        square = [(-r, -r), (-r, r), (r, r), (r, -r)]

        my_polygon(self, (width/2 - 40, height/2-6), square)
        my_polygon(self, (width/2 - 40 - 8, height/2+8), square)
        my_polygon(self, (width/2 - 40 + 8, height/2+8), square)


class Lv3(ttk.Canvas):
    def __init__(
            self, *args, **kwargs):
        self.width = width = 200
        self.height = height = 60
        ttk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)

        self.setActive(True)

    def setActive(self, active):
        width = self.width
        height = self.height

        self.delete("all")

        self.create_rectangle(
                4, 4, width, height,
                fill=from_rgb((240, 160, 150)) if active
                else "#AAAAAA",
                outline="black",
                width=4 if active else 1,
                tags="face"
                )
        self.text = self.create_text(
                20 + width/2, height/2,
                text="Lv.3", font=("Molot", 22))

        r = 2
        square = [(-r, -r), (-r, r), (r, r), (r, -r)]
        my_polygon(self, (width/2 - 40, height/2+2), square)

        r = 4
        square = [(-r, -r), (-r, r), (r, r), (r, -r)]
        my_polygon(self, (width/2 - 40, height/2-6), square)
        my_polygon(self, (width/2 - 40 - 8, height/2+8), square)
        my_polygon(self, (width/2 - 40 + 8, height/2+8), square)
        self.create_arc(
                width/2 - 45, height/2 - 3,
                width/2 - 35, height/2 + 7,
                extent=359, style="chord")


class HumanLavel(ttk.Canvas):
    def __init__(
            self, *args, **kwargs):
        self.width = width = 200
        self.height = height = 60
        ttk.Canvas.__init__(self, *args, width=width, height=height, **kwargs)

        self.setActive(True)

    def setActive(self, active):
        width = self.width
        height = self.height

        self.delete("all")

        self.create_rectangle(
                4, 4, width, height,
                fill=from_rgb((200, 240, 240)) if active
                else "#AAAAAA",
                outline="black",
                width=4 if active else 1,
                tags="face"
                )
        self.text = self.create_text(
                20 + width/2, height/2,
                text="human", font=("Molot", 22))
        r = 4
        square = [(-r, -r), (-r, r), (r, r), (r, -r)]

        my_polygon(self, (width/2 - 60, height/2 - 10), square)
        self.create_line(
                (width/2 - 60 - 8, height/2 + 8),
                (width/2 - 60, height/2 - 6))
        self.create_line(
                (width/2 - 60 + 8, height/2 + 8),
                (width/2 - 60, height/2 - 6))
        self.create_line(
                (width/2 - 60, height/2 - 6),
                (width/2 - 60, height/2 + 16))
        self.create_line(
                (width/2 - 60, height/2 + 16),
                (width/2 - 60 - 8, height/2 + 16 + 8))
        self.create_line(
                (width/2 - 60, height/2 + 16),
                (width/2 - 60 + 8, height/2 + 16 + 8))

# }}}


# レベルセレクタ {{{

class LevelSelector(ttk.Frame):
    def __init__(self, selection, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.selection = selection
        self.n = len(selection)

        # prev ボタン
        prev_btn = self.btn = MyButton(
                self, width=100, height=60,
                text="prev", command=lambda ev: self.prev())
        prev_btn.grid(row=0, column=0)

        # next ボタン
        next_btn = self.btn = MyButton(
                self,
                width=100, height=60,
                text="next", command=lambda ev: self.next())
        next_btn.grid(row=2, column=0)

        self.cards = []
        for (AI, Card) in selection:
            frame = ttk.Frame(self)
            frame.grid(row=1, column=0, sticky="nsew")
            card = Card(frame)
            card.grid(row=1, column=0, sticky="nsew")
            self.cards.append(frame)

        self.index = 0
        self.raiseCard(0)

    def raiseCard(self, num):
        assert(0 <= num < self.n)
        self.cards[num].tkraise()

    def next(self):
        self.index += 1
        self.index %= self.n
        self.raiseCard(self.index)

    def prev(self):
        self.index -= 1
        self.index %= self.n
        self.raiseCard(self.index)

    def getAI(self):
        return self.selection[self.index][0]

    def getCard(self):
        return self.selection[self.index][1]

    def set(self, index):
        self.index = index
        self.raiseCard(self.index)

# }}}


# AIのセットアップ {{{

human = (GameAI(None, "human"), HumanLavel)
AI1 = (GameAI(think1, "computer (level1)"), Lv1)
AI2 = (GameAI(think2, "computer (level2)"), Lv2)
AI3 = (GameAI(think3, "computer (level3)"), Lv3)  # TODO

selection = [human, AI1, AI2, AI3]

# }}}


# プレイヤーカード {{{

# 先手/後手 流用
class Player(ttk.Frame):
    def __init__(self, *args, text, mark, col, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.width = width = 200
        self.height = height = 80

        canvas = ttk.Canvas(self, width=width, height=height)
        canvas.grid()

        canvas.create_rectangle(
                4, 4, width, height,
                fill=from_rgb((240, 240, 240)),
                outline="black", width=4, tags="face"
                )
        canvas.create_text(
                width/2 - 20, height/2,
                text=text, font=("Molot", 22))
        canvas.create_text(
                width/2 + 50, height/2,
                text=mark, font=("Molot", 40),
                fill=col)

# }}}


# メインループ
if __name__ == "__main__":
    app = TicTacToe()
    app.mainloop()
