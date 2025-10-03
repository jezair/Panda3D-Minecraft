import os
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.messagebox as mb


class SaveSlotManager:
    def __init__(self):
        self.PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SLOTS = ["saves/save1.dat", "saves/save2.dat", "saves/save3.dat", "saves/save4.dat", "saves/save5.dat"]
        self.WORK_SAVE = os.path.join(self.PROJECT_DIR, "saves/saved_map.dat")
        self.GAME_PY = os.path.join(self.PROJECT_DIR, "game.py")

        self.root = tk.Tk()
        self.root.title("Лаунчер")
        self.root.geometry("600x400")

        self.build_gui()
        self.root.mainloop()

    def build_gui(self):
        lbl = tk.Label(self.root, text="Виберіть слот збереження", font=("Arial", 14))
        lbl.pack(pady=10)

        for i in range(5):
            btn = tk.Button(self.root, text=f"слот {i + 1}", width=24, command=lambda i=i: self.use_slot(i))
            btn.pack(pady=6)

        lbl2 = tk.Label(
            self.root,
            text='''Слова напуття:
                    Для того щоб вийти з гри, натисніть конпку "Esc".
                    Ви можете створювати та руйнувати блоки на клавіши "b" i "v" відповідно.
                    Для пришвидшення бігу натисніть "е".
                    Приземляйтесь добре''',
            font=("Arial", 9)
        )
        lbl2.pack(side="bottom", pady=8)

        lbl3 = tk.Label(
            self.root,
            text="Після виходу з гри ваш прогрес буде збережений у обраному слоті",
            font=("Arial", 9)
        )
        lbl3.pack(side="bottom", pady=8)

    def use_slot(self, slot_index):
        slot_file = os.path.join(self.PROJECT_DIR, self.SLOTS[slot_index])

        # Step 1: Prepare saved_map.dat before running the game
        if os.path.exists(slot_file):
            try:
                shutil.copyfile(slot_file, self.WORK_SAVE)
                print(f"Copied {slot_file} -> {self.WORK_SAVE}")
            except Exception as e:
                mb.showerror("Помилка", f"Не вдалось скопіювати слот: {e}")
                return
        else:
            # If slot file doesn't exist, remove old working save if it exists
            if os.path.exists(self.WORK_SAVE):
                try:
                    os.remove(self.WORK_SAVE)
                    print(f"Removed existing {self.WORK_SAVE}")
                except Exception as e:
                    mb.showerror("Помилка", f"Не вдалось видалити старий працюючий слот: {e}")
                    return

        self.root.destroy()

        # Step 2: Launch the game
        python_exe = sys.executable or "python"
        try:
            subprocess.run([python_exe, self.GAME_PY], cwd=self.PROJECT_DIR)
        except Exception as e:
            mb.showerror("Помилка", f"Не вдалось зберегт гру: {e}")
            return

        # Step 3: After the game, copy saved_map.dat back to the selected slot if it exists
        if os.path.exists(self.WORK_SAVE):
            try:
                shutil.copyfile(self.WORK_SAVE, slot_file)
                print(f"Saved {self.WORK_SAVE} -> {slot_file}")
                mb.showinfo("Збережено", f"Прогрес та зміни збережено в {self.SLOTS[slot_index]}")
            except Exception as e:
                mb.showerror("Помилка", f"Не вдалось записати слот: {e}")
        else:
            mb.showinfo("Інфо", "Гра не створила слот saved_map.dat — слот не змінений.")


if __name__ == "__main__":
    SaveSlotManager()
