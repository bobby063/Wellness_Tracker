import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar
import os
import sys

# Ensure src/ is on the path so wellness_data can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wellness_data

# Paths relative to the project root (one level up from src/)
_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
_DATA_DIR = os.path.join(_PROJECT_ROOT, 'data')

# ── Design tokens ──────────────────────────────────────────────────
FONT    = "Segoe UI"            # modern Windows system font
BG      = "#F5F7FA"             # off-white page background
CARD    = "#FFFFFF"             # card surface
BORDER  = "#E5E7EB"             # subtle card border
PRIMARY = "#8E7CC3"             # muted purple accent (matches mood)
SECOND  = "#2A9D8F"             # soft teal accent (matches sleep)
TEXT1   = "#1F2937"             # near-black primary text
TEXT2   = "#6B7280"             # muted secondary text
MOOD_C  = "#8E7CC3"             # mood slider fill colour (muted purple)
ENERGY_C = "#E76F51"            # energy slider fill colour (warm coral)
SLEEP_C = "#2A9D8F"             # sleep slider fill colour (soft teal)
SUCCESS = "#059669"             # green status text
HOVER_P = "#7060A8"             # primary button hover (darker purple)
HOVER_S = "#6344DB"             # secondary button hover
# ───────────────────────────────────────────────────────────────────


# ── Custom canvas slider ───────────────────────────────────────────
class ModernSlider(tk.Frame):
    """A canvas-drawn slider that looks modern —
       thin rounded track, accent-coloured fill, round thumb,
       and a large live-updating value label above it."""

    TRACK_H      = 4
    THUMB_R      = 8
    CANVAS_PAD_X = 12          # horizontal padding inside the canvas

    def __init__(self, master, from_=0, to=10, default=5,
                 accent="#4F8EF7", length=360, variable=None, **kw):
        super().__init__(master, bg=CARD, **kw)
        self.lo = from_
        self.hi = to
        self.accent = accent
        self.slider_len = length
        self.var = variable if variable else tk.IntVar(value=default)
        self.var.set(default)

        # Value label — large, coloured, updates as slide moves
        self.val_label = tk.Label(self, text=str(default),
                                  font=(FONT, 13, "bold"),
                                  fg=accent, bg=CARD)
        self.val_label.pack(pady=(0, 0))

        # Canvas that draws the track + thumb
        self.canvas_w = length + self.CANVAS_PAD_X * 2
        self.canvas_h = self.THUMB_R * 2 + 2
        self.c = tk.Canvas(self, width=self.canvas_w, height=self.canvas_h,
                           bg=CARD, highlightthickness=0)
        self.c.pack()

        # Tick labels row (1 2 3 … 10)
        tick_frame = tk.Frame(self, bg=CARD)
        tick_frame.pack(fill="x", padx=self.CANVAS_PAD_X)
        for i in range(self.lo, self.hi + 1):
            tk.Label(tick_frame, text=str(i), font=(FONT, 6),
                     fg=TEXT2, bg=CARD).pack(side="left", expand=True)

        # Draw + bind
        self.c.bind("<Configure>", lambda e: self._draw())
        self.c.bind("<Button-1>", self._on_click)
        self.c.bind("<B1-Motion>", self._on_click)
        self.var.trace_add("write", lambda *_: self._draw())
        self._draw()

    # -- internal helpers ---------------------------------------------------

    def _val_to_x(self, val):
        ratio = (val - self.lo) / max(self.hi - self.lo, 1)
        return self.CANVAS_PAD_X + ratio * self.slider_len

    def _x_to_val(self, x):
        ratio = (x - self.CANVAS_PAD_X) / self.slider_len
        ratio = max(0.0, min(1.0, ratio))
        return round(self.lo + ratio * (self.hi - self.lo))

    def _draw(self):
        c = self.c
        c.delete("all")
        cy = self.canvas_h // 2
        x0 = self.CANVAS_PAD_X
        x1 = self.CANVAS_PAD_X + self.slider_len
        r  = self.TRACK_H // 2
        val = self.var.get()
        xv = self._val_to_x(val)

        # background track (rounded rectangle approximated with ovals + rect)
        c.create_oval(x0, cy - r, x0 + r * 2, cy + r, fill=BORDER, outline="")
        c.create_rectangle(x0 + r, cy - r, x1 - r, cy + r, fill=BORDER, outline="")
        c.create_oval(x1 - r * 2, cy - r, x1, cy + r, fill=BORDER, outline="")

        # filled portion (accent colour)
        if xv > x0 + r:
            c.create_oval(x0, cy - r, x0 + r * 2, cy + r, fill=self.accent, outline="")
            c.create_rectangle(x0 + r, cy - r, min(xv, x1 - r), cy + r,
                               fill=self.accent, outline="")
            if xv >= x1 - r:
                c.create_oval(x1 - r * 2, cy - r, x1, cy + r,
                              fill=self.accent, outline="")

        # thumb (white circle with accent ring)
        tr = self.THUMB_R
        c.create_oval(xv - tr, cy - tr, xv + tr, cy + tr,
                      fill="#FFFFFF", outline=self.accent, width=2.5)

        self.val_label.config(text=str(val))

    def _on_click(self, event):
        new = self._x_to_val(event.x)
        self.var.set(new)


# ── Hover-capable rounded button ──────────────────────────────────
class RoundButton(tk.Frame):
    """Frame wrapping a Canvas-drawn rounded-rect button with hover."""

    def __init__(self, master, text="", command=None,
                 bg_color=PRIMARY, hover_color=HOVER_P,
                 fg="white", width=160, height=42, radius=12, **kw):
        super().__init__(master, bg=master.cget("bg"), **kw)
        self._bg_col = bg_color
        self._hover = hover_color
        self._fg = fg
        self._cmd = command
        self._bw = width
        self._bh = height
        self._r = radius
        self._text = text
        self.c = tk.Canvas(self, width=width, height=height,
                           bg=master.cget("bg"), highlightthickness=0)
        self.c.pack()
        self._draw(self._bg_col)
        self.c.bind("<Enter>", lambda e: self._draw(self._hover))
        self.c.bind("<Leave>", lambda e: self._draw(self._bg_col))
        self.c.bind("<Button-1>", lambda e: self._cmd() if self._cmd else None)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return self.c.create_polygon(pts, smooth=True, **kw)

    def _draw(self, fill):
        self.c.delete("all")
        self._round_rect(1, 1, self._bw - 1, self._bh - 1, self._r,
                         fill=fill, outline="")
        self.c.create_text(self._bw // 2, self._bh // 2, text=self._text,
                           fill=self._fg, font=(FONT, 11, "bold"))


# ── Card helper ───────────────────────────────────────────────────
def make_card(parent, **pack_kw):
    """Return a Frame styled as a white card with a thin border."""
    card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                    highlightthickness=1)
    card.pack(fill="x", padx=28, pady=3, **pack_kw)
    return card


# ── Main application class ────────────────────────────────────────
class WellnessTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Wellness Tracker")
        self.root.geometry("520x580")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.current_day = datetime.now().day

        self._setup_styles()
        self.create_widgets()
        self.update_data_file()
        self.load_existing_data()

    # ── ttk theme / style overrides ───────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground="#F9FAFB", background="#F9FAFB",
                        foreground=TEXT1, arrowcolor=TEXT2,
                        borderwidth=1, relief="flat",
                        padding=4)
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#F9FAFB")],
                  selectbackground=[("readonly", "#F9FAFB")],
                  selectforeground=[("readonly", TEXT1)])

    # ── Build the UI ──────────────────────────────────────────────
    def create_widgets(self):
        # Scrollable area (future-proof for smaller screens)
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True)

        # ── Header ───────────────────────────────────────────────
        tk.Label(container, text="Daily Wellness Tracker",
                 font=(FONT, 16, "bold"), bg=BG, fg=TEXT1
                ).pack(pady=(4, 0))
        tk.Label(container, text="Log your daily mood, energy & sleep",
                 font=(FONT, 9), bg=BG, fg=TEXT2
                ).pack(pady=(0, 4))

        # ── Date card ────────────────────────────────────────────
        date_card = make_card(container)
        tk.Label(date_card, text="Select Date", font=(FONT, 10, "bold"),
                 bg=CARD, fg=TEXT1).pack(anchor="w", padx=16, pady=(8, 2))

        row1 = tk.Frame(date_card, bg=CARD)
        row1.pack(fill="x", padx=16, pady=(0, 2))

        tk.Label(row1, text="Month", font=(FONT, 9), bg=CARD, fg=TEXT2
                ).pack(side="left")
        self.month_var = tk.StringVar(value=str(self.current_month))
        self.month_combo = ttk.Combobox(row1, textvariable=self.month_var,
                                        values=[f"{i:02d}" for i in range(1, 13)],
                                        state="readonly", width=4)
        self.month_combo.pack(side="left", padx=(6, 16))
        self.month_combo.bind("<<ComboboxSelected>>", self.on_month_year_changed)

        tk.Label(row1, text="Year", font=(FONT, 9), bg=CARD, fg=TEXT2
                ).pack(side="left")
        self.year_var = tk.StringVar(value=str(self.current_year))
        self.year_combo = ttk.Combobox(row1, textvariable=self.year_var,
                                       values=[str(y) for y in range(self.current_year-5,
                                                                      self.current_year+6)],
                                       state="readonly", width=6)
        self.year_combo.pack(side="left", padx=(6, 16))
        self.year_combo.bind("<<ComboboxSelected>>", self.on_month_year_changed)

        tk.Label(row1, text="Day", font=(FONT, 9), bg=CARD, fg=TEXT2
                ).pack(side="left")
        self.day_var = tk.StringVar()
        self.day_combo = ttk.Combobox(row1, textvariable=self.day_var,
                                      values=self.get_days_in_month(),
                                      state="readonly", width=4)
        self.day_combo.pack(side="left", padx=(6, 0))
        self.day_combo.bind("<<ComboboxSelected>>", self.on_day_selected)
        self.day_var.set(f"{self.current_day:02d}")

        self.date_label = tk.Label(date_card, text="", font=(FONT, 9, "italic"),
                                   bg=CARD, fg=TEXT2)
        self.date_label.pack(anchor="w", padx=16, pady=(0, 6))

        # ── Mood card ────────────────────────────────────────────
        mood_card = make_card(container)
        tk.Label(mood_card, text="Mood", font=(FONT, 10, "bold"),
                 bg=CARD, fg=TEXT1).pack(anchor="w", padx=16, pady=(5, 0))
        tk.Label(mood_card, text="How is your mood today?",
                 font=(FONT, 8), bg=CARD, fg=TEXT2
                ).pack(anchor="w", padx=16, pady=(0, 0))

        self.score_var = tk.IntVar(value=5)
        self.mood_slider = ModernSlider(mood_card, from_=1, to=10, default=5,
                                        accent=MOOD_C, length=380,
                                        variable=self.score_var)
        self.mood_slider.pack(padx=12, pady=(0, 4))

        # ── Energy card ──────────────────────────────────────────
        energy_card = make_card(container)
        tk.Label(energy_card, text="Energy", font=(FONT, 11, "bold"),
                 bg=CARD, fg=TEXT1).pack(anchor="w", padx=16, pady=(5, 0))
        tk.Label(energy_card, text="How is your energy level?",
                 font=(FONT, 8), bg=CARD, fg=TEXT2
                ).pack(anchor="w", padx=16, pady=(0, 0))

        self.energy_var = tk.IntVar(value=5)
        self.energy_slider = ModernSlider(energy_card, from_=1, to=10, default=5,
                                          accent=ENERGY_C, length=380,
                                          variable=self.energy_var)
        self.energy_slider.pack(padx=12, pady=(0, 4))

        # ── Sleep card ───────────────────────────────────────────
        sleep_card = make_card(container)
        tk.Label(sleep_card, text="Sleep", font=(FONT, 10, "bold"),
                 bg=CARD, fg=TEXT1).pack(anchor="w", padx=16, pady=(5, 0))
        tk.Label(sleep_card, text="Hours of sleep last night",
                 font=(FONT, 8), bg=CARD, fg=TEXT2
                ).pack(anchor="w", padx=16, pady=(0, 0))

        self.sleep_var = tk.IntVar(value=7)
        self.sleep_slider = ModernSlider(sleep_card, from_=0, to=10, default=7,
                                         accent=SLEEP_C, length=380,
                                         variable=self.sleep_var)
        self.sleep_slider.pack(padx=12, pady=(0, 4))

        # ── Buttons ──────────────────────────────────────────────

        btn_row = tk.Frame(container, bg=BG)
        btn_row.pack(pady=(6, 2))

        RoundButton(btn_row, text="Save Score", command=self.save_score,
                    bg_color=PRIMARY, hover_color=HOVER_P,
                    width=174, height=36, radius=10).pack(side="left", padx=8)
        RoundButton(btn_row, text="View Chart", command=self.view_chart,
                    bg_color=SECOND, hover_color=HOVER_S,
                    width=174, height=36, radius=10).pack(side="left", padx=8)

        # ── Status label ─────────────────────────────────────────
        self.status_label = tk.Label(container, text="", font=(FONT, 9),
                                     bg=BG, fg=SUCCESS)
        self.status_label.pack(pady=(2, 6))

    def get_days_in_month(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            _, days = calendar.monthrange(year, month)
            return [f"{day:02d}" for day in range(1, days + 1)]
        except:
            return [f"{day:02d}" for day in range(1, 32)]

    def on_month_year_changed(self, event=None):
        self.day_combo['values'] = self.get_days_in_month()
        self.update_data_file()
        self.day_var.set('')
        self.date_label.config(text='')
        self.score_var.set(5)   # reset mood slider to default
        self.energy_var.set(5)  # reset energy slider to default
        self.sleep_var.set(7)   # reset sleep slider to default

    def update_data_file(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            wellness_data.DATA_FILE = os.path.join(_DATA_DIR, f'wellness_data_{year}_{month:02d}.csv')
            wellness_data.initialize_data_file()
        except:
            pass

    def on_day_selected(self, event):
        day = self.day_var.get()
        if day:
            try:
                year = int(self.year_var.get())
                month = int(self.month_var.get())
                date_str = f"{year}-{month:02d}-{day}"
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                month_name = date_obj.strftime("%B")
                self.date_label.config(text=f"{day_name}, {month_name} {int(day)}, {year}")

                data = wellness_data.load_data()
                existing_entry = data.get(date_str, {})
                existing_score = existing_entry.get('mood_score') if isinstance(existing_entry, dict) else existing_entry
                existing_energy = existing_entry.get('energy_score') if isinstance(existing_entry, dict) else None
                existing_sleep = existing_entry.get('sleep_hours') if isinstance(existing_entry, dict) else None
                # Load saved values into sliders, fall back to sensible defaults
                try:
                    self.score_var.set(int(float(existing_score)))
                except (TypeError, ValueError):
                    self.score_var.set(5)
                try:
                    self.energy_var.set(int(float(existing_energy)))
                except (TypeError, ValueError):
                    self.energy_var.set(5)
                try:
                    self.sleep_var.set(int(float(existing_sleep)))
                except (TypeError, ValueError):
                    self.sleep_var.set(7)
            except:
                self.date_label.config(text="Invalid date")

    def save_score(self):
        day = self.day_var.get()

        if not day:
            messagebox.showerror("Error", "Please select a day")
            return

        # Both sliders enforce valid ranges — read directly, no validation needed
        score_float = float(self.score_var.get())
        energy_float = float(self.energy_var.get())
        sleep_float = float(self.sleep_var.get())

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        date_str = f"{year}-{month:02d}-{day}"

        self.update_data_file()
        wellness_data.save_mood_score(date_str, str(score_float))
        wellness_data.save_energy_score(date_str, str(energy_float))
        wellness_data.save_sleep_hours(date_str, str(sleep_float))

        chart_ok = self.generate_chart_silent()
        if chart_ok:
            chart_filename = os.path.join(_PROJECT_ROOT, f"wellness_chart_{year}_{month:02d}.png")
            try:
                if os.path.exists(chart_filename):
                    os.startfile(chart_filename)
            except Exception as e:
                print(f"Could not open chart image: {e}")

        month_name = datetime(year, month, 1).strftime("%B")
        status = f"Saved: mood {int(score_float)}, energy {int(energy_float)}, sleep {int(sleep_float)}hrs — {month_name} {int(day)}"
        if not chart_ok:
            status += "  (chart failed — matplotlib missing?)"
        self.status_label.config(text=status)

    def generate_chart_silent(self):
        try:
            import wellness_chart
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            data_file = os.path.join(_DATA_DIR, f'wellness_data_{year}_{month:02d}.csv')
            wellness_chart.generate_chart(data_file, save_only=True)
            return True
        except Exception as e:
            print(f"Chart generation failed: {e}")
            return False

    def view_chart(self):
        try:
            import wellness_chart
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            data_file = os.path.join(_DATA_DIR, f'wellness_data_{year}_{month:02d}.csv')
            chart_path = wellness_chart.generate_chart(data_file, save_only=True)
            if os.path.exists(chart_path):
                os.startfile(chart_path)
            self.status_label.config(text="Chart displayed!")
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying chart: {str(e)}")

    def load_existing_data(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WellnessTrackerApp(root)
    root.mainloop()
