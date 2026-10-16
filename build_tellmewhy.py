"""
Trình tạo trọn bộ Animation đồng bộ bài hát "TELL ME WHY" (Dương Domic)
Chủ đề: CỰC KỲ TÂM TRẠNG & NỖI BUỒN SÂU LẮNG (Chàng trai hút thuốc, lái xe trong đêm mưa, gương chiếu hậu, cần gạt nước)
Kèm theo: AUDIO EQUALIZER BARS (Các thanh nhạc nhảy sống động ở dưới theo nhịp nhạc)
Chuẩn quy cách AGENTS.md / Agent.md:
- 128x64 OLED monochrome 1-bit frames (tellmewhy_frames.bin)
- GIF preview 384x192 (tellmewhy.gif)
- C++ SFML source code (tell_me_why.cpp)
- Native Python Tkinter Desktop player (run_tellmewhy.py + run_tellmewhy.bat)
- Web Player chuẩn Mobile Full-Height (tell_me_why.html & index.html)
"""

import os
import sys
import wave
import struct
import math
import json
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def main():
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("=== TẠO BỘ ANIMATION CỰC BUỒN & EQUALIZER: TELL ME WHY (DƯƠNG DOMIC) ===")

    wav_path = "tellmewhy.wav"
    mp3_path = "tellmewhy.mp3"
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Không tìm thấy {wav_path}!")

    w = wave.open(wav_path, 'r')
    rate = w.getframerate()
    nchannels = w.getnchannels()
    nframes = w.getnframes()
    data = w.readframes(nframes)
    w.close()

    samples = np.frombuffer(data, dtype=np.int16)
    FRAME_MS = 70
    frame_samples = int(rate * (FRAME_MS / 1000.0))
    NUM_FRAMES = len(samples) // frame_samples
    print(f"Tổng số frame: {NUM_FRAMES} (~{NUM_FRAMES * FRAME_MS / 1000:.1f}s)")

    # 1. TÍNH TOÁN BĂNG TẦN EQUALIZER CHO 24 THANH NHẠC (AUDIO VISUALIZER)
    print("Đang phân tích 24 dải tần số FFT (Audio Visualizer)...")
    num_bars = 24
    all_bars_raw = []
    window = np.hanning(frame_samples)
    freqs = np.fft.rfftfreq(frame_samples, 1 / rate)
    band_edges = np.logspace(np.log10(45), np.log10(9000), num_bars + 1)

    energies = []
    for f in range(NUM_FRAMES):
        chunk = samples[f * frame_samples : (f + 1) * frame_samples]
        if len(chunk) < frame_samples:
            all_bars_raw.append([0.0] * num_bars)
            energies.append(0.0)
            continue

        # Năng lượng RMS
        rms = np.sqrt(np.mean(chunk.astype(float) ** 2))
        energies.append(float(rms))

        # FFT Spectrum
        fft_vals = np.abs(np.fft.rfft(chunk * window))
        bars = []
        for b in range(num_bars):
            mask = (freqs >= band_edges[b]) & (freqs < band_edges[b + 1])
            val = np.mean(fft_vals[mask]) if np.any(mask) else 0.0
            bars.append(float(val))
        all_bars_raw.append(bars)

    all_bars_raw = np.array(all_bars_raw)
    max_vals = np.percentile(all_bars_raw, 97, axis=0)
    max_vals[max_vals == 0] = 1
    norm_bars = np.clip(all_bars_raw / max_vals, 0.08, 1.0) ** 0.72

    max_e = max(energies) or 1
    norm_energies = [e / max_e for e in energies]

    # Chiều cao thanh nhạc (1 đến 8 pixels, nằm từ Y=63 lên đến Y=55)
    bar_heights_per_frame = []
    for f in range(NUM_FRAMES):
        bh = (norm_bars[f] * 7.5).astype(int) + 1
        bh = np.clip(bh, 1, 9).tolist()
        bar_heights_per_frame.append(bh)

    try:
        font_lyrics = ImageFont.truetype('segoeuib.ttf', 8)
        font_finale = ImageFont.truetype('segoeuib.ttf', 8)
    except Exception:
        font_lyrics = font_finale = ImageFont.load_default()

    def s_to_f(s):
        return round(s / 0.070)

    # 7 Phân đoạn lời bài hát đồng bộ từng từ theo giây (Tell Me Why - Dương Domic)
    KARAOKE_TIMED_PHRASES = [
        # Câu 1 (0.0s -> 3.8s) - Hút thuốc dưới đèn đường đêm mưa
        {
            "start_f": 0, "end_f": s_to_f(3.8), "action": 1,
            "lines": [
                [(0.2, "Từng"), (0.8, "cơn"), (1.4, "đau")],
                [(2.0, "tăng"), (2.6, "dần"), (3.1, "lên..."), (3.5, "🌧")]
            ]
        },
        # Câu 2 (3.8s -> 7.5s) - Thở vòng khói tròn, đồng hồ cát
        {
            "start_f": s_to_f(3.8), "end_f": s_to_f(7.5), "action": 2,
            "lines": [
                [(3.9, "Thời"), (4.5, "gian"), (5.0, "trôi")],
                [(5.6, "âm"), (6.2, "thầm"), (6.8, "đếm..."), (7.2, "⏳")]
            ]
        },
        # Câu 3 (7.5s -> 10.8s) - Lái xe trong đêm mưa một mình
        {
            "start_f": s_to_f(7.5), "end_f": s_to_f(10.8), "action": 3,
            "lines": [
                [(7.6, "Nỗi"), (8.1, "cô"), (8.6, "đơn")],
                [(9.1, "ghé"), (9.5, "qua"), (9.9, "đêm"), (10.3, "nay..."), (10.6, "🌙")]
            ]
        },
        # Câu 4 (10.8s -> 14.0s) - Cần gạt nước kính xe, gương chiếu hậu
        {
            "start_f": s_to_f(10.8), "end_f": s_to_f(14.0), "action": 4,
            "lines": [
                [(10.8, "Đêm"), (11.2, "qua,"), (11.6, "đêm"), (12.0, "nay")],
                [(12.4, "anh"), (12.8, "chẳng"), (13.2, "muốn")],
                [(13.5, "quay"), (13.8, "lại...")]
            ]
        },
        # Câu 5 (14.0s -> 17.5s) - Đỗ xe bên đường, tựa mui xe hút thuốc
        {
            "start_f": s_to_f(14.0), "end_f": s_to_f(17.5), "action": 5,
            "lines": [
                [(14.1, "Phải"), (14.6, "xa"), (15.1, "em")],
                [(15.6, "anh"), (16.2, "nào"), (16.8, "muốn..."), (17.2, "💔")]
            ]
        },
        # Câu 6 (17.5s -> 21.5s) - Nhìn điện thoại le lói, tim đau thắt
        {
            "start_f": s_to_f(17.5), "end_f": s_to_f(21.5), "action": 6,
            "lines": [
                [(17.6, "Vì"), (18.1, "chia"), (18.6, "đôi")],
                [(19.2, "vẫn"), (19.8, "còn")],
                [(20.3, "thương..."), (20.8, "♥"), (21.2, "✨")]
            ]
        },
        # Câu 7 (21.5s -> 26.04s) - Xe lăn bánh xa dần vào màn đêm
        {
            "start_f": s_to_f(21.5), "end_f": NUM_FRAMES, "action": 7,
            "lines": [
                [(21.6, "✨"), (22.0, "TELL"), (22.4, "ME"), (22.8, "WHY"), (23.2, "✨")],
                [(23.6, "Dương"), (24.0, "Domic")],
                [(24.5, "Vẫn"), (24.9, "còn"), (25.3, "thương"), (25.7, "nhau..."), (25.9, "💖")]
            ]
        }
    ]

    def get_karaoke_data(f_idx):
        cur_t = f_idx * 0.070
        active = None
        for p in KARAOKE_TIMED_PHRASES:
            if p["start_f"] <= f_idx <= p["end_f"]:
                active = p
                break
        if not active:
            return 1, []

        rendered_lines = []
        for line_words in active["lines"]:
            words_shown = [w for t, w in line_words if cur_t >= t]
            if words_shown:
                rendered_lines.append(" ".join(words_shown))
            else:
                rendered_lines.append("")
        return active["action"], rendered_lines

    print("Đang vẽ hoạt cảnh tâm trạng & các thanh nhạc Equalizer...")
    frame_images = []
    raw_all_bytes = bytearray()

    for f in range(NUM_FRAMES):
        img = Image.new('1', (128, 64), 1)  # 1 = Nền trắng
        draw = ImageDraw.Draw(img)
        energy = norm_energies[f]
        beat_bounce = int(energy * 2.5)

        # 1. Đường đất ngăn cách tại Y = 53
        draw.line([(0, 53), (127, 53)], fill=0)

        # 2. VẼ 24 THANH NHẠC EQUALIZER NHẢY DƯỚI ĐƯỜNG ĐẤT (Y: 55 đến 63)
        bars_h = bar_heights_per_frame[f]
        for b_idx in range(num_bars):
            bx = 4 + b_idx * 5
            bh = bars_h[b_idx]
            # Vẽ thanh nhạc từ đáy Y=63 nhảy lên
            draw.rectangle([bx, 63 - bh, bx + 2, 63], fill=0)

        # 3. Dải phân cách dọc nhẹ nhàng ở giữa (X = 56, Y = 4 đến 48)
        for dy in range(4, 50, 4):
            draw.point((56, dy), fill=0)

        # 4. VẼ LỜI KARAOKE BÊN PHẢI (X: 58 đến 126, tâm tại X=92)
        action, lines = get_karaoke_data(f)
        text_x = 92
        num_l = len(lines)
        if num_l == 2:
            y_starts = [20, 34]
        elif num_l == 3:
            y_starts = [15, 27, 39]
        else:
            y_starts = [9, 19, 29, 39]

        for i, text_str in enumerate(lines):
            if text_str and i < len(y_starts):
                draw.text((text_x, y_starts[i]), text_str, font=font_lyrics, fill=0, anchor='mm')

        # 5. VẼ HOẠT CẢNH CỰC BUỒN BÊN TRÁI (X: 0 đến 55, Y: 0 đến 52)
        is_blinking = (f % 35 in [0, 1])

        # Hạt mưa rơi rải rác
        for rx, r_seed in [(8, 11), (22, 17), (35, 7), (48, 23)]:
            ry = ((f * 3 + r_seed * 4) % 45) + 6
            if ry < 52:
                draw.line([(rx, ry), (rx - 1, ry + 2)], fill=0)

        if action == 1:
            # --- ACTION 1: HÚT THUỐC DƯỚI CỘT ĐÈN ĐƯỜNG ĐÊM MƯA ---
            # Cột đèn đường tại X=8
            draw.line([(8, 12), (8, 52)], fill=0)
            draw.line([(7, 12), (14, 8)], fill=0)
            draw.arc([11, 8, 19, 16], start=180, end=360, fill=0)  # Chụp đèn
            draw.line([(11, 12), (19, 12)], fill=0)
            # Quầng sáng hình nón
            for dy in range(16, 52, 4):
                draw.point([(8 + (dy - 16) // 3, dy)], fill=0)

            # Chàng trai đứng hút thuốc
            bx = 28
            by = 31 - beat_bounce
            # Đầu & Tóc rủ
            draw.ellipse([bx-4, by-5, bx+4, by+5], outline=0, fill=1)
            draw.line([(bx-4, by-2), (bx+2, by-4)], fill=0)
            draw.line([(bx-2, by-5), (bx+4, by-2)], fill=0)
            # Mắt nhắm buồn
            draw.line([(bx-3, by), (bx-1, by+1)], fill=0)
            # Áo khoác dài
            draw.polygon([(bx-4, by+6), (bx+4, by+6), (bx+5, by+16), (bx-5, by+16)], outline=0, fill=1)
            # Tay cầm điếu thuốc đưa lên môi
            draw.line([(bx-3, by+8), (bx-6, by+13)], fill=0)
            draw.line([(bx+3, by+8), (bx+6, by+2)], fill=0)
            # Điếu thuốc nhỏ
            draw.line([(bx+6, by+2), (bx+10, by+1)], fill=0)
            # Tàn thuốc đỏ nhấp nháy
            if f % 4 < 3:
                draw.point([(bx+10, by+1)], fill=0)
            # Làn khói thuốc uốn lượn
            for i in range(1, 9):
                sy = by - i * 2
                sx = int(bx + 10 + math.sin(f * 0.35 + i * 0.8) * (i * 0.7))
                if 0 <= sx < 55 and sy > 2:
                    draw.point([(sx, sy)], fill=0)

            # Chân
            draw.line([(bx-2, by+17), (bx-2, 52)], fill=0)
            draw.line([(bx+2, by+17), (bx+2, 52)], fill=0)

        elif action == 2:
            # --- ACTION 2: RÍT THUỐC, THỞ VÒNG KHÓI TRÒN (SMOKE RINGS) ---
            bx = 20
            by = 30 - beat_bounce

            # Chàng trai nhìn nghiêng ngửa đầu thở khói
            draw.ellipse([bx-5, by-5, bx+4, by+5], outline=0, fill=1)
            draw.polygon([(bx-5, by-2), (bx-6, by-5), (bx, by-7), (bx+4, by-3)], outline=0, fill=0)
            draw.point([(bx+1, by)], fill=0)  # Mắt nhìn nghiêng
            draw.rectangle([bx-4, by+6, bx+4, by+15], outline=0, fill=1)
            draw.line([(bx-3, by+8), (bx-6, by+14)], fill=0)
            # Điếu thuốc kẹp trên tay buông xuống
            draw.line([(bx+3, by+8), (bx+6, by+12)], fill=0)
            draw.line([(bx+6, by+12), (bx+9, by+13)], fill=0)
            draw.point([(bx+9, by+13)], fill=0)

            # Các vòng khói thuốc tròn (Smoke rings) bay lên
            ring_phase = (f * 0.8) % 24
            # Vòng khói 1
            r1_y = int(by - 2 - ring_phase * 0.6)
            r1_x = int(bx + 7 + ring_phase * 0.8)
            draw.ellipse([r1_x-2, r1_y-1, r1_x+2, r1_y+1], outline=0, fill=1)
            # Vòng khói 2
            r2_y = int(by - 6 - ((ring_phase + 10) % 24) * 0.6)
            r2_x = int(bx + 12 + ((ring_phase + 10) % 24) * 0.8)
            draw.ellipse([r2_x-3, r2_y-2, r2_x+3, r2_y+2], outline=0, fill=1)

            # Đồng hồ cát đếm thời gian
            hx = 45
            hy = 14
            draw.polygon([(hx-4, hy-6), (hx+4, hy-6), (hx, hy), (hx+4, hy+6), (hx-4, hy+6), (hx, hy)], outline=0, fill=1)
            draw.line([(hx-5, hy-6), (hx+5, hy-6)], fill=0)
            draw.line([(hx-5, hy+6), (hx+5, hy+6)], fill=0)
            draw.point([(hx, hy+2 + (f % 4))], fill=0)  # Cát rơi

            # Chân
            draw.line([(bx-2, by+16), (bx-2, 52)], fill=0)
            draw.line([(bx+2, by+16), (bx+2, 52)], fill=0)

        elif action == 3:
            # --- ACTION 3: LÁI XE TRONG ĐÊM MƯA CÔ ĐỘC (NIGHT DRIVE) ---
            # Chiếc xe ô tô nhìn bên hông
            car_y = 42
            # Thân xe
            draw.rectangle([6, car_y, 48, car_y + 6], outline=0, fill=1)
            # Mui xe cong
            draw.polygon([(14, car_y), (20, car_y - 9), (36, car_y - 9), (42, car_y)], outline=0, fill=1)
            # Kính xe
            draw.polygon([(20, car_y - 1), (22, car_y - 8), (34, car_y - 8), (38, car_y - 1)], outline=0, fill=1)

            # Chàng trai sau tay lái bên trong xe
            draw.ellipse([25, car_y - 7, 31, car_y - 1], outline=0, fill=1)  # Đầu
            draw.line([(28, car_y - 1), (33, car_y + 1)], fill=0)  # Tay lái
            # Điếu thuốc kẹp trên tay thò ra ngoài cửa kính
            draw.line([(25, car_y - 1), (20, car_y - 3)], fill=0)
            draw.point([(19, car_y - 3)], fill=0)
            # Tàn khói bay lùi về sau
            for k in range(1, 6):
                draw.point([(18 - k * 2, car_y - 3 - int(math.sin(f*0.5 + k)*2))], fill=0)

            # Bánh xe trước & sau xoay tròn
            wheel_rot = (f * 2) % 4
            for wx in [16, 40]:
                draw.ellipse([wx-4, car_y+3, wx+4, car_y+11], outline=0, fill=1)
                # Nan hoa bánh xe xoay
                if wheel_rot in [0, 2]:
                    draw.line([(wx-3, car_y+7), (wx+3, car_y+7)], fill=0)
                    draw.line([(wx, car_y+4), (wx, car_y+10)], fill=0)
                else:
                    draw.line([(wx-2, car_y+5), (wx+2, car_y+9)], fill=0)
                    draw.line([(wx-2, car_y+9), (wx+2, car_y+5)], fill=0)

            # Đèn pha xe phía trước chiếu sáng
            draw.line([(48, car_y + 2), (55, car_y - 2)], fill=0)
            draw.line([(48, car_y + 4), (55, car_y + 7)], fill=0)

            # Vệt kẻ đường lướt nhanh về sau
            road_shift = (f * 4) % 12
            for rx in range(0, 56, 12):
                pos = rx - road_shift
                if 0 <= pos < 52:
                    draw.line([(pos, 52), (min(55, pos + 5), 52)], fill=0)

        elif action == 4:
            # --- ACTION 4: CẦN GẠT NƯỚC KÍNH XE & GƯƠNG CHIẾU HẬU ---
            # Gương chiếu hậu ô tô ở trên phản chiếu ánh mắt buồn
            draw.rectangle([14, 8, 42, 20], outline=0, fill=1)
            draw.line([(28, 4), (28, 8)], fill=0)  # Chân gương
            # Đôi mắt buồn nhìn trong gương chiếu hậu
            draw.arc([20, 11, 26, 17], start=0, end=180, fill=0)
            draw.arc([30, 11, 36, 17], start=0, end=180, fill=0)
            draw.point([(23, 14), (33, 14)], fill=0)

            # Kính chắn gió phía dưới với cần gạt nước gạt qua lại
            draw.rectangle([4, 25, 52, 51], outline=0, fill=1)
            # Cần gạt nước xoay góc
            wiper_angle = math.sin(f * 0.45) * 16
            draw.line([(28, 50), (int(28 + wiper_angle), 28)], fill=0)
            # Cánh gạt cao su
            draw.line([(int(28 + wiper_angle - 4), 28), (int(28 + wiper_angle + 4), 28)], fill=0)

            # Giọt nước mưa chảy trên kính
            for kx, ky in [(10, 32), (18, 40), (38, 30), (46, 42), (24, 36)]:
                d_y = ((ky + f * 2) % 22) + 26
                draw.line([(kx, d_y), (kx, d_y + 2)], fill=0)

        elif action == 5:
            # --- ACTION 5: ĐỖ XE VEN ĐƯỜNG, TỰA LƯNG VÀO XE HÚT THUỐC ---
            # Xe đỗ ở góc trái
            draw.rectangle([2, 40, 26, 48], outline=0, fill=1)
            draw.polygon([(6, 40), (12, 33), (22, 33), (26, 40)], outline=0, fill=1)
            draw.ellipse([8, 45, 14, 51], outline=0, fill=1)
            draw.ellipse([20, 45, 26, 51], outline=0, fill=1)

            # Chàng trai tựa lưng vào đầu xe
            bx = 32
            by = 31
            draw.ellipse([bx-4, by-5, bx+4, by+5], outline=0, fill=1)
            draw.line([(bx-4, by-2), (bx+3, by-4)], fill=0)  # Tóc ướt mưa
            draw.line([(bx-3, by), (bx-1, by+1)], fill=0)  # Mắt cúi gằm
            # Giọt lệ rơi
            draw.point([(bx+1, by + 2 + (f % 4))], fill=0)
            # Thân tựa nghiêng vào xe
            draw.polygon([(bx-4, by+6), (bx+4, by+6), (bx+5, by+16), (bx-5, by+16)], outline=0, fill=1)
            # Tay chụm che điếu thuốc
            draw.line([(bx-3, by+8), (bx+4, by+4)], fill=0)
            draw.line([(bx+3, by+8), (bx+5, by+4)], fill=0)
            draw.point([(bx+6, by+4)], fill=0)
            # Khói thuốc bay nghi ngút
            for i in range(1, 8):
                draw.point([(int(bx + 6 + math.sin(f*0.3 + i)*1.5), by + 3 - i * 2)], fill=0)

            # Trái tim rạn vỡ nhói đau
            draw.polygon([(bx+10, by-2), (bx+7, by-6), (bx+13, by-6)], outline=0, fill=0)
            draw.line([(bx+10, by-6), (bx+10, by-2)], fill=1)

            # Chân bắt chéo tựa xe
            draw.line([(bx-2, by+17), (bx-5, 52)], fill=0)
            draw.line([(bx+2, by+17), (bx+1, 52)], fill=0)

        elif action == 6:
            # --- ACTION 6: NGỒI TRÊN XE, NHÌN ĐIỆN THOẠI PHÁT SÁNG ---
            # Chàng trai ngồi trên mui xe
            bx = 24
            by = 28 - beat_bounce
            draw.ellipse([bx-4, by-5, bx+4, by+5], outline=0, fill=1)
            draw.line([(bx-3, by), (bx-1, by+1)], fill=0)  # Mắt nhìn xuống
            draw.rectangle([bx-4, by+6, bx+4, by+15], outline=0, fill=1)

            # Tay cầm chiếc điện thoại phát sáng
            draw.line([(bx+3, by+8), (bx+8, by+10)], fill=0)
            draw.rectangle([bx+8, by+7, bx+13, by+14], outline=0, fill=0)  # Điện thoại
            draw.rectangle([bx+9, by+8, bx+12, by+12], outline=0, fill=1)  # Màn hình phát sáng

            # Điếu thuốc kẹp tay trái buông thõng
            draw.line([(bx-3, by+8), (bx-6, by+14)], fill=0)
            draw.line([(bx-6, by+14), (bx-9, by+15)], fill=0)
            draw.point([(bx-9, by+15)], fill=0)  # Tàn thuốc
            # Khói thuốc
            draw.point([(bx-10, by+13), (bx-11, by+10), (bx-10, by+8)], fill=0)

            # Trái tim lớn rạn vỡ đập thắt lại theo nhịp bass
            hx = 40
            hy = 14 - int(math.sin(f * 0.3) * 2)
            hw = 4 + beat_bounce
            draw.polygon([(hx, hy+hw), (hx-hw, hy), (hx-hw+1, hy-hw//2), (hx, hy-hw//3), (hx+hw-1, hy-hw//2), (hx+hw, hy)], outline=0, fill=0)
            draw.line([(hx, hy-hw//3), (hx-1, hy+1), (hx+1, hy+2), (hx, hy+hw)], fill=1)  # Vết nứt

            # Chân thả lỏng ngồi trên thành xe
            draw.line([(bx-2, by+16), (bx-2, by+23)], fill=0)
            draw.line([(bx-2, by+23), (bx+2, by+23)], fill=0)
            # Thân xe dưới chân
            draw.rectangle([10, by+20, 48, 52], outline=0, fill=1)
            draw.ellipse([14, 46, 20, 52], outline=0, fill=1)
            draw.ellipse([38, 46, 44, 52], outline=0, fill=1)

        elif action == 7:
            # --- ACTION 7: XE LĂN BÁNH XA DẦN VÀO MÀN ĐÊM VÔ TẬN ---
            # Phối cảnh đường hun hút về điểm vô cực (X=28, Y=26)
            draw.line([(28, 26), (6, 52)], fill=0)
            draw.line([(28, 26), (50, 52)], fill=0)
            # Vạch giữa đường mờ dần
            for wy in range(28, 52, 6):
                draw.line([(28, wy), (28, wy + 3)], fill=0)

            # Chiếc xe nhỏ dần lùi về phía xa
            car_dist = int(math.sin(f * 0.1) * 2)
            cx = 28
            cy = 38 + car_dist
            # Xe nhìn từ phía sau
            draw.rectangle([cx-8, cy, cx+8, cy+6], outline=0, fill=1)
            draw.polygon([(cx-6, cy), (cx-4, cy-4), (cx+4, cy-4), (cx+6, cy)], outline=0, fill=1)
            # 2 đốm đèn hậu đỏ rực
            draw.point([(cx-6, cy+3), (cx+6, cy+3)], fill=0)
            # Khói xe xả ra
            draw.point([(cx-7, cy+6), (cx-9, cy+5), (cx-10, cy+3)], fill=0)

            # Điếu thuốc tàn nằm lại bên vệ đường
            draw.line([(42, 50), (45, 51)], fill=0)
            if f % 4 < 2:
                draw.point([(42, 50)], fill=0)

            # Sao lấp lánh tĩnh lặng
            for sx, sy in [(12, 10), (44, 8), (20, 16), (36, 14)]:
                if (f + sx) % 6 < 3:
                    draw.point([(sx, sy)], fill=0)

        # 6. CHUYỂN THÀNH 1024 BYTES (1 bit/pixel MSB-first)
        frame_bytes = bytearray(1024)
        for y in range(64):
            for x in range(128):
                byte_idx = y * 16 + (x // 8)
                bit_idx = 7 - (x % 8)
                is_white = 1 if img.getpixel((x, y)) else 0
                if is_white:
                    frame_bytes[byte_idx] |= (1 << bit_idx)

        raw_all_bytes.extend(frame_bytes)
        frame_images.append(img)

    # 1. Ghi file binary OLED
    bin_file = "tellmewhy_frames.bin"
    with open(bin_file, "wb") as f:
        f.write(raw_all_bytes)
    print(f"Đã tạo {bin_file} ({len(raw_all_bytes)} bytes)")

    # 2. Xuất file ảnh GIF (384x192)
    gif_file = "tellmewhy.gif"
    print(f"Đang tạo {gif_file}...")
    gif_frames = []
    for im in frame_images:
        scaled = im.resize((384, 192), Image.Resampling.NEAREST).convert('P')
        gif_frames.append(scaled)
    gif_frames[0].save(gif_file, save_all=True, append_images=gif_frames[1:], duration=FRAME_MS, loop=0)
    print(f"Đã tạo {gif_file} thành công!")

    # 3. Tạo C++ SFML source code
    cpp_file = "tell_me_why.cpp"
    print(f"Đang tạo {cpp_file}...")
    with open(cpp_file, "w", encoding="utf-8") as f:
        f.write(f"""#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
#include <iostream>
#include <fstream>
#include <vector>

constexpr int WIDTH = 128;
constexpr int HEIGHT = 64;
constexpr int SCALE = 6;
constexpr int FRAME_SIZE = (WIDTH * HEIGHT) / 8;
constexpr int NUM_FRAMES = {NUM_FRAMES};
constexpr float FRAME_TIME = 0.070f;

int main() {{
    sf::RenderWindow window(sf::VideoMode(WIDTH * SCALE, HEIGHT * SCALE), "TELL ME WHY - Duong Domic [SFML Equalizer Player]");
    window.setFramerateLimit(60);

    // Doc frame tu tellmewhy_frames.bin
    std::ifstream binFile("tellmewhy_frames.bin", std::ios::binary);
    if (!binFile) {{
        std::cerr << "Khong the mo file tellmewhy_frames.bin!" << std::endl;
        return -1;
    }}
    std::vector<uint8_t> allFrames(NUM_FRAMES * FRAME_SIZE);
    binFile.read(reinterpret_cast<char*>(allFrames.data()), allFrames.size());
    binFile.close();

    sf::Music music;
    if (music.openFromFile("tellmewhy.mp3")) {{
        music.setLoop(true);
        music.play();
    }}

    sf::Texture texture;
    texture.create(WIDTH, HEIGHT);
    sf::Sprite sprite(texture);
    sprite.setScale(SCALE, SCALE);

    sf::Clock clock;
    std::vector<sf::Uint8> pixels(WIDTH * HEIGHT * 4, 255);

    while (window.isOpen()) {{
        sf::Event event;
        while (window.pollEvent(event)) {{
            if (event.type == sf::Event::Closed || 
               (event.type == sf::Event::KeyPressed && event.key.code == sf::Keyboard::Escape))
                window.close();
            if (event.type == sf::Event::KeyPressed && event.key.code == sf::Keyboard::Space) {{
                if (music.getStatus() == sf::Music::Playing) music.pause();
                else music.play();
            }}
        }}

        float t = music.getStatus() == sf::Music::Playing ? music.getPlayingOffset().asSeconds() : clock.getElapsedTime().asSeconds();
        int frameIdx = static_cast<int>(t / FRAME_TIME) % NUM_FRAMES;
        const uint8_t* frameData = &allFrames[frameIdx * FRAME_SIZE];

        for (int y = 0; y < HEIGHT; ++y) {{
            for (int x = 0; x < WIDTH; ++x) {{
                int byteIdx = y * 16 + (x / 8);
                int bitIdx = 7 - (x % 8);
                bool isWhite = (frameData[byteIdx] >> bitIdx) & 1;
                sf::Uint8 color = isWhite ? 255 : 0;
                int pIdx = (y * WIDTH + x) * 4;
                pixels[pIdx] = color;
                pixels[pIdx + 1] = color;
                pixels[pIdx + 2] = color;
                pixels[pIdx + 3] = 255;
            }}
        }}

        texture.update(pixels.data());
        window.clear();
        window.draw(sprite);
        window.display();
    }}
    return 0;
}}
""")
    print(f"Đã tạo {cpp_file}!")

    # 4. Tạo Desktop Python Tkinter Runner
    py_player_file = "run_tellmewhy.py"
    with open(py_player_file, "w", encoding="utf-8") as f:
        f.write(f'''"""
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
NUM_FRAMES = {NUM_FRAMES}
FRAME_DURATION = 0.070
TOTAL_DURATION = {NUM_FRAMES * 0.070:.2f}

def build_ppm_frames(raw_bytes, invert=False):
    header = f"P6\\n{{WIDTH}} {{HEIGHT}}\\n255\\n".encode("ascii")
    color_on = b"\\x00\\x00\\x00" if not invert else b"\\xff\\xff\\xff"
    color_off = b"\\xff\\xff\\xff" if not invert else b"\\x00\\x00\\x00"
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
        self.root.title("TELL ME WHY 💔 - Dương Domic (Smoking & Car Drive Animation)")
        self.root.geometry(f"{{WINDOW_WIDTH}}x{{WINDOW_HEIGHT}}")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0914")

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
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Consolas", 10, "bold"), fg="#ff70a6", bg="#0d0914", pady=8)
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
        status_text = f"Frame: {{self.current_frame + 1}}/{{self.num_frames}} ({{cur_s:.1f}}s/{{TOTAL_DURATION:.1f}}s) | {{music_text}} [M] | [Space] Play/Pause"
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
            self.status_var.set(f"Tạm dừng (Frame {{self.current_frame + 1}}/{{self.num_frames}})")

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
''')
    print(f"Đã tạo {py_player_file}!")

    # 5. Tạo file run_tellmewhy.bat
    with open("run_tellmewhy.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\npython run_tellmewhy.py\npause\n")

    # 6. Tạo Web Player tell_me_why.html hoàn chỉnh
    print("Đang tạo tell_me_why.html chuẩn Mobile Full-Height & Audio Equalizer...")
    frames_b64 = base64.b64encode(raw_all_bytes).decode('ascii')
    with open(mp3_path, "rb") as af:
        audio_b64 = base64.b64encode(af.read()).decode('ascii')

    # Chuyển mảng chiều cao thanh nhạc thành JSON
    bars_json = json.dumps(bar_heights_per_frame)

    html_code = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>TELL ME WHY 💔 - Dương Domic (Smoking & Car Drive Animation)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --accent-pink: #ff4d8d;
            --accent-purple: #9d4edd;
            --text-main: #f0f4f8;
            --text-muted: #a0aec0;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
            -webkit-user-select: none;
            -webkit-tap-highlight-color: transparent;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            min-height: 100dvh;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(ellipse at 50% 30%, #150d24 0%, #06030c 100%);
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text-main);
            touch-action: manipulation;
        }}
        .glow-1 {{
            position: absolute;
            width: min(80vw, 380px);
            height: min(80vw, 380px);
            background: radial-gradient(circle, rgba(255, 77, 141, 0.22) 0%, transparent 70%);
            top: 8%;
            left: 5%;
            filter: blur(50px);
            pointer-events: none;
        }}
        .glow-2 {{
            position: absolute;
            width: min(85vw, 420px);
            height: min(85vw, 420px);
            background: radial-gradient(circle, rgba(157, 78, 221, 0.2) 0%, transparent 70%);
            bottom: 8%;
            right: 5%;
            filter: blur(60px);
            pointer-events: none;
        }}
        .app-card {{
            position: relative;
            z-index: 2;
            width: 94%;
            max-width: 480px;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(20, 13, 34, 0.85);
            border: 1px solid rgba(255, 105, 180, 0.28);
            border-radius: 24px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65), 0 0 35px rgba(255, 77, 141, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            padding: 16px;
        }}
        .header {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 12px;
            text-align: center;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: rgba(255, 77, 141, 0.16);
            border: 1px solid rgba(255, 77, 141, 0.35);
            color: #ff8fb6;
            padding: 3px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }}
        .song-title {{
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, #ffffff 0%, #ffc2d4 50%, #d8b4fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.2;
        }}
        .song-artist {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2px;
            font-weight: 400;
        }}
        .screen-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 2 / 1;
            border-radius: 16px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.2);
            cursor: pointer;
        }}
        canvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .play-overlay {{
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            background: rgba(10, 6, 20, 0.48);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            transition: opacity 0.3s ease, visibility 0.3s ease;
            z-index: 10;
        }}
        .play-overlay.hidden {{
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }}
        .play-btn-circle {{
            width: 66px;
            height: 66px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff4d8d 0%, #f72585 50%, #9d4edd 100%);
            box-shadow: 0 0 30px rgba(255, 77, 141, 0.8), 0 8px 24px rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            animation: pulseBeat 2s infinite ease-in-out;
        }}
        .play-btn-circle svg {{
            width: 32px;
            height: 32px;
            fill: #ffffff;
            margin-left: 4px;
        }}
        .play-btn-text {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #ffffff;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 5px 16px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            letter-spacing: 0.3px;
        }}
        @keyframes pulseBeat {{
            0%, 100% {{ transform: scale(1); box-shadow: 0 0 22px rgba(255, 77, 141, 0.7); }}
            50% {{ transform: scale(1.08); box-shadow: 0 0 38px rgba(255, 77, 141, 0.95), 0 0 16px rgba(157, 78, 221, 0.8); }}
        }}
        .bottom-bar {{
            width: 100%;
            margin-top: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .progress-track {{
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 3px;
            overflow: hidden;
            cursor: pointer;
            position: relative;
        }}
        .progress-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #ff4d8d, #a855f7);
            border-radius: 3px;
            box-shadow: 0 0 10px rgba(255, 77, 141, 0.8);
            transition: width 0.08s linear;
        }}
        .controls-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 4px;
        }}
        .icon-action-btn {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #ffffff;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }}
        .icon-action-btn:hover, .icon-action-btn:active {{
            background: rgba(255, 77, 141, 0.25);
            border-color: var(--accent-pink);
            transform: scale(1.06);
        }}
        .icon-action-btn svg {{
            width: 18px;
            height: 18px;
            fill: currentColor;
        }}
        .icon-action-btn svg.hidden {{
            display: none;
        }}
        .mode-toggle-btn {{
            background: rgba(255, 77, 141, 0.15);
            border: 1px solid rgba(255, 77, 141, 0.4);
            color: #ffb3ce;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.76rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .mode-toggle-btn:hover {{
            background: rgba(255, 77, 141, 0.3);
            color: #ffffff;
        }}
        .time-tag {{
            font-family: 'Outfit', monospace;
            font-size: 0.82rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
        @media (max-width: 640px) {{
            html, body {{
                width: 100%;
                height: 100%;
                height: 100dvh;
                overflow: hidden;
            }}
            .glow-1 {{
                width: 65vw;
                height: 65vw;
                top: 0;
                left: 0;
                opacity: 0.3;
            }}
            .glow-2 {{
                width: 75vw;
                height: 75vw;
                bottom: 0;
                right: 0;
                opacity: 0.3;
            }}
            .app-card {{
                width: 100%;
                max-width: 100%;
                height: 100%;
                height: 100dvh;
                border-radius: 0;
                border: none;
                box-shadow: none;
                padding: max(8px, env(safe-area-inset-top, 0px)) 12px max(10px, env(safe-area-inset-bottom, 0px));
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                background: rgba(18, 12, 34, 0.94);
            }}
            .header {{
                margin-bottom: 6px;
                flex-shrink: 0;
            }}
            .badge {{
                font-size: 0.72rem;
                padding: 2px 10px;
                margin-bottom: 3px;
            }}
            .song-title {{
                font-size: 1.25rem;
            }}
            .song-artist {{
                font-size: 0.75rem;
            }}
            .screen-wrapper {{
                flex: 1;
                width: 100%;
                height: 100%;
                min-height: 0;
                aspect-ratio: unset;
                border-radius: 18px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.25);
            }}
            .bottom-bar {{
                margin-top: 8px;
                gap: 8px;
                flex-shrink: 0;
            }}
            .controls-row {{
                padding: 0 2px;
            }}
            .icon-action-btn {{
                width: 36px;
                height: 36px;
            }}
            .mode-toggle-btn {{
                padding: 4px 10px;
                font-size: 0.72rem;
            }}
            .time-tag {{
                font-size: 0.76rem;
            }}
        }}
        @media (max-height: 520px) {{
            .header {{
                display: none;
            }}
            .app-card {{
                padding: 4px 10px;
            }}
            .screen-wrapper {{
                flex: 1;
                min-height: 0;
            }}
            .bottom-bar {{
                margin-top: 4px;
                gap: 4px;
            }}
        }}
    </style>
</head>
<body>
    <div class="glow-1"></div>
    <div class="glow-2"></div>

    <div class="app-card">
        <div class="header">
            <div class="badge">💔 TELL ME WHY 💔</div>
            <div class="song-title">TELL ME WHY</div>
            <div class="song-artist">Dương Domic • Feeling Soundzz</div>
        </div>

        <div class="screen-wrapper" id="screenWrapper">
            <canvas id="screenCanvas"></canvas>
            <div class="play-overlay" id="playOverlay">
                <div class="play-btn-circle">
                    <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </div>
                <div class="play-btn-text" id="playBtnText">Chạm để lắng nghe 💔</div>
            </div>
        </div>

        <div class="bottom-bar">
            <div class="progress-track" id="progressTrack">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="controls-row">
                <button class="icon-action-btn" id="btnPlayPause" aria-label="Play/Pause">
                    <svg id="iconPlay" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                    <svg id="iconPause" class="hidden" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                </button>
                <div class="time-tag" id="timeDisplay">00:00 / 00:26</div>
                <button class="mode-toggle-btn" id="btnToggleMode">✨ HD Sắc Nét</button>
                <button class="icon-action-btn" id="btnMute" aria-label="Mute/Unmute">
                    <span id="muteEmoji">🔊</span>
                </button>
            </div>
        </div>
    </div>

    <audio id="bgMusic" loop preload="auto" playsinline>
        <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
    </audio>

    <script>
        const NUM_FRAMES = {NUM_FRAMES};
        const FRAME_DURATION = 0.070;
        const TOTAL_DURATION = {NUM_FRAMES * 0.070:.2f};
        const EQUALIZER_BARS = {bars_json};

        const KARAOKE_TIMED_PHRASES = [
            {{
                start_t: 0.0, end_t: 3.8, action: 1,
                lines: [
                    [{{t: 0.2, w: "Từng"}}, {{t: 0.8, w: "cơn"}}, {{t: 1.4, w: "đau"}}],
                    [{{t: 2.0, w: "tăng"}}, {{t: 2.6, w: "dần"}}, {{t: 3.1, w: "lên..."}}, {{t: 3.5, w: "🌧"}}]
                ]
            }},
            {{
                start_t: 3.8, end_t: 7.5, action: 2,
                lines: [
                    [{{t: 3.9, w: "Thời"}}, {{t: 4.5, w: "gian"}}, {{t: 5.0, w: "trôi"}}],
                    [{{t: 5.6, w: "âm"}}, {{t: 6.2, w: "thầm"}}, {{t: 6.8, w: "đếm..."}}, {{t: 7.2, w: "⏳"}}]
                ]
            }},
            {{
                start_t: 7.5, end_t: 10.8, action: 3,
                lines: [
                    [{{t: 7.6, w: "Nỗi"}}, {{t: 8.1, w: "cô"}}, {{t: 8.6, w: "đơn"}}],
                    [{{t: 9.1, w: "ghé"}}, {{t: 9.5, w: "qua"}}, {{t: 9.9, w: "đêm"}}, {{t: 10.3, w: "nay..."}}, {{t: 10.6, w: "🌙"}}]
                ]
            }},
            {{
                start_t: 10.8, end_t: 14.0, action: 4,
                lines: [
                    [{{t: 10.8, w: "Đêm"}}, {{t: 11.2, w: "qua,"}}, {{t: 11.6, w: "đêm"}}, {{t: 12.0, w: "nay"}}],
                    [{{t: 12.4, w: "anh"}}, {{t: 12.8, w: "chẳng"}}, {{t: 13.2, w: "muốn"}}],
                    [{{t: 13.5, w: "quay"}}, {{t: 13.8, w: "lại..."}}]
                ]
            }},
            {{
                start_t: 14.0, end_t: 17.5, action: 5,
                lines: [
                    [{{t: 14.1, w: "Phải"}}, {{t: 14.6, w: "xa"}}, {{t: 15.1, w: "em"}}],
                    [{{t: 15.6, w: "anh"}}, {{t: 16.2, w: "nào"}}, {{t: 16.8, w: "muốn..."}}, {{t: 17.2, w: "💔"}}]
                ]
            }},
            {{
                start_t: 17.5, end_t: 21.5, action: 6,
                lines: [
                    [{{t: 17.6, w: "Vì"}}, {{t: 18.1, w: "chia"}}, {{t: 18.6, w: "đôi"}}],
                    [{{t: 19.2, w: "vẫn"}}, {{t: 19.8, w: "còn"}}],
                    [{{t: 20.3, w: "thương..."}}, {{t: 20.8, w: "♥"}}, {{t: 21.2, w: "✨"}}]
                ]
            }},
            {{
                start_t: 21.5, end_t: TOTAL_DURATION + 1, action: 7,
                lines: [
                    [{{t: 21.6, w: "✨"}}, {{t: 22.0, w: "TELL"}}, {{t: 22.4, w: "ME"}}, {{t: 22.8, w: "WHY"}}, {{t: 23.2, w: "✨"}}],
                    [{{t: 23.6, w: "Dương"}}, {{t: 24.0, w: "Domic"}}],
                    [{{t: 24.5, w: "Vẫn"}}, {{t: 24.9, w: "còn"}}, {{t: 25.3, w: "thương"}}, {{t: 25.7, w: "nhau..."}}, {{t: 25.9, w: "💖"}}]
                ]
            }}
        ];

        const ALL_BYTES_B64 = "{frames_b64}";
        let allBytes = null;
        try {{
            const binaryStr = atob(ALL_BYTES_B64);
            allBytes = new Uint8Array(binaryStr.length);
            for (let i = 0; i < binaryStr.length; i++) {{
                allBytes[i] = binaryStr.charCodeAt(i);
            }}
        }} catch(e) {{
            console.error("Lỗi giải mã base64:", e);
        }}

        const canvas = document.getElementById('screenCanvas');
        const ctx = canvas.getContext('2d');
        const screenWrapper = document.getElementById('screenWrapper');
        const playOverlay = document.getElementById('playOverlay');
        const playBtnText = document.getElementById('playBtnText');
        const btnPlayPause = document.getElementById('btnPlayPause');
        const iconPlay = document.getElementById('iconPlay');
        const iconPause = document.getElementById('iconPause');
        const progressTrack = document.getElementById('progressTrack');
        const progressFill = document.getElementById('progressFill');
        const timeDisplay = document.getElementById('timeDisplay');
        const btnMute = document.getElementById('btnMute');
        const muteEmoji = document.getElementById('muteEmoji');
        const btnToggleMode = document.getElementById('btnToggleMode');
        const bgMusic = document.getElementById('bgMusic');

        let isPlaying = false;
        let isHDMode = true;

        function resizeCanvas() {{
            const rect = screenWrapper.getBoundingClientRect();
            const dpr = Math.max(2, window.devicePixelRatio || 1);
            canvas.width = Math.round(rect.width * dpr);
            canvas.height = Math.round(rect.height * dpr);
        }}
        window.addEventListener('resize', () => {{
            resizeCanvas();
            render(bgMusic.currentTime || 0);
        }});
        resizeCanvas();

        function getActiveKaraoke(cur_t) {{
            let active = null;
            for (let p of KARAOKE_TIMED_PHRASES) {{
                if (cur_t >= p.start_t && cur_t <= p.end_t) {{
                    active = p;
                    break;
                }}
            }}
            if (!active) active = KARAOKE_TIMED_PHRASES[0];

            let lines = [];
            for (let lineWords of active.lines) {{
                let shown = lineWords.filter(w => cur_t >= w.t).map(w => w.w);
                lines.push(shown.join(" "));
            }}
            return {{ action: active.action, lines }};
        }}

        function drawHeart(ctx, x, y, size, S, fill = true) {{
            ctx.save();
            ctx.fillStyle = '#ff4d8d';
            ctx.strokeStyle = '#000000';
            ctx.beginPath();
            const topY = (y - size * 0.3) * S;
            ctx.moveTo(x * S, (y + size) * S);
            ctx.bezierCurveTo((x - size * 1.2) * S, (y + size * 0.2) * S, (x - size * 1.2) * S, topY, x * S, (y - size * 0.1) * S);
            ctx.bezierCurveTo((x + size * 1.2) * S, topY, (x + size * 1.2) * S, (y + size * 0.2) * S, x * S, (y + size) * S);
            if (fill) ctx.fill();
            ctx.stroke();
            ctx.restore();
        }}

        function drawStar(ctx, x, y, r, S) {{
            ctx.beginPath();
            ctx.moveTo(x * S, (y - r) * S);
            ctx.lineTo(x * S, (y + r) * S);
            ctx.moveTo((x - r) * S, y * S);
            ctx.lineTo((x + r) * S, y * S);
            ctx.stroke();
        }}

        function renderPixelFrame(cur_t) {{
            if (!allBytes) return;
            const S = Math.min(canvas.width / 128.0, canvas.height / 64.0);
            const offsetX = Math.round((canvas.width - 128 * S) / 2);
            const offsetY = Math.round((canvas.height - 64 * S) / 2);
            const frameIdx = Math.min(NUM_FRAMES - 1, Math.floor(cur_t / FRAME_DURATION));

            ctx.imageSmoothingEnabled = false;
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(offsetX, offsetY);

            const startByte = frameIdx * 1024;
            ctx.fillStyle = '#000000';

            for (let y = 0; y < 64; y++) {{
                for (let x = 0; x < 128; x++) {{
                    const byteIdx = startByte + y * 16 + Math.floor(x / 8);
                    const bitIdx = 7 - (x % 8);
                    const pixelOn = (allBytes[byteIdx] >> bitIdx) & 1;
                    if (!pixelOn) {{
                        ctx.fillRect(Math.round(x * S), Math.round(y * S), Math.ceil(S), Math.ceil(S));
                    }}
                }}
            }}
            ctx.restore();
            updateProgress(cur_t);
        }}

        function render(cur_t) {{
            if (!isHDMode) {{
                renderPixelFrame(cur_t);
                return;
            }}

            const S = Math.min(canvas.width / 128.0, canvas.height / 64.0);
            const offsetX = Math.round((canvas.width - 128 * S) / 2);
            const offsetY = Math.round((canvas.height - 64 * S) / 2);
            const f = Math.min(NUM_FRAMES - 1, Math.floor(cur_t / 0.070));
            const beatBounce = Math.abs(Math.sin(cur_t * Math.PI * 2.1)) * 1.5;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(offsetX, offsetY);

            const lw = Math.max(1.8, S * 0.38);
            ctx.lineWidth = lw;
            ctx.strokeStyle = '#000000';
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            // 1. Đường đất chạy ngang tràn viền tại Y = 53
            ctx.beginPath();
            ctx.moveTo(-offsetX, 53 * S);
            ctx.lineTo(canvas.width - offsetX, 53 * S);
            ctx.stroke();

            // 2. EQUALIZER BARS NHẢY THEO NHẠC DƯỚI ĐƯỜNG ĐẤT (Y: 55 đến 63)
            const currentBars = EQUALIZER_BARS[f] || [];
            ctx.fillStyle = '#111827';
            for (let b = 0; b < 24; b++) {{
                const bh = currentBars[b] || 1;
                const bx = (4 + b * 5) * S;
                const bw = 3 * S;
                const by = (63 - bh) * S;
                const bHeight = bh * S;
                ctx.fillRect(bx, by, bw, bHeight);
            }}

            // 3. Vách ngăn dải chấm ở giữa
            ctx.fillStyle = '#000000';
            for (let dy = 6; dy < 50; dy += 4) {{
                ctx.beginPath();
                ctx.arc(56 * S, dy * S, S * 0.28, 0, Math.PI * 2);
                ctx.fill();
            }}

            // 4. Karaoke lời bài hát bên phải (X=92)
            const {{ action, lines }} = getActiveKaraoke(cur_t);
            const text_x = 92 * S;
            const y_starts = lines.length === 2 
                ? [20 * S, 34 * S]
                : (lines.length === 3 ? [15 * S, 27 * S, 39 * S] : [9 * S, 19 * S, 29 * S, 39 * S]);

            const fontSize = Math.round(S * 3.6);
            ctx.font = `bold ${{fontSize}}px "Outfit", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#111827';

            lines.forEach((lineText, idx) => {{
                if (lineText && idx < y_starts.length) {{
                    ctx.fillText(lineText, text_x, y_starts[idx]);
                }}
            }});

            // Hạt mưa rơi nhẹ
            ctx.strokeStyle = '#000000';
            [8, 22, 35, 48].forEach((rx, s_idx) => {{
                const ry = ((f * 3 + (s_idx + 1) * 11) % 44) + 6;
                if (ry < 52) {{
                    ctx.beginPath();
                    ctx.moveTo(rx * S, ry * S);
                    ctx.lineTo((rx - 1) * S, (ry + 2.5) * S);
                    ctx.stroke();
                }}
            }});

            // 5. DIỄN HOẠT CỰC BUỒN BÊN TRÁI (X: 0..55)
            if (action === 1) {{
                // ACTION 1: Hút thuốc dưới cột đèn đường đêm mưa
                const bx = 28;
                const by = 31 - beatBounce;

                // Cột đèn
                ctx.beginPath();
                ctx.moveTo(8 * S, 12 * S);
                ctx.lineTo(8 * S, 53 * S);
                ctx.moveTo(7 * S, 12 * S);
                ctx.lineTo(14 * S, 8 * S);
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(15 * S, 12 * S, 4 * S, Math.PI, 0);
                ctx.stroke();

                // Quầng sáng mờ từ đèn
                ctx.fillStyle = 'rgba(0,0,0,0.05)';
                ctx.beginPath();
                ctx.moveTo(15 * S, 12 * S);
                ctx.lineTo(0, 53 * S);
                ctx.lineTo(24 * S, 53 * S);
                ctx.closePath();
                ctx.fill();

                // Chàng trai
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(bx * S, by * S, 4.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Mắt nhắm buồn
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, (by + 1) * S);
                ctx.stroke();

                // Áo măng-tô
                ctx.beginPath();
                ctx.moveTo((bx - 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 5.5) * S, (by + 16) * S);
                ctx.lineTo((bx - 5.5) * S, (by + 16) * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Tay cầm điếu thuốc
                ctx.beginPath();
                ctx.moveTo((bx + 3) * S, (by + 8) * S);
                ctx.lineTo((bx + 6) * S, (by + 2) * S);
                ctx.lineTo((bx + 10) * S, (by + 1) * S);
                ctx.stroke();

                // Tàn thuốc đỏ nhấp nháy
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx + 10) * S, (by + 1) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Khói thuốc bay lượn
                ctx.strokeStyle = '#000000';
                for (let k = 1; k < 8; k++) {{
                    const sy = (by - k * 2.2) * S;
                    const sx = (bx + 10 + Math.sin(f * 0.35 + k * 0.8) * (k * 0.8)) * S;
                    ctx.beginPath();
                    ctx.arc(sx, sy, S * (0.4 + k * 0.15), 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Chân
                ctx.beginPath();
                ctx.moveTo((bx - 2) * S, (by + 16) * S);
                ctx.lineTo((bx - 2) * S, 53 * S);
                ctx.moveTo((bx + 2) * S, (by + 16) * S);
                ctx.lineTo((bx + 2) * S, 53 * S);
                ctx.stroke();

            }} else if (action === 2) {{
                // ACTION 2: Rít thuốc, nhả khói thành vòng tròn (Smoke Rings)
                const bx = 20;
                const by = 30 - beatBounce;

                // Đầu ngửa nhìn nghiêng
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(bx * S, by * S, 4.8 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Tóc
                ctx.fillStyle = '#000000';
                ctx.beginPath();
                ctx.moveTo((bx - 5) * S, (by - 2) * S);
                ctx.lineTo((bx - 6) * S, (by - 6) * S);
                ctx.lineTo(bx * S, (by - 7) * S);
                ctx.lineTo((bx + 4) * S, (by - 3) * S);
                ctx.closePath();
                ctx.fill();

                // Mắt nghiêng
                ctx.beginPath();
                ctx.arc((bx + 1) * S, by * S, 0.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Thân
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.roundRect((bx - 4) * S, (by + 6) * S, 8 * S, 10 * S, 2 * S);
                ctx.fill();
                ctx.stroke();

                // Điếu thuốc kẹp trên tay
                ctx.beginPath();
                ctx.moveTo((bx + 3) * S, (by + 8) * S);
                ctx.lineTo((bx + 6) * S, (by + 12) * S);
                ctx.lineTo((bx + 9) * S, (by + 13) * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx + 9) * S, (by + 13) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // 2 vòng khói tròn (Smoke rings)
                ctx.strokeStyle = '#000000';
                const ring_phase = (f * 0.8) % 24;
                const r1_y = (by - 2 - ring_phase * 0.6) * S;
                const r1_x = (bx + 8 + ring_phase * 0.8) * S;
                ctx.beginPath();
                ctx.ellipse(r1_x, r1_y, 3 * S, 1.8 * S, 0, 0, Math.PI * 2);
                ctx.stroke();

                const r2_y = (by - 6 - ((ring_phase + 10) % 24) * 0.6) * S;
                const r2_x = (bx + 14 + ((ring_phase + 10) % 24) * 0.8) * S;
                ctx.beginPath();
                ctx.ellipse(r2_x, r2_y, 4.2 * S, 2.5 * S, 0, 0, Math.PI * 2);
                ctx.stroke();

                // Đồng hồ cát
                ctx.beginPath();
                ctx.moveTo(40 * S, 8 * S);
                ctx.lineTo(50 * S, 8 * S);
                ctx.lineTo(45 * S, 14 * S);
                ctx.lineTo(50 * S, 20 * S);
                ctx.lineTo(40 * S, 20 * S);
                ctx.lineTo(45 * S, 14 * S);
                ctx.closePath();
                ctx.stroke();

                // Chân
                ctx.beginPath();
                ctx.moveTo((bx - 2) * S, (by + 16) * S);
                ctx.lineTo((bx - 2) * S, 53 * S);
                ctx.moveTo((bx + 2) * S, (by + 16) * S);
                ctx.lineTo((bx + 2) * S, 53 * S);
                ctx.stroke();

            }} else if (action === 3) {{
                // ACTION 3: LÁI XE TRONG ĐÊM MƯA CÔ ĐỘC (NIGHT DRIVE)
                const car_y = 42 * S;
                // Thân xe
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.rect(6 * S, car_y, 42 * S, 7 * S);
                ctx.fill();
                ctx.stroke();

                // Mui xe & kính
                ctx.beginPath();
                ctx.moveTo(14 * S, car_y);
                ctx.lineTo(20 * S, car_y - 9 * S);
                ctx.lineTo(36 * S, car_y - 9 * S);
                ctx.lineTo(42 * S, car_y);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Kính xe trong suốt
                ctx.fillStyle = 'rgba(0,0,0,0.06)';
                ctx.beginPath();
                ctx.moveTo(20 * S, car_y - 1 * S);
                ctx.lineTo(22 * S, car_y - 8 * S);
                ctx.lineTo(34 * S, car_y - 8 * S);
                ctx.lineTo(38 * S, car_y - 1 * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Người lái xe bên trong
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(28 * S, car_y - 4 * S, 3 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Tay lái & điếu thuốc gác cửa sổ
                ctx.beginPath();
                ctx.moveTo(27 * S, car_y - 2 * S);
                ctx.lineTo(20 * S, car_y - 3 * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc(19 * S, car_y - 3 * S, 1 * S, 0, Math.PI * 2);
                ctx.fill();

                // Khói thuốc bay lùi về sau
                ctx.strokeStyle = '#000000';
                for (let k = 1; k < 6; k++) {{
                    ctx.beginPath();
                    ctx.arc((18 - k * 2.5) * S, (car_y - 3 * S - Math.sin(f * 0.5 + k) * 2 * S), 0.8 * S, 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Bánh xe
                [16, 40].forEach(wx => {{
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(wx * S, car_y + 7 * S, 4.5 * S, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.stroke();
                    // Vành xe xoay
                    ctx.beginPath();
                    ctx.arc(wx * S, car_y + 7 * S, 1.8 * S, 0, Math.PI * 2);
                    ctx.stroke();
                }});

                // Đèn pha xe chiếu sáng phía trước
                ctx.fillStyle = 'rgba(255, 77, 141, 0.15)';
                ctx.beginPath();
                ctx.moveTo(48 * S, car_y + 2 * S);
                ctx.lineTo(55 * S, car_y - 3 * S);
                ctx.lineTo(55 * S, car_y + 8 * S);
                ctx.closePath();
                ctx.fill();

            }} else if (action === 4) {{
                // ACTION 4: CẦN GẠT NƯỚC KÍNH CHẮN GIÓ & GƯƠNG CHIẾU HẬU
                // Gương chiếu hậu
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.roundRect(14 * S, 8 * S, 28 * S, 12 * S, 3 * S);
                ctx.fill();
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(28 * S, 4 * S);
                ctx.lineTo(28 * S, 8 * S);
                ctx.stroke();

                // Đôi mắt nhìn trong gương
                ctx.beginPath();
                ctx.arc(22 * S, 14 * S, 2 * S, 0, Math.PI);
                ctx.arc(34 * S, 14 * S, 2 * S, 0, Math.PI);
                ctx.stroke();
                ctx.fillStyle = '#000000';
                ctx.beginPath();
                ctx.arc(22 * S, 14 * S, 0.8 * S, 0, Math.PI * 2);
                ctx.arc(34 * S, 14 * S, 0.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Kính chắn gió bên dưới
                ctx.strokeStyle = '#000000';
                ctx.strokeRect(4 * S, 24 * S, 48 * S, 28 * S);

                // Cần gạt nước gạt qua lại
                const wiper_x = 28 + Math.sin(f * 0.45) * 16;
                ctx.beginPath();
                ctx.moveTo(28 * S, 51 * S);
                ctx.lineTo(wiper_x * S, 28 * S);
                ctx.stroke();
                // Thanh gạt cao su
                ctx.lineWidth = lw * 1.5;
                ctx.beginPath();
                ctx.moveTo((wiper_x - 5) * S, 28 * S);
                ctx.lineTo((wiper_x + 5) * S, 28 * S);
                ctx.stroke();
                ctx.lineWidth = lw;

            }} else if (action === 5) {{
                // ACTION 5: ĐỖ XE VEN ĐƯỜNG, TỰA XE HÚT THUỐC DƯỚI MƯA
                // Xe đỗ góc trái
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.rect(2 * S, 40 * S, 24 * S, 8 * S);
                ctx.fill();
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(6 * S, 40 * S);
                ctx.lineTo(12 * S, 33 * S);
                ctx.lineTo(22 * S, 33 * S);
                ctx.lineTo(26 * S, 40 * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Chàng trai tựa xe
                const bx = 32;
                const by = 31;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(bx * S, by * S, 4.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Mắt nhắm buồn cúi gằm
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, (by + 1) * S);
                ctx.stroke();

                // Áo tựa nghiêng
                ctx.beginPath();
                ctx.moveTo((bx - 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 5.5) * S, (by + 16) * S);
                ctx.lineTo((bx - 5.5) * S, (by + 16) * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Tay chụm che điếu thuốc
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 8) * S);
                ctx.lineTo((bx + 4) * S, (by + 4) * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx + 5) * S, (by + 4) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Trái tim vỡ nhói đau
                drawHeart(ctx, bx + 10, by - 3, 3 * S, 1, false);

                // Chân tựa xe
                ctx.strokeStyle = '#000000';
                ctx.beginPath();
                ctx.moveTo((bx - 2) * S, (by + 16) * S);
                ctx.lineTo((bx - 5) * S, 53 * S);
                ctx.moveTo((bx + 2) * S, (by + 16) * S);
                ctx.lineTo((bx + 1) * S, 53 * S);
                ctx.stroke();

            }} else if (action === 6) {{
                // ACTION 6: NGỒI TRÊN XE, NHÌN MÀN HÌNH ĐIỆN THOẠI PHÁT SÁNG
                const bx = 24;
                const by = 28 - beatBounce;

                // Thân xe dưới chân
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(8 * S, 46 * S, 40 * S, 7 * S);
                ctx.strokeRect(8 * S, 46 * S, 40 * S, 7 * S);

                // Chàng trai
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(bx * S, by * S, 4.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                ctx.beginPath();
                ctx.roundRect((bx - 4) * S, (by + 6) * S, 8 * S, 10 * S, 2 * S);
                ctx.fill();
                ctx.stroke();

                // Màn hình điện thoại phát sáng
                ctx.fillStyle = '#ff4d8d';
                ctx.fillRect((bx + 7) * S, (by + 7) * S, 5 * S, 7 * S);
                ctx.strokeRect((bx + 7) * S, (by + 7) * S, 5 * S, 7 * S);

                // Điếu thuốc kẹp trên tay buông xuống
                ctx.strokeStyle = '#000000';
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 8) * S);
                ctx.lineTo((bx - 8) * S, (by + 13) * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx - 8) * S, (by + 13) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Trái tim lớn đập phập phồng đau nhói
                const heartSize = 4.2 + beatBounce * 1.5;
                const hy = 13 - Math.sin(f * 0.3) * 2;
                drawHeart(ctx, 40, hy, heartSize, S);

            }} else if (action === 7) {{
                // ACTION 7: XE LĂN BÁNH XA DẦN VÀO MÀN ĐÊM VÔ TẬN
                // Con đường hun hút về điểm vô cực (28, 26)
                ctx.beginPath();
                ctx.moveTo(28 * S, 26 * S);
                ctx.lineTo(6 * S, 53 * S);
                ctx.moveTo(28 * S, 26 * S);
                ctx.lineTo(50 * S, 53 * S);
                ctx.stroke();

                // Chiếc xe nhỏ dần lùi về phía xa
                const car_dist = Math.sin(f * 0.1) * 2;
                const cx = 28;
                const cy = 38 + car_dist;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.rect((cx - 8) * S, cy * S, 16 * S, 6 * S);
                ctx.fill();
                ctx.stroke();

                // Đèn hậu đỏ
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((cx - 6) * S, (cy + 3) * S, 1.5 * S, 0, Math.PI * 2);
                ctx.arc((cx + 6) * S, (cy + 3) * S, 1.5 * S, 0, Math.PI * 2);
                ctx.fill();

                // Khói xả ống pô
                ctx.strokeStyle = '#000000';
                ctx.beginPath();
                ctx.arc((cx - 8) * S, (cy + 6) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.stroke();

                // Sao lấp lánh trên bầu trời
                drawStar(ctx, 12, 10, 2.5, S);
                drawStar(ctx, 44, 8, 2.5, S);
            }}

            ctx.restore();
            updateProgress(cur_t);
        }}

        function updateProgress(cur_t) {{
            const ratio = Math.min(1, Math.max(0, cur_t / TOTAL_DURATION));
            progressFill.style.width = (ratio * 100) + '%';

            const curSec = Math.floor(cur_t);
            const totSec = Math.floor(TOTAL_DURATION);
            const curStr = `00:${{curSec < 10 ? '0' : ''}}${{curSec}}`;
            const totStr = `00:${{totSec < 10 ? '0' : ''}}${{totSec}}`;
            timeDisplay.textContent = `${{curStr}} / ${{totStr}}`;
        }}

        function step() {{
            if (!isPlaying) return;

            const cur_t = bgMusic.currentTime;
            render(cur_t);

            if (cur_t >= TOTAL_DURATION || bgMusic.ended) {{
                bgMusic.currentTime = 0;
                bgMusic.play().catch(() => {{}});
            }}
            requestAnimationFrame(step);
        }}

        function play() {{
            isPlaying = true;
            playOverlay.classList.add('hidden');
            iconPlay.classList.add('hidden');
            iconPause.classList.remove('hidden');

            bgMusic.play().then(() => {{
                requestAnimationFrame(step);
            }}).catch(e => {{
                console.log("Audio play deferred:", e);
                requestAnimationFrame(step);
            }});
        }}

        function pause() {{
            isPlaying = false;
            playOverlay.classList.remove('hidden');
            playBtnText.textContent = 'Tiếp tục 💔';
            iconPlay.classList.remove('hidden');
            iconPause.classList.add('hidden');

            bgMusic.pause();
        }}

        function togglePlay() {{
            if (isPlaying) {{
                pause();
            }} else {{
                play();
            }}
        }}

        screenWrapper.addEventListener('click', togglePlay);
        btnPlayPause.addEventListener('click', (e) => {{
            e.stopPropagation();
            togglePlay();
        }});

        btnMute.addEventListener('click', (e) => {{
            e.stopPropagation();
            bgMusic.muted = !bgMusic.muted;
            muteEmoji.textContent = bgMusic.muted ? '🔇' : '🔊';
        }});

        progressTrack.addEventListener('click', (e) => {{
            e.stopPropagation();
            const rect = progressTrack.getBoundingClientRect();
            const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            bgMusic.currentTime = pos * TOTAL_DURATION;
            render(bgMusic.currentTime);
        }});

        btnToggleMode.addEventListener('click', (e) => {{
            e.stopPropagation();
            isHDMode = !isHDMode;
            btnToggleMode.textContent = isHDMode ? '✨ HD Sắc Nét' : '👾 Pixel Cổ Điển';
            render(bgMusic.currentTime);
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                togglePlay();
            }} else if (e.key === 'm' || e.key === 'M') {{
                btnMute.click();
            }}
        }});

        render(0);
    </script>
</body>
</html>
'''

    with open("tell_me_why.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("Đã tạo tell_me_why.html thành công!")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("Đã cập nhật index.html thành công!")

    print("\n=== HOÀN TẤT BỘ ANIMATION CỰC BUỒN & AUDIO EQUALIZER! ===")
    print("1. tellmewhy_frames.bin (Dữ liệu OLED SSD1306 có equalizer)")
    print("2. tellmewhy.gif (Ảnh GIF 384x192 khói thuốc, lái xe & thanh nhạc)")
    print("3. tell_me_why.cpp (C++ SFML độc lập)")
    print("4. run_tellmewhy.py + run_tellmewhy.bat (Trình phát Desktop native)")
    print("5. tell_me_why.html & index.html (Web Player siêu mượt Mobile Full-Height)")

if __name__ == "__main__":
    main()
