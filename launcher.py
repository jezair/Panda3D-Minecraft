import os
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.messagebox as mb

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SLOTS = ["save1.dat", "save2.dat", "save3.dat"]
WORK_SAVE = os.path.join(PROJECT_DIR, "saved_map.dat")
GAME_PY = os.path.join(PROJECT_DIR, "game.py")




def use_slot(slot_index):
    slot_file = os.path.join(PROJECT_DIR, SLOTS[slot_index])

    # 1) Подготовка saved_map.dat перед запуском игры
    if os.path.exists(slot_file):
        try:
            shutil.copyfile(slot_file, WORK_SAVE)
            print(f"Copied {slot_file} -> {WORK_SAVE}")
        except Exception as e:
            mb.showerror("Ошибка", f"Не удалось скопировать слот: {e}")
            return
    else:
        # если слота нет — удаляем старый рабочий сейв (чтобы игра стартовала с land.txt)
        if os.path.exists(WORK_SAVE):
            try:
                os.remove(WORK_SAVE)
                print(f"Removed existing {WORK_SAVE}")
            except Exception as e:
                mb.showerror("Ошибка", f"Не удалось удалить старый рабочий сейв: {e}")
                return

    root.destroy()

    # 2) Запускаем game.py с рабочей директорией PROJECT_DIR (важно!)
    python_exe = sys.executable or "python"
    try:
        subprocess.run([python_exe, GAME_PY], cwd=PROJECT_DIR)
    except Exception as e:
        mb.showerror("Ошибка", f"Не удалось запустить игру: {e}")
        return

    # 3) После выхода — если игра создала saved_map.dat, копируем его в слот
    if os.path.exists(WORK_SAVE):
        try:
            shutil.copyfile(WORK_SAVE, slot_file)
            print(f"Saved {WORK_SAVE} -> {slot_file}")
            mb.showinfo("Сохранено", f"Прогресс сохранён в {SLOTS[slot_index]}")
        except Exception as e:
            mb.showerror("Ошибка", f"Не удалось записать слот: {e}")
    else:
        mb.showinfo("Инфо", "Игра не создала файл saved_map.dat — слот не изменён.")


# ===== GUI =====
root = tk.Tk()
root.title("Выбор слота сохранения")
root.geometry("320x200")

lbl = tk.Label(root, text="Выберите слот сохранения", font=("Arial", 14))
lbl.pack(pady=10)

for i in range(3):
    def make_cmd(i=i):
        return lambda: use_slot(i)
    btn = tk.Button(root, text=f"Слот {i+1}", width=24, command=make_cmd())
    btn.pack(pady=6)

lbl2 = tk.Label(root, text="После выхода из игры прогресс сохранится в выбранном слоте", font=("Arial", 9))
lbl2.pack(side="bottom", pady=8)

root.mainloop()
