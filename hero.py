from panda3d.core import WindowProperties, Vec3
from direct.showbase.InputStateGlobal import inputState

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

KEY_JUMP = "space"


class Hero:
    def __init__(self, pos, land):
        self.land = land  # карта (не используется, но пригодится)

        # создаём модель героя (смiley-шарик)
        self.hero = loader.loadModel('smiley')
        self.hero.setColor(1, 0.5, 0)  # оранжевый
        self.hero.setScale(0.3)  # уменьшаем
        self.hero.setPos(pos)  # позиция в мире
        self.hero.reparentTo(render)  # добавляем в сцену

        # привязываем камеру к герою (режим от первого лица)
        self.cameraBind()

        # назначаем управление
        self.accept_events()

        # параметры
        self.speed = 7  # базовая скорость передвижения
        self.sensitivity = 0.13  # чувствительность мыши

        self.vz = 0
        self.gravity = -10
        self.jump_speed = 5
        self.on_ground = False
        self.run_speed = 2    # множитель бега

        # настройка мыши
        self.centerMouse()

        # задачи, выполняемые каждый кадр
        taskMgr.add(self.update_camera, "update_camera")  # обработка мыши
        taskMgr.add(self.update_movement, "update_movement")  # обработка клавиш

    # ---------- КАМЕРА ----------
    def cameraBind(self):
        """Привязать камеру к герою (вид от первого лица)."""
        base.disableMouse()  # отключаем встроенное управление камерой
        base.camera.setH(180)  # поворот (смотрим вперёд)
        base.camera.reparentTo(self.hero)  # камера прикреплена к герою
        base.camera.setPos(0, 0, 2)  # камера чуть выше "глаз"
        self.cameraOn = True

    def cameraUp(self):
        """Отключить привязку камеры (свободный полёт камерой)."""
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)  # отвязываем камеру
        base.enableMouse()  # включаем стандартное управление

        # включаем курсор
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)

        self.cameraOn = False

    def changeView(self):
        """Переключение между режимом от первого лица и свободной камерой."""
        if self.cameraOn:
            self.cameraUp()
        else:
            self.cameraBind()

    def update_camera(self, task):
        """Обработка движения мыши: вращение героя и камеры."""
        if self.cameraOn and base.mouseWatcherNode.hasMouse():
            # получаем текущее положение мыши
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()

            # центр экрана
            cx = base.win.getXSize() // 2
            cy = base.win.getYSize() // 2

            # смещение мыши от центра
            dx = (x - cx) * self.sensitivity
            dy = (y - cy) * self.sensitivity

            # поворот героя вокруг оси (Yaw — влево/вправо)
            self.hero.setH(self.hero.getH() - dx)

            # поворот камеры вверх/вниз (Pitch), ограниченный углами
            new_pitch = base.camera.getP() - dy
            new_pitch = max(-60, min(60, new_pitch))  # ограничиваем угол
            base.camera.setP(new_pitch)

            # возвращаем мышь в центр
            self.centerMouse()

        return task.cont

    def centerMouse(self):
        """Прячем курсор и ставим его в центр экрана."""
        wp = WindowProperties()
        wp.setCursorHidden(True)
        base.win.requestProperties(wp)

        cx = base.win.getXSize() // 2
        cy = base.win.getYSize() // 2
        base.win.movePointer(0, cx, cy)

    # ---------- ДВИЖЕНИЕ ----------
    def update_movement(self, task):
        """Обновляем положение героя по зажатым клавишам."""
        dt = globalClock.getDt()  # время с прошлого кадра (для плавности)
        direction = Vec3(0, 0, 0)  # направление движения

        # инверсия управления
        if inputState.isSet(KEY_FORWARD):
            direction.y -= 1  # W = назад
        if inputState.isSet(KEY_BACK):
            direction.y += 1  # S = вперёд
        if inputState.isSet(KEY_LEFT):
            direction.x += 1  # A = вправо
        if inputState.isSet(KEY_RIGHT):
            direction.x -= 1  # D = влево

        # бег
        current_speed = self.speed  # стандартная скорость
        if inputState.isSet(KEY_RUN):
            current_speed *= self.run_speed  # умножаем на множитель бега

        # если есть движение
        if direction.length() > 0:
            direction.normalize()
            direction *= current_speed * dt  # используем текущую скорость
            # переводим направление из локальных координат героя в глобальные
            new_pos = self.hero.getPos() + render.getRelativeVector(self.hero, direction)
            # обновляем позицию героя
            target_block = (round(new_pos.x), round(new_pos.y), round(self.hero.getZ()))
            if self.land.isEmpty(target_block):
                self.hero.setPos(new_pos)

        # --- гравитация и прыжок ---
        self.vz += self.gravity * dt
        new_z = self.hero.getZ() + self.vz * dt

        foot_x = round(self.hero.getX())
        foot_y = round(self.hero.getY())
        foot_z = round(new_z - 0.5)

        if not self.land.isEmpty((foot_x, foot_y, foot_z)):
            self.hero.setZ(foot_z + 1)
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
        """Возвращает координаты блока перед героем"""
        angle = self.hero.getH() % 360
        x_from = round(self.hero.getX())
        y_from = round(self.hero.getY())
        z_from = round(self.hero.getZ())

        dx, dy = self.check_dir(angle)
        return x_from + dx, y_from + dy, z_from

    def check_dir(self, angle):
        """Определяет направление по углу (ось X/Y)."""
        if 0 <= angle <= 20 or angle >= 340:
            return (0, -1)
        elif angle <= 65:
            return (1, -1)
        elif angle <= 110:
            return (1, 0)
        elif angle <= 155:
            return (1, 1)
        elif angle <= 200:
            return (0, 1)
        elif angle <= 245:
            return (-1, 1)
        elif angle <= 290:
            return (-1, 0)
        elif angle <= 335:
            return (-1, -1)
        return (0, -1)

    def build(self):
        pos = self.look_at()
        self.land.addBlock(pos)

    def destroy(self):
        pos = self.look_at()
        self.land.delBlock(pos)

    # ---------- СОБЫТИЯ ----------
    def accept_events(self):
        """Регистрируем слежение за клавишами."""
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

