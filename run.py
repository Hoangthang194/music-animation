"""
Python Player cho animation 'I miss you...' (bestfriends.cpp)
Tái hiện chính xác cửa sổ SFML gốc (400x400, tỉ lệ 2x, vị trí 72x136, 70ms/frame)
Tích hợp nhạc nền Rex Orange County - Best Friend (chuẩn theo trend TikTok).
"""

import os
import re
import sys
import time
import tkinter as tk
import winsound

# Kích thước cửa sổ chuẩn SFML
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
CANVAS_X = 72
CANVAS_Y = 136
FRAME_W = 128
FRAME_H = 62
SCALE = 2
FPS_DELAY_MS = 70  # sf::sleep(sf::milliseconds(70))

WHITE = b'\xff\xff\xff'
BLACK = b'\x00\x00\x00'

def load_frames():
    """Tải và parse dữ liệu frame từ frames.bin hoặc bestfriends.cpp"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(script_dir, "frames.bin")
    
    if os.path.exists(bin_path):
        with open(bin_path, "rb") as f:
            raw = f.read()
            return raw
            
    cpp_path = os.path.join(script_dir, "bestfriends.cpp")
    if os.path.exists(cpp_path):
        with open(cpp_path, "r", encoding="utf-8") as f:
            text = f.read()
        hex_tokens = re.findall(r'0x[0-9a-fA-F]+', text[:text.rfind('main()')])
        raw = bytes([int(x, 16) for x in hex_tokens])
        try:
            with open(bin_path, "wb") as f:
                f.write(raw)
        except Exception:
            pass
        return raw

    raise FileNotFoundError("Không tìm thấy frames.bin hoặc bestfriends.cpp!")

def build_ppm_frames(raw_data, inverted=False):
    """
    Sinh mảng dữ liệu ảnh PPM (P6) siêu nhanh bằng LUT (Lookup Table).
    Mỗi frame mất < 0.3ms để decode!
    """
    num_frames = len(raw_data) // 1024
    
    fg_color = WHITE if inverted else BLACK
    bg_color = BLACK if inverted else WHITE
    
    # Bảng tra cứu 256 byte -> 16 pixel RGB (mỗi pixel x2 bề ngang)
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
            for _ in range(SCALE):
                rows.append(row)
        ppm_frames.append(hdr + b''.join(rows))
        
    return ppm_frames

class AnimationPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("I miss you... 🎵 Best Friend")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        
        # Center cửa sổ trên màn hình
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        pos_x = (screen_w - WINDOW_WIDTH) // 2
        pos_y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wav_path = os.path.join(self.script_dir, "music.wav")
        self.music_enabled = os.path.exists(self.wav_path)
        self.is_muted = False

        self.raw_data = load_frames()
        self.num_frames = len(self.raw_data) // 1024
        self.inverted = False
        self.is_playing = True
        self.loop = True
        self.delay_ms = FPS_DELAY_MS
        self.current_frame = 0
        self.after_id = None
        
        # Canvas hiển thị
        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Label thông tin / phím tắt ở góc dưới
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            self.canvas,
            textvariable=self.status_var,
            bg="white",
            fg="#777777",
            font=("Segoe UI", 8)
        )
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

        # Sinh dữ liệu ảnh PPM
        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames

        # Image placeholder
        self.image_item = self.canvas.create_image(CANVAS_X, CANVAS_Y, anchor="nw")

        # Bind phím điều khiển
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
        self.root.bind("<Up>", self.speed_up)
        self.root.bind("<Down>", self.speed_down)
        self.root.bind("<Escape>", lambda e: self.on_close())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Click chuột để Pause/Play
        self.canvas.bind("<Button-1>", self.toggle_play)

        # Bật nhạc nền
        self.play_audio()
        self.update_frame()

    def play_audio(self):
        if self.music_enabled and not self.is_muted:
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
                winsound.PlaySound(self.wav_path, flags)
            except Exception:
                pass

    def stop_audio(self):
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def get_photo(self, index):
        if self.photo_cache[index] is None:
            self.photo_cache[index] = tk.PhotoImage(
                data=self.ppm_frames[index],
                format="PPM"
            )
        return self.photo_cache[index]

    def render_current(self):
        photo = self.get_photo(self.current_frame)
        self.canvas.itemconfig(self.image_item, image=photo)
        music_text = "🔇 Mute" if self.is_muted else "🎵 Nhạc BẬT"
        status_text = f"Frame: {self.current_frame + 1}/{self.num_frames} | {music_text} [M] | [Space] Play/Pause | [R] Restart"
        self.status_var.set(status_text)

    def update_frame(self):
        if self.is_playing:
            self.render_current()
            self.current_frame += 1
            if self.current_frame >= self.num_frames:
                if self.loop:
                    self.current_frame = 0
                    self.play_audio()
                else:
                    self.current_frame = self.num_frames - 1
                    self.is_playing = False
                    self.stop_audio()
                    self.status_var.set("Hoàn tất! Bấm [R] để xem lại, [Space] để phát.")
                    return

            self.after_id = self.root.after(self.delay_ms, self.update_frame)

    def toggle_play(self, event=None):
        self.is_playing = not self.is_playing
        if self.is_playing:
            if self.current_frame >= self.num_frames - 1:
                self.current_frame = 0
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.play_audio()
            self.update_frame()
        else:
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.stop_audio()
            self.status_var.set(f"Tạm dừng (Frame {self.current_frame + 1}/{self.num_frames}) - Bấm Space để tiếp tục")

    def toggle_mute(self, event=None):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_audio()
        else:
            if self.is_playing:
                self.play_audio()
        self.render_current()

    def restart(self, event=None):
        self.current_frame = 0
        self.is_playing = True
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.play_audio()
        self.update_frame()

    def next_frame(self, event=None):
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.render_current()

    def prev_frame(self, event=None):
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.stop_audio()
        self.current_frame = (self.current_frame - 1 + self.num_frames) % self.num_frames
        self.render_current()

    def toggle_loop(self, event=None):
        self.loop = not self.loop
        state = "BẬT" if self.loop else "TẮT"
        self.status_var.set(f"Chế độ lặp lại: {state}")

    def toggle_invert(self, event=None):
        self.inverted = not self.inverted
        bg = "black" if self.inverted else "white"
        fg = "#888888"
        self.root.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.status_label.configure(bg=bg, fg=fg)
        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames
        self.render_current()

    def speed_up(self, event=None):
        self.delay_ms = max(20, self.delay_ms - 15)

    def speed_down(self, event=None):
        self.delay_ms = min(300, self.delay_ms + 15)

    def on_close(self):
        self.stop_audio()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AnimationPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
