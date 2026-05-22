import customtkinter as ctk
import random
import string
import json
import os
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FILE_NAME = "password_history.json"

class PasswordGenerator:

    def __init__(self, root):

        self.root = root
        self.root.title("CYBERPASS GENERATOR")
        self.root.geometry("1200x750")
        self.root.configure(fg_color="#070b14")

        self.history = []

        # ===== SIDEBAR =====
        sidebar = ctk.CTkFrame(
            root,
            width=250,
            fg_color="#0f172a",
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")

        logo = ctk.CTkLabel(
            sidebar,
            text="🔐 CYBERPASS",
            font=("Poppins", 30, "bold"),
            text_color="#00d4ff"
        )
        logo.pack(pady=(40, 15))

        subtitle = ctk.CTkLabel(
            sidebar,
            text="Advanced Security Generator",
            font=("Poppins", 14),
            text_color="gray"
        )
        subtitle.pack()

        # ===== MAIN =====
        main = ctk.CTkFrame(
            root,
            fg_color="#070b14"
        )
        main.pack(side="right", fill="both", expand=True)

        title = ctk.CTkLabel(
            main,
            text="⚡ PASSWORD GENERATOR",
            font=("Poppins", 34, "bold")
        )
        title.pack(pady=(30, 20))

        # ===== SETTINGS =====
        settings = ctk.CTkFrame(
            main,
            fg_color="#111827",
            corner_radius=20
        )
        settings.pack(fill="x", padx=30)

        self.length_label = ctk.CTkLabel(
            settings,
            text="Password Length: 12",
            font=("Poppins", 18, "bold")
        )
        self.length_label.pack(pady=(20, 10))

        self.slider = ctk.CTkSlider(
            settings,
            from_=6,
            to=40,
            number_of_steps=34,
            command=self.update_length
        )
        self.slider.set(12)
        self.slider.pack(fill="x", padx=30)

        # ===== OPTIONS =====
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.number_var = ctk.BooleanVar(value=True)
        self.symbol_var = ctk.BooleanVar(value=True)

        options_frame = ctk.CTkFrame(
            settings,
            fg_color="transparent"
        )
        options_frame.pack(pady=20)

        options = [
            ("Uppercase", self.upper_var),
            ("Lowercase", self.lower_var),
            ("Numbers", self.number_var),
            ("Symbols", self.symbol_var)
        ]

        for text, var in options:

            check = ctk.CTkCheckBox(
                options_frame,
                text=text,
                variable=var,
                font=("Poppins", 14)
            )

            check.pack(side="left", padx=20)

        # ===== PASSWORD OUTPUT =====
        output_frame = ctk.CTkFrame(
            main,
            fg_color="#111827",
            corner_radius=20
        )
        output_frame.pack(fill="x", padx=30, pady=20)

        self.password_entry = ctk.CTkEntry(
            output_frame,
            height=60,
            font=("Consolas", 20, "bold"),
            corner_radius=15
        )
        self.password_entry.pack(fill="x", padx=20, pady=20)

        # ===== BUTTONS =====
        button_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        button_frame.pack(pady=15)

        buttons = [
            ("⚡ Generate", self.generate_password, "#2563eb"),
            ("📋 Copy", self.copy_password, "#22c55e"),
            ("🗑 Clear", self.clear_password, "#ef4444")
        ]

        for text, command, color in buttons:

            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=180,
                height=50,
                fg_color=color,
                hover_color=color,
                font=("Poppins", 14, "bold")
            )

            btn.pack(side="left", padx=12)

        # ===== STRENGTH =====
        self.strength_label = ctk.CTkLabel(
            main,
            text="Strength: Medium",
            font=("Poppins", 18, "bold"),
            text_color="#f59e0b"
        )
        self.strength_label.pack(pady=10)

        # ===== HISTORY =====
        history_frame = ctk.CTkFrame(
            main,
            fg_color="#111827",
            corner_radius=20
        )
        history_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        history_title = ctk.CTkLabel(
            history_frame,
            text="🕘 PASSWORD HISTORY",
            font=("Poppins", 22, "bold")
        )
        history_title.pack(pady=15)

        self.history_box = ctk.CTkTextbox(
            history_frame,
            font=("Consolas", 14)
        )

        self.history_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.load_history()

    # ===== LENGTH =====
    def update_length(self, value):

        self.length_label.configure(
            text=f"Password Length: {int(value)}"
        )

    # ===== GENERATE =====
    def generate_password(self):

        characters = ""

        if self.upper_var.get():
            characters += string.ascii_uppercase

        if self.lower_var.get():
            characters += string.ascii_lowercase

        if self.number_var.get():
            characters += string.digits

        if self.symbol_var.get():
            characters += string.punctuation

        if characters == "":

            messagebox.showwarning(
                "Warning",
                "Select at least one option!"
            )

            return

        length = int(self.slider.get())

        password = "".join(
            random.choice(characters)
            for _ in range(length)
        )

        self.password_entry.delete(0, "end")

        self.password_entry.insert(0, password)

        self.update_strength(length)

        self.history.append(password)

        self.update_history()

        self.save_history()

    # ===== STRENGTH =====
    def update_strength(self, length):

        if length < 8:

            self.strength_label.configure(
                text="Strength: Weak",
                text_color="#ef4444"
            )

        elif length < 15:

            self.strength_label.configure(
                text="Strength: Medium",
                text_color="#f59e0b"
            )

        else:

            self.strength_label.configure(
                text="Strength: Strong",
                text_color="#22c55e"
            )

    # ===== COPY =====
    def copy_password(self):

        password = self.password_entry.get()

        if password:

            self.root.clipboard_clear()

            self.root.clipboard_append(password)

            messagebox.showinfo(
                "Copied",
                "Password copied successfully!"
            )

    # ===== CLEAR =====
    def clear_password(self):

        self.password_entry.delete(0, "end")

    # ===== HISTORY =====
    def update_history(self):

        self.history_box.delete("1.0", "end")

        for password in reversed(self.history):

            self.history_box.insert(
                "end",
                f"🔑 {password}\n\n"
            )

    # ===== SAVE =====
    def save_history(self):

        with open(FILE_NAME, "w") as file:

            json.dump(self.history, file)

    # ===== LOAD =====
    def load_history(self):

        if os.path.exists(FILE_NAME):

            try:

                with open(FILE_NAME, "r") as file:

                    self.history = json.load(file)

            except:

                self.history = []

        self.update_history()

# ===== MAIN =====
root = ctk.CTk()

app = PasswordGenerator(root)

root.mainloop()