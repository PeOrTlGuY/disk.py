import os
import threading
import tkinter as tk
from send2trash import send2trash
from tkinter import filedialog, ttk, messagebox


class DiskAnalyzer:
    def __init__(self, window):
        self.window = window
        self.window.title("Disk Analyzer")
        self.window.geometry("1000x700")

        self.scanning = False
        self.current_folder = ""
        self.last_folders = []

        # =========================
        # ЗАГОЛОВОК
        # =========================

        title = tk.Label(
            window,
            text="💾 Disk Analyzer",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=10)

        # =========================
        # КНОПКИ
        # =========================

        buttons = tk.Frame(window)
        buttons.pack(pady=5)

        self.select_button = tk.Button(
            buttons,
            text="📁 Вибрати папку",
            command=self.select_folder
        )
        self.select_button.pack(side="left", padx=5)

        self.junk_button = tk.Button(
            buttons,
            text="🧹 Сканувати непотрібні файли",
            command=self.scan_junk
        )
        self.junk_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            buttons,
            text="⛔ Зупинити",
            command=self.stop_scan,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(
            buttons,
            text="🗑️ Видалити вибране",
            command=self.delete_selected
        )
        self.delete_button.pack(side="left", padx=5)

        self.chart_button = tk.Button(
            buttons,
            text="📊 Карта диска",
            command=self.show_disk_map
        )
        self.chart_button.pack(side="left", padx=5)

        self.smart_button = tk.Button(
            buttons,
            text="🧹 Розумне очищення",
            command=self.smart_clean
        )
        self.smart_button.pack(side="left", padx=5)

        # =========================
        # ПРОГРЕС
        # =========================

        self.progress = ttk.Progressbar(
            window,
            mode="indeterminate"
        )
        self.progress.pack(
            fill="x",
            padx=30,
            pady=5
        )

        self.status = tk.Label(
            window,
            text="Оберіть папку для сканування"
        )
        self.status.pack(pady=5)

        # =========================
        # ПАНЕЛЬ
        # =========================

        paned = ttk.PanedWindow(
            window,
            orient=tk.VERTICAL
        )
        paned.pack(
            expand=True,
            fill="both",
            padx=15,
            pady=10
        )

        # =========================
        # ПАПКИ
        # =========================

        folder_frame = ttk.LabelFrame(
            paned,
            text="📁 Папки"
        )

        self.folder_table = ttk.Treeview(
            folder_frame,
            columns=("folder", "size"),
            show="headings",
            selectmode="extended"
        )

        self.folder_table.heading(
            "folder",
            text="Папка"
        )

        self.folder_table.heading(
            "size",
            text="Розмір"
        )

        self.folder_table.column(
            "folder",
            width=700
        )

        self.folder_table.column(
            "size",
            width=150
        )

        folder_scroll = ttk.Scrollbar(
            folder_frame,
            orient="vertical",
            command=self.folder_table.yview
        )

        self.folder_table.configure(
            yscrollcommand=folder_scroll.set
        )

        self.folder_table.pack(
            side="left",
            expand=True,
            fill="both"
        )

        folder_scroll.pack(
            side="right",
            fill="y"
        )

        paned.add(folder_frame)

        # =========================
        # ФАЙЛИ
        # =========================

        file_frame = ttk.LabelFrame(
            paned,
            text="📄 Найбільші файли"
        )

        self.file_table = ttk.Treeview(
            file_frame,
            columns=("file", "size", "path"),
            show="headings",
            selectmode="extended"
        )

        self.file_table.heading(
            "file",
            text="Файл"
        )

        self.file_table.heading(
            "size",
            text="Розмір"
        )

        self.file_table.heading(
            "path",
            text="Шлях"
        )

        self.file_table.column(
            "file",
            width=250
        )

        self.file_table.column(
            "size",
            width=120
        )

        self.file_table.column(
            "path",
            width=500
        )

        file_scroll = ttk.Scrollbar(
            file_frame,
            orient="vertical",
            command=self.file_table.yview
        )

        self.file_table.configure(
            yscrollcommand=file_scroll.set
        )

        self.file_table.pack(
            side="left",
            expand=True,
            fill="both"
        )

        file_scroll.pack(
            side="right",
            fill="y"
        )

        paned.add(file_frame)

    # =========================
    # ВИБІР ПАПКИ
    # =========================

    def select_folder(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.current_folder = folder

        self.start_scan(folder)

    # =========================
    # ПОЧАТОК СКАНУВАННЯ
    # =========================

    def start_scan(self, folder):

        self.scanning = True

        self.select_button.config(
            state="disabled"
        )

        self.junk_button.config(
            state="disabled"
        )

        self.stop_button.config(
            state="normal"
        )

        self.progress.start(10)

        self.status.config(
            text=f"Сканування: {folder}"
        )

        self.clear_tables()

        thread = threading.Thread(
            target=self.scan_folder,
            args=(folder,),
            daemon=True
        )

        thread.start()

    # =========================
    # СКАНУВАННЯ
    # =========================

    def scan_folder(self, folder):

        folders = []
        files = []

        try:

            for root, dirs, filenames in os.walk(folder):

                if not self.scanning:
                    break

                for filename in filenames:

                    if not self.scanning:
                        break

                    path = os.path.join(
                        root,
                        filename
                    )

                    try:

                        size = os.path.getsize(path)

                        files.append(
                            (
                                filename,
                                size,
                                path
                            )
                        )

                    except (
                        PermissionError,
                        FileNotFoundError
                    ):
                        pass

            # Розмір папок
            try:

                for item in os.listdir(folder):

                    if not self.scanning:
                        break

                    path = os.path.join(
                        folder,
                        item
                    )

                    if os.path.isdir(path):

                        size = self.get_folder_size(path)

                        folders.append(
                            (
                                item,
                                size
                            )
                        )

            except PermissionError:
                pass

        except PermissionError:
            pass

        folders.sort(
            key=lambda x: x[1],
            reverse=True
        )

        files.sort(
            key=lambda x: x[1],
            reverse=True
        )

        # Показуємо тільки 200 найбільших
        files = files[:200]

        self.window.after(
            0,
            self.show_results,
            folders,
            files
        )

    # =========================
    # РОЗМІР ПАПКИ
    # =========================

    def get_folder_size(self, folder):

        total = 0

        try:

            for root, dirs, files in os.walk(folder):

                if not self.scanning:
                    break

                for file in files:

                    try:

                        path = os.path.join(
                            root,
                            file
                        )

                        total += os.path.getsize(
                            path
                        )

                    except (
                        PermissionError,
                        FileNotFoundError
                    ):
                        pass

        except (
            PermissionError,
            FileNotFoundError
        ):
            pass

        return total

    # =========================
    # ПОКАЗ РЕЗУЛЬТАТІВ
    # =========================

    def show_results(self, folders, files):

        self.progress.stop()

        self.select_button.config(
            state="normal"
        )

        self.junk_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="disabled"
        )

        self.last_folders = list(folders)

        for name, size in folders:

            self.folder_table.insert(
                "",
                "end",
                values=(
                    name,
                    self.format_size(size)
                )
            )

        for name, size, path in files:

            self.file_table.insert(
                "",
                "end",
                values=(
                    name,
                    self.format_size(size),
                    path
                )
            )

        self.status.config(
            text=f"Папок: {len(folders)} | Файлів: {len(files)}"
        )

    # =========================
    # СКАНЕР НЕПОТРІБНИХ ФАЙЛІВ
    # =========================

    def scan_junk(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.current_folder = folder

        self.scanning = True

        self.select_button.config(
            state="disabled"
        )

        self.junk_button.config(
            state="disabled"
        )

        self.stop_button.config(
            state="normal"
        )

        self.progress.start(10)

        self.clear_tables()

        self.status.config(
            text="Пошук непотрібних файлів..."
        )

        thread = threading.Thread(
            target=self.find_junk,
            args=(folder,),
            daemon=True
        )

        thread.start()

    def find_junk(self, folder):

        junk = []

        junk_extensions = {
            ".tmp",
            ".temp",
            ".bak",
            ".old",
            ".cache"
        }

        junk_names = {
            "thumbs.db",
            ".ds_store"
        }

        try:

            for root, dirs, files in os.walk(folder):

                if not self.scanning:
                    break

                for filename in files:

                    if not self.scanning:
                        break

                    path = os.path.join(
                        root,
                        filename
                    )

                    lower_name = filename.lower()

                    extension = os.path.splitext(
                        lower_name
                    )[1]

                    if (
                        extension in junk_extensions
                        or lower_name in junk_names
                    ):

                        try:

                            size = os.path.getsize(
                                path
                            )

                            junk.append(
                                (
                                    filename,
                                    size,
                                    path
                                )
                            )

                        except (
                            PermissionError,
                            FileNotFoundError
                        ):
                            pass

        except PermissionError:
            pass

        junk.sort(
            key=lambda x: x[1],
            reverse=True
        )

        self.window.after(
            0,
            self.show_junk,
            junk
        )

    # =========================
    # ПОКАЗ НЕПОТРІБНИХ
    # =========================

    def show_junk(self, junk):

        self.progress.stop()

        self.select_button.config(
            state="normal"
        )

        self.junk_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="disabled"
        )

        for name, size, path in junk:

            self.file_table.insert(
                "",
                "end",
                values=(
                    name,
                    self.format_size(size),
                    path
                )
            )

        total = sum(
            item[1] for item in junk
        )

        self.status.config(
            text=(
                f"Знайдено: {len(junk)} файлів | "
                f"Можна перевірити: {self.format_size(total)}"
            )
        )

    # =========================
    # ВИДАЛЕННЯ ВИБРАНОГО
    # =========================

    def delete_selected(self):

        selected_folders = list(self.folder_table.selection())
        selected_files = list(self.file_table.selection())

        if not selected_folders and not selected_files:
            messagebox.showwarning(
                "Нічого не вибрано",
                "Вибери один або декілька файлів/папок.\n\n"
                "Для декількох об'єктів використовуй Ctrl або Shift."
            )
            return

        folder_paths = []
        for item_id in selected_folders:
            values = self.folder_table.item(item_id, "values")
            if values:
                folder_paths.append((item_id, os.path.join(self.current_folder, values[0])))

        file_paths = []
        for item_id in selected_files:
            values = self.file_table.item(item_id, "values")
            if values and len(values) >= 3:
                file_paths.append((item_id, values[2]))

        # Якщо вибрана папка містить вибраний файл, файл окремо не чіпаємо.
        filtered_files = []
        for item_id, file_path in file_paths:
            inside_folder = any(
                os.path.commonpath([os.path.abspath(file_path), os.path.abspath(folder_path)])
                == os.path.abspath(folder_path)
                for _, folder_path in folder_paths
                if os.path.exists(folder_path)
            )
            if not inside_folder:
                filtered_files.append((item_id, file_path))

        folder_count = len(folder_paths)
        file_count = len(filtered_files)

        answer = messagebox.askyesno(
            "Перемістити в кошик",
            f"Перемістити в кошик?\n\n"
            f"📁 Папок: {folder_count}\n"
            f"📄 Файлів: {file_count}\n\n"
            f"Файли не будуть видалені назавжди — вони потраплять у\n"
            f"кошик/Recycle Bin, якщо це підтримується системою."
        )

        if not answer:
            return

        deleted_folder_ids = []
        deleted_file_ids = []
        errors = []

        # Спочатку папки, щоб вкладені файли не залишалися окремими.
        for item_id, folder_path in folder_paths:
            try:
                if os.path.exists(folder_path):
                    send2trash(folder_path)
                deleted_folder_ids.append(item_id)
            except Exception as e:
                errors.append(f"Папка: {folder_path}\n{e}")

        for item_id, file_path in filtered_files:
            try:
                if os.path.exists(file_path):
                    send2trash(file_path)
                deleted_file_ids.append(item_id)
            except Exception as e:
                errors.append(f"Файл: {file_path}\n{e}")

        for item_id in deleted_folder_ids:
            self.folder_table.delete(item_id)

        for item_id in deleted_file_ids:
            self.file_table.delete(item_id)

        success_count = len(deleted_folder_ids) + len(deleted_file_ids)

        if errors:
            messagebox.showerror(
                "Частково виконано",
                f"У кошик переміщено: {success_count}\n\n"
                f"Не вдалося перемістити: {len(errors)}\n\n"
                + "\n\n".join(errors[:5])
            )

        self.status.config(
            text=f"У кошик переміщено: {success_count} об'єктів"
        )

    # =========================
    # РОЗУМНЕ ОЧИЩЕННЯ
    # =========================

    def smart_clean(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.current_folder = folder
        self.scanning = True
        self.progress.start(10)
        self.status.config(text="Пошук кандидатів для очищення...")

        self.select_button.config(state="disabled")
        self.junk_button.config(state="disabled")
        self.smart_button.config(state="disabled")
        self.stop_button.config(state="normal")

        thread = threading.Thread(
            target=self.find_smart_cleanup,
            args=(folder,),
            daemon=True
        )
        thread.start()

    def find_smart_cleanup(self, folder):

        results = []
        now = __import__("time").time()
        day = 24 * 60 * 60

        junk_extensions = {".tmp", ".temp", ".bak", ".old", ".cache"}
        junk_names = {"thumbs.db", ".ds_store"}

        try:
            for root, dirs, files in os.walk(folder):
                if not self.scanning:
                    break

                for filename in files:
                    if not self.scanning:
                        break

                    path = os.path.join(root, filename)
                    lower = filename.lower()
                    ext = os.path.splitext(lower)[1]

                    try:
                        size = os.path.getsize(path)
                        mtime = os.path.getmtime(path)
                    except (PermissionError, FileNotFoundError, OSError):
                        continue

                    category = None
                    safety = None
                    reason = None

                    if ext in junk_extensions or lower in junk_names:
                        category = "Тимчасові / службові"
                        safety = "🟢 Безпечно"
                        reason = "Типовий тимчасовий або службовий файл"

                    elif ext == ".log" and now - mtime > 30 * day:
                        category = "Старі журнали (.log)"
                        safety = "🟡 Перевірити"
                        reason = "Файл журналу старше 30 днів"

                    elif os.path.basename(root).lower() == "downloads" and now - mtime > 90 * day:
                        category = "Старі завантаження"
                        safety = "🟡 Перевірити"
                        reason = "Файл у Downloads старше 90 днів"

                    if category:
                        results.append((category, safety, size, path, reason))

        except PermissionError:
            pass

        results.sort(key=lambda x: x[2], reverse=True)

        self.window.after(0, self.show_smart_cleanup, results)

    def show_smart_cleanup(self, results):

        self.progress.stop()
        self.select_button.config(state="normal")
        self.junk_button.config(state="normal")
        self.smart_button.config(state="normal")
        self.stop_button.config(state="disabled")

        window = tk.Toplevel(self.window)
        window.title("🧹 Розумне очищення")
        window.geometry("1150x650")
        window.minsize(800, 450)

        tk.Label(
            window,
            text="🧹 Кандидати для очищення",
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 4))

        total = sum(item[2] for item in results)
        tk.Label(
            window,
            text=f"Знайдено: {len(results)} | Потенційно можна звільнити: {self.format_size(total)}",
            font=("Arial", 11)
        ).pack(pady=(0, 8))

        frame = ttk.Frame(window)
        frame.pack(expand=True, fill="both", padx=15, pady=5)

        tree = ttk.Treeview(
            frame,
            columns=("category", "safety", "size", "path", "reason"),
            show="headings",
            selectmode="extended"
        )

        headings = {
            "category": "Категорія",
            "safety": "Безпека",
            "size": "Розмір",
            "path": "Шлях",
            "reason": "Причина"
        }
        widths = {
            "category": 170,
            "safety": 120,
            "size": 100,
            "path": 430,
            "reason": 250
        }

        for col in tree["columns"]:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col])

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        for category, safety, size, path, reason in results:
            tree.insert("", "end", values=(
                category, safety, self.format_size(size), path, reason
            ))

        buttons = tk.Frame(window)
        buttons.pack(pady=10)

        def delete_selected_smart():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Нічого не вибрано", "Вибери файли для очищення.", parent=window)
                return

            paths = []
            safe_count = 0
            total_selected = 0

            for item_id in selected:
                values = tree.item(item_id, "values")
                path = values[3]
                safety = values[1]
                if os.path.isfile(path):
                    paths.append((item_id, path))
                    total_selected += os.path.getsize(path) if os.path.exists(path) else 0
                    if safety == "🟢 Безпечно":
                        safe_count += 1

            answer = messagebox.askyesno(
                "Підтвердження",
                f"Перемістити в Кошик: {len(paths)} файлів?\n\n"
                f"Розмір: {self.format_size(total_selected)}\n"
                f"🟢 Безпечно: {safe_count}\n"
                f"🟡 Потрібно перевірити: {len(paths) - safe_count}",
                parent=window
            )
            if not answer:
                return

            errors = []
            done = 0
            for item_id, path in paths:
                try:
                    send2trash(path)
                    tree.delete(item_id)
                    done += 1
                except Exception as e:
                    errors.append(f"{path}\n{e}")

            if errors:
                messagebox.showerror(
                    "Частково виконано",
                    f"У Кошик переміщено: {done}\n"
                    f"Помилок: {len(errors)}\n\n" + "\n\n".join(errors[:5]),
                    parent=window
                )
            else:
                messagebox.showinfo(
                    "Готово",
                    f"У Кошик переміщено {done} файлів.",
                    parent=window
                )

            self.status.config(text=f"Очищення: у Кошик переміщено {done} файлів")

        def select_safe():
            tree.selection_remove(tree.selection())
            for item_id in tree.get_children():
                if tree.item(item_id, "values")[1] == "🟢 Безпечно":
                    tree.selection_add(item_id)

        tk.Button(
            buttons, text="🟢 Вибрати безпечні", command=select_safe
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="🗑️ Перемістити в Кошик", command=delete_selected_smart
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="Закрити", command=window.destroy
        ).pack(side="left", padx=5)

        if not results:
            messagebox.showinfo(
                "Розумне очищення",
                "Потенційно непотрібних файлів не знайдено.",
                parent=window
            )

        self.status.config(
            text=f"Розумне очищення: знайдено {len(results)} кандидатів | {self.format_size(total)}"
        )

    # =========================
    # КАРТА ДИСКА
    # =========================

    def show_disk_map(self):

        if not self.last_folders:
            messagebox.showinfo(
                "Карта диска",
                "Спочатку проскануй папку, щоб побудувати карту."
            )
            return

        folders = [
            (name, size)
            for name, size in self.last_folders
            if size > 0
        ]

        if not folders:
            messagebox.showinfo(
                "Карта диска",
                "У вибраній папці немає підпапок із даними."
            )
            return

        map_window = tk.Toplevel(self.window)
        map_window.title("📊 Карта зайнятого місця")
        map_window.geometry("1100x700")
        map_window.minsize(700, 500)

        header = tk.Label(
            map_window,
            text=f"📊 Зайняте місце: {self.current_folder}",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=(10, 5))

        total = sum(size for _, size in folders)

        info = tk.Label(
            map_window,
            text=f"Показано папок: {len(folders)} | Загальний розмір: {self.format_size(total)}",
            font=("Arial", 11)
        )
        info.pack(pady=(0, 8))

        canvas = tk.Canvas(
            map_window,
            background="white",
            highlightthickness=0
        )
        canvas.pack(expand=True, fill="both", padx=15, pady=10)

        def open_folder_analysis(folder_path):
            if not os.path.isdir(folder_path):
                messagebox.showwarning(
                    "Папка недоступна",
                    "Ця папка більше не існує або недоступна."
                )
                return

            map_window.destroy()
            self.current_folder = folder_path
            self.start_scan(folder_path)

        def draw_map(event=None):
            canvas.delete("all")

            width = max(canvas.winfo_width(), 1)
            height = max(canvas.winfo_height(), 1)
            padding = 4

            # Найбільші папки спочатку.
            items = sorted(folders, key=lambda x: x[1], reverse=True)

            # Розкладаємо папки у прямокутники, пропорційні їхньому розміру.
            def layout(items, x, y, w, h, horizontal=True):
                if not items or w <= 0 or h <= 0:
                    return []

                if len(items) == 1:
                    return [(items[0], x, y, w, h)]

                total_size = sum(size for _, size in items)
                if total_size <= 0:
                    return []

                # Вибираємо першу групу приблизно половини площі.
                running = 0
                split_index = 1
                target = total_size / 2

                for i, (_, size) in enumerate(items[:-1], start=1):
                    running += size
                    if abs(running - target) < abs(
                        sum(s for _, s in items[:split_index]) - target
                    ):
                        split_index = i

                first = items[:split_index]
                second = items[split_index:]
                first_size = sum(size for _, size in first)
                ratio = first_size / total_size

                result = []

                if horizontal:
                    first_w = w * ratio
                    result.extend(layout(first, x, y, first_w, h, not horizontal))
                    result.extend(layout(second, x + first_w, y, w - first_w, h, not horizontal))
                else:
                    first_h = h * ratio
                    result.extend(layout(first, x, y, w, first_h, not horizontal))
                    result.extend(layout(second, x, y + first_h, w, h - first_h, not horizontal))

                return result

            rectangles = layout(items, 0, 0, width, height, width >= height)

            for (name, size), x, y, w, h in rectangles:
                x1 = x + padding
                y1 = y + padding
                x2 = x + w - padding
                y2 = y + h - padding

                if x2 <= x1 or y2 <= y1:
                    continue

                folder_path = os.path.join(self.current_folder, name)

                rect_id = canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="#333333",
                    width=2,
                    tags=("folder_rect",)
                )

                # Клік по прямокутнику відкриває аналіз цієї папки.
                canvas.tag_bind(
                    rect_id,
                    "<Button-1>",
                    lambda event, path=folder_path: open_folder_analysis(path)
                )
                canvas.tag_bind(
                    rect_id,
                    "<Enter>",
                    lambda event: canvas.config(cursor="hand2")
                )
                canvas.tag_bind(
                    rect_id,
                    "<Leave>",
                    lambda event: canvas.config(cursor="")
                )

                # Показуємо назву тільки якщо прямокутник достатньо великий.
                if w >= 100 and h >= 55:
                    percent = size / total * 100
                    text = (
                        f"{name}\n"
                        f"{self.format_size(size)}\n"
                        f"{percent:.1f}%"
                    )
                    canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=text,
                        font=("Arial", 11, "bold"),
                        justify="center"
                    )

        canvas.bind("<Configure>", draw_map)

    # =========================
    # ЗУПИНКА СКАНУВАННЯ
    # =========================

    def stop_scan(self):

        self.scanning = False

        self.progress.stop()

        self.select_button.config(
            state="normal"
        )

        self.junk_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="disabled"
        )

        self.status.config(
            text="Сканування зупинено"
        )

    # =========================
    # ОЧИСТИТИ ТАБЛИЦІ
    # =========================

    def clear_tables(self):

        for item in self.folder_table.get_children():

            self.folder_table.delete(item)

        for item in self.file_table.get_children():

            self.file_table.delete(item)

    # =========================
    # ФОРМАТ РОЗМІРУ
    # =========================

    @staticmethod
    def format_size(size):

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]

        for unit in units:

            if size < 1024:

                return f"{size:.2f} {unit}"

            size /= 1024

        return f"{size:.2f} PB"


# =========================
# ЗАПУСК
# =========================

window = tk.Tk()

app = DiskAnalyzer(window)

window.mainloop()
