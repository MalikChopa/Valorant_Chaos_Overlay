import tkinter as tk
import customtkinter as ctk
import random
import ctypes
import os
import sys
import keyboard

# ==========================================
# FIX ANTI-CRASH POUR LE MODE --NOCONSOLE
# ==========================================
class NullWriter:
    def write(self, text): pass
    def flush(self): pass

if sys.stdout is None: sys.stdout = NullWriter()
if sys.stderr is None: sys.stderr = NullWriter()
# ==========================================

class ValorantChaosOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Chaos Overlay - Core")
        
        # --- CONFIGURATION DYNAMIQUE ---
        self.timer_interval = tk.IntVar(value=60) # Secondes
        self.gif_filename = "dance.gif"
        
        # États des malus
        self.malus_states = {
            "flashbang": tk.BooleanVar(value=True),
            "tunnel_vision": tk.BooleanVar(value=True),
            "hud_blocker": tk.BooleanVar(value=True),
            "fake_crosshair": tk.BooleanVar(value=True),
            "scanlines": tk.BooleanVar(value=True),
            "gif_dance": tk.BooleanVar(value=True),
            "fake_crash": tk.BooleanVar(value=True)
        }
        
        # Initialisation
        self.setup_overlay_window()
        self.load_gif_frames()
        
        # Raccourci clavier global pour ouvrir le menu Admin
        # Utilisation de root.after pour rester "Thread-Safe" avec Tkinter
        keyboard.add_hotkey('home', lambda: self.root.after(0, self.open_admin_panel))
        
        self.timer_id = None
        self.start_timer()

    # ==========================================
    # NOYAU & SYSTÈME
    # ==========================================
    def setup_overlay_window(self):
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        self.transparent_color = '#000001'
        self.root.config(bg=self.transparent_color)
        self.root.wm_attributes("-transparentcolor", self.transparent_color)
        
        self.make_click_through()
        
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, 
                                bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack()

    def make_click_through(self):
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_NOACTIVATE = 0x08000000 # Empêche de voler le focus de Valorant
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def get_resource_path(self, filename):
        try: base_path = sys._MEIPASS
        except Exception: base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, filename)

    def load_gif_frames(self):
        self.gif_frames = []
        gif_path = self.get_resource_path(self.gif_filename)
        if not os.path.exists(gif_path): return
        try:
            idx = 0
            while True:
                self.gif_frames.append(tk.PhotoImage(file=gif_path, format=f"gif -index {idx}"))
                idx += 1
        except tk.TclError: pass

    # ==========================================
    # PANNEAU D'ADMINISTRATION
    # ==========================================
    def open_admin_panel(self):
        if hasattr(self, 'admin_window') and self.admin_window.winfo_exists():
            self.admin_window.focus()
            return

        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Admin Panel - Valorant Chaos")
        self.admin_window.geometry("350x450")
        self.admin_window.wm_attributes("-topmost", True)
        self.admin_window.configure(padx=20, pady=20)
        self.admin_window.attributes('-alpha', 0.95)

        tk.Label(self.admin_window, text="⚙️ Paramètres", font=("Arial", 14, "bold")).pack(pady=(0, 15))

        frame_timer = tk.Frame(self.admin_window)
        frame_timer.pack(fill="x", pady=5)
        tk.Label(frame_timer, text="Fréquence (secondes) :").pack(side="left")
        tk.Entry(frame_timer, textvariable=self.timer_interval, width=5).pack(side="right")

        tk.Label(self.admin_window, text="Malus Actifs :", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))

        for malus_name, var in self.malus_states.items():
            ttk.Checkbutton(self.admin_window, text=malus_name.replace("_", " ").title(), variable=var).pack(anchor="w")

        ttk.Button(self.admin_window, text="Sauvegarder & Relancer", command=self.save_and_restart).pack(pady=20, fill="x")

    def save_and_restart(self):
        self.admin_window.destroy()
        self.start_timer()

    # ==========================================
    # LOGIQUE DE LA ROULETTE
    # ==========================================
    def start_timer(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        
        interval_ms = self.timer_interval.get() * 1000
        self.timer_id = self.root.after(interval_ms, self.trigger_malus)

    def trigger_malus(self):
        active_malus = [name for name, var in self.malus_states.items() if var.get()]
        if not active_malus: active_malus = ["rien"]
        self.start_roulette_ui(random.choice(active_malus), active_malus)

    def start_roulette_ui(self, final_choice, active_malus):
        self.roulette_items = []
        bg_width, bg_height = 350, 80
        y_pos = self.screen_height // 3
        
        bg = self.canvas.create_rectangle(20, y_pos, 20 + bg_width, y_pos + bg_height, fill="#1a1a1a", outline="#ff4655", width=3)
        self.roulette_items.append(bg)
        
        text_id = self.canvas.create_text(20 + (bg_width // 2), y_pos + (bg_height // 2), text="...", fill="white", font=("Arial", 22, "bold"), justify="center")
        self.roulette_items.append(text_id)
        self.animate_roulette(30, 50, text_id, final_choice, active_malus)

    def animate_roulette(self, spins_left, delay, text_id, final_choice, all_malus):
        if spins_left > 0:
            self.canvas.itemconfig(text_id, text=random.choice(all_malus).replace("_", " ").upper(), fill="#ece8e1")
            new_delay = delay + int(120 / spins_left) 
            self.root.after(new_delay, lambda: self.animate_roulette(spins_left - 1, new_delay, text_id, final_choice, all_malus))
        else:
            self.canvas.itemconfig(text_id, text=f">> {final_choice.replace('_', ' ').upper()} <<", fill="#ff4655")
            self.root.after(1500, lambda: self.execute_malus(final_choice))

    def execute_malus(self, choix):
        for item in self.roulette_items: self.canvas.delete(item)
        getattr(self, f"effect_{choix}", lambda: None)()
        self.start_timer()

    # ==========================================
    # 5. EFFETS VISUELS
    # ==========================================
    def effect_flashbang(self):
        flash = self.canvas.create_rectangle(0, 0, self.screen_width, self.screen_height, fill="white", outline="")
        self.root.after(2500, lambda: self.canvas.delete(flash))

    def effect_tunnel_vision(self):
        cx, cy, r = self.screen_width // 2, self.screen_height // 2, 300 
        rects = [
            self.canvas.create_rectangle(0, 0, self.screen_width, cy - r, fill="black", outline=""),
            self.canvas.create_rectangle(0, cy + r, self.screen_width, self.screen_height, fill="black", outline=""),
            self.canvas.create_rectangle(0, cy - r, cx - r, cy + r, fill="black", outline=""),
            self.canvas.create_rectangle(cx + r, cy - r, self.screen_width, cy + r, fill="black", outline="")
        ]
        self.root.after(8000, lambda: [self.canvas.delete(rect) for rect in rects])

    def effect_hud_blocker(self):
        rects = [
            self.canvas.create_rectangle(0, 0, self.screen_width * 0.20, self.screen_height * 0.30, fill="black", outline=""),
            self.canvas.create_rectangle(self.screen_width * 0.75, self.screen_height * 0.80, self.screen_width, self.screen_height, fill="black", outline=""),
            self.canvas.create_rectangle(self.screen_width * 0.25, self.screen_height * 0.85, self.screen_width * 0.45, self.screen_height, fill="black", outline="")
        ]
        self.root.after(12000, lambda: [self.canvas.delete(rect) for rect in rects])

    def effect_fake_crosshair(self):
        fx, fy, size, thick = (self.screen_width // 2) + 45, (self.screen_height // 2) - 40, 150, 8
        lines = [
            self.canvas.create_rectangle(fx - size, fy - thick//2, fx + size, fy + thick//2, fill="#00ff00", outline=""),
            self.canvas.create_rectangle(fx - thick//2, fy - size, fx + thick//2, fy + size, fill="#00ff00", outline="")
        ]
        self.root.after(10000, lambda: [self.canvas.delete(l) for l in lines])

    def effect_scanlines(self):
        lines = [self.canvas.create_rectangle(0, y, self.screen_width, y + 4, fill="black", outline="") for y in range(0, self.screen_height, 8)]
        self.root.after(10000, lambda: [self.canvas.delete(l) for l in lines])

    def effect_fake_crash(self):
        items = [
            self.canvas.create_rectangle(0, 0, self.screen_width, self.screen_height, fill="#003399", outline=""),
            self.canvas.create_text(self.screen_width // 2, self.screen_height // 2, text="VANGUARD ANTI-CHEAT CRITICAL ERROR\nDisconnecting...", fill="white", font=("Courier", 28, "bold"), justify="center")
        ]
        self.root.after(2500, lambda: [self.canvas.delete(i) for i in items])

    def effect_blind_spot(self):
        spot = self.canvas.create_oval((self.screen_width//2)-80, (self.screen_height//2)-80, (self.screen_width//2)+80, (self.screen_height//2)+80, fill="black", outline="#ff4655", width=2)
        self.root.after(8000, lambda: self.canvas.delete(spot))

    def effect_paranoia(self):
        pings = []
        for _ in range(4):
            px, py = (self.screen_width//2) + random.choice([random.randint(-400, -100), random.randint(100, 400)]), (self.screen_height//2) + random.randint(-300, 300)
            pings.extend([
                self.canvas.create_polygon(px, py-15, px+15, py, px, py+15, px-15, py, fill="#ff4655", outline="white"),
                self.canvas.create_text(px, py-30, text="!!!", fill="#ff4655", font=("Arial", 12, "bold"))
            ])
        self.root.after(4000, lambda: [self.canvas.delete(p) for p in pings])

    def effect_screen_crack(self):
        cracks, sx, sy = [], random.randint(300, self.screen_width - 300), random.randint(200, self.screen_height - 200)
        for _ in range(15):
            x, y, coords = sx, sy, [sx, sy]
            for _ in range(random.randint(3, 5)):
                x += random.randint(-400, 400); y += random.randint(-400, 400)
                coords.extend([x, y])
            cracks.append(self.canvas.create_line(*coords, fill="#e0e0e0", width=random.randint(1, 3)))
        self.root.after(8000, lambda: [self.canvas.delete(c) for c in cracks])

    def effect_mosquito(self):
        self.mosq_x, self.mosq_y, self.mosq_dx, self.mosq_dy, self.mosq_active = self.screen_width//2, self.screen_height//2, 25, 25, True
        self.mosq_obj = self.canvas.create_rectangle(self.mosq_x, self.mosq_y, self.mosq_x+15, self.mosq_y+15, fill="black", outline="")
        self.animate_mosquito()
        self.root.after(10000, self.stop_mosquito)

    def animate_mosquito(self):
        if hasattr(self, 'mosq_active') and self.mosq_active:
            self.mosq_x += self.mosq_dx; self.mosq_y += self.mosq_dy
            if self.mosq_x <= 0 or self.mosq_x >= self.screen_width - 15: self.mosq_dx *= -1
            if self.mosq_y <= 0 or self.mosq_y >= self.screen_height - 15: self.mosq_dy *= -1
            if random.random() < 0.05: self.mosq_dx, self.mosq_dy = random.choice([-30, -15, 15, 30]), random.choice([-30, -15, 15, 30])
            self.canvas.coords(self.mosq_obj, self.mosq_x, self.mosq_y, self.mosq_x+15, self.mosq_y+15)
            self.root.after(30, self.animate_mosquito)

    def stop_mosquito(self):
        self.mosq_active = False
        if hasattr(self, 'mosq_obj'): self.canvas.delete(self.mosq_obj)

    def effect_gif_dance(self):
        if not self.gif_frames: return
        self.is_animating = True
        self.gif_canvas_obj = self.canvas.create_image(self.screen_width // 2, self.screen_height // 2, image=self.gif_frames[0])
        self.animate_gif(0)
        self.root.after(6000, self.stop_gif)

    def animate_gif(self, frame_idx):
        if self.is_animating:
            self.canvas.itemconfig(self.gif_canvas_obj, image=self.gif_frames[frame_idx])
            self.root.after(40, lambda: self.animate_gif((frame_idx + 1) % len(self.gif_frames)))

    def stop_gif(self):
        self.is_animating = False
        if hasattr(self, 'gif_canvas_obj'): self.canvas.delete(self.gif_canvas_obj)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ValorantChaosOverlay(root)
        root.mainloop()
    except Exception: pass