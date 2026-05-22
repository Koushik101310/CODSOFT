import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FILE_NAME = "contacts.json"

class ContactManager:

    def __init__(self, root):

        self.root = root
        self.root.title("NEXUS CONTACT MANAGER")
        self.root.geometry("1200x750")
        self.root.configure(fg_color="#070b14")

        self.contacts = []

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
            text="📇 CONTACT HUB",
            font=("Poppins", 28, "bold"),
            text_color="#00d4ff"
        )
        logo.pack(pady=(40, 15))

        subtitle = ctk.CTkLabel(
            sidebar,
            text="Modern CRM Dashboard",
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
            text="⚡ CONTACT MANAGEMENT SYSTEM",
            font=("Poppins", 32, "bold")
        )
        title.pack(pady=(30, 20))

        # ===== FORM =====
        form = ctk.CTkFrame(
            main,
            fg_color="#111827",
            corner_radius=20
        )
        form.pack(fill="x", padx=30)

        self.name_entry = self.create_entry(form, "Full Name")
        self.phone_entry = self.create_entry(form, "Phone Number")
        self.email_entry = self.create_entry(form, "Email Address")
        self.address_entry = self.create_entry(form, "Address")

        # ===== BUTTONS =====
        button_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        button_frame.pack(pady=25)

        buttons = [
            ("➕ Add", self.add_contact, "#2563eb"),
            ("✏ Update", self.update_contact, "#f59e0b"),
            ("🗑 Delete", self.delete_contact, "#ef4444"),
            ("🔍 Search", self.search_contact, "#22c55e"),
            ("♻ Refresh", self.refresh_contacts, "#8b5cf6")
        ]

        for text, command, color in buttons:

            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=160,
                height=50,
                fg_color=color,
                hover_color=color,
                font=("Poppins", 14, "bold")
            )

            btn.pack(side="left", padx=10)

        # ===== LISTBOX =====
        list_frame = ctk.CTkFrame(
            main,
            fg_color="#111827",
            corner_radius=20
        )
        list_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        heading = ctk.CTkLabel(
            list_frame,
            text="📋 SAVED CONTACTS",
            font=("Poppins", 22, "bold")
        )
        heading.pack(pady=15)

        self.contact_list = Listbox(
            list_frame,
            font=("Consolas", 14),
            bg="#1a1a1a",
            fg="white",
            selectbackground="#2563eb",
            relief="flat",
            height=15
        )

        self.contact_list.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.contact_list.bind(
            "<<ListboxSelect>>",
            self.select_contact
        )

        self.load_contacts()

    # ===== CREATE ENTRY =====
    def create_entry(self, parent, placeholder):

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=50,
            font=("Poppins", 14),
            corner_radius=12
        )

        entry.pack(
            fill="x",
            padx=20,
            pady=10
        )

        return entry

    # ===== ADD =====
    def add_contact(self):

        contact = {
            "name": self.name_entry.get(),
            "phone": self.phone_entry.get(),
            "email": self.email_entry.get(),
            "address": self.address_entry.get()
        }

        if contact["name"] == "":
            messagebox.showwarning(
                "Warning",
                "Name required!"
            )
            return

        self.contacts.append(contact)

        self.save_contacts()

        self.refresh_contacts()

        self.clear_entries()

    # ===== REFRESH =====
    def refresh_contacts(self):

        self.contact_list.delete(0, END)

        for contact in self.contacts:

            display = f"{contact['name']}   |   {contact['phone']}"

            self.contact_list.insert(END, display)

    # ===== SELECT =====
    def select_contact(self, event):

        try:

            index = self.contact_list.curselection()[0]

            selected = self.contacts[index]

            self.clear_entries()

            self.name_entry.insert(0, selected["name"])
            self.phone_entry.insert(0, selected["phone"])
            self.email_entry.insert(0, selected["email"])
            self.address_entry.insert(0, selected["address"])

        except:
            pass

    # ===== UPDATE =====
    def update_contact(self):

        try:

            index = self.contact_list.curselection()[0]

            self.contacts[index] = {
                "name": self.name_entry.get(),
                "phone": self.phone_entry.get(),
                "email": self.email_entry.get(),
                "address": self.address_entry.get()
            }

            self.save_contacts()

            self.refresh_contacts()

            messagebox.showinfo(
                "Updated",
                "Contact updated successfully!"
            )

        except:

            messagebox.showwarning(
                "Warning",
                "Select a contact!"
            )

    # ===== DELETE =====
    def delete_contact(self):

        try:

            index = self.contact_list.curselection()[0]

            del self.contacts[index]

            self.save_contacts()

            self.refresh_contacts()

            self.clear_entries()

            messagebox.showinfo(
                "Deleted",
                "Contact deleted successfully!"
            )

        except:

            messagebox.showwarning(
                "Warning",
                "Select a contact!"
            )

    # ===== SEARCH =====
    def search_contact(self):

        keyword = self.name_entry.get().lower()

        self.contact_list.delete(0, END)

        for contact in self.contacts:

            if keyword in contact["name"].lower():

                display = f"{contact['name']}   |   {contact['phone']}"

                self.contact_list.insert(END, display)

    # ===== CLEAR =====
    def clear_entries(self):

        self.name_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.address_entry.delete(0, END)

    # ===== SAVE =====
    def save_contacts(self):

        with open(FILE_NAME, "w") as file:

            json.dump(self.contacts, file)

    # ===== LOAD =====
    def load_contacts(self):

        if os.path.exists(FILE_NAME):

            try:

                with open(FILE_NAME, "r") as file:

                    self.contacts = json.load(file)

            except:

                self.contacts = []

        self.refresh_contacts()

# ===== MAIN =====
root = ctk.CTk()

app = ContactManager(root)

root.mainloop()