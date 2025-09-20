from direct.showbase.ShowBase import ShowBase
from mapmanager import Mapmanager
from panda3d.core import CardMaker, TextureStage
from hero import Hero
from panda3d.core import Vec4


class Game(ShowBase):
   def __init__(self):
       ShowBase.__init__(self)
       self.land = Mapmanager()
       x, y = self.land.loadLand("land.txt")
       self.music = self.loader.loadMusic("minecraft-run-music-394978.mp3")
       self.music.setVolume(0.5)
       self.music.setLoop(True)
       self.music.play()
       self.sky = self.loader.loadModel("block.egg")  # или "skybox.bam"
       self.sky.reparentTo(self.render)
       base.setBackgroundColor(Vec4(0.5, 0.7, 1, 1))
        # Масштабируем и центрируем, чтобы он окружал игрока
       self.sky.setScale(500)
       self.sky.setPos(0, 0, 0)

        # Чтобы небо всегда было за героем
    #    self.taskMgr.add(self.update_sky, "update_sky")
       self.hero = Hero((x // 2, y // 2, 5), self.land)
       base.camLens.setFov(90)


game = Game()
game.run()
