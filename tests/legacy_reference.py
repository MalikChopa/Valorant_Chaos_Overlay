"""Copie verbatim des effets et de la roulette de l'ancien valorant_roulette.py (commit a74abcb).

Sert uniquement de référence aux tests de parité : lignes 236-251 et 262-361 du fichier
d'origine, recopiées sans modification. Ne pas éditer ce bloc."""

# mypy: ignore-errors
# flake8: noqa
import random


class LegacyOverlay:
    """Hôte minimal : `root` (faux minuteur) et `canvas` (faux canvas) fournis par le test."""

    def __init__(self, root, canvas, screen_width, screen_height, gif_frames=None):
        self.root = root
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gif_frames = gif_frames or []
        self.executed = []

    def execute_malus(self, choix):
        # Version test de execute_malus (lignes 253-257) : efface la roulette et note le choix.
        for item in self.roulette_items: self.canvas.delete(item)
        self.executed.append(choix)

    def start_roulette_ui(self, final_choice, active_malus):
        self.roulette_items = []
        w, h, y = 350, 80, self.screen_height // 3
        self.roulette_items.append(self.canvas.create_rectangle(20, y, 20 + w, y + h, fill="#0f1923", outline="#ff4655", width=3))
        text_id = self.canvas.create_text(20 + (w // 2), y + (h // 2), text="...", fill="#ece8e1", font=("Arial", 22, "bold"), justify="center")
        self.roulette_items.append(text_id)
        self.animate_roulette(30, 50, text_id, final_choice, active_malus)

    def animate_roulette(self, spins_left, delay, text_id, final_choice, all_malus):
        if spins_left > 0:
            self.canvas.itemconfig(text_id, text=random.choice(all_malus).replace("_", " ").upper())
            new_delay = delay + int(120 / spins_left) 
            self.root.after(new_delay, lambda: self.animate_roulette(spins_left - 1, new_delay, text_id, final_choice, all_malus))
        else:
            self.canvas.itemconfig(text_id, text=f">> {final_choice.replace('_', ' ').upper()} <<", fill="#ff4655")
            self.root.after(1500, lambda: self.execute_malus(final_choice))

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
            px = (self.screen_width//2) + random.choice([random.randint(-400, -100), random.randint(100, 400)])
            py = (self.screen_height//2) + random.randint(-300, 300)
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

    def effect_mlg_gif(self):
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
