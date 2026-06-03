import tkinter as tk
from tkinter import filedialog, messagebox
import cypher


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Шифратор (ID: 70225220)")

        # Начальные размеры окна шифратора
        self.window_width = 500
        self.window_height = 540

        self.root.configure(bg="#1e1e1e")

        # Отключаем стандартную верхнюю полосу Windows!
        self.root.overrideredirect(True)

        # Цвета
        self.bg_main = "#1e1e1e"
        self.bg_element = "#2d2d2d"
        self.fg_green = "#00ff66"
        self.fg_text = "#e0e0e0"
        self.font_mono = ("Consolas", 11)
        self.font_sans = ("Arial", 10, "bold")

        # Центрируем окно на экране при запуске
        self.center_window()

        # ----------------------------------------------------
        # СОБСТВЕННАЯ ВЕРХНЯЯ ПАНЕЛЬ (Замена белой полосы)
        # ----------------------------------------------------
        self.title_bar = tk.Frame(root, bg="#151515", height=30)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.pack_propagate(False)  # Запрещаем сжиматься

        # Название программы в нашей полосе
        self.title_label = tk.Label(
            self.title_bar, text="  Шифратор (ID: 70225220)",
            bg="#151515", fg="#888888", font=("Arial", 9, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        # Кнопка закрытия "X"
        self.close_button = tk.Button(
            self.title_bar, text="✕", command=root.destroy,
            bg="#151515", fg="#888888", relief="flat", font=("Arial", 10),
            activebackground="#ff3333", activeforeground="white", bd=0, width=4
        )
        self.close_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg="#ff3333", fg="white"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg="#151515", fg="#888888"))

        # Кнопка сворачивания "_"
        self.minimize_button = tk.Button(
            self.title_bar, text="—", command=self.minimize_window,
            bg="#151515", fg="#888888", relief="flat", font=("Arial", 8),
            activebackground=self.bg_element, activeforeground=self.fg_green, bd=0, width=4
        )
        self.minimize_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.minimize_button.bind("<Enter>",
                                  lambda e: self.minimize_button.config(bg=self.bg_element, fg=self.fg_green))
        self.minimize_button.bind("<Leave>", lambda e: self.minimize_button.config(bg="#151515", fg="#888888"))

        # Привязываем события мыши к нашей полосе, чтобы окно можно было перетаскивать
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        # ----------------------------------------------------
        # ОСНОВНОЙ ИНТЕРФЕЙС
        # ----------------------------------------------------
        self.btn_load = tk.Button(
            root, text=" ЗАГРУЗИТЬ ФАЙЛ ", command=self.load_file,
            bg=self.bg_element, fg=self.fg_green, activebackground=self.fg_green, activeforeground=self.bg_main,
            font=self.font_sans, relief="flat", bd=1, highlightthickness=1, highlightbackground=self.fg_green
        )
        self.btn_load.pack(fill=tk.X, pady=(15, 5), padx=15)
        self.setup_hover(self.btn_load)

        self.txt_out = tk.Text(
            root, height=12, width=50, state=tk.DISABLED,
            bg=self.bg_element, fg=self.fg_text, font=self.font_mono,
            relief="flat", bd=5, insertbackground=self.fg_green, selectbackground="#004d1a"
        )
        self.txt_out.pack(fill=tk.BOTH, expand=True, pady=5, padx=15)

        self.lbl_in = tk.Label(
            root, text="НОВАЯ СТРОКА ДЛЯ ДОБАВЛЕНИЯ:",
            bg=self.bg_main, fg=self.fg_green, font=("Arial", 9, "bold")
        )
        self.lbl_in.pack(anchor="nw", padx=15, pady=(10, 2))

        self.txt_in = tk.Text(
            root, height=3, width=50,
            bg=self.bg_element, fg=self.fg_text, font=self.font_mono,
            relief="flat", bd=5, insertbackground=self.fg_green, selectbackground="#004d1a"
        )
        self.txt_in.pack(fill=tk.X, pady=5, padx=15)

        btn_frame = tk.Frame(root, bg=self.bg_main)
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        self.btn_add = tk.Button(
            btn_frame, text="ДОБАВИТЬ СТРОКУ", command=self.add_line,
            bg=self.bg_element, fg=self.fg_green, activebackground=self.fg_green, activeforeground=self.bg_main,
            font=self.font_sans, relief="flat", bd=1, highlightthickness=1, highlightbackground=self.fg_green
        )
        self.btn_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.setup_hover(self.btn_add)

        self.btn_save = tk.Button(
            btn_frame, text="ЗАШИФРОВАТЬ И СОХРАНИТЬ", command=self.save_file,
            bg=self.bg_element, fg=self.fg_green, activebackground=self.fg_green, activeforeground=self.bg_main,
            font=self.font_sans, relief="flat", bd=1, highlightthickness=1, highlightbackground=self.fg_green
        )
        self.btn_save.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.setup_hover(self.btn_save)

        self.status = tk.Label(
            root, text="Система готова к работе",
            bg=self.bg_main, fg="#888888", font=("Arial", 9, "italic")
        )
        self.status.pack(side="bottom", anchor="sw", padx=15, pady=5)

        # ----------------------------------------------------
        # ПРИВЯЗКА СОБЫТИЙ ДЛЯ ИЗМЕНЕНИЯ РАЗМЕРА ОКНА (RESIZE)
        # ----------------------------------------------------
        self.root.bind("<Motion>", self.check_border_zone)
        self.root.bind("<ButtonPress-1>", self.start_resize_or_move, add="+")
        self.root.bind("<B1-Motion>", self.do_resize_or_move, add="+")

    # ----------------------------------------------------
    # ФУНКЦИЯ ЦЕНТРИРОВАНИЯ ОКНА ПРИ СТАРТЕ
    # ----------------------------------------------------
    def center_window(self):
        """Вычисляет координаты центра экрана и помещает туда окно."""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_coordinate = int((screen_width / 2) - (self.window_width / 2))
        y_coordinate = int((screen_height / 2) - (self.window_height / 2))

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_coordinate}+{y_coordinate}")

    # ----------------------------------------------------
    # ЛОГИКА ДИНАМИЧЕСКОГО ИЗМЕНЕНИЯ РАЗМЕРА ОКНА (RESIZE)
    # ----------------------------------------------------
    def check_border_zone(self, event):
        """Проверяет, находится ли курсор у края окна, и меняет его вид."""
        border_size = 8
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = event.x
        y = event.y

        self.resize_direction = ""

        if x >= w - border_size and y >= h - border_size:
            self.resize_direction = "se"
            self.root.config(cursor="size_nw_se")
        elif x >= w - border_size:
            self.resize_direction = "e"
            self.root.config(cursor="size_we")
        elif y >= h - border_size:
            self.resize_direction = "s"
            self.root.config(cursor="size_ns")
        else:
            self.root.config(cursor="")

    def start_resize_or_move(self, event):
        """Запоминает начальную геометрию перед ресайзом."""
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()

    def do_resize_or_move(self, event):
        """Выполняет масштабирование окна."""
        if not hasattr(self, 'resize_direction') or self.resize_direction == "":
            return

        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y

        new_width = self.start_width
        new_height = self.start_height

        if "e" in self.resize_direction:
            new_width = max(400, self.start_width + delta_x)  # 400 — минимальная ширина
        if "s" in self.resize_direction:
            new_height = max(350, self.start_height + delta_y)  # 350 — минимальная высота

        self.window_width = new_width
        self.window_height = new_height
        self.root.geometry(f"{new_width}x{new_height}")

    # ----------------------------------------------------
    # СЕРВИСНЫЕ МЕТОДЫ ДЛЯ КАСТОМНОЙ ПАНЕЛИ И ПЕРЕМЕЩЕНИЯ
    # ----------------------------------------------------
    def start_move(self, event):
        self.resize_direction = ""  # Сбрасываем ресайз при перетаскивании за шапку
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        if hasattr(self, 'resize_direction') and self.resize_direction != "":
            return
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.root.update_idletasks()
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.bind("<FocusIn>", lambda e: self.root.overrideredirect(True))

    def setup_hover(self, button):
        button.bind("<Enter>", lambda e: button.config(bg=self.fg_green, fg=self.bg_main))
        button.bind("<Leave>", lambda e: button.config(bg=self.bg_element, fg=self.fg_green))

    # ----------------------------------------------------
    # ФУНКЦИОНАЛЬНАЯ ЛОГИКА РАБОТЫ С ФАЙЛАМИ
    # ----------------------------------------------------
    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                encrypted_content = f.read()
            decrypted_content = cypher.decrypt(encrypted_content)
            self.txt_out.config(state=tk.NORMAL)
            self.txt_out.delete("1.0", tk.END)
            self.txt_out.insert(tk.END, decrypted_content)
            self.txt_out.config(state=tk.DISABLED)
            self.status.config(text="Файл успешно загружен и дешифрован", fg=self.fg_green)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
            self.status.config(text="Ошибка чтения файла", fg="#ff3333")

    def add_line(self):
        new_text = self.txt_in.get("1.0", tk.END).strip()
        if not new_text: return
        self.txt_out.config(state=tk.NORMAL)
        current_text = self.txt_out.get("1.0", tk.END).strip()
        if current_text:
            self.txt_out.insert(tk.END, "\n" + new_text)
        else:
            self.txt_out.insert(tk.END, new_text)
        self.txt_out.config(state=tk.DISABLED)
        self.txt_in.delete("1.0", tk.END)
        self.status.config(text="Строка успешно добавлена в буфер", fg=self.fg_green)

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not filepath: return
        try:
            content = self.txt_out.get("1.0", tk.END).strip()
            encrypted_content = cypher.encrypt(content)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(encrypted_content)
            self.status.config(text="Данные зашифрованы и сохранены", fg=self.fg_green)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            self.status.config(text="Ошибка сохранения файла", fg="#ff3333")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
