import pickle
from panda3d.core import Vec3

class Mapmanager():
    """ Управління карткою з різними текстурами """
    def __init__(self):
        # модель кубика
        self.model = 'block'  # block.egg
        # словарь текстур для разных типов блоков
        self.textures = {
            "Grass": loader.loadTexture("assets/Grass.png"),
            "Dirt": loader.loadTexture("assets/Dirt.png"),
            "Cobblestone": loader.loadTexture("assets/Cobblestone.png")
        }

        # создаем основной узел карты
        self.startNew()

    def startNew(self):
        """Создаёт основу для новой карты"""
        self.land = render.attachNewNode("Land")
        self.pets = render.attachNewNode("Pets")

    def getTextureByHeight(self, z):
        """Выбираем текстуру по высоте блока"""
        if z == 0:
            return self.textures["Cobblestone"]
        elif z == 1 or z == 2:
            return self.textures["Dirt"]
        else:
            return self.textures["Grass"]

    def addBlock(self, position):
        block = loader.loadModel(self.model)
        tex = self.getTextureByHeight(int(position[2]))
        block.setTexture(tex)
        block.setPos(position)
        key = f"{int(position[0])},{int(position[1])},{int(position[2])}"
        block.setTag("at", key)
        block.reparentTo(self.land)

    def clear(self):
        """Обнулює карту"""
        self.land.removeNode()
        self.pets.removeNode()
        self.startNew()

    def loadLand(self, filename):
        """Создаёт карту из текстового файла"""
        self.clear()
        with open(filename) as file:
            y = 0
            for line in file:
                x = 0
                line = line.split(' ')
                for z in line:
                    for z0 in range(int(z)+1):
                        self.addBlock((x, y, z0))
                    x += 1
                y += 1
        return x, y

    # --- поиск блоков и питомцев ---
    def findBlocks(self, pos):
        key = f"{int(pos[0])},{int(pos[1])},{int(pos[2])}"
        return self.land.findAllMatches("=at=" + key)

    def addPet(self, position):
        pet = loader.loadModel("panda")
        if not pet:
            print("❌ Не удалось загрузить модель паука.")
            return
        pet.setScale(0.1)
        pet.setPos(position)
        pet.setHpr(0, 0, 0)
        pet.setTag("pet_at", str(position))
        pet.reparentTo(self.pets)

    def buildPet(self, pos):
        x, y, z = pos
        new = self.findHighestEmpty(pos)
        if new[2] <= z + 1:
            self.addPet(new)

    def findPets(self, pos):
        return self.pets.findAllMatches("=pet_at=" + str(pos))

    def isEmpty(self, pos):
        blocks = self.findBlocks(pos)
        pets = self.findPets(pos)
        return not (blocks or pets)

    def findHighestEmpty(self, pos):
        x, y, z = pos
        z = 1
        while not self.isEmpty((x, y, z)):
            z += 1
        return (x, y, z)

    # --- строительство / ломание ---
    def buildBlock(self, pos):
        x, y, z = pos
        new = self.findHighestEmpty(pos)
        if new[2] <= z + 1:
            self.addBlock(new)

    def delBlock(self, pos):
        blocks = self.findBlocks(pos)
        for block in blocks:
            block.removeNode()

    # --- сохранение / загрузка ---
    def saveMap(self):
        blocks = self.land.getChildren()
        with open("saved_map.dat", "wb") as saved_map:
            pickle.dump(len(blocks), saved_map)
            for block in blocks:
                x,y,z = block.getPos()
                pickle.dump((int(x), int(y), int(z)), saved_map)
        print("Map Saved ✅")

    def loadMap(self):
        self.clear()
        try:
            with open("saved_map.dat", "rb") as sm:
                length = pickle.load(sm)
                for _ in range(length):
                    pos = pickle.load(sm)
                    self.addBlock(pos)
            print("Map Loaded ✅")
        except:
            print("Error map load ❌")

