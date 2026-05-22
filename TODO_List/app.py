

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
import time
import random
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "tasks.json"
DATA_FILE.parent.mkdir(exist_ok=True)

THEMES = {
    "Midnight": {
        "bg":          "#0A0E1A",
        "sidebar":     "#0D1120",
        "card":        "#111827",
        "card2":       "#131C2E",
        "surface":     "#1A2235",
        "border":      "#1E2D45",
        "accent":      "#00D4FF",
        "accent2":     "#7B61FF",
        "accent3":     "#00FF9C",
        "danger":      "#FF4D6A",
        "warning":     "#FFB830",
        "text":        "#E8EEF7",
        "text_dim":    "#6B7A99",
        "text_muted":  "#3D4F6B",
        "high":        "#FF4D6A",
        "medium":      "#FFB830",
        "low":         "#00FF9C",
    },
    "Aurora": {
        "bg":          "#07091A",
        "sidebar":     "#0A0C1F",
        "card":        "#0F1328",
        "card2":       "#111530",
        "surface":     "#161A38",
        "border":      "#1D2245",
        "accent":      "#A78BFA",
        "accent2":     "#F472B6",
        "accent3":     "#34D399",
        "danger":      "#F87171",
        "warning":     "#FBBF24",
        "text":        "#E2E8F5",
        "text_dim":    "#6677A8",
        "text_muted":  "#333D66",
        "high":        "#F87171",
        "medium":      "#FBBF24",
        "low":         "#34D399",
    },
    "Carbon": {
        "bg":          "#0C0C0C",
        "sidebar":     "#101010",
        "card":        "#161616",
        "card2":       "#1A1A1A",
        "surface":     "#202020",
        "border":      "#2A2A2A",
        "accent":      "#FF6B35",
        "accent2":     "#FFD700",
        "accent3":     "#39FF14",
        "danger":      "#FF3333",
        "warning":     "#FFD700",
        "text":        "#F0F0F0",
        "text_dim":    "#666666",
        "text_muted":  "#333333",
        "high":        "#FF3333",
        "medium":      "#FFD700",
        "low":         "#39FF14",
    },
}

CATEGORIES = ["All", "Work", "Personal", "Health", "Learning", "Finance", "Creative"]
PRIORITIES  = ["High", "Medium", "Low"]

QUOTES = [
    "The secret of getting ahead is getting started.",
    "Focus on being productive instead of busy.",
    "Small steps every day lead to big results.",
    "Done is better than perfect.",
    "Your future is created by what you do today.",
    "Discipline is choosing between what you want now and what you want most.",
    "Work hard in silence. Let success make the noise.",
    "One task at a time. One day at a time.",
    "Progress, not perfection.",
    "The key is not to prioritize your schedule, but to schedule your priorities.",
]

class NexusNotification:
    """Sleek floating notification that auto-dismisses."""

    def __init__(self, parent, message: str, kind: str = "success"):
        self.parent = parent
        colors = {
            "success": ("#00FF9C", "#001A0F"),
            "error":   ("#FF4D6A", "#1A0009"),
            "info":    ("#00D4FF", "#001A26"),
            "warning": ("#FFB830", "#1A1000"),
        }
        icons = {"success": "✓", "error": "✕", "info": "ℹ", "warning": "⚠"}

        fg, bg = colors.get(kind, colors["info"])
        icon   = icons.get(kind, "ℹ")

        self.win = ctk.CTkToplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(fg_color=bg)

        # Position bottom-right
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        self.win.geometry(f"340x64+{px + pw - 360}+{py + ph - 90}")

        # Border frame
        border = ctk.CTkFrame(self.win, fg_color=fg, corner_radius=12)
        border.pack(fill="both", expand=True, padx=1, pady=1)

        inner = ctk.CTkFrame(border, fg_color=bg, corner_radius=11)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        ctk.CTkLabel(inner, text=icon, font=("Consolas", 18, "bold"),
                     text_color=fg, width=36).pack(side="left", padx=(14, 6), pady=12)
        ctk.CTkLabel(inner, text=message, font=("Segoe UI", 12),
                     text_color="#DDEEFF", anchor="w").pack(side="left", fill="x", expand=True)

        # Fade-out after 2.5 s
        self.win.after(2500, self._close)

    def _close(self):
        try:
            self.win.destroy()
        except Exception:
            pass

class TaskDialog(ctk.CTkToplevel):
    """Modal dialog for creating or editing a task."""

    def __init__(self, parent, theme: dict, task: dict = None):
        super().__init__(parent)
        self.theme   = theme
        self.result  = None
        self.editing = task is not None

        self.title("Edit Task" if self.editing else "New Task")
        self.geometry("520x540")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg"])
        self.attributes("-topmost", True)
        self.grab_set()

        self._build(task or {})
        self.after(100, self._center)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_x()
        py = self.master.winfo_y()
        w, h = 520, 540
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _build(self, task: dict):
        t = self.theme

        # Header
        hdr = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        label_text = "✎  Edit Task" if self.editing else "＋  New Task"
        ctk.CTkLabel(hdr, text=label_text, font=("Segoe UI", 16, "bold"),
                     text_color=t["accent"]).pack(side="left", padx=24, pady=16)

        body = ctk.CTkScrollableFrame(self, fg_color=t["bg"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        def section(parent, label):
            ctk.CTkLabel(parent, text=label, font=("Segoe UI", 11, "bold"),
                         text_color=t["text_dim"]).pack(anchor="w", padx=24, pady=(16, 4))

        # Title
        section(body, "TASK TITLE")
        self.title_var = ctk.StringVar(value=task.get("title", ""))
        title_entry = ctk.CTkEntry(body, textvariable=self.title_var,
                                   placeholder_text="What needs to be done?",
                                   font=("Segoe UI", 13), height=44,
                                   fg_color=t["surface"], border_color=t["border"],
                                   border_width=1, corner_radius=10,
                                   text_color=t["text"])
        title_entry.pack(fill="x", padx=24)
        title_entry.focus()

        # Description
        section(body, "DESCRIPTION (OPTIONAL)")
        self.desc_text = ctk.CTkTextbox(body, height=80, font=("Segoe UI", 12),
                                        fg_color=t["surface"], border_color=t["border"],
                                        border_width=1, corner_radius=10,
                                        text_color=t["text"])
        self.desc_text.pack(fill="x", padx=24)
        if task.get("description"):
            self.desc_text.insert("0.0", task["description"])

        # Priority & Category row
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 4))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        lf = ctk.CTkFrame(row, fg_color="transparent")
        lf.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(lf, text="PRIORITY", font=("Segoe UI", 11, "bold"),
                     text_color=t["text_dim"]).pack(anchor="w", pady=(16, 4))
        self.priority_var = ctk.StringVar(value=task.get("priority", "Medium"))
        ctk.CTkOptionMenu(lf, values=PRIORITIES, variable=self.priority_var,
                          fg_color=t["surface"], button_color=t["accent2"],
                          button_hover_color=t["accent"], dropdown_fg_color=t["card"],
                          font=("Segoe UI", 12), height=40,
                          corner_radius=10).pack(fill="x")

        rf = ctk.CTkFrame(row, fg_color="transparent")
        rf.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(rf, text="CATEGORY", font=("Segoe UI", 11, "bold"),
                     text_color=t["text_dim"]).pack(anchor="w", pady=(16, 4))
        self.cat_var = ctk.StringVar(value=task.get("category", "Personal"))
        ctk.CTkOptionMenu(rf, values=CATEGORIES[1:], variable=self.cat_var,
                          fg_color=t["surface"], button_color=t["accent2"],
                          button_hover_color=t["accent"], dropdown_fg_color=t["card"],
                          font=("Segoe UI", 12), height=40,
                          corner_radius=10).pack(fill="x")

        # Due date
        section(body, "DUE DATE (OPTIONAL)")
        self.due_var = ctk.StringVar(value=task.get("due_date", ""))
        ctk.CTkEntry(body, textvariable=self.due_var,
                     placeholder_text="e.g. 2025-12-31",
                     font=("Segoe UI", 12), height=40,
                     fg_color=t["surface"], border_color=t["border"],
                     border_width=1, corner_radius=10,
                     text_color=t["text"]).pack(fill="x", padx=24)

        # Footer buttons
        footer = ctk.CTkFrame(self, fg_color=t["card"], corner_radius=0, height=72)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkButton(footer, text="Cancel", width=110, height=40,
                      fg_color=t["surface"], hover_color=t["border"],
                      font=("Segoe UI", 12), corner_radius=10,
                      text_color=t["text_dim"],
                      command=self.destroy).pack(side="right", padx=(8, 24), pady=16)

        save_text = "Save Changes" if self.editing else "Create Task"
        ctk.CTkButton(footer, text=save_text, width=140, height=40,
                      fg_color=t["accent2"], hover_color=t["accent"],
                      font=("Segoe UI", 12, "bold"), corner_radius=10,
                      text_color="#FFFFFF",
                      command=self._save).pack(side="right", padx=4, pady=16)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        title = self.title_var.get().strip()
        if not title:
            NexusNotification(self, "Task title cannot be empty.", "error")
            return
        self.result = {
            "title":       title,
            "description": self.desc_text.get("0.0", "end").strip(),
            "priority":    self.priority_var.get(),
            "category":    self.cat_var.get(),
            "due_date":    self.due_var.get().strip(),
        }
        self.destroy()


# ─────────────────────────────────────────────────────────
#  TASK CARD WIDGET
# ─────────────────────────────────────────────────────────
class TaskCard(ctk.CTkFrame):
    """A single task row with hover effects and action buttons."""

    def __init__(self, parent, task: dict, theme: dict,
                 on_toggle, on_edit, on_delete):
        super().__init__(parent, fg_color=theme["card"],
                         corner_radius=12, border_width=1,
                         border_color=theme["border"])
        self.task    = task
        self.theme   = theme
        self._normal = theme["card"]
        self._hover  = theme["surface"]

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._build(on_toggle, on_edit, on_delete)

    def _priority_color(self, p):
        return {
            "High":   self.theme["high"],
            "Medium": self.theme["medium"],
            "Low":    self.theme["low"],
        }.get(p, self.theme["text_dim"])

    def _build(self, on_toggle, on_edit, on_delete):
        t    = self.theme
        task = self.task
        done = task.get("completed", False)
        pri  = task.get("priority", "Medium")
        pc   = self._priority_color(pri)

        # Left accent bar
        bar = ctk.CTkFrame(self, fg_color=pc, width=4, corner_radius=4)
        bar.pack(side="left", fill="y", padx=(6, 0), pady=8)

        # Checkbox
        self._chk_var = ctk.BooleanVar(value=done)
        chk = ctk.CTkCheckBox(self, variable=self._chk_var, text="",
                               width=24, height=24,
                               checkbox_width=22, checkbox_height=22,
                               corner_radius=6,
                               fg_color=t["accent2"], border_color=t["border"],
                               hover_color=t["accent"],
                               command=lambda: on_toggle(task["id"]))
        chk.pack(side="left", padx=(10, 8), pady=12)

        # Text content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=8)

        title_color = t["text_dim"] if done else t["text"]
        title_font  = ("Segoe UI", 13, "bold") if not done else ("Segoe UI", 13)
        title_label = ctk.CTkLabel(content, text=task["title"],
                                   font=title_font, text_color=title_color,
                                   anchor="w")
        title_label.pack(anchor="w")

        # Meta row
        meta_parts = []
        if task.get("category"):
            meta_parts.append(f"⬡ {task['category']}")
        if task.get("due_date"):
            meta_parts.append(f"◷ {task['due_date']}")
        meta_parts.append(f"◈ {pri}")

        ts = datetime.fromisoformat(task["created_at"]).strftime("%b %d, %Y")
        meta_parts.append(f"↑ {ts}")

        meta = "   ·   ".join(meta_parts)
        ctk.CTkLabel(content, text=meta, font=("Segoe UI", 10),
                     text_color=t["text_dim"], anchor="w").pack(anchor="w", pady=(2, 0))

        if task.get("description"):
            desc = task["description"][:80] + ("…" if len(task["description"]) > 80 else "")
            ctk.CTkLabel(content, text=desc, font=("Segoe UI", 11, "italic"),
                         text_color=t["text_muted"], anchor="w").pack(anchor="w")

        # Done badge
        if done:
            ctk.CTkLabel(self, text="✓ Done",
                         fg_color="#003B22", text_color=t["low"],
                         font=("Segoe UI", 10, "bold"),
                         corner_radius=6, padx=8, pady=3).pack(side="right", padx=8)

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=(4, 12))

        ctk.CTkButton(btn_frame, text="✎", width=30, height=30,
                      fg_color=t["surface"], hover_color=t["accent2"],
                      font=("Segoe UI", 13), corner_radius=8,
                      text_color=t["text_dim"],
                      command=lambda: on_edit(task["id"])).pack(pady=2)

        ctk.CTkButton(btn_frame, text="✕", width=30, height=30,
                      fg_color=t["surface"], hover_color=t["danger"],
                      font=("Segoe UI", 12, "bold"), corner_radius=8,
                      text_color=t["text_dim"],
                      command=lambda: on_delete(task["id"])).pack(pady=2)

    def _on_enter(self, _):
        self.configure(fg_color=self._hover)

    def _on_leave(self, _):
        self.configure(fg_color=self._normal)

class NexusApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self._theme_name = "Midnight"
        self.theme       = THEMES[self._theme_name]

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("NEXUS — Productivity Dashboard")
        self.geometry("1280x800")
        self.minsize(1000, 660)
        self.configure(fg_color=self.theme["bg"])

        # State
        self.tasks:         list  = []
        self._filter_status = "All"   # All / Pending / Completed
        self._filter_cat    = "All"
        self._search_query  = ""
        self._active_nav    = "Dashboard"

        # Load & build
        self._load_tasks()
        self._build_layout()
        self._render_tasks()

        # Keyboard shortcuts
        self.bind("<Control-n>", lambda e: self._open_add_dialog())
        self.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.bind("<Control-d>", lambda e: self._delete_selected())
        self.bind("<F5>",        lambda e: self._render_tasks())

        # Start live clock
        self._update_clock()

        # Animated progress bar pulse
        self._progress_pulse()

    def _load_tasks(self):
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def _save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def _next_id(self) -> int:
        return max((t["id"] for t in self.tasks), default=0) + 1

    def _build_layout(self):
        # ── sidebar ──
        self.sidebar = ctk.CTkFrame(self, fg_color=self.theme["sidebar"],
                                    width=230, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── main ──
        self.main = ctk.CTkFrame(self, fg_color=self.theme["bg"], corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self._build_main()

    def _build_sidebar(self):
        t = self.theme

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=76)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="⬡ NEXUS",
                     font=("Consolas", 20, "bold"),
                     text_color=t["accent"]).pack(side="left", padx=22, pady=20)

        # Divider
        ctk.CTkFrame(self.sidebar, fg_color=t["border"], height=1).pack(fill="x", padx=16)

        # Nav label
        ctk.CTkLabel(self.sidebar, text="NAVIGATION",
                     font=("Segoe UI", 10, "bold"),
                     text_color=t["text_muted"]).pack(anchor="w", padx=22, pady=(16, 6))

        # Nav items
        self._nav_btns = {}
        nav_items = [
            ("Dashboard", "⊞"),
            ("All Tasks",  "☰"),
            ("Pending",    "◷"),
            ("Completed",  "✓"),
        ]
        for label, icon in nav_items:
            self._nav_btns[label] = self._nav_button(label, icon)

        # Categories label
        ctk.CTkFrame(self.sidebar, fg_color=t["border"], height=1).pack(fill="x", padx=16, pady=(16, 0))
        ctk.CTkLabel(self.sidebar, text="CATEGORIES",
                     font=("Segoe UI", 10, "bold"),
                     text_color=t["text_muted"]).pack(anchor="w", padx=22, pady=(12, 6))

        for cat in CATEGORIES[1:]:
            self._nav_button(cat, "◈", is_cat=True)

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Theme switcher
        ctk.CTkFrame(self.sidebar, fg_color=t["border"], height=1).pack(fill="x", padx=16)
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=56)
        theme_frame.pack(fill="x")
        theme_frame.pack_propagate(False)

        ctk.CTkLabel(theme_frame, text="Theme", font=("Segoe UI", 11),
                     text_color=t["text_dim"]).pack(side="left", padx=20)
        self._theme_var = ctk.StringVar(value=self._theme_name)
        ctk.CTkOptionMenu(theme_frame,
                          values=list(THEMES.keys()),
                          variable=self._theme_var,
                          width=100, height=32,
                          fg_color=t["surface"],
                          button_color=t["accent2"],
                          button_hover_color=t["accent"],
                          dropdown_fg_color=t["card"],
                          font=("Segoe UI", 11),
                          corner_radius=8,
                          command=self._switch_theme).pack(side="right", padx=14, pady=12)

     
        ctk.CTkLabel(self.sidebar,
                     text="Ctrl+N  New   Ctrl+F  Search",
                     font=("Consolas", 9),
                     text_color=t["text_muted"],
                     justify="center").pack(pady=(4, 12))

    def _nav_button(self, label: str, icon: str, is_cat: bool = False):
        t       = self.theme
        active  = (label == self._active_nav)
        bg      = t["surface"] if active else "transparent"
        fg      = t["accent"] if active else t["text_dim"]

        btn = ctk.CTkButton(self.sidebar,
                            text=f"  {icon}  {label}",
                            anchor="w",
                            height=38,
                            fg_color=bg,
                            hover_color=t["surface"],
                            font=("Segoe UI", 12, "bold" if active else "normal"),
                            text_color=fg,
                            corner_radius=8,
                            command=lambda l=label, c=is_cat: self._nav_click(l, c))
        btn.pack(fill="x", padx=14, pady=2)
        return btn

    def _nav_click(self, label: str, is_cat: bool):
        self._active_nav = label
        if is_cat:
            self._filter_cat = label
            self._filter_status = "All"
        else:
            self._filter_cat = "All"
            if label == "Pending":
                self._filter_status = "Pending"
            elif label == "Completed":
                self._filter_status = "Completed"
            else:
                self._filter_status = "All"

        self._refresh_sidebar_highlight()
        self._render_tasks()

        # Update header title
        self.page_title_label.configure(text=label)

    def _refresh_sidebar_highlight(self):
        # Rebuild sidebar to reflect new active state
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._build_sidebar()
    def _build_main(self):
        t = self.theme

        # ── top bar ──
        topbar = ctk.CTkFrame(self.main, fg_color=t["card"],
                               height=64, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.page_title_label = ctk.CTkLabel(
            topbar, text=self._active_nav,
            font=("Segoe UI", 18, "bold"),
            text_color=t["text"])
        self.page_title_label.pack(side="left", padx=28)

        # Clock
        self.clock_label = ctk.CTkLabel(
            topbar, text="",
            font=("Consolas", 13),
            text_color=t["text_dim"])
        self.clock_label.pack(side="right", padx=28)

        # Date
        self.date_label = ctk.CTkLabel(
            topbar, text="",
            font=("Segoe UI", 11),
            text_color=t["text_muted"])
        self.date_label.pack(side="right", padx=(0, 6))

        # ── dashboard stats strip ──
        self.stats_strip = ctk.CTkFrame(self.main, fg_color="transparent", height=110)
        self.stats_strip.pack(fill="x", padx=24, pady=(20, 0))
        self.stats_strip.pack_propagate(False)
        self._build_stats()

        # ── progress bar section ──
        prog_frame = ctk.CTkFrame(self.main, fg_color=t["card"],
                                   corner_radius=12, height=72)
        prog_frame.pack(fill="x", padx=24, pady=(16, 0))
        prog_frame.pack_propagate(False)
        self._build_progress(prog_frame)

        # ── quote ──
        self.quote_label = ctk.CTkLabel(
            self.main,
            text=f'❝  {random.choice(QUOTES)}  ❞',
            font=("Segoe UI", 11, "italic"),
            text_color=t["text_muted"],
            wraplength=900, anchor="w")
        self.quote_label.pack(anchor="w", padx=30, pady=(12, 4))

        # ── toolbar ──
        toolbar = ctk.CTkFrame(self.main, fg_color="transparent", height=54)
        toolbar.pack(fill="x", padx=24, pady=(8, 0))
        toolbar.pack_propagate(False)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search())
        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍  Search tasks…",
            font=("Segoe UI", 12), height=40, width=300,
            fg_color=t["surface"], border_color=t["border"],
            border_width=1, corner_radius=10,
            text_color=t["text"])
        self.search_entry.pack(side="left")

        # Filter
        self._status_var = ctk.StringVar(value="All")
        ctk.CTkSegmentedButton(
            toolbar,
            values=["All", "Pending", "Completed"],
            variable=self._status_var,
            font=("Segoe UI", 11),
            fg_color=t["surface"],
            selected_color=t["accent2"],
            selected_hover_color=t["accent"],
            unselected_color=t["surface"],
            unselected_hover_color=t["border"],
            text_color=t["text"],
            corner_radius=10,
            command=self._on_filter_status
        ).pack(side="left", padx=14)

        # Add button
        ctk.CTkButton(
            toolbar,
            text="＋  New Task",
            width=130, height=40,
            fg_color=t["accent2"],
            hover_color=t["accent"],
            font=("Segoe UI", 12, "bold"),
            corner_radius=10,
            text_color="#FFFFFF",
            command=self._open_add_dialog
        ).pack(side="right")

        # Sort
        self._sort_var = ctk.StringVar(value="Newest")
        ctk.CTkOptionMenu(
            toolbar,
            values=["Newest", "Oldest", "Priority", "A–Z"],
            variable=self._sort_var,
            width=120, height=40,
            fg_color=t["surface"],
            button_color=t["surface"],
            button_hover_color=t["border"],
            dropdown_fg_color=t["card"],
            font=("Segoe UI", 11),
            corner_radius=10,
            text_color=t["text_dim"],
            command=lambda _: self._render_tasks()
        ).pack(side="right", padx=(0, 10))

        ctk.CTkLabel(toolbar, text="Sort:", font=("Segoe UI", 11),
                     text_color=t["text_dim"]).pack(side="right", padx=(0, 4))

        # ── task list ──
        ctk.CTkFrame(self.main, fg_color=t["border"], height=1).pack(fill="x", padx=24, pady=(12, 0))

        self.task_scroll = ctk.CTkScrollableFrame(
            self.main, fg_color="transparent",
            scrollbar_button_color=t["surface"],
            scrollbar_button_hover_color=t["border"])
        self.task_scroll.pack(fill="both", expand=True, padx=24, pady=(8, 12))

    def _build_stats(self):
        t     = self.theme
        total = len(self.tasks)
        done  = sum(1 for x in self.tasks if x.get("completed"))
        pend  = total - done
        high  = sum(1 for x in self.tasks if x.get("priority") == "High" and not x.get("completed"))

        cards = [
            ("Total Tasks",      str(total), "⬡", t["accent"]),
            ("Completed",        str(done),  "✓", t["low"]),
            ("Pending",          str(pend),  "◷", t["warning"]),
            ("High Priority",    str(high),  "!", t["danger"]),
        ]

        for widget in self.stats_strip.winfo_children():
            widget.destroy()

        for i, (label, val, icon, color) in enumerate(cards):
            card = ctk.CTkFrame(self.stats_strip, fg_color=t["card"],
                                corner_radius=12, border_width=1,
                                border_color=t["border"])
            card.pack(side="left", expand=True, fill="both",
                      padx=(0 if i == 0 else 10, 0))

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(14, 4))

            ctk.CTkLabel(top, text=label, font=("Segoe UI", 10, "bold"),
                         text_color=t["text_dim"]).pack(side="left")
            ctk.CTkLabel(top, text=icon, font=("Segoe UI", 14, "bold"),
                         text_color=color).pack(side="right")

            ctk.CTkLabel(card, text=val,
                         font=("Segoe UI", 30, "bold"),
                         text_color=color).pack(anchor="w", padx=16)

    def _build_progress(self, parent):
        t     = self.theme
        total = len(self.tasks)
        done  = sum(1 for x in self.tasks if x.get("completed"))
        pct   = (done / total * 100) if total else 0

        parent.columnconfigure(1, weight=1)

        ctk.CTkLabel(parent, text="Productivity",
                     font=("Segoe UI", 12, "bold"),
                     text_color=t["text_dim"]).grid(row=0, column=0,
                                                     padx=(20, 14), pady=(10, 0),
                                                     sticky="w")

        self.progress_bar = ctk.CTkProgressBar(
            parent, height=10,
            fg_color=t["surface"],
            progress_color=t["accent2"],
            corner_radius=5)
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(12, 0))
        self.progress_bar.set(pct / 100)

        self.pct_label = ctk.CTkLabel(
            parent, text=f"{pct:.0f}%",
            font=("Consolas", 13, "bold"),
            text_color=t["accent"],
            width=48)
        self.pct_label.grid(row=0, column=2, padx=(0, 20), pady=(10, 0))

    def _update_progress(self):
        total = len(self.tasks)
        done  = sum(1 for x in self.tasks if x.get("completed"))
        pct   = (done / total * 100) if total else 0
        try:
            self.progress_bar.set(pct / 100)
            self.pct_label.configure(text=f"{pct:.0f}%")
        except Exception:
            pass

    def _progress_pulse(self):
        """Subtle animated shimmer on progress bar."""
        try:
            current = self.progress_bar.get()
            # tiny oscillation for living feel
        except Exception:
            pass
        self.after(3000, self._progress_pulse)

    # ── task rendering ────────────────────────────────────
    def _filtered_tasks(self) -> list:
        tasks = list(self.tasks)

        # Category
        if self._filter_cat != "All":
            tasks = [t for t in tasks if t.get("category") == self._filter_cat]

        # Status
        status = self._filter_status or self._status_var.get()
        if status == "Pending":
            tasks = [t for t in tasks if not t.get("completed")]
        elif status == "Completed":
            tasks = [t for t in tasks if t.get("completed")]

        # Search
        q = self._search_query.lower()
        if q:
            tasks = [t for t in tasks
                     if q in t["title"].lower()
                     or q in t.get("description", "").lower()
                     or q in t.get("category", "").lower()]

        # Sort
        sort = self._sort_var.get()
        pri_order = {"High": 0, "Medium": 1, "Low": 2}
        if sort == "Newest":
            tasks.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort == "Oldest":
            tasks.sort(key=lambda x: x["created_at"])
        elif sort == "Priority":
            tasks.sort(key=lambda x: pri_order.get(x.get("priority", "Low"), 2))
        elif sort == "A–Z":
            tasks.sort(key=lambda x: x["title"].lower())

        return tasks

    def _render_tasks(self):
        # Clear
        for w in self.task_scroll.winfo_children():
            w.destroy()

        tasks = self._filtered_tasks()

        if not tasks:
            empty = ctk.CTkFrame(self.task_scroll, fg_color=self.theme["card"],
                                 corner_radius=16, height=200)
            empty.pack(fill="x", pady=20)
            ctk.CTkLabel(empty, text="⬡",
                         font=("Segoe UI", 48),
                         text_color=self.theme["text_muted"]).pack(pady=(40, 4))
            ctk.CTkLabel(empty, text="No tasks found",
                         font=("Segoe UI", 16, "bold"),
                         text_color=self.theme["text_dim"]).pack()
            ctk.CTkLabel(empty, text="Press Ctrl+N to create a new task",
                         font=("Segoe UI", 12),
                         text_color=self.theme["text_muted"]).pack(pady=(4, 40))
            return

        for task in tasks:
            card = TaskCard(
                self.task_scroll, task, self.theme,
                on_toggle=self._toggle_task,
                on_edit=self._edit_task,
                on_delete=self._delete_task,
            )
            card.pack(fill="x", pady=4)

        # Refresh stats & progress
        self._build_stats()
        self._update_progress()

    # ── task actions ──────────────────────────────────────
    def _open_add_dialog(self):
        dlg = TaskDialog(self, self.theme)
        self.wait_window(dlg)
        if dlg.result:
            now = datetime.now().isoformat()
            task = {
                "id":          self._next_id(),
                "completed":   False,
                "created_at":  now,
                "updated_at":  now,
                **dlg.result,
            }
            self.tasks.append(task)
            self._save_tasks()
            self._render_tasks()
            NexusNotification(self, f'Task "{task["title"]}" created!', "success")

    def _toggle_task(self, task_id: int):
        for t in self.tasks:
            if t["id"] == task_id:
                t["completed"]  = not t["completed"]
                t["updated_at"] = datetime.now().isoformat()
                status = "completed ✓" if t["completed"] else "reopened"
                NexusNotification(self, f'Task {status}!',
                                   "success" if t["completed"] else "info")
                break
        self._save_tasks()
        self._render_tasks()

    def _edit_task(self, task_id: int):
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        dlg = TaskDialog(self, self.theme, task=task)
        self.wait_window(dlg)
        if dlg.result:
            task.update(dlg.result)
            task["updated_at"] = datetime.now().isoformat()
            self._save_tasks()
            self._render_tasks()
            NexusNotification(self, "Task updated successfully.", "info")

    def _delete_task(self, task_id: int):
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        if messagebox.askyesno("Delete Task",
                               f'Delete "{task["title"]}"?',
                               icon="warning"):
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self._save_tasks()
            self._render_tasks()
            NexusNotification(self, "Task deleted.", "error")

    def _delete_selected(self):
        """Delete all completed tasks — Ctrl+D shortcut."""
        completed = [t for t in self.tasks if t.get("completed")]
        if not completed:
            NexusNotification(self, "No completed tasks to delete.", "warning")
            return
        if messagebox.askyesno("Clear Completed",
                               f"Delete {len(completed)} completed task(s)?",
                               icon="warning"):
            self.tasks = [t for t in self.tasks if not t.get("completed")]
            self._save_tasks()
            self._render_tasks()
            NexusNotification(self, f"{len(completed)} tasks cleared.", "success")

    # ── search / filter ───────────────────────────────────
    def _on_search(self):
        self._search_query = self.search_var.get()
        self._render_tasks()

    def _on_filter_status(self, value: str):
        self._filter_status = value
        self._render_tasks()

    # ── clock ─────────────────────────────────────────────
    def _update_clock(self):
        now = datetime.now()
        try:
            self.clock_label.configure(text=now.strftime("%H:%M:%S"))
            self.date_label.configure(text=now.strftime("%A, %B %d %Y"))
        except Exception:
            pass
        self.after(1000, self._update_clock)

    # ── theme switching ───────────────────────────────────
    def _switch_theme(self, name: str):
        self._theme_name = name
        self.theme = THEMES[name]
        self._active_nav = "Dashboard"
        self._filter_status = "All"
        self._filter_cat = "All"

        # Rebuild entire UI
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=self.theme["bg"])
        self._build_layout()
        self._render_tasks()
        NexusNotification(self, f"Theme switched to {name}.", "info")


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
def main():
    app = NexusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
