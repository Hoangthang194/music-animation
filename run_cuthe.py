"""
Desktop Player 'CỨ THẾ' - Bố cục chuẩn bản gốc
Trái: Hoạt ảnh nhân vật phong phú theo từng câu hát.
Phải: Chữ chạy Karaoke từng từ theo nhịp bài hát.
"""
import os
import sys
import time
import tkinter as tk
import winsound

WINDOW_WIDTH = 512
WINDOW_HEIGHT = 286
CANVAS_X = 0
CANVAS_Y = 0
FRAME_W = 128
FRAME_H = 64
SCALE = 4
NUM_FRAMES = 585

WHITE = b'\xff\xff\xff'
BLACK = b'\x00\x00\x00'

def load_frames():
    with open("cuthe_frames.bin", "rb") as f:
        return f.read()

def build_ppm_frames(raw_data, inverted=False):
    num_frames = len(raw_data) // 1024
    fg_color = WHITE if inverted else BLACK
    bg_color = BLACK if inverted else WHITE
    lut = []
    for b in range(256):
        chunk = bytearray()
        for bit in range(7, -1, -1):
            pixel_on = (b >> bit) & 1
            col = bg_color if pixel_on else fg_color
            chunk.extend(col * SCALE)
        lut.append(bytes(chunk))
    hdr = f"P6\n{FRAME_W * SCALE} {FRAME_H * SCALE}\n255\n".encode("ascii")
    ppm_frames = []
    for f in range(num_frames):
        fb = raw_data[f * 1024 : (f + 1) * 1024]
        rows = []
        for y in range(FRAME_H):
            row = b''.join(lut[fb[y * 16 + i]] for i in range(16))
            for _ in range(SCALE): rows.append(row)
        ppm_frames.append(hdr + b''.join(rows))
    return ppm_frames

class CuThePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Cứ Thế - Orange x Hoàng Dũng 💖 [20-10]")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        pos_x = (screen_w - WINDOW_WIDTH) // 2
        pos_y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")

        self.wav_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cuthe_chorus.wav")
        self.music_enabled = os.path.exists(self.wav_path)
        self.is_muted = False

        self.raw_data = load_frames()
        self.num_frames = len(self.raw_data) // 1024
        self.inverted = False
        self.is_playing = True
        self.loop = True
        self.current_frame = 0
        self.after_id = None
        
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(self.canvas, textvariable=self.status_var, bg="white", fg="#777777", font=("Segoe UI", 8))
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames

        self.image_item = self.canvas.create_image(CANVAS_X, CANVAS_Y, anchor="nw")

        self.root.bind("<space>", self.toggle_play)
        self.root.bind("<Right>", self.next_frame)
        self.root.bind("<Left>", self.prev_frame)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)
        self.root.bind("<l>", self.toggle_loop)
        self.root.bind("<L>", self.toggle_loop)
        self.root.bind("<m>", self.toggle_mute)
        self.root.bind("<M>", self.toggle_mute)
        self.root.bind("<i>", self.toggle_invert)
        self.root.bind("<I>", self.toggle_invert)
        self.root.bind("<Escape>", lambda e: self.on_close())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas.bind("<Button-1>", self.toggle_play)

        self.start_time = None
        self.play_audio()
        self.update_frame()

    def play_audio(self):
        self.start_time = time.perf_counter() - (self.current_frame * 0.070)
        if self.music_enabled and not self.is_muted:
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
                winsound.PlaySound(self.wav_path, flags)
            except Exception: pass

    def stop_audio(self):
        self.start_time = None
        try: winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception: pass

    def get_photo(self, index):
        if self.photo_cache[index] is None:
            self.photo_cache[index] = tk.PhotoImage(data=self.ppm_frames[index], format="PPM")
        return self.photo_cache[index]

    def render_current(self):
        photo = self.get_photo(self.current_frame)
        self.canvas.itemconfig(self.image_item, image=photo)
        music_text = "🔇 Mute" if self.is_muted else "🎵 Nhạc BẬT"
        status_text = f"Frame: {self.current_frame + 1}/{self.num_frames} | {music_text} [M] | [Space] Play/Pause | [R] Restart"
        self.status_var.set(status_text)

    def update_frame(self):
        if self.is_playing:
            if self.start_time is None:
                self.start_time = time.perf_counter() - (self.current_frame * 0.070)
            elapsed = time.perf_counter() - self.start_time
            self.current_frame = int(elapsed / 0.070)
            if self.current_frame >= self.num_frames:
                if self.loop:
                    self.current_frame = 0
                    self.play_audio()
                else:
                    self.current_frame = self.num_frames - 1
                    self.is_playing = False
                    self.stop_audio()
                    return
            self.render_current()
            self.after_id = self.root.after(30, self.update_frame)

    def toggle_play(self, event=None):
        self.is_playing = not self.is_playing
        if self.is_playing:
            if self.current_frame >= self.num_frames - 1: self.current_frame = 0
            if self.after_id: self.root.after_cancel(self.after_id)
            self.play_audio()
            self.update_frame()
        else:
            if self.after_id: self.root.after_cancel(self.after_id)
            self.stop_audio()
            self.status_var.set(f"Tạm dừng (Frame {self.current_frame + 1}/{self.num_frames})")

    def toggle_mute(self, event=None):
        self.is_muted = not self.is_muted
        if self.is_muted: self.stop_audio()
        else:
            if self.is_playing: self.play_audio()
        self.render_current()

    def restart(self, event=None):
        self.current_frame = 0
        self.is_playing = True
        if self.after_id: self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.play_audio()
        self.update_frame()

    def next_frame(self, event=None):
        self.is_playing = False
        if self.after_id: self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.render_current()

    def prev_frame(self, event=None):
        self.is_playing = False
        if self.after_id: self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.current_frame = (self.current_frame - 1 + self.num_frames) % self.num_frames
        self.render_current()

    def toggle_loop(self, event=None):
        self.loop = not self.loop
        self.status_var.set(f"Chế độ lặp lại: {'BẬT' if self.loop else 'TẮT'}")

    def toggle_invert(self, event=None):
        self.inverted = not self.inverted
        bg = "black" if self.inverted else "white"
        self.root.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.status_label.configure(bg=bg, fg="#888888")
        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames
        self.render_current()

    def on_close(self):
        self.stop_audio()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CuThePlayer(root)
    root.mainloop()
