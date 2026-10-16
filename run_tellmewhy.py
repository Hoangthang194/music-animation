"""
Trình phát Desktop native Animation TELL ME WHY (Dương Domic)
Chạy trực tiếp bằng Python native (Tkinter + winsound), không cần cài thư viện ngoài!
Phím tắt:
- Space: Tạm dừng / Tiếp tục
- M: Bật / Tắt âm thanh
- R: Xem lại từ đầu
- L: Bật / Tắt lặp lại
- I: Đổi chế độ Sáng / Tối (Invert)
- Esc: Thoát
"""

import tkinter as tk
import time
import os
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

WIDTH = 128
HEIGHT = 64
SCALE = 6
WINDOW_WIDTH = WIDTH * SCALE
WINDOW_HEIGHT = HEIGHT * SCALE + 50
NUM_FRAMES = 372
FRAME_DURATION = 0.070
TOTAL_DURATION = 26.04

def build_ppm_frames(raw_bytes, invert=False):
    header = f"P6\n{WIDTH} {HEIGHT}\n255\n".encode("ascii")
    color_on = b"\x00\x00\x00" if not invert else b"\xff\xff\xff"
    color_off = b"\xff\xff\xff" if not invert else b"\x00\x00\x00"
    frames = []
    for f in range(NUM_FRAMES):
        start = f * 1024
        pixels = bytearray()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                b_idx = start + y * 16 + (x // 8)
                bit_idx = 7 - (x % 8)
                is_white = (raw_bytes[b_idx] >> bit_idx) & 1
                pixels.extend(color_off if is_white else color_on)
        frames.append(header + bytes(pixels))
    return frames

class TellMeWhyPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("TELL ME WHY 💖 - Dương Domic (Animation Player)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#111116")

        self.num_frames = NUM_FRAMES
        with open("tellmewhy_frames.bin", "rb") as f:
            self.raw_data = f.read()

        self.inverted = False
        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames

        self.wav_path = os.path.abspath("tellmewhy.wav")
        self.music_enabled = os.path.exists(self.wav_path) and HAS_WINSOUND
        self.is_playing = True
        self.is_muted = False
        self.loop = True
        self.current_frame = 0
        self.after_id = None

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=HEIGHT * SCALE, bg="white", highlightthickness=0)
        self.canvas.pack(side="top")
        self.image_item = self.canvas.create_image(0, 0, anchor="nw")

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Consolas", 10, "bold"), fg="#ff8fb6", bg="#111116", pady=8)
        self.status_label.pack(side="bottom", fill="x")

        root.bind("<space>", self.toggle_play)
        root.bind("<r>", self.restart)
        root.bind("<R>", self.restart)
        root.bind("<m>", self.toggle_mute)
        root.bind("<M>", self.toggle_mute)
        root.bind("<l>", self.toggle_loop)
        root.bind("<L>", self.toggle_loop)
        root.bind("<i>", self.toggle_invert)
        root.bind("<I>", self.toggle_invert)
        root.bind("<Escape>", lambda e: self.on_close())
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.start_time = None
        self.play_audio()
        self.update_frame()

    def play_audio(self):
        self.start_time = time.perf_counter() - (self.current_frame * FRAME_DURATION)
        if self.music_enabled and not self.is_muted:
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
                winsound.PlaySound(self.wav_path, flags)
            except Exception: pass

    def stop_audio(self):
        self.start_time = None
        if HAS_WINSOUND:
            try: winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception: pass

    def get_photo(self, index):
        if self.photo_cache[index] is None:
            raw_photo = tk.PhotoImage(data=self.ppm_frames[index], format="PPM")
            self.photo_cache[index] = raw_photo.zoom(SCALE, SCALE)
        return self.photo_cache[index]

    def render_current(self):
        photo = self.get_photo(self.current_frame)
        self.canvas.itemconfig(self.image_item, image=photo)
        music_text = "🔇 Mute" if self.is_muted else "🎵 Nhạc BẬT"
        cur_s = self.current_frame * FRAME_DURATION
        status_text = f"Frame: {self.current_frame + 1}/{self.num_frames} ({cur_s:.1f}s/{TOTAL_DURATION:.1f}s) | {music_text} [M] | [Space] Play/Pause"
        self.status_var.set(status_text)

    def update_frame(self):
        if self.is_playing:
            if self.start_time is None:
                self.start_time = time.perf_counter() - (self.current_frame * FRAME_DURATION)
            elapsed = time.perf_counter() - self.start_time
            self.current_frame = int(elapsed / FRAME_DURATION)
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

    def toggle_loop(self, event=None):
        self.loop = not self.loop

    def toggle_invert(self, event=None):
        self.inverted = not self.inverted
        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames
        self.render_current()

    def on_close(self):
        self.stop_audio()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TellMeWhyPlayer(root)
    root.mainloop()
