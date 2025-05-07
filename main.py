import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from google import genai  # Убедитесь, что библиотека genai установлена: pip install google-genai

# Настройте ваш API-ключ
genaiapi = "AIzaSyChOA1AM8hnGrIwkZgfy-ndXl5ciVbWSeg"

# Отправить запрос к модели
client = genai.Client(api_key=genaiapi)


class ShatterCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Shatter: Code Editor")
        self.root.attributes("-fullscreen", True)  # Установить полноэкранный режим
        self.root.overrideredirect(True)  # Убрать стандартный заголовок окна

        # Создать пользовательский заголовок окна
        self.title_bar = tk.Frame(self.root, bg="black", relief="raised", bd=2)
        self.title_bar.pack(side="top", fill="x")

        # Добавить текст заголовка
        self.title_label = tk.Label(self.title_bar, text="Shatter: Code Editor", bg="black", fg="white")
        self.title_label.pack(side="left", padx=10)

        self.close_button = tk.Button(self.title_bar, text="X", bg="black", fg="white", command=self.root.quit)
        self.close_button.pack(side="right", padx=5)

        self.close_button = tk.Button(self.title_bar, text="-", bg="black", fg="white", command=self.minimize_window)
        self.close_button.pack(side="right", padx=5)

        # Создать текстовый виджет для редактора
        self.text_area = tk.Text(self.root, wrap="none", undo=True, font=("Courier", 12))
        self.text_area.pack(fill="both", expand=True)

        # Создать фрейм для чата
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill="x", side="bottom")

        # Поле для ввода сообщений
        self.chat_input = tk.Entry(self.chat_frame, font=("Courier", 12))
        self.chat_input.pack(fill="x", side="top")
        self.chat_input.bind("<Return>", self.send_message)

        # Поле для вывода сообщений
        self.chat_output = tk.Text(self.chat_frame, height=10, wrap="word", font=("Courier", 10), state="disabled")
        self.chat_output.pack(fill="x", side="bottom")

        # Добавить строку меню
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New..", command=self.new_file)
        file_menu.add_command(label="Open..", command=self.open_file)
        file_menu.add_command(label="Save..", command=self.save_file)
        file_menu.add_command(label="Save as..", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Change theme to black..", command=self.switch_to_dark_theme)
        file_menu.add_separator()
        file_menu.add_command(label="Exit..", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Меню "Редактировать"
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo..", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo..", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut..", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy..", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste..", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Меню "Запуск"
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_script)
        run_menu.add_command(label="Compile", command=self.compile_script)
        self.menu_bar.add_cascade(label="Run", menu=run_menu)

        # Инициализация пути к файлу
        self.file_path = None

    def minimize_window(self):
        """Свернуть окно."""
        self.root.overrideredirect(False)  # Отключить пользовательский заголовок
        self.root.iconify()  # Свернуть окно
        self.root.wait_visibility()  # Дождаться, пока окно станет видимым
        self.root.overrideredirect(True)  # Включить пользовательский заголовок

    def switch_to_dark_theme(self):
        """Change the theme to dark."""
        self.text_area.config(bg="black", fg="white", insertbackground="white")
        self.chat_output.config(bg="black", fg="white")
        self.chat_input.config(bg="black", fg="white")
        self.chat_input.config(bg="black", fg="white")

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.root.title("Shatter - New File")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
            self.file_path = file_path
            self.root.title(f"Shatter - {file_path}")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END).strip())
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END).strip())
            self.file_path = file_path
            self.root.title(f"Shatter - {file_path}")

    def run_script(self):
        if not self.file_path:
            messagebox.showerror("ERROR", "Save file before running.")
            return

        try:
            result = subprocess.run(["python", self.file_path], capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            self.append_to_chat_output(f"Result of run:\n{output}")
        except Exception as e:
            self.append_to_chat_output(f"Error while running: {str(e)}")

    def compile_script(self):
        if not self.file_path:
            messagebox.showerror("Error", "Save file before compiling.")
            return

        try:
            # Пример компиляции Python-скрипта в .pyc
            result = subprocess.run(["python", "-m", "py_compile", self.file_path], capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            self.append_to_chat_output(f"Compile result:\n{output}")
        except Exception as e:
            self.append_to_chat_output(f"Error while compiling: {str(e)}")

    def send_message(self, event):
        user_message = self.chat_input.get()
        self.chat_input.delete(0, tk.END)

        # Отобразить сообщение пользователя
        self.append_to_chat_output(f"You: {user_message}")

        # Отправить запрос к модели
        try:
            response = self.get_ai_response(user_message)
            self.append_to_chat_output(f"Gemini: {response}")
        except Exception as e:
            self.append_to_chat_output(f"Error: {str(e)}")

    def get_ai_response(self, message):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
        )
        return response.text

    def append_to_chat_output(self, text):
        self.chat_output.config(state="normal")
        self.chat_output.insert(tk.END, text + "\n")
        self.chat_output.config(state="disabled")
        self.chat_output.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ShatterCodeEditor(root)
    root.mainloop()