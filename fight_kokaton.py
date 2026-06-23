import os
import random
import sys
import time

import pygame as pg


WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect，爆弾Rect，ビームRect
    戻り値：横方向，縦方向の画面内判定結果
    """
    yoko, tate = True, True

    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False

    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False

    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """

    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    imgs = {
        (0, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),
        (+5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),
        (+5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),
        (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 135, 0.9),
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 180, 0.9),
        (-5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -135, 0.9),
        (0, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 0.9),
        (+5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(0, 0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface) -> None:
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: pg.key.ScancodeWrapper, screen: pg.Surface) -> None:
        sum_mv = [0, 0]

        for key, mv in __class__.delta.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        self.rct.move_ip(sum_mv)

        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.rct.move_ip(-sum_mv[0], 0)
        if not tate:
            self.rct.move_ip(0, -sum_mv[1])

        self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが発射するビームに関するクラス
    """

    def __init__(self, bird: Bird):
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()

        # ビームの左座標が，こうかとんの右座標になるように配置
        self.rct.left = bird.rct.right
        self.rct.centery = bird.rct.centery

        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface) -> None:
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """

    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2 * rad, 2 * rad))
        self.img.set_colorkey((0, 0, 0))
        pg.draw.circle(self.img, color, (rad, rad), rad)

        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)

        self.vx, self.vy = random.choice([-5, +5]), random.choice([-5, +5])

    def update(self, screen: pg.Surface) -> None:
        yoko, tate = check_bound(self.rct)

        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1

        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


def main() -> None:
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    clock = pg.time.Clock()

    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beam = None

    while True:
        space_down = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                space_down = True

        screen.blit(bg_img, [0, 0])

        # 爆弾とビームの衝突判定
        for i, bomb in enumerate(bombs):
            if beam is not None:
                if beam.rct.colliderect(bomb.rct):
                    bird.change_img(9, screen)
                    beam = None
                    bombs[i] = None

        # こうかとんと爆弾の衝突判定
        for bomb in bombs:
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    bird.change_img(8, screen)

                    fonto = pg.font.Font(None, 80)
                    txt = fonto.render("Game Over", True, (255, 0, 0))
                    screen.blit(txt, [WIDTH // 2 - 150, HEIGHT // 2])

                    pg.display.update()
                    time.sleep(1)
                    return

        bombs = [bomb for bomb in bombs if bomb is not None]

        key_lst = pg.key.get_pressed()

        if space_down:
            beam = Beam(bird)

        bird.update(key_lst, screen)

        for bomb in bombs:
            bomb.update(screen)

        if beam is not None:
            beam.update(screen)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
