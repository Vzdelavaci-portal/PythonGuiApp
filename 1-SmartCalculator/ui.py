"""Nexus Calc desktop interface."""

from __future__ import annotations

import math
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from calculator_engine import CalculatorEngine, CalculatorError
from converters import CurrencyService, TEMPERATURES, UNITS, convert_unit
from history_manager import HistoryManager
from theme_manager import THEMES


APP_DIR = Path(__file__).resolve().parent


class SmartCalculatorStudio(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Nexus Calc — Smart Calculator Studio")
        self.geometry("1280x800")
        self.minsize(1050, 700)

        self.engine = CalculatorEngine()
        self.history = HistoryManager()
        self.currency = CurrencyService()
        self.theme_name = "Dark"
        self.theme = THEMES[self.theme_name]
        self.sound_enabled = True
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._configure_window()
        self._show_splash()
        self.after(850, self._build_app)

    def _configure_window(self) -> None:
        self.configure(fg_color=self.theme["bg"])
        icon_path = APP_DIR / "assets" / "nexus-calc.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.bind("<Return>", lambda _event: self.calculate())
        self.bind("<Escape>", lambda _event: self.clear_expression())
        self.bind("<Control-l>", lambda _event: self.entry.focus_set() if hasattr(self, "entry") else None)

    def _show_splash(self) -> None:
        splash_path = APP_DIR / "assets" / "nexus-calc-splash.png"
        if not splash_path.exists():
            return
        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True)
        width, height = 720, 420
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        splash.geometry(f"{width}x{height}+{x}+{y}")
        image = ctk.CTkImage(Image.open(splash_path), size=(width, height))
        label = ctk.CTkLabel(splash, text="", image=image)
        label.image = image
        label.pack(fill="both", expand=True)
        splash.attributes("-topmost", True)
        self.withdraw()
        self.after(800, lambda: (splash.destroy(), self.deiconify()))

    def _build_app(self) -> None:
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=(0, 22), pady=22)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._build_topbar()
        self.page_host = ctk.CTkFrame(self.content, fg_color="transparent")
        self.page_host.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

        self._build_calculator_page()
        self._build_graph_page()
        self._build_currency_page()
        self._build_units_page()
        self._build_history_page()
        self._build_statistics_page()
        self.show_page("Kalkulačka")

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, width=232, corner_radius=0, fg_color=self.theme["panel"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="NEXUS", text_color=self.theme["accent"],
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
        ).grid(row=0, column=0, padx=24, pady=(30, 0), sticky="w")
        ctk.CTkLabel(
            self.sidebar, text="CALC STUDIO", text_color=self.theme["muted"],
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
        ).grid(row=1, column=0, padx=25, pady=(0, 28), sticky="w")

        items = [
            ("Kalkulačka", "⌨"), ("Graf funkcí", "⌁"), ("Měny", "¤"),
            ("Jednotky", "↔"), ("Historie", "◷"), ("Statistiky", "▥"),
        ]
        for row, (name, icon) in enumerate(items, start=2):
            button = ctk.CTkButton(
                self.sidebar, text=f"  {icon}   {name}", anchor="w", height=46,
                corner_radius=12, fg_color="transparent", hover_color=self.theme["card"],
                text_color=self.theme["text"], font=ctk.CTkFont("Segoe UI", 14),
                command=lambda page=name: self.show_page(page),
            )
            button.grid(row=row, column=0, sticky="ew", padx=15, pady=3)
            self.nav_buttons[name] = button

        self.sound_switch = ctk.CTkSwitch(
            self.sidebar, text="Zvuky tlačítek", command=self._toggle_sound,
            progress_color=self.theme["accent"], text_color=self.theme["muted"],
        )
        self.sound_switch.select()
        self.sound_switch.grid(row=9, column=0, padx=24, pady=(12, 6), sticky="w")
        ctk.CTkLabel(
            self.sidebar, text="v2.0 · Crafted in Python",
            text_color=self.theme["muted"], font=ctk.CTkFont(size=10),
        ).grid(row=10, column=0, padx=24, pady=(6, 22), sticky="w")

    def _build_topbar(self) -> None:
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        self.page_title = ctk.CTkLabel(
            bar, text="Kalkulačka", text_color=self.theme["text"],
            font=ctk.CTkFont("Segoe UI", 25, "bold"),
        )
        self.page_title.grid(row=0, column=0, sticky="w")
        self.angle_button = ctk.CTkSegmentedButton(
            bar, values=["DEG", "RAD"], width=145, command=self._set_angle_mode,
            selected_color=self.theme["accent2"], selected_hover_color=self.theme["accent2"],
        )
        self.angle_button.set("DEG")
        self.angle_button.grid(row=0, column=1, padx=12)
        self.theme_menu = ctk.CTkOptionMenu(
            bar, values=["Dark", "Light", "Neon"], width=125,
            command=self.apply_theme, fg_color=self.theme["card"],
            button_color=self.theme["accent2"],
        )
        self.theme_menu.set(self.theme_name)
        self.theme_menu.grid(row=0, column=2)

    def _new_page(self, name: str) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.page_host, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        self.pages[name] = page
        return page

    def _card(self, parent, **kwargs) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent, fg_color=self.theme["card"], corner_radius=22,
            border_width=1, border_color=self.theme["grid"], **kwargs
        )

    def _build_calculator_page(self) -> None:
        page = self._new_page("Kalkulačka")
        page.grid_columnconfigure(0, weight=3)
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(0, weight=1)

        calc = self._card(page)
        calc.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        calc.grid_columnconfigure(tuple(range(5)), weight=1)
        calc.grid_rowconfigure(2, weight=1)

        display = ctk.CTkFrame(calc, fg_color=self.theme["panel"], corner_radius=18)
        display.grid(row=0, column=0, columnspan=5, sticky="ew", padx=18, pady=18)
        display.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            display, placeholder_text="Napiš výraz… např. sin(45) + sqrt(16)",
            height=46, border_width=0, fg_color="transparent", text_color=self.theme["muted"],
            font=ctk.CTkFont("Consolas", 18),
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=17, pady=(13, 0))
        self.result_label = ctk.CTkLabel(
            display, text="0", anchor="e", text_color=self.theme["text"],
            font=ctk.CTkFont("Consolas", 38, "bold"),
        )
        self.result_label.grid(row=1, column=0, sticky="ew", padx=17, pady=(0, 13))

        keys = [
            ["MC", "MR", "M+", "⌫", "AC"],
            ["sin", "cos", "tan", "(", ")"],
            ["ln", "log", "√", "^", "÷"],
            ["7", "8", "9", "π", "×"],
            ["4", "5", "6", "%", "-"],
            ["1", "2", "3", "e", "+"],
            ["0", "00", ".", "ans", "="],
        ]
        for row, values in enumerate(keys, start=1):
            for col, value in enumerate(values):
                is_equal = value == "="
                is_operator = value in {"÷", "×", "-", "+", "^"}
                button = ctk.CTkButton(
                    calc, text=value, height=48, corner_radius=13,
                    fg_color=self.theme["accent2"] if is_equal else (
                        self.theme["panel"] if not is_operator else self.theme["grid"]
                    ),
                    hover_color=self.theme["accent"] if is_equal else self.theme["accent2"],
                    text_color=self.theme["text"], font=ctk.CTkFont("Segoe UI", 16, "bold"),
                    command=lambda token=value: self._key(token),
                )
                button.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        science = self._card(page)
        science.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        science.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            science, text="VĚDECKÝ PANEL", anchor="w", text_color=self.theme["accent"],
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 8))
        ctk.CTkLabel(
            science, text="Rychlé funkce", anchor="w", text_color=self.theme["text"],
            font=ctk.CTkFont("Segoe UI", 21, "bold"),
        ).grid(row=1, column=0, sticky="ew", padx=22)

        funcs = [
            ("x²", "^2"), ("x³", "^3"), ("1/x", "1/("), ("|x|", "abs("),
            ("asin", "asin("), ("acos", "acos("), ("atan", "atan("), ("n!", "fact("),
            ("floor", "floor("), ("ceil", "ceil("), ("exp", "exp("), ("τ", "tau"),
        ]
        grid = ctk.CTkFrame(science, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="nsew", padx=17, pady=15)
        grid.grid_columnconfigure((0, 1), weight=1)
        for index, (label, token) in enumerate(funcs):
            ctk.CTkButton(
                grid, text=label, height=42, fg_color=self.theme["panel"],
                hover_color=self.theme["accent2"], corner_radius=11,
                command=lambda value=token: self._insert(value),
            ).grid(row=index // 2, column=index % 2, sticky="ew", padx=5, pady=5)

        self.quick_history = ctk.CTkScrollableFrame(
            science, label_text="Poslední výpočty", fg_color=self.theme["panel"],
            label_text_color=self.theme["muted"], corner_radius=15,
        )
        self.quick_history.grid(row=3, column=0, sticky="nsew", padx=22, pady=(0, 22))
        science.grid_rowconfigure(3, weight=1)
        self.refresh_history()

    def _build_graph_page(self) -> None:
        page = self._new_page("Graf funkcí")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        controls = self._card(page)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        controls.grid_columnconfigure(0, weight=1)
        self.graph_expression = ctk.CTkEntry(
            controls, height=44, placeholder_text="Funkce: sin(x), x^2 - 4, sqrt(abs(x))…"
        )
        self.graph_expression.insert(0, "sin(x)")
        self.graph_expression.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        self.x_min = ctk.CTkEntry(controls, width=85, height=44)
        self.x_min.insert(0, "-10")
        self.x_min.grid(row=0, column=1, padx=5)
        self.x_max = ctk.CTkEntry(controls, width=85, height=44)
        self.x_max.insert(0, "10")
        self.x_max.grid(row=0, column=2, padx=5)
        ctk.CTkButton(
            controls, text="Vykreslit", height=44, width=120,
            fg_color=self.theme["accent2"], command=self.plot_function,
        ).grid(row=0, column=3, padx=16)
        self.graph_host = self._card(page)
        self.graph_host.grid(row=1, column=0, sticky="nsew")
        self.graph_host.grid_rowconfigure(0, weight=1)
        self.graph_host.grid_columnconfigure(0, weight=1)
        self.graph_placeholder = ctk.CTkLabel(
            self.graph_host, text="⌁\n\nGraf se zobrazí zde",
            text_color=self.theme["muted"], font=ctk.CTkFont(size=20),
        )
        self.graph_placeholder.grid(row=0, column=0)
        self.graph_canvas = None

    def _build_currency_page(self) -> None:
        page = self._new_page("Měny")
        page.grid_columnconfigure(0, weight=1)
        card = self._card(page)
        card.grid(row=0, column=0, sticky="new", padx=100, pady=55)
        card.grid_columnconfigure((0, 1), weight=1)
        self._section_heading(card, "PŘEVOD MĚN", "Aktuální kurzy s offline zálohou")
        self.currency_value = ctk.CTkEntry(card, height=54, font=ctk.CTkFont(size=20))
        self.currency_value.insert(0, "1000")
        self.currency_value.grid(row=2, column=0, columnspan=2, sticky="ew", padx=30, pady=20)
        self.currency_from = ctk.CTkOptionMenu(card, values=list(self.currency.CURRENCIES))
        self.currency_from.set("CZK")
        self.currency_from.grid(row=3, column=0, sticky="ew", padx=(30, 8))
        self.currency_to = ctk.CTkOptionMenu(card, values=list(self.currency.CURRENCIES))
        self.currency_to.set("EUR")
        self.currency_to.grid(row=3, column=1, sticky="ew", padx=(8, 30))
        ctk.CTkButton(
            card, text="⇅  Převést", height=48, fg_color=self.theme["accent2"],
            command=self.convert_currency,
        ).grid(row=4, column=0, columnspan=2, padx=30, pady=24)
        self.currency_result = ctk.CTkLabel(
            card, text="—", text_color=self.theme["accent"],
            font=ctk.CTkFont("Consolas", 32, "bold"),
        )
        self.currency_result.grid(row=5, column=0, columnspan=2, pady=(0, 4))
        self.currency_status = ctk.CTkLabel(card, text="", text_color=self.theme["muted"])
        self.currency_status.grid(row=6, column=0, columnspan=2, pady=(0, 30))

    def _build_units_page(self) -> None:
        page = self._new_page("Jednotky")
        page.grid_columnconfigure(0, weight=1)
        card = self._card(page)
        card.grid(row=0, column=0, sticky="new", padx=100, pady=45)
        card.grid_columnconfigure((0, 1), weight=1)
        self._section_heading(card, "PŘEVOD JEDNOTEK", "Délka, hmotnost, teplota, objem a další")
        categories = list(UNITS) + ["Teplota"]
        self.unit_category = ctk.CTkOptionMenu(
            card, values=categories, command=self._update_unit_choices
        )
        self.unit_category.set("Délka")
        self.unit_category.grid(row=2, column=0, columnspan=2, padx=30, pady=15)
        self.unit_value = ctk.CTkEntry(card, height=50)
        self.unit_value.insert(0, "1")
        self.unit_value.grid(row=3, column=0, columnspan=2, sticky="ew", padx=30, pady=10)
        units = list(UNITS["Délka"])
        self.unit_from = ctk.CTkOptionMenu(card, values=units)
        self.unit_from.set(units[0])
        self.unit_from.grid(row=4, column=0, sticky="ew", padx=(30, 8))
        self.unit_to = ctk.CTkOptionMenu(card, values=units)
        self.unit_to.set(units[1])
        self.unit_to.grid(row=4, column=1, sticky="ew", padx=(8, 30))
        ctk.CTkButton(
            card, text="Převést jednotky", height=48, fg_color=self.theme["accent2"],
            command=self.convert_units,
        ).grid(row=5, column=0, columnspan=2, padx=30, pady=24)
        self.unit_result = ctk.CTkLabel(
            card, text="—", text_color=self.theme["accent"],
            font=ctk.CTkFont("Consolas", 30, "bold"),
        )
        self.unit_result.grid(row=6, column=0, columnspan=2, pady=(0, 30))

    def _build_history_page(self) -> None:
        page = self._new_page("Historie")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        actions = ctk.CTkFrame(page, fg_color="transparent")
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        actions.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            actions, text="Exportovat CSV", width=150, command=self.export_history,
            fg_color=self.theme["accent2"],
        ).grid(row=0, column=1, padx=5)
        ctk.CTkButton(
            actions, text="Vymazat historii", width=150, command=self.clear_history,
            fg_color=self.theme["danger"],
        ).grid(row=0, column=2, padx=5)
        self.history_frame = ctk.CTkScrollableFrame(
            page, fg_color=self.theme["card"], corner_radius=20
        )
        self.history_frame.grid(row=1, column=0, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)

    def _build_statistics_page(self) -> None:
        page = self._new_page("Statistiky")
        page.grid_columnconfigure((0, 1, 2), weight=1)
        self.stat_labels = {}
        for column, (key, title, icon) in enumerate([
            ("total", "Celkem výpočtů", "∑"), ("today", "Dnes", "◷"), ("favorite", "Nejčastější typ", "★")
        ]):
            card = self._card(page)
            card.grid(row=0, column=column, sticky="ew", padx=7, pady=(0, 15))
            ctk.CTkLabel(
                card, text=icon, text_color=self.theme["accent"], font=ctk.CTkFont(size=26)
            ).pack(pady=(22, 4))
            value = ctk.CTkLabel(
                card, text="0", text_color=self.theme["text"],
                font=ctk.CTkFont("Segoe UI", 29, "bold"),
            )
            value.pack()
            self.stat_labels[key] = value
            ctk.CTkLabel(card, text=title, text_color=self.theme["muted"]).pack(pady=(0, 22))
        self.stats_detail = self._card(page)
        self.stats_detail.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=7)
        page.grid_rowconfigure(1, weight=1)

    def _section_heading(self, parent, eyebrow: str, title: str) -> None:
        ctk.CTkLabel(
            parent, text=eyebrow, text_color=self.theme["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(30, 5))
        ctk.CTkLabel(
            parent, text=title, text_color=self.theme["text"],
            font=ctk.CTkFont("Segoe UI", 21, "bold"),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 5))

    def show_page(self, name: str) -> None:
        self._click_sound()
        self.pages[name].tkraise()
        self.page_title.configure(text=name)
        for page_name, button in self.nav_buttons.items():
            button.configure(
                fg_color=self.theme["accent2"] if page_name == name else "transparent"
            )
        if name == "Historie":
            self.refresh_history()
        elif name == "Statistiky":
            self.refresh_statistics()

    def _key(self, token: str) -> None:
        self._click_sound()
        if token == "=":
            self.calculate()
        elif token == "AC":
            self.clear_expression()
        elif token == "⌫":
            self.entry.delete(max(0, len(self.entry.get()) - 1), tk.END)
        elif token == "MC":
            self.engine.memory = 0.0
        elif token == "MR":
            self._insert(str(self.engine.memory))
        elif token == "M+":
            try:
                self.engine.memory += float(self.result_label.cget("text").replace(" ", ""))
            except ValueError:
                pass
        else:
            mapping = {
                "sin": "sin(", "cos": "cos(", "tan": "tan(", "ln": "ln(",
                "log": "log(", "√": "sqrt(", "π": "pi", "e": "e",
            }
            self._insert(mapping.get(token, token))

    def _insert(self, value: str) -> None:
        self.entry.insert(self.entry.index(tk.INSERT), value)
        self.entry.focus_set()

    def clear_expression(self) -> None:
        self.entry.delete(0, tk.END)
        self.result_label.configure(text="0", text_color=self.theme["text"])

    def calculate(self) -> None:
        expression = self.entry.get()
        try:
            result = self.engine.calculate(expression)
            formatted = self.engine.format_result(result)
            self.history.add(expression, formatted)
            self._animate_result(formatted)
            self.refresh_history()
        except CalculatorError as exc:
            self.result_label.configure(text=str(exc), text_color=self.theme["danger"])

    def _animate_result(self, text: str, step: int = 0) -> None:
        colors = [self.theme["accent2"], self.theme["accent"], self.theme["text"]]
        sizes = [30, 42, 38]
        self.result_label.configure(
            text=text, text_color=colors[min(step, 2)],
            font=ctk.CTkFont("Consolas", sizes[min(step, 2)], "bold"),
        )
        if step < 2:
            self.after(80, lambda: self._animate_result(text, step + 1))

    def refresh_history(self) -> None:
        if hasattr(self, "quick_history"):
            for child in self.quick_history.winfo_children():
                child.destroy()
            for item in self.history.get_last(5):
                button = ctk.CTkButton(
                    self.quick_history,
                    text=f"{item['expression']}  =  {item['result']}",
                    anchor="w", height=34, fg_color="transparent",
                    hover_color=self.theme["card"], text_color=self.theme["muted"],
                    command=lambda expression=item["expression"]: self._reuse(expression),
                )
                button.pack(fill="x", pady=2)
        if hasattr(self, "history_frame"):
            for child in self.history_frame.winfo_children():
                child.destroy()
            items = self.history.get_last(200)
            if not items:
                ctk.CTkLabel(
                    self.history_frame, text="Historie je zatím prázdná.",
                    text_color=self.theme["muted"],
                ).grid(row=0, column=0, pady=50)
            for row, item in enumerate(items):
                line = ctk.CTkFrame(
                    self.history_frame, fg_color=self.theme["panel"], corner_radius=12
                )
                line.grid(row=row, column=0, sticky="ew", padx=8, pady=4)
                line.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    line, text=item["expression"], anchor="w", text_color=self.theme["muted"]
                ).grid(row=0, column=0, sticky="ew", padx=14, pady=(8, 0))
                ctk.CTkLabel(
                    line, text=f"= {item['result']}", anchor="w",
                    text_color=self.theme["accent"], font=ctk.CTkFont("Consolas", 17, "bold"),
                ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))
                ctk.CTkLabel(
                    line, text=item.get("category", "Výpočet"),
                    text_color=self.theme["muted"], font=ctk.CTkFont(size=10),
                ).grid(row=0, column=1, rowspan=2, padx=14)

    def _reuse(self, expression: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, expression)
        self.entry.focus_set()

    def plot_function(self) -> None:
        try:
            import numpy as np
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except ImportError:
            messagebox.showerror("Chybí závislost", "Nainstaluj matplotlib a numpy.")
            return
        try:
            minimum, maximum = float(self.x_min.get()), float(self.x_max.get())
            if minimum >= maximum:
                raise ValueError
            xs = np.linspace(minimum, maximum, 800)
            ys = []
            for x in xs:
                try:
                    value = float(self.engine.calculate(self.graph_expression.get(), {"x": float(x)}))
                    ys.append(value if math.isfinite(value) and abs(value) < 1e8 else np.nan)
                except CalculatorError:
                    ys.append(np.nan)
            if all(np.isnan(value) for value in ys):
                raise CalculatorError("Funkci nelze v tomto rozsahu vykreslit.")
        except (ValueError, CalculatorError) as exc:
            messagebox.showerror("Graf", str(exc) or "Zkontroluj rozsah osy X.")
            return

        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
        self.graph_placeholder.grid_remove()
        figure = Figure(figsize=(8, 5), dpi=100, facecolor=self.theme["plot"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(self.theme["plot"])
        axis.plot(xs, ys, color=self.theme["accent"], linewidth=2.2)
        axis.axhline(0, color=self.theme["muted"], linewidth=.8)
        axis.axvline(0, color=self.theme["muted"], linewidth=.8)
        axis.grid(True, color=self.theme["grid"], alpha=.55)
        axis.tick_params(colors=self.theme["muted"])
        for spine in axis.spines.values():
            spine.set_color(self.theme["grid"])
        axis.set_title(f"f(x) = {self.graph_expression.get()}", color=self.theme["text"], pad=14)
        figure.tight_layout()
        self.graph_canvas = FigureCanvasTkAgg(figure, master=self.graph_host)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.history.add(self.graph_expression.get(), f"x ∈ ⟨{minimum}; {maximum}⟩", "Graf")

    def convert_currency(self) -> None:
        try:
            value = float(self.currency_value.get().replace(",", "."))
        except ValueError:
            self.currency_result.configure(text="Neplatná částka", text_color=self.theme["danger"])
            return
        self.currency_result.configure(text="Načítám…", text_color=self.theme["muted"])

        def worker() -> None:
            result, status = self.currency.convert(
                value, self.currency_from.get(), self.currency_to.get()
            )
            self.after(0, lambda: self._currency_done(value, result, status))

        threading.Thread(target=worker, daemon=True).start()

    def _currency_done(self, value: float, result: float, status: str) -> None:
        text = f"{result:,.2f} {self.currency_to.get()}".replace(",", " ")
        self.currency_result.configure(text=text, text_color=self.theme["accent"])
        self.currency_status.configure(text=status)
        expression = f"{value:g} {self.currency_from.get()} → {self.currency_to.get()}"
        self.history.add(expression, text, "Měny")

    def _update_unit_choices(self, category: str) -> None:
        values = list(TEMPERATURES if category == "Teplota" else UNITS[category])
        self.unit_from.configure(values=values)
        self.unit_to.configure(values=values)
        self.unit_from.set(values[0])
        self.unit_to.set(values[1])

    def convert_units(self) -> None:
        try:
            value = float(self.unit_value.get().replace(",", "."))
            result = convert_unit(
                self.unit_category.get(), value, self.unit_from.get(), self.unit_to.get()
            )
            text = f"{result:,.8g} {self.unit_to.get()}".replace(",", " ")
            self.unit_result.configure(text=text, text_color=self.theme["accent"])
            expression = f"{value:g} {self.unit_from.get()} → {self.unit_to.get()}"
            self.history.add(expression, text, "Jednotky")
        except (ValueError, KeyError):
            self.unit_result.configure(text="Neplatná hodnota", text_color=self.theme["danger"])

    def export_history(self) -> None:
        target = filedialog.asksaveasfilename(
            title="Export historie", defaultextension=".csv",
            filetypes=[("CSV soubor", "*.csv")], initialfile="nexus-calc-history.csv",
        )
        if target:
            self.history.export_csv(target)
            messagebox.showinfo("Export", "Historie byla úspěšně exportována.")

    def clear_history(self) -> None:
        if messagebox.askyesno("Vymazat historii", "Opravdu chceš smazat všechny záznamy?"):
            self.history.clear()
            self.refresh_history()

    def refresh_statistics(self) -> None:
        stats = self.history.statistics()
        categories = stats["categories"]
        favorite = categories.most_common(1)[0][0] if categories else "—"
        self.stat_labels["total"].configure(text=str(stats["total"]))
        self.stat_labels["today"].configure(text=str(stats["today"]))
        self.stat_labels["favorite"].configure(text=favorite)
        for child in self.stats_detail.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.stats_detail, text="Rozložení aktivit", text_color=self.theme["text"],
            font=ctk.CTkFont("Segoe UI", 20, "bold"),
        ).pack(anchor="w", padx=25, pady=(22, 14))
        total = max(1, int(stats["total"]))
        for name in ("Výpočet", "Graf", "Měny", "Jednotky"):
            row = ctk.CTkFrame(self.stats_detail, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=6)
            count = categories.get(name, 0)
            ctk.CTkLabel(row, text=name, width=100, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(
                row, progress_color=self.theme["accent"], fg_color=self.theme["panel"]
            )
            bar.pack(side="left", fill="x", expand=True, padx=15)
            bar.set(count / total)
            ctk.CTkLabel(row, text=str(count), width=40).pack(side="right")

    def apply_theme(self, name: str) -> None:
        self.theme_name = name
        self.theme = THEMES[name]
        ctk.set_appearance_mode("light" if name == "Light" else "dark")
        # Rebuilding guarantees that every custom glass color is updated consistently.
        for child in self.winfo_children():
            child.destroy()
        self.pages.clear()
        self.nav_buttons.clear()
        self.graph_canvas = None
        self.configure(fg_color=self.theme["bg"])
        self._build_app()

    def _set_angle_mode(self, mode: str) -> None:
        self.engine.angle_mode = mode

    def _toggle_sound(self) -> None:
        self.sound_enabled = bool(self.sound_switch.get())

    def _click_sound(self) -> None:
        if not self.sound_enabled:
            return
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
        except (ImportError, RuntimeError):
            self.bell()
