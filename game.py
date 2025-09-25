from direct.showbase.ShowBase import ShowBase
from mapmanager import Mapmanager
from panda3d.core import Vec4
from hero import Hero
import os
from panda3d.core import Filename

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.land = Mapmanager()

        # Если есть saved_map.dat — загружаем его через loadMap().
        # Иначе — загружаем обычный мир land.txt через loadLand().
        if os.path.exists("saved_map.dat"):
            print("Found saved_map.dat — loading saved map")
            try:
                # loadMap() у тебя читает saved_map.dat и создаёт блоки
                self.land.loadMap()
            except Exception as e:
                print("Error during loadMap():", e)
            # Попробуем вычислить центр карты по существующим блокам,
            # чтобы поставить героя в центр сохранённой области.
            try:
                children = list(self.land.getChildren())
                positions = []
                for b in children:
                    p = b.getPos()
                    positions.append((p.getX(), p.getY()))
            except Exception:
                positions = []

            if positions:
                xs = [p[0] for p in positions]
                ys = [p[1] for p in positions]
                cx = int((min(xs) + max(xs)) / 2)
                cy = int((min(ys) + max(ys)) / 2)
                start_pos = (cx, cy, 50)
            else:
                start_pos = (10, 10, 50)
        else:
            # если сохранения нет — загружаем land.txt (твоя текущая логика)
            x, y = self.land.loadLand("land.txt")
            start_pos = (x // 2, y // 2, 5)

        # ===== Музыка и небо =====
        try:
            self.music = self.loader.loadMusic(os.path.join("subwoofer-lullaby-m.mp3"))
            self.music.setVolume(0.5)
            self.music.setLoop(True)
            self.music.play()
        except Exception as e:
            print("Music load error:", e)

        try:
            self.sky = self.loader.loadModel("block.egg")
            self.sky.reparentTo(self.render)
            base.setBackgroundColor(Vec4(0.5, 0.7, 1, 1))
            self.sky.setScale(500)
            self.sky.setPos(0, 0, 0)
        except Exception as e:
            print("Sky load error:", e)

        # ===== Герой =====
        self.hero = Hero(start_pos, self.land)
        base.camLens.setFov(90)

        # При нажатии ESC — сохраняем через saveMap() и выходим.
        self.accept("escape", self.save_and_exit)

    def save_and_exit(self):
        try:
            # saveMap() у тебя сохраняет в saved_map.dat
            self.land.saveMap()
            print("Map saved to saved_map.dat")
        except Exception as e:
            print("Error saving map:", e)
        # корректный выход из Panda3D
        self.userExit()


if __name__ == "__main__":
    game = Game()
    game.run()
