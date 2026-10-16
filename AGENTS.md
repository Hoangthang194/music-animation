# 🎵 Music Animation Agent Skill Guide (`AGENTS.md`)

Tài liệu này đóng gói toàn bộ quy trình, kiến trúc kỹ thuật và hướng dẫn từng bước để **Agent tự động tạo hoạt ảnh Pixel Art & HD Vector đồng bộ nhịp nhạc từ một file MP3 bất kỳ**.

Lần sau, người dùng chỉ cần cung cấp file `.mp3` (và lời bài hát nếu có), Agent sẽ tự động thực hiện toàn bộ các bước để tạo ra trọn bộ sản phẩm chất lượng cao.

---

## 🎯 1. Mục Tiêu & Sản Phẩm Đầu Ra (Output Artifacts)

Khi nhận file MP3, Agent sẽ tạo ra trọn bộ 5 sản phẩm:

1. **`index.html` (Web Player Siêu Đẹp)**:
   - Tự động nhúng trực tiếp âm thanh & dữ liệu frame dưới dạng Base64 (chạy offline 100% không lo lỗi CORS/404).
   - 2 chế độ xem: **✨ HD Sắc Nét** (Vector Canvas chống vỡ hạt) & **👾 Pixel Cổ Điển** (Mô phỏng màn hình OLED SSD1306).
   - Giao diện chuẩn Mobile-First: **Frame trắng chiếm full chiều cao (`100dvh`, `flex: 1`)**, tự động căn giữa hoạt cảnh không bị méo, bo góc tinh tế, hỗ trợ xoay ngang màn hình.
   - Trình điều khiển đầy đủ: Play/Pause, thanh tua tiến trình, thời gian chạy, nút Mute, phím tắt Space/M.
2. **`[ten_bai]_20_10.gif` / `animation.gif`**:
   - Ảnh GIF chuẩn kích thước 384x192 (phóng to x3 từ 128x64 bằng nội suy `NEAREST`), gửi tặng ngay qua chat/Facebook/Zalo.
3. **`[ten_bai]_frames.bin`**:
   - File nhị phân chuẩn 1-bit monochrome (1024 bytes/frame) để nạp thẳng vào vi điều khiển ESP32 / Arduino / Raspberry Pi với màn hình OLED 0.96" SSD1306.
4. **`run_[ten_bai].py` + `run_[ten_bai].bat`**:
   - Trình phát hoạt ảnh trên Desktop viết bằng Python Tkinter native, hỗ trợ phát nhạc đồng bộ bằng `winsound`/`wave`, có phím tắt điều khiển.
5. **`[ten_bai].cpp`**:
   - Mã nguồn C++ tích hợp thư viện đồ hoạ SFML, nhúng sẵn mảng nhị phân `allFrames[NUM_FRAMES][1024]` để biên dịch thành file `.exe` độc lập.

---

## 📐 2. Bố Cục & Thông Số Kỹ Thuật Chuẩn

- **Độ phân giải màn hình**: `128 x 64` pixel (tỷ lệ 2:1).
- **Tốc độ khung hình (Frame Rate)**: `70 ms / frame` (~`14.28 FPS`).
- **Dung lượng 1 frame**: `(128 * 64) / 8 = 1024 bytes` (1 bit/pixel, MSB-first: bit 7 là pixel x%8=0, bit 0 là pixel x%8=7. Giá trị `1` = màu trắng, `0` = màu đen).
- **Phân chia không gian màn hình**:
  - **Mặt đất (Ground Line)**: Kẻ ngang tại toạ độ `Y = 54` qua toàn màn hình.
  - **Vách ngăn (Dashed Divider)**: Kẻ dải chấm tại toạ độ `X = 56` từ `Y = 6` đến `Y = 50`.
  - **Nửa bên trái (X: 0 đến 55)**: Khu vực diễn hoạt cặp đôi nhân vật Chibi (Nam & Nữ) cùng các phụ kiện (hoa, tim, ô, đám mây, sao, pháo hoa).
  - **Nửa bên phải (X: 57 đến 127)**: Khu vực hiển thị lời bài hát Karaoke chạy từng từ, căn giữa tại `X = 92`.

---

## 🛠️ 3. Quy Trình Thực Hiện Từng Bước Cho Agent

### Bước 1: Tiếp Nhận & Tiền Xử Lý Audio
1. Đọc file MP3 đầu vào (ví dụ `music.mp3` hoặc `song.mp3`).
2. Nếu bài hát dài, cắt lấy đoạn Điệp khúc (Chorus) hoặc đoạn hay nhất (~30s - 45s) để tối ưu thời lượng animation và dung lượng file:
   ```bash
   ffmpeg -y -ss 00:01:15 -to 00:01:56 -i input.mp3 -ac 2 -ar 44100 chorus.mp3
   ```
3. Chuyển sang định dạng WAV 16-bit 44.1kHz để Python phân tích biên độ âm thanh:
   ```bash
   ffmpeg -y -i chorus.mp3 -ac 1 -ar 44100 -sample_fmt s16 chorus.wav
   ```
4. Đọc mẫu âm thanh và tính toán năng lượng RMS trên từng frame 70ms:
   ```python
   import wave, struct, math
   w = wave.open("chorus.wav", 'r')
   rate = w.getframerate()
   nchannels = w.getnchannels()
   nframes = w.getnframes()
   data = w.readframes(nframes)
   w.close()

   samples = struct.unpack_from(f'<{nframes * nchannels}h', data)[0::nchannels]
   FRAME_MS = 70
   frame_samples = int(rate * (FRAME_MS / 1000.0))
   NUM_FRAMES = len(samples) // frame_samples

   energies = []
   for i in range(NUM_FRAMES):
       chunk = samples[i * frame_samples : (i + 1) * frame_samples]
       rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) if chunk else 0
       energies.append(rms)
   max_e = max(energies) or 1
   norm_energies = [e / max_e for e in energies] # Mảng 0.0 -> 1.0 điều khiển độ nhún nhân vật
   ```

---

### Bước 2: Thiết Lập Lời Bài Hát & Karaoke Timestamps (`KARAOKE_TIMED_PHRASES`)
Tạo danh sách các câu hát khớp theo giây. Mỗi câu hát tương ứng với 1 `action` diễn hoạt của nhân vật:

```python
def s_to_f(seconds):
    return round(seconds / 0.070)

KARAOKE_TIMED_PHRASES = [
    {
        "start_f": 0, "end_f": s_to_f(4.5), "action": 1,
        "lines": [
            [(0.2, "Lời"), (0.6, "bài"), (1.0, "hát")],
            [(1.5, "chạy"), (1.9, "từng"), (2.3, "từ")],
            [(2.8, "khớp"), (3.2, "theo"), (3.6, "nhạc...")]
        ]
    },
    # Thêm các câu tiếp theo tương ứng từng mốc giây ca sĩ hát...
]
```

---

### Bước 3: Biên Đạo Hoạt Cảnh Chibi Theo Lời Bài Hát (Action Catalog)
Thiết kế các động tác đáng yêu cho nhân vật nam và nữ dựa trên nhịp `beat_bounce = int(norm_energies[f] * 2.5)`:

1. **Action 1 (Mơ mộng / Say ngủ)**:
   - Nam nằm mơ, có đám mây giấc mơ bồng bềnh bên trên (`cy = 13 + sin(f*0.2)`), trong mây có trái tim nhỏ.
2. **Action 2 (Thức giấc / Ngạc nhiên & Ngại ngùng)**:
   - Nam mở to mắt, má ửng hồng; Nữ xuất hiện với nơ cài tóc và mỉm cười.
3. **Action 3 (Nắm tay & Tim phập phồng)**:
   - Nam và Nữ đứng gần nhau tại `X=28`, tay nắm chặt; phía trên có trái tim lớn phập phồng theo beat nhạc.
4. **Action 4 (Khiêu vũ / Nhún nhảy nhịp nhàng)**:
   - Cặp đôi đu đưa theo điệu nhạc (`sway = sin(f*0.4) * 3`), tay giơ cao nắm nhau xoay vòng, sao lấp lánh xung quanh.
5. **Action 5 (Tặng bó hoa & Nhảy chân sáo)**:
   - Nam cầm bó hoa hồng tặng Nữ; Nữ nhảy cẫng lên vui sướng (`jump = abs(sin(f*0.45)) * 6`), trái tim bay lên cao.
6. **Action 6 (Che ô dưới mưa)**:
   - Đám mây xám mưa rơi tí tách, Nam cầm chiếc ô tròn che cho Nữ, Nữ nép sát vào Nam ấm áp.
7. **Action 7 (Ôm ấm áp & Bóng bay trái tim)**:
   - Cặp đôi ôm nhau tình cảm; trên tay cầm quả bóng bay hình trái tim bay lượn nhẹ nhàng.
8. **Action 8 / Finale (Chúc mừng & Bắn pháo hoa)**:
   - Hai bạn đứng cạnh nhau vẫy tay chào; phía trên bắn pháo hoa / ngôi sao lấp lánh kèm lời chúc (ví dụ: *"CHÚC MỪNG 20/10 💖"* hoặc ngày kỷ niệm).

---

### Bước 4: Tạo File Nhị Phân 1024 Bytes & File GIF
Dùng thư viện `Pillow` (PIL) vẽ từng frame 128x64:
```python
from PIL import Image, ImageDraw, ImageFont

frame_images = []
raw_all_bytes = bytearray()

for f in range(NUM_FRAMES):
    img = Image.new('1', (128, 64), 1) # Nền trắng
    draw = ImageDraw.Draw(img)
    
    # 1. Vẽ mặt đất, cỏ, vách ngăn
    draw.line([(0, 54), (127, 54)], fill=0)
    for dy in range(6, 50, 4): draw.point((56, dy), fill=0)
    
    # 2. Vẽ chữ Karaoke bên phải (X=92)
    # ...
    
    # 3. Vẽ nhân vật theo action bên trái
    # ...
    
    # 4. Chuyển thành 1024 bytes (1 bit/pixel MSB-first)
    frame_bytes = bytearray(1024)
    for y in range(64):
        for x in range(128):
            byte_idx = y * 16 + (x // 8)
            bit_idx = 7 - (x % 8)
            if img.getpixel((x, y)): # pixel màu trắng
                frame_bytes[byte_idx] |= (1 << bit_idx)
    raw_all_bytes.extend(frame_bytes)
    frame_images.append(img)

# Lưu .bin
with open("frames.bin", "wb") as f:
    f.write(raw_all_bytes)

# Lưu GIF phóng to 384x192
gif_frames = [im.resize((384, 192), Image.Resampling.NEAREST).convert('P') for im in frame_images]
gif_frames[0].save("animation.gif", save_all=True, append_images=gif_frames[1:], duration=70, loop=0)
```

---

### Bước 5: Tạo Web Player `index.html` Chuẩn Mobile Full-Height

Quy chuẩn kỹ thuật bắt buộc cho `index.html`:
1. **Âm thanh và Frame nhúng sẵn Base64**:
   - `audio_b64 = base64.b64encode(open('chorus.mp3', 'rb').read()).decode('ascii')`
   - `frames_b64 = base64.b64encode(raw_all_bytes).decode('ascii')`
   - Nhúng trực tiếp vào thẻ `<audio id="bgMusic">` và biến `const ALL_BYTES_B64 = "..."`.
2. **CSS Mobile Full-Height**:
   ```css
   @media (max-width: 640px) {
       html, body {
           width: 100%; height: 100%; height: 100dvh; overflow: hidden;
       }
       .app-card {
           width: 100%; max-width: 100%; height: 100%; height: 100dvh;
           border-radius: 0; border: none; box-shadow: none;
           padding: max(8px, env(safe-area-inset-top, 0px)) 12px max(10px, env(safe-area-inset-bottom, 0px));
           display: flex; flex-direction: column; justify-content: space-between;
           background: rgba(18, 12, 34, 0.94);
       }
       .header { margin-bottom: 6px; flex-shrink: 0; }
       .screen-wrapper {
           flex: 1; width: 100%; height: 100%; min-height: 0;
           aspect-ratio: unset; border-radius: 18px;
           box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.25);
       }
       .bottom-bar { margin-top: 8px; gap: 8px; flex-shrink: 0; }
   }
   @media (max-height: 520px) {
       .header { display: none; }
       .app-card { padding: 4px 10px; }
       .screen-wrapper { flex: 1; min-height: 0; }
       .bottom-bar { margin-top: 4px; gap: 4px; }
   }
   ```
3. **Canvas Auto-Centering Không Méo Hình**:
   ```javascript
   function resizeCanvas() {
       const rect = screenWrapper.getBoundingClientRect();
       const dpr = Math.max(2, window.devicePixelRatio || 1);
       canvas.width = Math.round(rect.width * dpr);
       canvas.height = Math.round(rect.height * dpr);
   }

   function render(cur_t) {
       const S = Math.min(canvas.width / 128.0, canvas.height / 64.0);
       const offsetX = Math.round((canvas.width - 128 * S) / 2);
       const offsetY = Math.round((canvas.height - 64 * S) / 2);

       ctx.clearRect(0, 0, canvas.width, canvas.height);
       ctx.fillStyle = '#ffffff';
       ctx.fillRect(0, 0, canvas.width, canvas.height);

       ctx.save();
       ctx.translate(offsetX, offsetY);

       // Đường đất chạy tràn viền ngang
       ctx.beginPath();
       ctx.moveTo(-offsetX, 54 * S);
       ctx.lineTo(canvas.width - offsetX, 54 * S);
       ctx.stroke();

       // Toàn bộ logic vẽ nhân vật và karaoke giữ nguyên toạ độ 128x64...
       // ...

       ctx.restore();
       updateProgress(cur_t);
   }
   ```

---

### Bước 6: Tạo File C++ SFML và Python Tkinter Desktop

1. **`[ten_bai].cpp`**:
   - Sử dụng `sf::RenderWindow`, `sf::Texture`, `sf::Sprite`, `sf::Music`.
   - Khởi tạo mảng `uint8_t allFrames[NUM_FRAMES][1024]`.
   - Vòng lặp `while (window.isOpen())` đọc thời gian từ `music.getPlayingOffset().asSeconds()` để hiển thị frame tương ứng.
2. **`run_[ten_bai].py` + `run_[ten_bai].bat`**:
   - Dùng thư viện Python có sẵn `tkinter`, `winsound`, `time`.
   - Chuyển đổi mảng byte thành định dạng ảnh PPM hiển thị mượt mà trên Canvas Tkinter.
   - Hỗ trợ đầy đủ phím tắt: `Space` (Play/Pause), `M` (Mute), `R` (Restart), `L` (Loop), `I` (Invert màu).

---

## 💬 4. Mẫu Câu Lệnh Kích Hoạt Nhanh

Khi người dùng gửi bài nhạc mới, họ chỉ cần nói:
> *"Tôi có file nhạc `bai_hat_moi.mp3` trong thư mục, hãy tạo bộ animation đồng bộ theo file Agent.md nhé."*

Agent sẽ lập tức:
1. Kiểm tra file âm thanh và trích xuất đoạn điệp khúc.
2. Tìm kiếm lời bài hát (nếu chưa có) và lập bảng thời gian karaoke.
3. Chạy pipeline tạo toàn bộ: `.bin`, `.gif`, `index.html`, `.cpp`, `.py`.
4. Đẩy lên Git / bàn giao cho người dùng kiểm tra ngay trên trình duyệt điện thoại và máy tính.
