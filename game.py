from direct.showbase.ShowBase import ShowBase
from mapmanager import Mapmanager
from panda3d.core import Vec4, Filename, PNMImage
from hero import Hero
import os

import sys
import datetime

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.land = Mapmanager()

        # Если есть saved_map.dat — загружаем его через loadMap().
        if os.path.exists("saves/saved_map.dat"):
            print("Found saved_map.dat — loading saved map")
            try:
                self.land.loadMap()
            except Exception as e:
                print("Error during loadMap():", e)
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
                start_pos = (cx, cy, 100)
            else:
                start_pos = (10, 10, 100)
        else:
            x, y = self.land.loadLand("land.txt")
            start_pos = (x // 2, y // 2, 5)

        # ===== Музыка и небо =====
        try:
            self.music = self.loader.loadMusic(os.path.join("music/minecraft-music.mp3"))

            self.music.setVolume(0.5)
            self.music.setLoop(True)
            self.music.play()
        except Exception as e:
            print("Music load error:", e)

        try:
            self.sky = self.loader.loadModel("assets/block.egg")
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

        # ===== Скриншоты =====
        width, height = 1280, 720
        self.buffer = self.win.makeTextureBuffer("screenshot_buffer", width, height)

        if not self.buffer:
            print("Ошибка: не удалось создать offscreen буфер")
        else:
            self.side_cam = self.makeCamera(self.buffer)
            self.side_cam.reparentTo(self.render)
            self.side_cam.setPos(20, -30, 15)
            self.side_cam.setHpr(15, -10, 0)

        self.accept("f2", self.take_screenshot)

    def save_and_exit(self):
        try:
            self.land.saveMap()
            print("Map saved to saved_map.dat")
        except Exception as e:
            print("Error saving map:", e)
        self.userExit()

    # ===== Метод для скриншотов =====
    def take_screenshot(self):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        screenshot_dir = os.path.join(base_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")

        self.graphicsEngine.renderFrame()
        self.graphicsEngine.flipFrame()

        if not self.buffer:
            print("Немає буфера для скриншотів")
            return

        ok = self.buffer.saveScreenshot(Filename.fromOsSpecific(filename))
        if ok:
            print(f"[OK] Скриншот збереженно: {filename}")
            return
        else:
            print("[!] saveScreenshot не спрацював.")

        img = PNMImage()
        if self.buffer.getScreenshot(img):
            img.write(Filename.fromOsSpecific(filename))
            print(f"[OK] Скриншот готов): {filename}")
        else:
            print("[X] не вдалось зберегти")


if __name__ == "__main__":
    game = Game()
    game.run()
