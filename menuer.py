from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from launcher import SaveSlotManager

class Menuer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)


        #adding the text tot the menuer
        self.Label = DirectLabel(text = "Starting screen", scale = 0.15, pos = Vec3(0, 0, 0.7), text_bg = (0, 0, 0, 1),
                                 text_fg = (1, 1, 1, 1), textMayChange = 1)
        #le button for GAME
        self.Button_game = DirectButton(text = "Turn on the launcher", scale = 0.15, pos = Vec3(0, 0, 0.2), text_bg = (0, 0.5, 0, 1),
                                   text_fg = (1, 1, 1, 1), textMayChange = 1, command = self.begin_game)
        # le button for QUIT
        self.Button_quit = DirectButton(text="Exit", scale=0.15, pos=Vec3(0, 0, -0.5), text_bg=(0, 0.5, 0, 1),
                                   text_fg=(1, 1, 1, 1), textMayChange = 1, command=self.quit_game)

    def destroy_menu_ui(self):
        self.Label.destroy()
        self.Button_game.destroy()
        self.Button_quit.destroy()

    def begin_game(self):
        if __name__ == "__main__":
            game = SaveSlotManager()
            game

    def quit_game(self):
        self.userExit()


if __name__ == "__main__":
    menu = Menuer()
    menu.run()