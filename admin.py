import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import cypher
import csv
import os
import datetime


class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Админ Панель (ID: 70225220)")

        # Задаем размеры окна
        self.window_width = 800
        self.window_height = 620

        self.root.configure(bg="#1e1e1e")

        # Отключаем стандартную верхнюю полосу Windows
        self.root.overrideredirect(True)

        # Константы стилей
        self.bg_main = "#1e1e1e"
        self.bg_element = "#2d2d2d"
        self.fg_green = "#00ff66"
        self.fg_text = "#e0e0e0"
        self.font_mono = ("Consolas", 10)
        self.font_sans = ("Arial", 9, "bold")

        # Словарь для хранения полных текстов сообщений
        self.full_messages = {}

        # Центрируем окно на экране при запуске
        self.center_window()

        # ----------------------------------------------------
        # КАСТОМНАЯ ВЕРХНЯЯ ПАНЕЛЬ (Заголовок окна)
        # ----------------------------------------------------
        self.title_bar = tk.Frame(root, bg="#151515", height=30)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.pack_propagate(False)

        self.title_label = tk.Label(
            self.title_bar, text="  Система: Панель Администратора (ID: 70225220)",
            bg="#151515", fg="#888888", font=("Arial", 9, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        self.close_button = tk.Button(
            self.title_bar, text="✕", command=root.destroy,
            bg="#151515", fg="#888888", relief="flat", font=("Arial", 10),
            activebackground="#ff3333", activeforeground="white", bd=0, width=4
        )
        self.close_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg="#ff3333", fg="white"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg="#151515", fg="#888888"))

        self.minimize_button = tk.Button(
            self.title_bar, text="—", command=self.minimize_window,
            bg="#151515", fg="#888888", relief="flat", font=("Arial", 8),
            activebackground=self.bg_element, activeforeground=self.fg_green, bd=0, width=4
        )
        self.minimize_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.minimize_button.bind("<Enter>",
                                  lambda e: self.minimize_button.config(bg=self.bg_element, fg=self.fg_green))
        self.minimize_button.bind("<Leave>", lambda e: self.minimize_button.config(bg="#151515", fg="#888888"))

        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        # ----------------------------------------------------
        # СТИЛИЗАЦИЯ ТАБЛИЦЫ (Treeview)
        # ----------------------------------------------------
        self.current_file = "messages.csv"

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background=self.bg_element,
                        foreground=self.fg_text,
                        fieldbackground=self.bg_element,
                        rowheight=24,
                        font=self.font_mono,
                        bordertransform=0,
                        borderwidth=0)

        style.configure("Treeview.Heading",
                        background="#151515",
                        foreground=self.fg_green,
                        font=self.font_sans,
                        borderwidth=1,
                        relief="flat")

        style.map("Treeview", background=[("selected", "#004d1a")], foreground=[("selected", self.fg_green)])
        style.map("Treeview.Heading", background=[("active", self.bg_element)], foreground=[("active", self.fg_green)])

        self.tree = ttk.Treeview(root, columns=("ID", "Time", "IP", "ShortText"), show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Time", text="Время")
        self.tree.heading("IP", text="IP Адрес")
        self.tree.heading("ShortText", text="Маркер (Первое слово)")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Time", width=140, anchor="center")
        self.tree.column("IP", width=130, anchor="center")
        self.tree.column("ShortText", width=440, anchor="w")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 5))

        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        # ----------------------------------------------------
        # ПАНЕЛЬ: ПОЛНЫЙ ПРОСМОТР ТЕКСТА СООБЩЕНИЯ
        # ----------------------------------------------------
        self.lbl_preview = tk.Label(
            root, text="СОДЕРЖИМОЕ ВЫБРАННОГО СООБЩЕНИЯ:",
            bg=self.bg_main, fg=self.fg_green, font=("Arial", 8, "bold")
        )
        self.lbl_preview.pack(anchor="nw", padx=15, pady=(5, 2))

        self.txt_preview = tk.Text(
            root, height=5, bg=self.bg_element, fg=self.fg_text,
            font=self.font_mono, relief="flat", bd=5, selectbackground="#004d1a", wrap=tk.WORD
        )
        self.txt_preview.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.txt_preview.insert(tk.END, "Выберите строку в таблице выше, чтобы прочитать полный текст...")
        self.txt_preview.config(state=tk.DISABLED)

        # ----------------------------------------------------
        # КОНТЕЙНЕР И КНОПКИ УПРАВЛЕНИЯ
        # ----------------------------------------------------
        btn_frame = tk.Frame(root, bg=self.bg_main)
        btn_frame.pack(fill=tk.X, padx=15, pady=(5, 10))

        buttons_config = [
            ("ОБНОВИТЬ ↻", self.refresh_table),
            ("ЗАГРУЗИТЬ CSV", self.load_csv),
            ("ДОБАВИТЬ", self.add_record),
            ("УДАЛИТЬ", self.delete_record),
            ("ВВЕРХ ▲", self.move_up),
            ("ВНИЗ ▼", self.move_down),
            ("СОХРАНИТЬ CSV", self.save_csv)
        ]

        for text, cmd in buttons_config:
            is_refresh = text == "ОБНОВИТЬ ↻"
            default_bg = "#252525" if is_refresh else self.bg_element

            btn = tk.Button(
                btn_frame, text=text, command=cmd,
                bg=default_bg, fg=self.fg_green, activebackground=self.fg_green, activeforeground=self.bg_main,
                font=self.font_sans, relief="flat", bd=1, highlightthickness=1, highlightbackground=self.fg_green
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            self.setup_hover(btn, is_refresh)

        # Строка статуса
        self.status = tk.Label(
            root, text=" Системный лог готов к администрированию",
            bg=self.bg_main, fg="#888888", font=("Arial", 9, "italic")
        )
        self.status.pack(side="bottom", anchor="sw", padx=15, pady=5)

        # ----------------------------------------------------
        # ПРИВЯЗКА СОБЫТИЙ ДЛЯ ИЗМЕНЕНИЯ РАЗМЕРА ОКНА
        # ----------------------------------------------------
        self.root.bind("<Motion>", self.check_border_zone)
        self.root.bind("<ButtonPress-1>", self.start_resize_or_move, add="+")
        self.root.bind("<B1-Motion>", self.do_resize_or_move, add="+")

        self.refresh_table()
        self.auto_refresh()

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
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()

    def do_resize_or_move(self, event):
        if not hasattr(self, 'resize_direction') or self.resize_direction == "":
            return

        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y

        new_width = self.start_width
        new_height = self.start_height

        if "e" in self.resize_direction:
            new_width = max(600, self.start_width + delta_x)
        if "s" in self.resize_direction:
            new_height = max(400, self.start_height + delta_y)

        self.window_width = new_width
        self.window_height = new_height
        self.root.geometry(f"{new_width}x{new_height}")

    # ----------------------------------------------------
    # ОСТАЛЬНЫЕ МЕТОДЫ (Обработка данных, перемещение, автообновление)
    # ----------------------------------------------------
    def on_select_record(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        full_text = self.full_messages.get(item_id, "")

        self.txt_preview.config(state=tk.NORMAL)
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert(tk.END, full_text)
        self.txt_preview.config(state=tk.DISABLED)

    def get_first_word(self, text):
        clean_text = text.strip()
        if not clean_text:
            return "..."
        first_word = clean_text.split()[0]
        if len(first_word) > 25:
            return first_word[:25] + "..."
        return first_word

    def auto_refresh(self):
        self.refresh_table(is_auto=True)
        self.root.after(3000, self.auto_refresh)

    def setup_hover(self, button, is_refresh=False):
        default_bg = "#252525" if is_refresh else self.bg_element
        button.bind("<Enter>", lambda e: button.config(bg=self.fg_green, fg=self.bg_main))
        button.bind("<Leave>", lambda e: button.config(bg=default_bg, fg=self.fg_green))

    def start_move(self, event):
        self.resize_direction = ""
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

    def refresh_table(self, is_auto=False):
        selected_item_db_id = None
        selected = self.tree.selection()
        if selected:
            selected_item_db_id = self.tree.item(selected[0], "values")[0]

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.full_messages.clear()

        if os.path.exists(self.current_file):
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) == 4:
                            dec_text = cypher.decrypt(row[3])
                            short_text = self.get_first_word(dec_text)
                            item = self.tree.insert("", "end", values=(row[0], row[1], row[2], short_text))
                            self.full_messages[item] = dec_text

                            if selected_item_db_id and row[0] == selected_item_db_id:
                                self.tree.selection_set(item)

                if not is_auto:
                    self.status.config(
                        text=f" Данные принудительно обновлены из файла: {os.path.basename(self.current_file)}",
                        fg=self.fg_green)
                else:
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    self.status.config(text=f" Синхронизация с сервером активна. Последнее автообновление: {now}",
                                       fg="#888888")
            except Exception as e:
                if not is_auto:
                    messagebox.showerror("Ошибка", f"Не удалось прочитать CSV: {e}")
                self.status.config(text=" Конфликт доступа к CSV. Ожидание освобождения файла...", fg="#ff3333")

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if path:
            self.current_file = path
            self.refresh_table()

    def add_record(self):
        text = simpledialog.askstring("Новая запись", "Введите текст сообщения:")
        if text is not None and text.strip() != "":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip = "127.0.0.1 (admin)"

            existing_ids = []
            for item in self.tree.get_children():
                try:
                    existing_ids.append(int(self.tree.item(item, "values")[0]))
                except ValueError:
                    pass
            next_id = max(existing_ids) + 1 if existing_ids else 1

            short_text = self.get_first_word(text)
            item = self.tree.insert("", "end", values=(next_id, timestamp, ip, short_text))
            self.full_messages[item] = text
            self.status.config(text=" Новая запись временно добавлена в таблицу. Не забудьте сохранить!",
                               fg=self.fg_green)

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите строку для удаления")
            return
        for item in selected:
            if item in self.full_messages:
                del self.full_messages[item]
            self.tree.delete(item)
        self.status.config(text=" Запись удалена из буфера таблицы. Требуется сохранение CSV.", fg=self.fg_green)

        self.txt_preview.config(state=tk.NORMAL)
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert(tk.END, "Запись удалена.")
        self.txt_preview.config(state=tk.DISABLED)

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            index = self.tree.index(item)
            if index > 0:
                self.tree.move(item, self.tree.parent(item), index - 1)

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in reversed(selected):
            index = self.tree.index(item)
            if index < len(self.tree.get_children()) - 1:
                self.tree.move(item, self.tree.parent(item), index + 1)

    def save_csv(self):
        try:
            with open(self.current_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    full_text = self.full_messages.get(item, "")
                    enc_text = cypher.encrypt(full_text)
                    writer.writerow([values[0], values[1], values[2], enc_text])
            messagebox.showinfo("Успех", "Данные успешно зашифрованы и сохранены")
            self.status.config(text=" База данных CSV успешно синхронизирована и сохранена", fg=self.fg_green)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            self.status.config(text=" Ошибка записи в файл конфигурации", fg="#ff3333")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
