from __future__ import annotations

import colorsys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from ._color import normalize_hex
from ._palette import Palette
from ._png import save_palette_png
from ._presets import list_presets, preset_label, preset_size

COLORBLIND_OPTIONS = {
    "None": None,
    "Protanopia": "protanopia",
    "Deuteranopia": "deuteranopia",
    "Tritanopia": "tritanopia",
    "Achromatopsia": "achromatopsia",
}

BACKGROUND_OPTIONS = {
    "White": "white",
    "Black": "black",
    "Light": "light",
    "Dark": "dark",
}

PRESET_OPTIONS = {"None": None}
PRESET_OPTIONS.update({preset_label(name): name for name in list_presets()})

PICKER_SIZE = 180
HUE_BAR_WIDTH = 26
PICKER_STEP = 3


def preset_palette_state(
    preset_name: str,
    n: int,
    mode: str,
    colorblind: str | None,
    background: str = "white",
) -> tuple[list[str], list[bool]]:
    colors = Palette(mode=mode, colorblind=colorblind, background=background).preset(preset_name, n=n)
    locked_count = min(preset_size(preset_name), len(colors))
    locked = [index < locked_count for index in range(len(colors))]
    return colors, locked


class PaletteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Paper Palette")
        self.geometry("900x560")
        self.resizable(False, False)

        self.colors: list[str | None] = []
        self.locked: list[bool] = []
        self.swatches: list[tk.Frame] = []
        self.labels: list[tk.Label] = []
        self.lock_labels: list[tk.Label] = []
        self._click_job: str | None = None

        self.n_var = tk.IntVar(value=6)
        self.mode_var = tk.StringVar(value="aesthetic")
        self.colorblind_var = tk.StringVar(value="None")
        self.background_var = tk.StringVar(value="White")
        self.preset_var = tk.StringVar(value="None")
        self.status_var = tk.StringVar(value="Set n, roll the dice, click to lock, double-click to edit HEX.")

        self._build_controls()
        self._build_swatch_area()
        self._set_count()

    def _build_controls(self) -> None:
        controls = tk.Frame(self, padx=16, pady=14)
        controls.pack(fill=tk.X)

        tk.Label(controls, text="n").grid(row=0, column=0, sticky="w")
        n_spin = tk.Spinbox(
            controls,
            from_=1,
            to=24,
            textvariable=self.n_var,
            width=5,
            command=self._set_count,
        )
        n_spin.grid(row=0, column=1, padx=(6, 18), sticky="w")
        n_spin.bind("<Return>", lambda _event: self._set_count())
        n_spin.bind("<FocusOut>", lambda _event: self._set_count())

        tk.Label(controls, text="mode").grid(row=0, column=2, sticky="w")
        tk.OptionMenu(controls, self.mode_var, "aesthetic", "categorical").grid(
            row=0,
            column=3,
            padx=(6, 18),
            sticky="w",
        )

        tk.Label(controls, text="colorblind").grid(row=0, column=4, sticky="w")
        tk.OptionMenu(controls, self.colorblind_var, *COLORBLIND_OPTIONS).grid(
            row=0,
            column=5,
            padx=(6, 18),
            sticky="w",
        )

        tk.Button(controls, text="🎲", width=4, command=self.roll).grid(row=0, column=6, padx=(0, 8))

        tk.Label(controls, text="background").grid(row=0, column=7, sticky="w")
        tk.OptionMenu(controls, self.background_var, *BACKGROUND_OPTIONS).grid(
            row=0,
            column=8,
            padx=(6, 0),
            sticky="w",
        )

        tk.Label(controls, text="preset").grid(row=1, column=0, pady=(10, 0), sticky="w")
        tk.OptionMenu(controls, self.preset_var, *PRESET_OPTIONS).grid(
            row=1,
            column=1,
            columnspan=3,
            padx=(6, 18),
            pady=(10, 0),
            sticky="w",
        )
        tk.Button(controls, text="Apply Preset", command=self.apply_preset).grid(
            row=1,
            column=4,
            columnspan=2,
            pady=(10, 0),
            sticky="w",
        )
        tk.Button(controls, text="Save", command=self.save_png).grid(row=1, column=6, padx=(0, 8), pady=(10, 0))
        tk.Button(controls, text="Copy Python Array", command=self.copy_array).grid(
            row=1,
            column=7,
            columnspan=2,
            pady=(10, 0),
            sticky="w",
        )

        controls.columnconfigure(9, weight=1)
        tk.Label(controls, textvariable=self.status_var, anchor="e").grid(
            row=1,
            column=9,
            padx=(14, 0),
            pady=(10, 0),
            sticky="ew",
        )

    def _build_swatch_area(self) -> None:
        self.swatch_area = tk.Frame(self, padx=16, pady=10)
        self.swatch_area.pack(fill=tk.BOTH, expand=True)

    def _set_count(self) -> None:
        try:
            count = int(self.n_var.get())
        except (tk.TclError, ValueError):
            count = len(self.colors) or 1

        count = max(1, min(24, count))
        self.n_var.set(count)

        current = len(self.colors)
        if count > current:
            self.colors.extend([None] * (count - current))
            self.locked.extend([False] * (count - current))
        elif count < current:
            self.colors = self.colors[:count]
            self.locked = self.locked[:count]

        self._render_swatches()

    def _render_swatches(self) -> None:
        for child in self.swatch_area.winfo_children():
            child.destroy()
        self.swatches.clear()
        self.labels.clear()
        self.lock_labels.clear()

        count = len(self.colors)
        columns = 4 if count <= 12 else 6
        for index in range(count):
            wrapper = tk.Frame(self.swatch_area, padx=6, pady=6)
            wrapper.grid(row=index // columns, column=index % columns, sticky="nsew")

            swatch = tk.Frame(
                wrapper,
                width=150,
                height=92,
                bg=self.colors[index] or "#F4F4F4",
                highlightthickness=2,
                highlightbackground="#111111" if self.locked[index] else "#D7D7D7",
                cursor="hand2",
            )
            swatch.pack(fill=tk.BOTH, expand=True)
            swatch.pack_propagate(False)
            swatch.bind("<Button-1>", lambda _event, i=index: self.schedule_toggle_lock(i))
            swatch.bind("<Double-Button-1>", lambda _event, i=index: self.cancel_toggle_and_edit(i))

            code_label = tk.Label(
                swatch,
                text=self.colors[index] or "",
                bg=self.colors[index] or "#F4F4F4",
                fg=self._text_color(self.colors[index]),
                font=("Menlo", 13),
            )
            code_label.pack(expand=True)
            code_label.bind("<Button-1>", lambda _event, i=index: self.schedule_toggle_lock(i))
            code_label.bind("<Double-Button-1>", lambda _event, i=index: self.cancel_toggle_and_edit(i))

            lock_label = tk.Label(
                swatch,
                text="LOCKED" if self.locked[index] else "",
                bg=self.colors[index] or "#F4F4F4",
                fg=self._text_color(self.colors[index]),
                font=("Menlo", 9),
            )
            lock_label.pack(side=tk.BOTTOM, pady=(0, 8))

            self.swatches.append(swatch)
            self.labels.append(code_label)
            self.lock_labels.append(lock_label)

        for column in range(columns):
            self.swatch_area.columnconfigure(column, weight=1)
        for row in range((count + columns - 1) // columns):
            self.swatch_area.rowconfigure(row, weight=1)

    def roll(self) -> None:
        self._set_count()
        locked_colors = [color for color, locked in zip(self.colors, self.locked) if locked and color]

        try:
            generated = Palette(
                mode=self.mode_var.get(),
                colorblind=COLORBLIND_OPTIONS[self.colorblind_var.get()],
                background=BACKGROUND_OPTIONS[self.background_var.get()],
            ).generate(len(self.colors), seed_colors=locked_colors)
        except ValueError as exc:
            messagebox.showerror("Palette error", str(exc), parent=self)
            return

        new_colors = generated[len(locked_colors) :]
        next_index = 0
        for index, locked in enumerate(self.locked):
            if locked and self.colors[index]:
                continue
            self.colors[index] = new_colors[next_index]
            next_index += 1

        self.status_var.set("Generated a new palette.")
        self._render_swatches()

    def apply_preset(self) -> None:
        preset_name = PRESET_OPTIONS[self.preset_var.get()]
        if preset_name is None:
            messagebox.showinfo("Preset", "Choose a preset first.", parent=self)
            return

        self._set_count()
        try:
            colors, locked = preset_palette_state(
                preset_name=preset_name,
                n=len(self.colors),
                mode=self.mode_var.get(),
                colorblind=COLORBLIND_OPTIONS[self.colorblind_var.get()],
                background=BACKGROUND_OPTIONS[self.background_var.get()],
            )
        except ValueError as exc:
            messagebox.showerror("Preset", str(exc), parent=self)
            return

        self.colors = colors
        self.locked = locked
        self.n_var.set(len(colors))
        locked_count = sum(locked)
        self.status_var.set(f"Applied preset: {self.preset_var.get()}; locked {locked_count} preset colors.")
        self._render_swatches()

    def toggle_lock(self, index: int) -> None:
        if not self.colors[index]:
            self.status_var.set("Roll first or double-click to enter a HEX color.")
            return
        self.locked[index] = not self.locked[index]
        state = "locked" if self.locked[index] else "unlocked"
        self.status_var.set(f"{self.colors[index]} {state}.")
        self._render_swatches()

    def schedule_toggle_lock(self, index: int) -> None:
        if self._click_job is not None:
            self.after_cancel(self._click_job)
        self._click_job = self.after(220, lambda: self._run_scheduled_toggle(index))

    def _run_scheduled_toggle(self, index: int) -> None:
        self._click_job = None
        self.toggle_lock(index)

    def cancel_toggle_and_edit(self, index: int) -> None:
        if self._click_job is not None:
            self.after_cancel(self._click_job)
            self._click_job = None
        self.open_hex_editor(index)

    def open_hex_editor(self, index: int) -> None:
        window = tk.Toplevel(self)
        window.title(f"Edit color {index + 1}")
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()

        initial_color = normalize_hex(self.colors[index] or "#1E88E5")
        hue, saturation, value_level = self._hex_to_hsv(initial_color)
        picker_state = {"hue": hue, "saturation": saturation, "value": value_level}
        syncing = {"active": False}

        value = tk.StringVar(value=initial_color)

        body = tk.Frame(window, padx=16, pady=16)
        body.grid(row=0, column=0, sticky="nsew")

        sv_canvas = tk.Canvas(
            body,
            width=PICKER_SIZE,
            height=PICKER_SIZE,
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            cursor="crosshair",
        )
        sv_canvas.grid(row=0, column=0, rowspan=4, sticky="n")

        hue_canvas = tk.Canvas(
            body,
            width=HUE_BAR_WIDTH,
            height=PICKER_SIZE,
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            cursor="sb_v_double_arrow",
        )
        hue_canvas.grid(row=0, column=1, rowspan=4, padx=(10, 16), sticky="n")

        preview = tk.Frame(
            body,
            width=160,
            height=72,
            bg=value.get(),
            highlightthickness=1,
            highlightbackground="#B8B8B8",
        )
        preview.grid(row=0, column=2, columnspan=2, sticky="ew")
        preview.grid_propagate(False)

        tk.Label(body, text="HEX").grid(row=1, column=2, pady=(18, 6), sticky="w")
        entry = tk.Entry(body, textvariable=value, width=14, font=("Menlo", 13))
        entry.grid(row=1, column=3, padx=(8, 0), pady=(18, 6), sticky="w")

        error_var = tk.StringVar(value="")
        tk.Label(body, textvariable=error_var, fg="#B00020").grid(row=2, column=2, columnspan=2, sticky="w")

        def draw_hue_bar() -> None:
            hue_canvas.delete("all")
            for y in range(PICKER_SIZE):
                color = self._hsv_to_hex(y / (PICKER_SIZE - 1), 1.0, 1.0)
                hue_canvas.create_line(0, y, HUE_BAR_WIDTH, y, fill=color)
            draw_hue_marker()

        def draw_sv_plane() -> None:
            sv_canvas.delete("all")
            hue_value = picker_state["hue"]
            for x in range(0, PICKER_SIZE, PICKER_STEP):
                saturation_value = x / (PICKER_SIZE - 1)
                for y in range(0, PICKER_SIZE, PICKER_STEP):
                    brightness_value = 1.0 - (y / (PICKER_SIZE - 1))
                    color = self._hsv_to_hex(hue_value, saturation_value, brightness_value)
                    sv_canvas.create_rectangle(
                        x,
                        y,
                        x + PICKER_STEP,
                        y + PICKER_STEP,
                        fill=color,
                        outline=color,
                    )
            draw_sv_marker()

        def draw_sv_marker() -> None:
            sv_canvas.delete("marker")
            x = picker_state["saturation"] * (PICKER_SIZE - 1)
            y = (1.0 - picker_state["value"]) * (PICKER_SIZE - 1)
            radius = 6
            sv_canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline="#FFFFFF",
                width=2,
                tags="marker",
            )
            sv_canvas.create_oval(
                x - radius - 1,
                y - radius - 1,
                x + radius + 1,
                y + radius + 1,
                outline="#111111",
                width=1,
                tags="marker",
            )

        def draw_hue_marker() -> None:
            hue_canvas.delete("marker")
            y = picker_state["hue"] * (PICKER_SIZE - 1)
            hue_canvas.create_rectangle(
                0,
                y - 3,
                HUE_BAR_WIDTH,
                y + 3,
                outline="#111111",
                width=2,
                tags="marker",
            )
            hue_canvas.create_rectangle(
                2,
                y - 1,
                HUE_BAR_WIDTH - 2,
                y + 1,
                outline="#FFFFFF",
                width=1,
                tags="marker",
            )

        def set_value_from_picker() -> None:
            syncing["active"] = True
            value.set(
                self._hsv_to_hex(
                    picker_state["hue"],
                    picker_state["saturation"],
                    picker_state["value"],
                )
            )
            syncing["active"] = False
            refresh_preview()

        def refresh_preview(*_args: object) -> None:
            try:
                normalized = normalize_hex(value.get())
            except ValueError:
                error_var.set("Invalid HEX color.")
                return

            preview.configure(bg=normalized)
            error_var.set("")
            if syncing["active"]:
                return
            new_hue, new_saturation, new_value = self._hex_to_hsv(normalized)
            picker_state["hue"] = new_hue
            picker_state["saturation"] = new_saturation
            picker_state["value"] = new_value
            draw_sv_plane()
            draw_hue_marker()

        def select_sv(event: tk.Event) -> None:
            x = self._clamp(float(event.x), 0.0, PICKER_SIZE - 1)
            y = self._clamp(float(event.y), 0.0, PICKER_SIZE - 1)
            picker_state["saturation"] = x / (PICKER_SIZE - 1)
            picker_state["value"] = 1.0 - (y / (PICKER_SIZE - 1))
            draw_sv_marker()
            set_value_from_picker()

        def select_hue(event: tk.Event) -> None:
            y = self._clamp(float(event.y), 0.0, PICKER_SIZE - 1)
            picker_state["hue"] = y / (PICKER_SIZE - 1)
            draw_sv_plane()
            draw_hue_marker()
            set_value_from_picker()

        def apply() -> None:
            try:
                normalized = normalize_hex(value.get())
            except ValueError as exc:
                error_var.set(str(exc))
                return
            self.colors[index] = normalized
            self.locked[index] = True
            self.status_var.set(f"{normalized} set and locked.")
            self._render_swatches()
            window.destroy()

        def clear() -> None:
            self.colors[index] = None
            self.locked[index] = False
            self.status_var.set(f"Color {index + 1} cleared.")
            self._render_swatches()
            window.destroy()

        value.trace_add("write", refresh_preview)
        sv_canvas.bind("<Button-1>", select_sv)
        sv_canvas.bind("<B1-Motion>", select_sv)
        hue_canvas.bind("<Button-1>", select_hue)
        hue_canvas.bind("<B1-Motion>", select_hue)

        tk.Button(body, text="Apply", command=apply).grid(
            row=3,
            column=2,
            padx=(0, 8),
            pady=(22, 0),
            sticky="ew",
        )
        tk.Button(body, text="Clear", command=clear).grid(
            row=3,
            column=3,
            padx=(0, 0),
            pady=(22, 0),
            sticky="ew",
        )
        tk.Button(body, text="Cancel", command=window.destroy).grid(
            row=4,
            column=2,
            columnspan=2,
            pady=(8, 0),
            sticky="ew",
        )
        entry.focus_set()
        entry.select_range(0, tk.END)
        entry.bind("<Return>", lambda _event: apply())
        draw_hue_bar()
        draw_sv_plane()
        refresh_preview()

    def copy_array(self) -> None:
        colors = [color for color in self.colors if color]
        array_text = "[" + ", ".join(repr(color) for color in colors) + "]"
        self.clipboard_clear()
        self.clipboard_append(array_text)
        self.status_var.set(f"Copied {len(colors)} colors as a Python array string.")

    def save_png(self) -> None:
        colors = [color for color in self.colors if color]
        if not colors:
            messagebox.showinfo("Save palette", "Roll a palette or enter at least one HEX color first.", parent=self)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path.cwd() / "outputs" / f"palette_{timestamp}.png"
        try:
            saved_path = save_palette_png(colors, output)
        except ValueError as exc:
            messagebox.showerror("Save palette", str(exc), parent=self)
            return

        self.status_var.set(f"Saved {saved_path}.")

    @staticmethod
    def _text_color(hex_color: str | None) -> str:
        if not hex_color:
            return "#333333"
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:7], 16)
        luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255.0
        return "#111111" if luminance > 0.58 else "#FFFFFF"

    @staticmethod
    def _hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
        normalized = normalize_hex(hex_color)
        red = int(normalized[1:3], 16) / 255.0
        green = int(normalized[3:5], 16) / 255.0
        blue = int(normalized[5:7], 16) / 255.0
        return colorsys.rgb_to_hsv(red, green, blue)

    @staticmethod
    def _hsv_to_hex(hue: float, saturation: float, value: float) -> str:
        red, green, blue = colorsys.hsv_to_rgb(
            PaletteApp._clamp_unit(hue),
            PaletteApp._clamp_unit(saturation),
            PaletteApp._clamp_unit(value),
        )
        return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"

    @staticmethod
    def _clamp_unit(value: float) -> float:
        return PaletteApp._clamp(value, 0.0, 1.0)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))


def main() -> None:
    app = PaletteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
