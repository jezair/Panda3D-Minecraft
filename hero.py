from panda3d.core import WindowProperties, Vec3
from direct.showbase.InputStateGlobal import inputState
from direct.interval.LerpInterval import LerpPosInterval
from direct.task import Task

# --- КЛАВИШИ ---
KEY_FORWARD = 'w'  # движение назад (инверсия управления)
KEY_BACK = 's'  # движение вперёд
KEY_LEFT = 'a'  # движение вправо
KEY_RIGHT = 'd'  # движение влево
KEY_SWITCH_CAMERA = 'c'  # переключение вида камеры
KEY_UP = 'space'  # полёт вверх
KEY_DOWN = 'shift'  # полёт вниз
KEY_RUN = 'e'

KEY_BUILD = "b"
KEY_DESTROY = "v"

KEY_SAVE = "k"
KEY_LOAD = "l"

KEY_JUMP = 'space'
KEY_SET_PET = "m"


class Hero:
    def __init__(self, pos, land):
        self.land = land

        # --- Герой с текстурой ---
        self.hero = loader.loadModel('smiley')  # сфера
        tex = loader.loadTexture("head.jpg")  # текстура лица
        self.hero.setTexture(tex, 1)
        self.hero.setScale(0.3)
        self.hero.setPos(pos)
        self.hero.reparentTo(render)

        self.cameraBind()
        self.accept_events()

        self.speed = 7
        self.sensitivity = 0.13

        # параметры движения
        self.vz = 0
        self.gravity = -10
        self.jump_speed = 5
        self.on_ground = False

        # питомец
        self.pet = None

        self.run_speed = 2  # множитель бега

        self.centerMouse()
        taskMgr.add(self.update_camera, "update_camera")
        taskMgr.add(self.update_movement, "update_movement")
        taskMgr.add(self.update_pet, "update_pet")  # движение питомца

    # ---------- КАМЕРА ----------
    def set_pet(self):
        """Создание питомца рядом с героем"""
        if not self.pet:
            pos = self.hero.getPos() + Vec3(1, 1, 0)
            self.pet = loader.loadModel("panda")
            self.pet.setScale(0.1)
            self.pet.setPos(pos)
            self.pet.reparentTo(render)
            print("Питомец создан ✅")
        else:
            print("Питомец уже есть")

    def update_pet(self, task):
        """Питомец идёт за героем"""
        if self.pet:
            hero_pos = self.hero.getPos()
            pet_pos = self.pet.getPos()
            dist = (hero_pos - pet_pos).length()
            if dist > 2:
                direction = (hero_pos - pet_pos)
                direction.normalize()
                step = direction * globalClock.getDt() * 3
                self.pet.setPos(pet_pos + step)
                self.pet.lookAt(self.hero)
        return task.cont

    def cameraBind(self):
        """Привязка камеры к герою (вид от первого лица)."""
        base.disableMouse()
        base.camera.setH(180)
        base.camera.reparentTo(self.hero)
        base.camera.setPos(0, 0, 2)
        self.cameraOn = True

    def cameraUp(self):
        """Свободный полёт камерой."""
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)
        base.enableMouse()
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)
        self.cameraOn = False

    def changeView(self):
        """Переключение вида камеры."""
        if self.cameraOn:
            self.cameraUp()
        else:
            self.cameraBind()

    def update_camera(self, task):
        if self.cameraOn and base.mouseWatcherNode.hasMouse():
            md = base.win.getPointer(0)
            x, y = md.getX(), md.getY()
            cx, cy = base.win.getXSize()//2, base.win.getYSize()//2
            dx, dy = (x - cx) * self.sensitivity, (y - cy) * self.sensitivity
            self.hero.setH(self.hero.getH() - dx)
            new_pitch = max(-60, min(60, base.camera.getP() - dy))
            base.camera.setP(new_pitch)
            self.centerMouse()
        return task.cont

    def centerMouse(self):
        wp = WindowProperties()
        wp.setCursorHidden(True)
        base.win.requestProperties(wp)
        base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)

    # ---------- ДВИЖЕНИЕ ----------
    def update_movement(self, task):
        dt = globalClock.getDt()
        direction = Vec3(0, 0, 0)
        if inputState.isSet(KEY_FORWARD): direction.y -= 1
        if inputState.isSet(KEY_BACK): direction.y += 1
        if inputState.isSet(KEY_LEFT): direction.x += 1
        if inputState.isSet(KEY_RIGHT): direction.x -= 1

        current_speed = self.speed
        if inputState.isSet(KEY_RUN):
            current_speed *= self.run_speed

        if direction.length() > 0:
            direction.normalize()
            direction *= current_speed * dt
            new_pos = self.hero.getPos() + render.getRelativeVector(self.hero, direction)
            target_block = (round(new_pos.x), round(new_pos.y), round(self.hero.getZ()))
            if self.land.isEmpty(target_block):
                self.hero.setPos(new_pos)

        # гравитация
        self.vz += self.gravity * dt
        new_z = self.hero.getZ() + self.vz * dt
        foot = (round(self.hero.getX()), round(self.hero.getY()), round(new_z - 0.5))
        if not self.land.isEmpty(foot):
            self.hero.setZ(foot[2] + 1)
            self.vz = 0
            self.on_ground = True
        else:
            self.hero.setZ(new_z)
            self.on_ground = False

        return task.cont

    def jump(self):
        if self.on_ground:
            self.vz = self.jump_speed
            self.on_ground = False

    # ---------- СТРОИТЕЛЬСТВО / ЛОМАНИЕ ----------
    def look_at(self):
        angle = self.hero.getH() % 360
        x, y, z = round(self.hero.getX()), round(self.hero.getY()), round(self.hero.getZ())
        dx, dy = self.check_dir(angle)
        return x + dx, y + dy, z

    def check_dir(self, angle):
        if 0 <= angle <= 20 or angle >= 340: return 0, -1
        elif angle <= 65: return 1, -1
        elif angle <= 110: return 1, 0
        elif angle <= 155: return 1, 1
        elif angle <= 200: return 0, 1
        elif angle <= 245: return -1, 1
        elif angle <= 290: return -1, 0
        elif angle <= 335: return -1, -1
        return 0, -1

    def build(self):
        pos = self.look_at()
        self.land.addBlock(pos)

    def destroy(self):
        pos = self.look_at()
        self.land.delBlock(pos)

    # ---------- СОБЫТИЯ ----------
    def accept_events(self):
        inputState.watchWithModifiers(KEY_FORWARD, KEY_FORWARD)
        inputState.watchWithModifiers(KEY_BACK, KEY_BACK)
        inputState.watchWithModifiers(KEY_LEFT, KEY_LEFT)
        inputState.watchWithModifiers(KEY_RIGHT, KEY_RIGHT)
        inputState.watchWithModifiers(KEY_DOWN, KEY_DOWN)
        inputState.watchWithModifiers(KEY_RUN, KEY_RUN)

        base.accept(KEY_SWITCH_CAMERA, self.changeView)
        base.accept(KEY_BUILD, self.build)
        base.accept(KEY_DESTROY, self.destroy)
        base.accept(KEY_SAVE, self.land.saveMap)
        base.accept(KEY_LOAD, self.land.loadMap)
        base.accept(KEY_JUMP, self.jump)
        base.accept(KEY_SET_PET, self.set_pet)


