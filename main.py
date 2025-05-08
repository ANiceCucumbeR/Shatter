import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
from google import genai
import plistlib

API_KEY = "AIzaSyChOA1AM8hnGrIwkZgfy-ndXl5ciVbWSeg"
client = genai.Client(api_key=API_KEY)

class ShatterCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Shatter Code Editor")
        self.filename = None

        self.main_frame = tk.Frame(self.root, bg="#181818")
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Create the PanedWindow first!
        self.terminal_pane = tk.PanedWindow(self.main_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="#181818")
        self.terminal_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)  # <-- changed

        # Editor area (top)
        self.text_area = scrolledtext.ScrolledText(
            self.terminal_pane, bg="#181818", fg="#f8f8f2",
            insertbackground="#f8f8f2", font=("Consolas", 12)
        )

        # Output terminal (bottom, resizable, small by default)
        self.terminal_output = scrolledtext.ScrolledText(
            self.terminal_pane, bg="#181818", fg="#39ff14",
            height=4, font=("Consolas", 12)
        )
        self.terminal_output.insert(tk.END, "Output terminal ready...\n")
        self.terminal_output.configure(state=tk.DISABLED)

        # Add both widgets to the PanedWindow
        self.terminal_pane.add(self.text_area)
        self.terminal_pane.add(self.terminal_output, minsize=40)

        # Mile AI chat area (right, initially hidden)
        self.chat_frame = tk.Frame(self.main_frame, bg="#222222", width=200)
        self.chat_label = tk.Label(self.chat_frame, text="Mile AI Chat", bg="#222222", fg="#f8f8f2", font=("Arial", 12, "bold"))
        self.chat_label.pack(pady=5)
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, bg="#222222", fg="#f8f8f2", height=40, width=28, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 14))
        self.chat_display.pack(fill=tk.BOTH, expand=0, padx=5, pady=5)
        self.chat_entry = tk.Entry(self.chat_frame, bg="#181818", fg="#f8f8f2", insertbackground="#f8f8f2", width=28)
        self.chat_entry.pack(fill=tk.X, padx=5, pady=5)
        self.chat_entry.bind("<Return>", self.send_mile_message)
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_mile_message, bg="#282828", fg="#f8f8f2")
        self.send_button.pack(padx=5, pady=(0, 5))
        self.chat_visible = False  # Track chat visibility

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#282828", fg="#f8f8f2")
        filemenu = tk.Menu(menubar, tearoff=0, bg="#282828", fg="#f8f8f2")
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        runmenu = tk.Menu(menubar, tearoff=0, bg="#282828", fg="#f8f8f2")
        runmenu.add_command(label="Run Script", command=self.run_script)
        menubar.add_cascade(label="Run", menu=runmenu)

        thememenu = tk.Menu(menubar, tearoff=0, bg="#282828", fg="#f8f8f2")
        thememenu.add_command(label="Black Theme", command=self.set_black_theme)
        menubar.add_cascade(label="Theme", menu=thememenu)

        milemenu = tk.Menu(menubar, tearoff=0, bg="#282828", fg="#f8f8f2")
        milemenu.add_command(label="Show/Hide Mile AI Chat", command=self.toggle_mile_chat)
        menubar.add_cascade(label="Mile", menu=milemenu)

        self.root.config(menu=menubar)

    def show_terminal_output(self, output):
        self.terminal_output.configure(state=tk.NORMAL)
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.insert(tk.END, output)
        self.terminal_output.see(tk.END)
        self.terminal_output.configure(state=tk.DISABLED)

    def toggle_mile_chat(self):
        if self.chat_visible:
            self.chat_frame.pack_forget()
            self.chat_visible = False
        else:
            self.chat_frame.pack(side=tk.RIGHT, fill=tk.Y)
            self.chat_visible = True
            self.chat_entry.focus_set()

    def open_file(self):
        self.filename = filedialog.askopenfilename(defaultextension=".txt",
                                                    filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("Text Documents", "*.txt"), ("Property List", "*.plist")])
        if self.filename:
            if self.filename.lower().endswith(".plist"):
                self.display_plist_in_editor()
            else:
                try:
                    with open(self.filename, "r", encoding="utf-8") as file:
                        self.text_area.delete(1.0, tk.END)
                        self.text_area.insert(tk.END, file.read())
                except UnicodeDecodeError:
                    messagebox.showerror("Open File", "Could not decode file. Try saving it as UTF-8.")

    def display_plist_in_editor(self):
        try:
            with open(self.filename, "rb") as f:
                plist_data = plistlib.load(f)
        except Exception as e:
            messagebox.showerror("Open File", f"Failed to open plist: {e}")
            return

        def format_plist(data, indent=0):
            lines = []
            prefix = " " * indent
            if isinstance(data, dict):
                for k, v in data.items():
                    lines.append(f"{prefix}{k}:")
                    lines.extend(format_plist(v, indent + 4))
            elif isinstance(data, list):
                for idx, v in enumerate(data):
                    lines.append(f"{prefix}- [{idx}]")
                    lines.extend(format_plist(v, indent + 4))
            else:
                lines.append(f"{prefix}{data}")
            return lines

        formatted = "\n".join(format_plist(plist_data))
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, formatted)

    def save_file(self):
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("Text Documents", "*.txt")])
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END))
    def run_script(self):
        if not self.filename:
            # Ask for filename if not saved yet
            self.save_file()
            if not self.filename:
                return  # User cancelled save dialog

        # Always save before running
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(self.text_area.get(1.0, tk.END))

        ext = os.path.splitext(self.filename)[1]
        if ext == ".py":
            cmd = ["python", self.filename]
        elif ext == ".sh":
            cmd = ["bash", self.filename]
        else:
            messagebox.showinfo("Run Script", "Unsupported script type.")
            return
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            self.show_terminal_output(output)
        except subprocess.CalledProcessError as e:
            self.show_terminal_output(e.output)

    def set_black_theme(self):
        self.root.configure(bg="#181818")
        self.text_area.configure(bg="#181818", fg="#f8f8f2", insertbackground="#f8f8f2")
        self.chat_frame.configure(bg="#222222")
        self.chat_label.configure(bg="#222222", fg="#f8f8f2")
        self.chat_display.configure(bg="#222222", fg="#f8f8f2")
        self.chat_entry.configure(bg="#181818", fg="#f8f8f2", insertbackground="#f8f8f2")
        self.send_button.configure(bg="#282828", fg="#f8f8f2")

    def focus_mile_chat(self):
        self.chat_entry.focus_set()

    def send_mile_message(self, event=None):
        user_message = self.chat_entry.get().strip()
        if not user_message:
            return
        self.append_chat("You", user_message)
        self.chat_entry.delete(0, tk.END)
        self.root.after(100, lambda: self.get_mile_response(user_message))

    def append_chat(self, sender, message):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def get_mile_response(self, prompt):
        try:
            response = client.models.generate_content(
                model = "gemini-2.0-flash",
                contents="Your name is Mile. You are a virtual helper for code editing. Give a productive, short answers. Help this user with their code.\n" + prompt
            )
            if hasattr(response, "text"):
                reply = response.text
            elif hasattr(response, "result"):
                reply = response.result
            else:
                reply = str(response)
        except Exception as e:
            reply = f"Error: {e}"
        self.append_chat("Mile", reply)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShatterCodeEditor(root)
    root.mainloop()
