"""
Pipeline tạo trọn bộ Animation Siêu Chi Tiết & Audio Visualizer Đồng Bộ Nhịp Nhạc
Bài hát: TELL ME WHY - Dương Domic
Thời lượng: ~26.04s (372 frames @ 70ms/frame)
Chủ đề: Sad Boy Lo-Fi Cinematic (Hút thuốc, Lái xe thể thao, Cần gạt nước kính xe, Đèn đường đêm mưa, Màn hình điện thoại phát sáng)
Dưới đường đất: 24 thanh nhạc Equalizer nhảy theo phổ tần số FFT âm thanh thực tế.
"""

import os
import sys
import wave
import struct
import math
import base64
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    wav_path = "tellmewhy.wav"
    mp3_path = "tellmewhy.mp3"

    if not os.path.exists(wav_path):
        print(f"Lỗi: Không tìm thấy {wav_path}")
        return

    print("Đang đọc và phân tích âm thanh FFT từ WAV...")
    w = wave.open(wav_path, 'r')
    rate = w.getframerate()
    nchannels = w.getnchannels()
    nframes = w.getnframes()
    raw_audio = w.readframes(nframes)
    w.close()

    total_samples = nframes * nchannels
    samples = np.frombuffer(raw_audio, dtype=np.int16)
    if nchannels > 1:
        samples = samples[::nchannels]  # Mono channel

    FRAME_MS = 70
    FRAME_SEC = FRAME_MS / 1000.0
    frame_samples = int(rate * FRAME_SEC)
    NUM_FRAMES = len(samples) // frame_samples

    print(f"Tổng số frame: {NUM_FRAMES} (Rate: {rate}Hz, Thời lượng: {NUM_FRAMES * FRAME_SEC:.2f}s)")

    # 1. TÍNH NĂNG LƯỢNG RMS & PHỔ TẦN SỐ FFT (24 BANDS CHO EQUALIZER BARS)
    energies = []
    num_bars = 24
    freq_bins = np.logspace(np.log10(40), np.log10(8000), num_bars + 1)
    bin_indices = np.clip((freq_bins / (rate / 2.0) * (frame_samples // 2)).astype(int), 0, frame_samples // 2)

    all_bars_raw = np.zeros((NUM_FRAMES, num_bars))

    for f in range(NUM_FRAMES):
        chunk = samples[f * frame_samples : (f + 1) * frame_samples].astype(float)
        rms = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0
        energies.append(rms)

        # FFT
        windowed = chunk * np.hanning(len(chunk))
        fft_vals = np.abs(np.fft.rfft(windowed))
        for b in range(num_bars):
            start_i = bin_indices[b]
            end_i = max(start_i + 1, bin_indices[b + 1])
            mag = np.mean(fft_vals[start_i:end_i]) if end_i > start_i else fft_vals[start_i]
            all_bars_raw[f, b] = mag

    # Chuẩn hoá thanh nhạc theo từng dải tần để các dải cao cũng nhảy đẹp
    max_vals = np.percentile(all_bars_raw, 96, axis=0)
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
    except Exception:
        font_lyrics = ImageFont.load_default()

    def s_to_f(s):
        return round(s / 0.070)

    # 7 Phân đoạn lời bài hát đồng bộ từng từ theo giây (Tell Me Why - Dương Domic)
    KARAOKE_TIMED_PHRASES = [
        # Câu 1 (0.0s -> 3.8s) - Hút thuốc dưới đèn đường đêm mưa
        {
            "start_f": 0, "end_f": s_to_f(3.8), "action": 1,
            "lines": [
                [(0.2, "Từng"), (0.8, "cơn"), (1.4, "đau")],
                [(2.0, "tăng"), (2.6, "dần"), (3.1, "lên...")]
            ]
        },
        # Câu 2 (3.8s -> 7.5s) - Thở vòng khói tròn, đồng hồ cát
        {
            "start_f": s_to_f(3.8), "end_f": s_to_f(7.5), "action": 2,
            "lines": [
                [(3.9, "Thời"), (4.5, "gian"), (5.0, "trôi")],
                [(5.6, "âm"), (6.2, "thầm"), (6.8, "đếm...")]
            ]
        },
        # Câu 3 (7.5s -> 10.8s) - Lái xe trong đêm mưa một mình
        {
            "start_f": s_to_f(7.5), "end_f": s_to_f(10.8), "action": 3,
            "lines": [
                [(7.6, "Nỗi"), (8.1, "cô"), (8.6, "đơn")],
                [(9.1, "ghé"), (9.5, "qua"), (9.9, "đêm"), (10.3, "nay...")]
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
                [(15.6, "anh"), (16.2, "nào"), (16.8, "muốn...")]
            ]
        },
        # Câu 6 (17.5s -> 21.5s) - Nhìn điện thoại le lói, tim đau thắt
        {
            "start_f": s_to_f(17.5), "end_f": s_to_f(21.5), "action": 6,
            "lines": [
                [(17.6, "Vì"), (18.1, "chia"), (18.6, "đôi")],
                [(19.2, "vẫn"), (19.8, "còn")],
                [(20.3, "thương...")]
            ]
        },
        # Câu 7 (21.5s -> 26.04s) - Xe lăn bánh xa dần vào màn đêm
        {
            "start_f": s_to_f(21.5), "end_f": NUM_FRAMES, "action": 7,
            "lines": [
                [(21.6, "*"), (22.0, "TELL"), (22.4, "ME"), (22.8, "WHY"), (23.2, "*")],
                [(23.6, "Dương"), (24.0, "Domic")],
                [(24.5, "Vẫn"), (24.9, "còn"), (25.3, "thương"), (25.7, "nhau...")]
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

    print("Đang vẽ hoạt cảnh pixel siêu chi tiết & thanh nhạc Equalizer...")
    frame_images = []
    raw_all_bytes = bytearray()

    for f in range(NUM_FRAMES):
        img = Image.new('1', (128, 64), 1)  # 1 = Nền trắng
        draw = ImageDraw.Draw(img)
        energy = norm_energies[f]
        beat_bounce = int(energy * 2.5)

        # 1. Đường đất chạy ngang tại Y = 53
        draw.line([(0, 53), (127, 53)], fill=0)

        # 2. VẼ 24 THANH NHẠC EQUALIZER NHẢY DƯỚI ĐƯỜNG ĐẤT (Y: 55 đến 63)
        bars_h = bar_heights_per_frame[f]
        for b_idx in range(num_bars):
            bx = 4 + b_idx * 5
            bh = bars_h[b_idx]
            # Segmented LED style
            for seg in range(bh):
                sy = 63 - seg
                draw.line([(bx, sy), (bx + 2, sy)], fill=0)

        # 3. Dải phân cách dọc chấm ở giữa (X = 56, Y = 4 đến 48)
        for dy in range(4, 51, 3):
            draw.point((56, dy), fill=0)

        # 4. LỜI BÀI HÁT KARAOKE BÊN PHẢI (X: 58 đến 126, tâm tại X=92)
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

        # 5. MƯA RƠI NHẸ TRONG NỀN
        for rx, r_seed in [(6, 5), (17, 13), (32, 9), (47, 21), (25, 17)]:
            ry = ((f * 3 + r_seed * 7) % 46) + 4
            if ry < 52:
                draw.line([(rx, ry), (rx - 1, ry + 3)], fill=0)

        # 6. DIỄN HOẠT SIÊU CHI TIẾT BÊN TRÁI (X: 0..55)
        if action == 1:
            # --- ACTION 1: VINTAGE STREET LAMP & TRENCH COAT BOY ---
            # Cột đèn đường cổ điển X=7
            draw.line([(7, 8), (7, 52)], fill=0)
            draw.line([(8, 10), (8, 52)], fill=0)
            draw.polygon([(4, 52), (10, 52), (9, 49), (5, 49)], outline=0, fill=0)
            # Tay đèn uốn cong
            draw.arc([4, 6, 12, 14], 180, 270, fill=0)
            draw.line([(8, 6), (15, 6)], fill=0)
            draw.arc([11, 6, 17, 12], 270, 360, fill=0)
            # Lồng đèn & bóng sáng
            draw.polygon([(13, 9), (19, 9), (18, 11), (14, 11)], outline=0, fill=0)
            draw.rectangle([14, 11, 18, 17], outline=0, fill=1)
            draw.point([(16, 14)], fill=0)
            draw.line([(14, 17), (16, 20)], fill=0)
            draw.line([(18, 17), (16, 20)], fill=0)

            # Quầng sáng rọi xuống vỉa hè
            for ly in range(21, 52, 3):
                dx = int((ly - 21) * 0.45)
                if 16 - dx >= 0: draw.point([(16 - dx, ly)], fill=0)
                if 16 + dx <= 54: draw.point([(16 + dx, ly)], fill=0)

            # Chàng trai đứng hút thuốc
            bx = 28
            by = 28 - beat_bounce

            # Đầu & Tóc anime lãng tử
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx-1, by-9), (bx+5, by-7), (bx+5, by-2), (bx+2, by-1)], outline=0, fill=0)
            # Mắt nhắm buồn cúi nhìn
            draw.line([(bx-3, by), (bx-1, by+1)], fill=0)
            draw.line([(bx+1, by+1), (bx+3, by)], fill=0)
            draw.line([(bx-3, by-2), (bx-1, by-3)], fill=0)
            draw.line([(bx+1, by-3), (bx+3, by-2)], fill=0)

            # Điếu thuốc ngậm trên môi
            draw.line([(bx+1, by+3), (bx+6, by+3)], fill=0)
            if f % 4 < 3:
                draw.point([(bx+7, by+3)], fill=0) # Tàn đỏ

            # Làn khói thuốc uốn lượn hình chữ S
            for i in range(1, 10):
                sy = by + 3 - i * 2
                sx = int(bx + 7 + math.sin(f * 0.35 + i * 0.7) * (i * 0.85))
                if 0 <= sx < 55 and sy > 2:
                    draw.point([(sx, sy)], fill=0)

            # Áo khoác dài cổ bẻ cao
            draw.polygon([(bx-4, by+6), (bx-2, by+4), (bx+2, by+4), (bx+4, by+6), (bx+3, by+9), (bx-3, by+9)], outline=0, fill=0)
            draw.polygon([(bx-5, by+8), (bx+5, by+8), (bx+6, by+19), (bx-6, by+19)], outline=0, fill=1)
            draw.line([(bx, by+8), (bx, by+19)], fill=0)
            draw.line([(bx-4, by+13), (bx-2, by+15)], fill=0) # Túi áo
            draw.line([(bx+4, by+13), (bx+2, by+15)], fill=0)

            # Quần & Giày
            draw.line([(bx-3, by+20), (bx-3, 50)], fill=0)
            draw.line([(bx+2, by+20), (bx+2, 50)], fill=0)
            draw.rectangle([bx-5, 50, bx-2, 52], fill=0)
            draw.rectangle([bx+1, 50, bx+4, 52], fill=0)

            # Vệt nước phản chiếu vỉa hè
            draw.ellipse([bx-7, 51, bx+9, 53], outline=0, fill=1)

        elif action == 2:
            # --- ACTION 2: RÍT THUỐC, THỞ VÒNG KHÓI TRÒN & ĐỒNG HỒ CÁT ---
            bx = 18
            by = 28 - beat_bounce

            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-6, by-3), (bx-5, by-8), (bx+1, by-9), (bx+5, by-6), (bx+5, by-1), (bx+1, by-2)], outline=0, fill=0)
            draw.line([(bx, by), (bx+2, by+1)], fill=0)
            draw.point([(bx+4, by+2)], fill=0) # Miệng thở khói

            # Áo & Cổ áo
            draw.polygon([(bx-4, by+6), (bx-2, by+4), (bx+2, by+4), (bx+4, by+6), (bx+3, by+9), (bx-3, by+9)], outline=0, fill=0)
            draw.polygon([(bx-5, by+8), (bx+5, by+8), (bx+6, by+19), (bx-6, by+19)], outline=0, fill=1)

            # Tay kẹp điếu thuốc
            draw.line([(bx+3, by+9), (bx+7, by+12)], fill=0)
            draw.line([(bx+7, by+12), (bx+11, by+11)], fill=0)
            draw.point([(bx+12, by+11)], fill=0)

            # 3 Vòng khói tròn bay lên mở rộng dần
            ring_t = (f * 0.7) % 20
            # Vòng 1
            r1_x = int(bx + 6 + ring_t * 0.5)
            r1_y = int(by + 1 - ring_t * 0.5)
            if 0 <= r1_x < 38 and r1_y > 2:
                draw.ellipse([r1_x-2, r1_y-1, r1_x+2, r1_y+1], outline=0, fill=1)
            # Vòng 2
            p2 = (ring_t + 7) % 20
            r2_x = int(bx + 11 + p2 * 0.6)
            r2_y = int(by - 3 - p2 * 0.5)
            if 0 <= r2_x < 38 and r2_y > 2:
                draw.ellipse([r2_x-3, r2_y-2, r2_x+3, r2_y+2], outline=0, fill=1)
            # Vòng 3
            p3 = (ring_t + 14) % 20
            r3_x = int(bx + 16 + p3 * 0.7)
            r3_y = int(by - 7 - p3 * 0.5)
            if 0 <= r3_x < 38 and r3_y > 2:
                draw.ellipse([r3_x-4, r3_y-2, r3_x+4, r3_y+2], outline=0, fill=1)

            # Chân & Giày
            draw.line([(bx-3, by+20), (bx-3, 50)], fill=0)
            draw.line([(bx+2, by+20), (bx+2, 50)], fill=0)
            draw.rectangle([bx-5, 50, bx-2, 52], fill=0)
            draw.rectangle([bx+1, 50, bx+4, 52], fill=0)

            # Đồng hồ cát cổ điển tại X=45, Y=16
            hx, hy = 45, 16
            draw.line([(hx-6, hy-8), (hx+6, hy-8)], fill=0)
            draw.line([(hx-5, hy-7), (hx+5, hy-7)], fill=0)
            draw.line([(hx-6, hy+8), (hx+6, hy+8)], fill=0)
            draw.line([(hx-5, hy+7), (hx+5, hy+7)], fill=0)
            draw.polygon([(hx-4, hy-6), (hx+4, hy-6), (hx+1, hy), (hx-1, hy)], outline=0, fill=1)
            draw.polygon([(hx-1, hy), (hx+1, hy), (hx+4, hy+6), (hx-4, hy+6)], outline=0, fill=1)
            draw.polygon([(hx-3, hy-4), (hx+3, hy-4), (hx, hy-1)], fill=0)
            draw.point([(hx, hy + 1 + (f % 4))], fill=0)
            draw.polygon([(hx-3, hy+6), (hx+3, hy+6), (hx, hy+4)], fill=0)

        elif action == 3:
            # --- ACTION 3: JDM SPORTS COUPE WITH SPINNING RIMS & HEADLIGHTS ---
            car_y = 39

            # Mũi xe & cản trước
            draw.line([(44, car_y + 4), (52, car_y + 5)], fill=0)
            draw.line([(52, car_y + 5), (52, car_y + 8)], fill=0)
            draw.line([(45, car_y + 8), (52, car_y + 8)], fill=0)
            # Nắp capo
            draw.line([(34, car_y + 2), (44, car_y + 4)], fill=0)
            # Kính chắn gió
            draw.line([(24, car_y - 6), (34, car_y + 2)], fill=0)
            # Mui xe & đuôi gió ducktail
            draw.line([(14, car_y - 6), (24, car_y - 6)], fill=0)
            draw.line([(7, car_y + 1), (14, car_y - 6)], fill=0)
            draw.line([(3, car_y + 2), (7, car_y + 1)], fill=0)
            draw.line([(3, car_y + 2), (3, car_y + 8)], fill=0)
            draw.line([(18, car_y + 8), (38, car_y + 8)], fill=0)

            # Khung cửa sổ & cột B
            draw.line([(21, car_y - 5), (21, car_y + 2)], fill=0)
            draw.line([(15, car_y + 1), (32, car_y + 1)], fill=0)

            # Silhouette người lái xe bên trong
            draw.ellipse([23, car_y - 5, 27, car_y - 1], fill=0)
            # Tay gác cửa sổ cầm điếu thuốc
            draw.line([(22, car_y + 1), (18, car_y)], fill=0)
            draw.point([(17, car_y)], fill=0)
            # Khói thuốc bay ngược về sau theo gió
            for k in range(1, 6):
                sx = 16 - k * 3
                sy = car_y - int(math.sin(f * 0.6 + k) * 2)
                if 0 <= sx < 54:
                    draw.point([(sx, sy)], fill=0)

            # 2 Bánh xe nan hoa 5 chấu xoay tròn theo nhịp
            rot = (f * 2) % 4
            for wx in [13, 42]:
                wy = car_y + 8
                draw.arc([wx-5, wy-4, wx+5, wy+6], 180, 360, fill=0)
                draw.ellipse([wx-4, wy-1, wx+4, wy+7], outline=0, fill=1)
                draw.point([(wx, wy+3)], fill=0)
                if rot in [0, 2]:
                    draw.line([(wx-2, wy+3), (wx+2, wy+3)], fill=0)
                    draw.line([(wx, wy+1), (wx, wy+5)], fill=0)
                else:
                    draw.line([(wx-2, wy+1), (wx+2, wy+5)], fill=0)
                    draw.line([(wx-2, wy+5), (wx+2, wy+1)], fill=0)

            # Đèn pha chiếu rực sáng phía trước
            draw.line([(52, car_y + 5), (55, car_y + 2)], fill=0)
            draw.line([(52, car_y + 6), (55, car_y + 9)], fill=0)
            draw.point([(54, car_y + 6)], fill=0)

            # Vệt kẻ đường lao nhanh về sau
            road_shift = (f * 4) % 10
            for rx in range(0, 56, 10):
                pos = rx - road_shift
                if 0 <= pos < 52:
                    draw.line([(pos, 51), (min(54, pos + 4), 51)], fill=0)

        elif action == 4:
            # --- ACTION 4: COCKPIT POV - GƯƠNG CHIẾU HẬU, BÙA TIM ĐUNG ĐƯA & CẦN GẠT NƯỚC ---
            # Gương chiếu hậu ô tô
            draw.polygon([(17, 5), (37, 5), (35, 15), (19, 15)], outline=0, fill=1)
            draw.line([(27, 2), (27, 5)], fill=0)

            # Phản chiếu đèn xe lùi xa trong gương
            draw.line([(22, 10), (25, 10)], fill=0)
            draw.line([(29, 10), (32, 10)], fill=0)
            draw.point([(23, 10), (31, 10)], fill=1)

            # Bùa trái tim vỡ đung đưa dưới gương chiếu hậu
            charm_sway = int(math.sin(f * 0.3) * 2)
            cx = 27 + charm_sway
            draw.line([(27, 15), (cx, 20)], fill=0)
            draw.polygon([(cx, 25), (cx-3, 22), (cx-2, 20), (cx, 21), (cx+2, 20), (cx+3, 22)], outline=0, fill=0)
            draw.line([(cx, 21), (cx, 24)], fill=1)

            # Mặt taplo & vô lăng 3 chấu bên dưới
            draw.rectangle([2, 43, 53, 52], outline=0, fill=1)
            draw.arc([8, 38, 30, 48], 180, 360, fill=0)
            # Vô lăng
            draw.arc([11, 37, 27, 51], 180, 360, fill=0)
            draw.line([(19, 44), (13, 46)], fill=0)
            draw.line([(19, 44), (25, 46)], fill=0)
            draw.line([(19, 44), (19, 50)], fill=0)
            # Đồng hồ công-tơ-mét
            draw.arc([35, 43, 45, 51], 180, 360, fill=0)
            draw.line([(40, 47), (43, 44)], fill=0)

            # Cần gạt nước gạt qua lại
            wiper_phase = math.sin(f * 0.45)
            tip_x = int(24 + wiper_phase * 16)
            tip_y = int(24 - abs(wiper_phase) * 4)
            draw.line([(36, 43), (tip_x, tip_y)], fill=0)
            draw.line([(tip_x - 4, tip_y - 2), (tip_x + 4, tip_y + 2)], fill=0)

            # Vết mưa chảy trên kính
            for gx, gy in [(6, 22), (12, 30), (46, 24), (49, 33), (8, 35)]:
                streak_y = ((gy + f * 2) % 20) + 18
                draw.line([(gx, streak_y), (gx - 1, streak_y + 3)], fill=0)

        elif action == 5:
            # --- ACTION 5: ĐỖ XE VEN ĐƯỜNG, TỰA LƯNG VÀO NẮP CAPO CHỤM TAY CHÂM THUỐC ---
            # Thân xe đỗ bên trái
            draw.line([(0, 36), (8, 36)], fill=0)
            draw.line([(8, 36), (15, 41)], fill=0)
            draw.line([(15, 41), (28, 42)], fill=0)
            draw.line([(28, 42), (28, 46)], fill=0)
            draw.line([(0, 47), (28, 47)], fill=0)
            draw.ellipse([6, 44, 14, 52], outline=0, fill=1)
            draw.point([(10, 48)], fill=0)

            # Chàng trai tựa vào nắp capo
            bx = 32
            by = 28
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx-1, by-9), (bx+5, by-7), (bx+5, by-2), (bx+2, by-1)], outline=0, fill=0)
            draw.line([(bx, by+1), (bx+2, by+2)], fill=0)
            if f % 6 > 2:
                draw.point([(bx+2, by+4)], fill=0) # Giọt lệ buồn

            # Thân áo tựa nghiêng
            draw.polygon([(bx-4, by+6), (bx+4, by+6), (bx+3, by+17), (bx-5, by+17)], outline=0, fill=1)

            # Hai tay chụm lại che gió châm lửa điếu thuốc
            draw.polygon([(bx+1, by+6), (bx+6, by+6), (bx+7, by+10), (bx+2, by+10)], outline=0, fill=1)
            if f % 3 == 0:
                draw.point([(bx+4, by+7)], fill=0)
            elif f % 3 == 1:
                draw.line([(bx+4, by+7), (bx+4, by+8)], fill=0)

            # Khói thuốc bốc lên giữa các ngón tay
            for i in range(1, 8):
                draw.point([(int(bx + 4 + math.sin(f*0.4 + i)*1.8), by + 5 - i * 2)], fill=0)

            # Chân bắt chéo tựa xe
            draw.line([(bx-3, by+18), (bx-6, 50)], fill=0)
            draw.line([(bx+1, by+18), (bx-1, 50)], fill=0)
            draw.rectangle([bx-8, 50, bx-5, 52], fill=0)
            draw.rectangle([bx-3, 50, bx, 52], fill=0)

            # Trái tim rạn vỡ lơ lửng trong đêm
            hx, hy = 44, 13
            draw.polygon([(hx, hy+5), (hx-4, hy), (hx-3, hy-4), (hx, hy-2), (hx+3, hy-4), (hx+4, hy)], outline=0, fill=1)
            draw.line([(hx, hy-2), (hx-1, hy+1), (hx+1, hy+2), (hx, hy+5)], fill=0)

        elif action == 6:
            # --- ACTION 6: NGỒI TRÊN NẮP CAPO, ÁNH SÁNG MÀN HÌNH ĐIỆN THOẠI ---
            # Thân xe thể thao bên dưới
            draw.line([(2, 42), (10, 42)], fill=0)
            draw.line([(10, 42), (18, 36)], fill=0)
            draw.line([(18, 36), (26, 36)], fill=0)
            draw.line([(26, 36), (33, 42)], fill=0)
            draw.line([(33, 42), (50, 43)], fill=0)
            draw.line([(50, 43), (50, 47)], fill=0)
            draw.line([(2, 48), (50, 48)], fill=0)
            draw.ellipse([8, 45, 16, 52], outline=0, fill=1)
            draw.ellipse([38, 45, 46, 52], outline=0, fill=1)

            # Chàng trai ngồi trên mui xe tại X=39
            bx = 39
            by = 26 - beat_bounce
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx-1, by-9), (bx+5, by-7), (bx+5, by-2), (bx+2, by-1)], outline=0, fill=0)
            draw.line([(bx, by+1), (bx+2, by+2)], fill=0)
            draw.polygon([(bx-4, by+6), (bx+4, by+6), (bx+4, by+16), (bx-4, by+16)], outline=0, fill=1)

            # Tay phải cầm điện thoại phát sáng
            draw.line([(bx+2, by+8), (bx+6, by+10)], fill=0)
            draw.rectangle([bx+6, by+8, bx+11, by+15], outline=0, fill=0)
            draw.rectangle([bx+7, by+9, bx+10, by+13], outline=0, fill=1)

            # Tay trái cầm điếu thuốc buông thõng
            draw.line([(bx-3, by+9), (bx-7, by+13)], fill=0)
            draw.point([(bx-8, by+13)], fill=0)
            if f % 4 < 2:
                draw.point([(bx-8, by+15)], fill=0) # Tàn tro rơi
            draw.point([(bx-9, by+10), (bx-8, by+7)], fill=0)

            # Chân thả buông theo mui xe
            draw.line([(bx-1, by+16), (bx-1, 44)], fill=0)
            draw.line([(bx+2, by+16), (bx+2, 44)], fill=0)
            draw.rectangle([bx-3, 43, bx, 45], fill=0)
            draw.rectangle([bx+1, 43, bx+4, 45], fill=0)

            # Trái tim rạn vỡ đập đau thắt lại theo nhịp bass
            hx, hy = 20, 13
            h_sz = 4 + beat_bounce
            draw.polygon([(hx, hy+h_sz), (hx-h_sz, hy), (hx-h_sz+1, hy-h_sz//2), (hx, hy-h_sz//3), (hx+h_sz-1, hy-h_sz//2), (hx+h_sz, hy)], outline=0, fill=1)
            draw.line([(hx, hy-h_sz//3), (hx-1, hy+1), (hx+1, hy+2), (hx, hy+h_sz)], fill=0)

        elif action == 7:
            # --- ACTION 7: CAO TỐC VÔ CỰC, XE LĂN BÁNH XA DẦN VÀO MÀN ĐÊM ---
            draw.line([(28, 20), (2, 52)], fill=0)
            draw.line([(28, 20), (54, 52)], fill=0)
            # Cọc tiêu lan can phối cảnh
            for gy in [26, 33, 42, 52]:
                sc = (gy - 20) / 32.0
                draw.line([(int(28 - 26 * sc), gy), (int(28 - 26 * sc), gy - int(3 * sc))], fill=0)
                draw.line([(int(28 + 26 * sc), gy), (int(28 + 26 * sc), gy - int(3 * sc))], fill=0)

            # Vạch kẻ tim đường lướt về phía trước
            dash_shift = (f * 3) % 9
            for dy in range(22, 52, 9):
                pos_y = dy + dash_shift
                if 22 <= pos_y < 51:
                    draw.line([(28, pos_y), (28, min(51, pos_y + 4))], fill=0)

            # Chiếc xe nhìn từ phía sau nhỏ dần
            cx, cy = 28, 38
            # Đuôi gió spoiler
            draw.line([(cx-11, cy-5), (cx+11, cy-5)], fill=0)
            draw.line([(cx-8, cy-5), (cx-8, cy-2)], fill=0)
            draw.line([(cx+8, cy-5), (cx+8, cy-2)], fill=0)
            # Kính chắn gió sau & mui xe
            draw.polygon([(cx-5, cy-4), (cx+5, cy-4), (cx+7, cy-1), (cx-7, cy-1)], outline=0, fill=1)
            # Cản sau & thân xe rộng thể thao
            draw.polygon([(cx-10, cy-1), (cx+10, cy-1), (cx+11, cy+5), (cx-11, cy+5)], outline=0, fill=1)
            # Dải đèn hậu LED xuyên suốt đỏ rực
            draw.line([(cx-9, cy+1), (cx+9, cy+1)], fill=0)
            draw.point([(cx-8, cy+1), (cx-7, cy+1), (cx+7, cy+1), (cx+8, cy+1)], fill=1)
            # 2 Lốp xe bám đường
            draw.rectangle([cx-10, cy+5, cx-7, cy+7], fill=0)
            draw.rectangle([cx+7, cy+5, cx+10, cy+7], fill=0)
            # Ống xả kép & làn khói phụt ra
            draw.point([(cx-5, cy+5), (cx+5, cy+5)], fill=0)
            draw.point([(cx-6, cy+6), (cx-7, cy+7), (cx+6, cy+6), (cx+7, cy+7)], fill=0)

            # Trăng lưỡi liềm & bầu trời đầy sao
            draw.arc([6, 5, 14, 13], 90, 270, fill=0)
            draw.arc([9, 5, 15, 13], 90, 270, fill=1)
            for sx, sy in [(18, 7), (40, 5), (48, 11), (14, 15)]:
                if (f + sx) % 5 < 3:
                    draw.point([(sx, sy)], fill=0)

        # 7. CHUYỂN THÀNH 1024 BYTES (1 bit/pixel MSB-first)
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

    # 1. Ghi file binary OLED SSD1306 (1024 bytes/frame)
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
constexpr int FRAME_SIZE = 1024;
constexpr int NUM_FRAMES = {NUM_FRAMES};
constexpr float FRAME_TIME = 0.070f;
constexpr float SCALE = 6.0f;

int main() {{
    sf::RenderWindow window(sf::VideoMode(WIDTH * SCALE, HEIGHT * SCALE), "TELL ME WHY 💔 - Duong Domic (OLED Animation)");
    window.setFramerateLimit(60);

    sf::Music music;
    if (!music.openFromFile("tellmewhy.wav") && !music.openFromFile("tellmewhy.mp3")) {{
        std::cerr << "Khong the mo file am thanh!" << std::endl;
    }} else {{
        music.play();
    }}

    std::ifstream binFile("tellmewhy_frames.bin", std::ios::binary);
    if (!binFile) {{
        std::cerr << "Khong the doc tellmewhy_frames.bin!" << std::endl;
        return 1;
    }}
    std::vector<uint8_t> allFrames(NUM_FRAMES * FRAME_SIZE);
    binFile.read(reinterpret_cast<char*>(allFrames.data()), allFrames.size());
    binFile.close();

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
        self.root.configure(bg="#0b0813")

        self.bin_path = os.path.join(os.path.dirname(__file__), "tellmewhy_frames.bin")
        self.wav_path = os.path.join(os.path.dirname(__file__), "tellmewhy.wav")

        with open(self.bin_path, "rb") as f:
            self.raw_data = f.read()

        self.num_frames = len(self.raw_data) // 1024
        self.current_frame = 0
        self.is_playing = True
        self.is_muted = False
        self.loop = True
        self.inverted = False
        self.start_time = None
        self.after_id = None

        self.ppm_frames = build_ppm_frames(self.raw_data, self.inverted)
        self.photo_cache = [None] * self.num_frames

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=HEIGHT * SCALE, bg="#000000", highlightthickness=0)
        self.canvas.pack(side=tk.TOP)

        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.get_photo(0))

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bg="#120c22", fg="#ff4d8d",
                                   font=("Segoe UI", 10, "bold"), anchor=tk.CENTER, pady=8)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.bind("<space>", self.toggle_play)
        self.root.bind("<m>", self.toggle_mute)
        self.root.bind("<M>", self.toggle_mute)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)
        self.root.bind("<l>", self.toggle_loop)
        self.root.bind("<L>", self.toggle_loop)
        self.root.bind("<i>", self.toggle_invert)
        self.root.bind("<I>", self.toggle_invert)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.play_audio()
        self.update_frame()

    def play_audio(self):
        if HAS_WINSOUND and os.path.exists(self.wav_path) and not self.is_muted:
            try:
                flags = winsound.SND_ASYNC | winsound.SND_FILENAME
                if self.loop: flags |= winsound.SND_LOOP
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
            --accent-cyan: #00f2fe;
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
            bottom: 5%;
            right: 5%;
            filter: blur(55px);
            pointer-events: none;
        }}
        .app-card {{
            position: relative;
            z-index: 10;
            width: min(94vw, 860px);
            max-height: 96dvh;
            background: rgba(18, 12, 34, 0.88);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 28px;
            padding: 22px 26px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 50px rgba(255, 77, 141, 0.15);
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .title-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .song-icon {{
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #ff4d8d, #9d4edd);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 8px 20px rgba(255, 77, 141, 0.4);
        }}
        .song-info h1 {{
            font-size: 1.18rem;
            font-weight: 700;
            background: linear-gradient(90deg, #ffffff, #ffb3d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px;
        }}
        .song-info p {{
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(255, 77, 141, 0.15);
            color: var(--accent-pink);
            border: 1px solid rgba(255, 77, 141, 0.3);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .badge:hover {{
            background: rgba(255, 77, 141, 0.25);
            transform: translateY(-1px);
        }}
        .screen-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 2 / 1;
            background: #ffffff;
            border-radius: 22px;
            overflow: hidden;
            box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08), 0 15px 40px rgba(0, 0, 0, 0.5);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        canvas {{
            width: 100%;
            height: 100%;
            display: block;
            image-rendering: auto;
        }}
        .play-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(10, 6, 20, 0.65);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            transition: opacity 0.3s ease, visibility 0.3s;
            z-index: 20;
        }}
        .play-overlay.hidden {{
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }}
        .big-play-btn {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));
            border: none;
            color: #ffffff;
            font-size: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(255, 77, 141, 0.5);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .big-play-btn:hover {{
            transform: scale(1.08);
            box-shadow: 0 12px 36px rgba(255, 77, 141, 0.7);
        }}
        .play-hint {{
            font-size: 0.88rem;
            font-weight: 600;
            color: #fce7f3;
            letter-spacing: 0.3px;
        }}
        .bottom-bar {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .progress-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .time-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            min-width: 75px;
        }}
        .time-label.right {{
            text-align: right;
        }}
        .progress-track {{
            position: relative;
            flex: 1;
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            cursor: pointer;
            overflow: hidden;
        }}
        .progress-fill {{
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 0%;
            background: linear-gradient(90deg, var(--accent-pink), var(--accent-purple));
            border-radius: 6px;
            transition: width 0.08s linear;
        }}
        .controls {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .btn-ctrl {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 14px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        .btn-ctrl:hover {{
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-1px);
        }}
        .btn-ctrl.primary {{
            background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));
            border: none;
            box-shadow: 0 4px 15px rgba(255, 77, 141, 0.35);
        }}

        @media (max-width: 640px) {{
            html, body {{
                width: 100%;
                height: 100%;
                height: 100dvh;
                overflow: hidden;
            }}
            .app-card {{
                width: 100%;
                max-width: 100%;
                height: 100%;
                height: 100dvh;
                max-height: 100dvh;
                border-radius: 0;
                border: none;
                box-shadow: none;
                padding: max(8px, env(safe-area-inset-top, 0px)) 12px max(10px, env(safe-area-inset-bottom, 0px));
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                gap: 0;
                background: rgba(14, 9, 26, 0.96);
            }}
            .header {{
                margin-bottom: 6px;
                flex-shrink: 0;
            }}
            .song-icon {{
                width: 36px;
                height: 36px;
                font-size: 18px;
            }}
            .song-info h1 {{
                font-size: 1.02rem;
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
            <div class="title-group">
                <div class="song-icon">💔</div>
                <div class="song-info">
                    <h1>TELL ME WHY</h1>
                    <p>Dương Domic • Lo-Fi Cinematic Animation</p>
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <a href="cu_the.html" class="badge" style="text-decoration: none; color: var(--text-muted); background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.15);" title="Xem bài Cứ Thế">🌸 Cứ Thế (20/10)</a>
                <span class="badge" style="background: rgba(255, 77, 141, 0.35); color: #fff; cursor: default;">💔 Tell Me Why</span>
                <button class="badge" id="btnToggleMode" title="Chuyển đổi chế độ hiển thị">✨ HD Sắc Nét</button>
            </div>
        </div>

        <div class="screen-wrapper" id="screenWrapper">
            <canvas id="screenCanvas"></canvas>
            <div class="play-overlay" id="playOverlay">
                <button class="big-play-btn" id="btnOverlayPlay" aria-label="Phát nhạc">▶</button>
                <div class="play-hint" id="playBtnText">Chạm để cảm nhận âm nhạc 💔</div>
            </div>
        </div>

        <div class="bottom-bar">
            <div class="progress-container">
                <div class="time-label" id="timeDisplay">00:00 / {NUM_FRAMES * 0.070:.0f}:00</div>
                <div class="progress-track" id="progressTrack">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
            <div class="controls">
                <button class="btn-ctrl primary" id="btnPlayPause">
                    <span id="iconPlay">▶ Phát</span>
                    <span id="iconPause" style="display:none;">⏸ Tạm dừng</span>
                </button>
                <button class="btn-ctrl" id="btnMute">
                    <span id="muteEmoji">🔊</span> Âm thanh
                </button>
            </div>
        </div>
    </div>

    <audio id="bgMusic" preload="auto">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>

    <script>
        const NUM_FRAMES = {NUM_FRAMES};
        const FRAME_DURATION = 0.070;
        const TOTAL_DURATION = {NUM_FRAMES * 0.070:.2f};
        const EQUALIZER_BARS = {bars_json};

        const KARAOKE_TIMED_PHRASES = [
            {{
                action: 1, start_t: 0.0, end_t: 3.8,
                lines: [
                    [{{t: 0.2, w: "Từng"}}, {{t: 0.8, w: "cơn"}}, {{t: 1.4, w: "đau"}}],
                    [{{t: 2.0, w: "tăng"}}, {{t: 2.6, w: "dần"}}, {{t: 3.1, w: "lên... 🌧"}}]
                ]
            }},
            {{
                action: 2, start_t: 3.8, end_t: 7.5,
                lines: [
                    [{{t: 3.9, w: "Thời"}}, {{t: 4.5, w: "gian"}}, {{t: 5.0, w: "trôi"}}],
                    [{{t: 5.6, w: "âm"}}, {{t: 6.2, w: "thầm"}}, {{t: 6.8, w: "đếm... ⏳"}}]
                ]
            }},
            {{
                action: 3, start_t: 7.5, end_t: 10.8,
                lines: [
                    [{{t: 7.6, w: "Nỗi"}}, {{t: 8.1, w: "cô"}}, {{t: 8.6, w: "đơn"}}],
                    [{{t: 9.1, w: "ghé"}}, {{t: 9.5, w: "qua"}}, {{t: 9.9, w: "đêm"}}, {{t: 10.3, w: "nay... 🌙"}}]
                ]
            }},
            {{
                action: 4, start_t: 10.8, end_t: 14.0,
                lines: [
                    [{{t: 10.8, w: "Đêm"}}, {{t: 11.2, w: "qua,"}}, {{t: 11.6, w: "đêm"}}, {{t: 12.0, w: "nay"}}],
                    [{{t: 12.4, w: "anh"}}, {{t: 12.8, w: "chẳng"}}, {{t: 13.2, w: "muốn"}}],
                    [{{t: 13.5, w: "quay"}}, {{t: 13.8, w: "lại..."}}]
                ]
            }},
            {{
                action: 5, start_t: 14.0, end_t: 17.5,
                lines: [
                    [{{t: 14.1, w: "Phải"}}, {{t: 14.6, w: "xa"}}, {{t: 15.1, w: "em"}}],
                    [{{t: 15.6, w: "anh"}}, {{t: 16.2, w: "nào"}}, {{t: 16.8, w: "muốn... 💔"}}]
                ]
            }},
            {{
                action: 6, start_t: 17.5, end_t: 21.5,
                lines: [
                    [{{t: 17.6, w: "Vì"}}, {{t: 18.1, w: "chia"}}, {{t: 18.6, w: "đôi"}}],
                    [{{t: 19.2, w: "vẫn"}}, {{t: 19.8, w: "còn"}}],
                    [{{t: 20.3, w: "thương... 💖"}}]
                ]
            }},
            {{
                action: 7, start_t: 21.5, end_t: TOTAL_DURATION + 1,
                lines: [
                    [{{t: 21.6, w: "✨"}}, {{t: 22.0, w: "TELL"}}, {{t: 22.4, w: "ME"}}, {{t: 22.8, w: "WHY"}}, {{t: 23.2, w: "✨"}}],
                    [{{t: 23.6, w: "Dương"}}, {{t: 24.0, w: "Domic"}}],
                    [{{t: 24.5, w: "Vẫn"}}, {{t: 24.9, w: "còn"}}, {{t: 25.3, w: "thương"}}, {{t: 25.7, w: "nhau..."}}]
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
            ctx.lineWidth = Math.max(1.2, S * 0.35);
            ctx.beginPath();
            const topY = (y - size * 0.3) * S;
            ctx.moveTo(x * S, (y + size) * S);
            ctx.bezierCurveTo((x - size * 1.2) * S, (y + size * 0.2) * S, (x - size * 1.2) * S, topY, x * S, (y - size * 0.1) * S);
            ctx.bezierCurveTo((x + size * 1.2) * S, topY, (x + size * 1.2) * S, (y + size * 0.2) * S, x * S, (y + size) * S);
            if (fill) ctx.fill();
            ctx.stroke();

            // Vết nứt zíc-zắc ở giữa trái tim
            ctx.beginPath();
            ctx.moveTo(x * S, (y - size * 0.1) * S);
            ctx.lineTo((x - 1) * S, (y + size * 0.3) * S);
            ctx.lineTo((x + 1) * S, (y + size * 0.5) * S);
            ctx.lineTo(x * S, (y + size) * S);
            ctx.stroke();
            ctx.restore();
        }}

        function drawStar(ctx, x, y, r, S) {{
            ctx.save();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1, S * 0.25);
            ctx.beginPath();
            ctx.moveTo(x * S, (y - r) * S);
            ctx.lineTo(x * S, (y + r) * S);
            ctx.moveTo((x - r) * S, y * S);
            ctx.lineTo((x + r) * S, y * S);
            ctx.stroke();
            ctx.restore();
        }}

        function drawAnimeHead(ctx, bx, by, S, look = 'down') {{
            ctx.save();
            // Đầu & da mặt
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1.4, S * 0.32);
            ctx.beginPath();
            ctx.arc(bx * S, by * S, 4.8 * S, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Mái tóc anime lãng tử có từng lọn rủ
            ctx.fillStyle = '#181224';
            ctx.beginPath();
            ctx.moveTo((bx - 5) * S, (by - 2) * S);
            ctx.bezierCurveTo((bx - 6) * S, (by - 7) * S, (bx - 2) * S, (by - 9) * S, (bx + 1) * S, (by - 9) * S);
            ctx.bezierCurveTo((bx + 5) * S, (by - 8) * S, (bx + 6) * S, (by - 4) * S, (bx + 5.2) * S, (by - 1.5) * S);
            ctx.lineTo((bx + 3.5) * S, (by - 1) * S);
            ctx.lineTo((bx + 2.5) * S, (by + 1.2) * S); // lọn tóc mái dài
            ctx.lineTo((bx + 1) * S, (by - 1) * S);
            ctx.lineTo((bx - 0.5) * S, (by + 1.5) * S); // lọn tóc mái giữa
            ctx.lineTo((bx - 2) * S, (by - 1) * S);
            ctx.lineTo((bx - 3.5) * S, (by + 0.5) * S); // lọn tóc mái trái
            ctx.closePath();
            ctx.fill();

            // Mắt và biểu cảm
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1.2, S * 0.28);
            if (look === 'down') {{
                // Mắt nhìn xuống buồn
                ctx.beginPath();
                ctx.moveTo((bx + 0.8) * S, (by + 1.2) * S);
                ctx.lineTo((bx + 3) * S, (by + 2) * S);
                ctx.stroke();
            }} else if (look === 'closed') {{
                // Mắt nhắm
                ctx.beginPath();
                ctx.moveTo((bx - 1) * S, by * S);
                ctx.lineTo((bx + 2) * S, (by + 1) * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((bx + 1) * S, by * S);
                ctx.lineTo((bx + 3) * S, by * S);
                ctx.stroke();
            }}
            ctx.restore();
        }}

        function drawSportsCarSide(ctx, S) {{
            const carY = 48 * S;
            ctx.save();
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1.6, S * 0.35);

            // Dáng xe thể thao coupe khí động học
            ctx.beginPath();
            ctx.moveTo(3 * S, carY); // cản sau
            ctx.lineTo(3 * S, carY - 6 * S);
            ctx.lineTo(8 * S, carY - 7 * S); // cánh gió ducktail
            ctx.lineTo(16 * S, carY - 14 * S); // kính sau dốc
            ctx.lineTo(26 * S, carY - 14 * S); // mui xe
            ctx.lineTo(33 * S, carY - 7 * S); // kính chắn gió
            ctx.lineTo(51 * S, carY - 6 * S); // nắp capo dài phẳng
            ctx.lineTo(52 * S, carY - 2 * S); // mũi xe
            ctx.lineTo(46 * S, carY); // cản trước
            ctx.lineTo(42 * S, carY);
            ctx.arc(38 * S, carY, 4.5 * S, 0, Math.PI, true); // hốc bánh trước
            ctx.lineTo(17 * S, carY);
            ctx.arc(13 * S, carY, 4.5 * S, 0, Math.PI, true); // hốc bánh sau
            ctx.lineTo(3 * S, carY);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Kính xe có màu tối mờ
            ctx.fillStyle = 'rgba(15, 23, 42, 0.12)';
            ctx.beginPath();
            ctx.moveTo(17 * S, carY - 7.5 * S);
            ctx.lineTo(18 * S, carY - 12.5 * S);
            ctx.lineTo(25 * S, carY - 12.5 * S);
            ctx.lineTo(31 * S, carY - 7.5 * S);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            // Cột B
            ctx.beginPath();
            ctx.moveTo(22 * S, carY - 12.5 * S);
            ctx.lineTo(22 * S, carY - 7.5 * S);
            ctx.stroke();

            // 2 Bánh xe lốp cao su + mâm hợp kim
            [13, 38].forEach(wx => {{
                ctx.fillStyle = '#0f172a';
                ctx.beginPath();
                ctx.arc(wx * S, carY, 4 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#e2e8f0';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(wx * S, carY, 2.3 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
                // Tâm mâm
                ctx.fillStyle = '#0f172a';
                ctx.beginPath();
                ctx.arc(wx * S, carY, 0.8 * S, 0, Math.PI * 2);
                ctx.fill();
            }});
            ctx.restore();
        }}

        function drawHighwayLandscape(ctx, S, f) {{
            const vpX = 28 * S;
            const vpY = 22 * S;

            ctx.save();

            // 1. Dải skyline thành phố xa xa trên đường chân trời (Cityscape ban đêm)
            ctx.fillStyle = 'rgba(15, 23, 42, 0.12)';
            [ [4, 7, 4], [9, 10, 5], [15, 6, 3.5], [37, 8, 4], [42, 11, 5], [48, 6, 4] ].forEach(([x, h, w]) => {{
                ctx.fillRect(x * S, (22 - h) * S, w * S, h * S);
                ctx.fillStyle = '#fef08a';
                ctx.fillRect((x + 1) * S, (22 - h + 2) * S, 0.8 * S, 0.8 * S);
                ctx.fillRect((x + 2.2) * S, (22 - h + 4) * S, 0.8 * S, 0.8 * S);
                ctx.fillStyle = 'rgba(15, 23, 42, 0.12)';
            }});

            // 2. Mặt đường nhựa cao tốc màu xám nhạt lo-fi
            ctx.fillStyle = '#f1f5f9';
            ctx.beginPath();
            ctx.moveTo(vpX, vpY);
            ctx.lineTo(2 * S, 53 * S);
            ctx.lineTo(54 * S, 53 * S);
            ctx.closePath();
            ctx.fill();

            // Gờ mép đường hai bên
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1.8, S * 0.38);
            ctx.beginPath();
            ctx.moveTo(vpX, vpY);
            ctx.lineTo(2 * S, 53 * S);
            ctx.moveTo(vpX, vpY);
            ctx.lineTo(54 * S, 53 * S);
            ctx.stroke();

            // 3. Cọc tiêu lan can phối cảnh hai bên
            [27, 34, 43, 53].forEach(gy => {{
                const sc = (gy - 22) / 31.0;
                const lX = vpX - 26 * sc * S;
                const rX = vpX + 26 * sc * S;
                ctx.beginPath();
                ctx.moveTo(lX, gy * S);
                ctx.lineTo(lX, (gy - 3.8 * sc) * S);
                ctx.moveTo(rX, gy * S);
                ctx.lineTo(rX, (gy - 3.8 * sc) * S);
                ctx.stroke();
            }});

            // 4. Vạch kẻ đường đứt đoạn lướt về phía trước
            const dashShift = (f * 2.5) % 8;
            ctx.strokeStyle = '#cbd5e1';
            ctx.lineWidth = Math.max(2, S * 0.45);
            for (let dy = 24; dy < 52; dy += 8) {{
                const curY = dy + dashShift;
                if (curY >= 23 && curY < 52) {{
                    const sc = (curY - 22) / 31.0;
                    ctx.beginPath();
                    ctx.moveTo(vpX, curY * S);
                    ctx.lineTo(vpX, Math.min(52 * S, (curY + 3.8 * sc) * S));
                    ctx.stroke();
                }}
            }}

            // 5. Trăng khuyết mềm mại & các ngôi sao
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(8 * S, 8 * S, 3.8 * S, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(10 * S, 7.2 * S, 3.4 * S, 0, Math.PI * 2);
            ctx.fill();

            // Sao lấp lánh
            [ [18, 7], [38, 6], [48, 11], [14, 15] ].forEach(([sx, sy], sIdx) => {{
                if ((f + sIdx * 3) % 6 < 4) {{
                    drawStar(ctx, sx, sy, 2.2, S);
                }}
            }});

            ctx.restore();
        }}

        function drawSportsCarRear(ctx, cx, cy, S, f) {{
            ctx.save();

            // 1. Hai lốp xe sau to bản bám đường
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(cx - 10.5 * S, cy + 5 * S, 4 * S, 3.8 * S); // lốp trái
            ctx.fillRect(cx + 6.5 * S, cy + 5 * S, 4 * S, 3.8 * S); // lốp phải

            // 2. Cản sau thể thao bè rộng
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = Math.max(1.6, S * 0.35);
            ctx.beginPath();
            ctx.roundRect(cx - 11 * S, cy - 1 * S, 22 * S, 7.5 * S, 2 * S);
            ctx.fill();
            ctx.stroke();

            // 3. Cabin & Kính sau dốc
            ctx.beginPath();
            ctx.moveTo(cx - 6 * S, cy - 6.5 * S);
            ctx.lineTo(cx + 6 * S, cy - 6.5 * S);
            ctx.lineTo(cx + 9 * S, cy - 1 * S);
            ctx.lineTo(cx - 9 * S, cy - 1 * S);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Mặt kính sau màu tối
            ctx.fillStyle = '#1e1b4b';
            ctx.beginPath();
            ctx.moveTo(cx - 5 * S, cy - 5.5 * S);
            ctx.lineTo(cx + 5 * S, cy - 5.5 * S);
            ctx.lineTo(cx + 7.5 * S, cy - 1.5 * S);
            ctx.lineTo(cx - 7.5 * S, cy - 1.5 * S);
            ctx.closePath();
            ctx.fill();

            // 4. Cánh gió thể thao GT Wing có 2 chân bắt cốp chắc chắn
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(cx - 7.5 * S, cy - 7.5 * S, 1.2 * S, 5.5 * S);
            ctx.fillRect(cx + 6.3 * S, cy - 7.5 * S, 1.2 * S, 5.5 * S);

            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1.8;
            ctx.beginPath();
            ctx.roundRect(cx - 13 * S, cy - 8.5 * S, 26 * S, 2 * S, 1 * S);
            ctx.fill();
            ctx.stroke();

            // 5. Dải đèn hậu LED đỏ rực phát quang
            ctx.save();
            ctx.shadowColor = '#ff1744';
            ctx.shadowBlur = 10;
            ctx.fillStyle = '#ff1744';
            ctx.fillRect(cx - 9.8 * S, cy + 0.8 * S, 19.6 * S, 2.2 * S);
            ctx.restore();

            // 6. Biển số xe ở giữa
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1;
            ctx.fillRect(cx - 3.5 * S, cy + 4 * S, 7 * S, 2.5 * S);
            ctx.strokeRect(cx - 3.5 * S, cy + 4 * S, 7 * S, 2.5 * S);

            // 7. Ống xả kép mạ crôm & khói xe
            ctx.fillStyle = '#64748b';
            ctx.beginPath();
            ctx.arc(cx - 6 * S, cy + 6.5 * S, 1.3 * S, 0, Math.PI * 2);
            ctx.arc(cx + 6 * S, cy + 6.5 * S, 1.3 * S, 0, Math.PI * 2);
            ctx.fill();

            // Khói xả mờ ảo bốc lên
            const smokeShift = (f * 0.4) % 1;
            ctx.fillStyle = 'rgba(100, 116, 139, 0.25)';
            ctx.beginPath();
            ctx.arc(cx - (7 + smokeShift * 2) * S, cy + (8 + smokeShift * 3) * S, (1.8 + smokeShift * 1.5) * S, 0, Math.PI * 2);
            ctx.arc(cx + (7 + smokeShift * 2) * S, cy + (8 + smokeShift * 3) * S, (1.8 + smokeShift * 1.5) * S, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
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

            // 1. Đường đất tràn viền ngang tại Y = 53
            ctx.beginPath();
            ctx.moveTo(-offsetX, 53 * S);
            ctx.lineTo(canvas.width - offsetX, 53 * S);
            ctx.stroke();

            // 2. EQUALIZER BARS SEGMENTED LED NHẢY THEO NHẠC (Y: 55 đến 63)
            const currentBars = EQUALIZER_BARS[f] || [];
            for (let b = 0; b < 24; b++) {{
                const bh = currentBars[b] || 1;
                const bx = (4 + b * 5) * S;
                const bw = 3 * S;
                const hue = 180 + (b / 24.0) * 150;
                ctx.fillStyle = `hsl(${{hue}}, 85%, 45%)`;
                for (let seg = 0; seg < bh; seg++) {{
                    const sy = (63 - seg) * S;
                    ctx.fillRect(bx, sy, bw, Math.max(1.2, S * 0.75));
                }}
            }}

            // 3. Vách ngăn dải chấm ở giữa X=56
            ctx.fillStyle = '#000000';
            for (let dy = 6; dy < 50; dy += 4) {{
                ctx.beginPath();
                ctx.arc(56 * S, dy * S, S * 0.3, 0, Math.PI * 2);
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

            // Mưa rơi nhẹ trong không gian
            ctx.strokeStyle = '#000000';
            [6, 17, 32, 47, 25].forEach((rx, s_idx) => {{
                const ry = ((f * 3 + (s_idx + 1) * 11) % 44) + 6;
                if (ry < 52) {{
                    ctx.beginPath();
                    ctx.moveTo(rx * S, ry * S);
                    ctx.lineTo((rx - 1.2) * S, (ry + 3.2) * S);
                    ctx.stroke();
                }}
            }});

            // 5. DIỄN HOẠT SIÊU CHI TIẾT BÊN TRÁI (X: 0..55)
            if (action === 1) {{
                // ACTION 1: CỘT ĐÈN ĐƯỜNG CỔ ĐIỂN & CHÀNG TRAI ÁO KHOÁC DÀI HÚT THUỐC
                const bx = 28;
                const by = 28 - beatBounce;

                // Cột đèn
                ctx.beginPath();
                ctx.moveTo(7 * S, 8 * S);
                ctx.lineTo(7 * S, 53 * S);
                ctx.moveTo(8 * S, 10 * S);
                ctx.lineTo(8 * S, 53 * S);
                ctx.stroke();
                // Tay đèn uốn lượn
                ctx.beginPath();
                ctx.arc(8 * S, 8 * S, 4 * S, Math.PI, 0);
                ctx.lineTo(16 * S, 8 * S);
                ctx.stroke();
                // Lồng đèn
                ctx.strokeRect(14 * S, 11 * S, 4 * S, 6 * S);
                ctx.fillStyle = '#fef08a';
                ctx.beginPath();
                ctx.arc(16 * S, 14 * S, 1.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Quầng sáng ấm áp toả xuống vỉa hè
                const lightGrad = ctx.createRadialGradient(16 * S, 14 * S, 2 * S, 16 * S, 36 * S, 24 * S);
                lightGrad.addColorStop(0, 'rgba(254, 240, 138, 0.25)');
                lightGrad.addColorStop(1, 'rgba(254, 240, 138, 0)');
                ctx.fillStyle = lightGrad;
                ctx.beginPath();
                ctx.moveTo(16 * S, 16 * S);
                ctx.lineTo(0, 53 * S);
                ctx.lineTo(34 * S, 53 * S);
                ctx.closePath();
                ctx.fill();

                // Chàng trai
                drawAnimeHead(ctx, bx, by, S, 'closed');

                // Điếu thuốc trên môi
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 1.4;
                ctx.beginPath();
                ctx.moveTo((bx + 1) * S, (by + 3) * S);
                ctx.lineTo((bx + 6) * S, (by + 3) * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx + 6.8) * S, (by + 3) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Làn khói uốn lượn
                ctx.strokeStyle = 'rgba(0,0,0,0.45)';
                for (let k = 1; k < 9; k++) {{
                    const sy = (by + 3 - k * 2.2) * S;
                    const sx = (bx + 7 + Math.sin(f * 0.35 + k * 0.7) * (k * 0.85)) * S;
                    ctx.beginPath();
                    ctx.arc(sx, sy, S * (0.4 + k * 0.15), 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Áo măng tô cổ bẻ cao
                ctx.fillStyle = '#ffffff';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.moveTo((bx - 5) * S, (by + 8) * S);
                ctx.lineTo((bx + 5) * S, (by + 8) * S);
                ctx.lineTo((bx + 6) * S, (by + 19) * S);
                ctx.lineTo((bx - 6) * S, (by + 19) * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                // Đường chỉ cúc áo
                ctx.beginPath();
                ctx.moveTo(bx * S, (by + 8) * S);
                ctx.lineTo(bx * S, (by + 19) * S);
                ctx.stroke();

                // Chân & vũng nước phản chiếu
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 20) * S);
                ctx.lineTo((bx - 3) * S, 53 * S);
                ctx.moveTo((bx + 2) * S, (by + 20) * S);
                ctx.lineTo((bx + 2) * S, 53 * S);
                ctx.stroke();

                ctx.strokeStyle = 'rgba(0,0,0,0.3)';
                ctx.beginPath();
                ctx.ellipse(bx * S, 52 * S, 8 * S, 1.5 * S, 0, 0, Math.PI * 2);
                ctx.stroke();

            }} else if (action === 2) {{
                // ACTION 2: THỞ CÁC VÒNG KHÓI TRÒN (SMOKE RINGS) & ĐỒNG HỒ CÁT
                const bx = 18;
                const by = 28 - beatBounce;

                drawAnimeHead(ctx, bx, by, S, 'closed');

                // Áo & tay kẹp điếu thuốc
                ctx.fillStyle = '#ffffff';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.roundRect((bx - 5) * S, (by + 8) * S, 10 * S, 11 * S, 2 * S);
                ctx.fill();
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo((bx + 3) * S, (by + 9) * S);
                ctx.lineTo((bx + 7) * S, (by + 12) * S);
                ctx.lineTo((bx + 11) * S, (by + 11) * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx + 12) * S, (by + 11) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // 3 Vòng khói tròn bay mở rộng dần
                ctx.strokeStyle = 'rgba(0,0,0,0.5)';
                ctx.lineWidth = 1.4;
                const ring_t = (f * 0.7) % 20;
                const r1_x = (bx + 6 + ring_t * 0.5) * S;
                const r1_y = (by + 1 - ring_t * 0.5) * S;
                ctx.beginPath();
                ctx.ellipse(r1_x, r1_y, 2.5 * S, 1.5 * S, 0, 0, Math.PI * 2);
                ctx.stroke();

                const p2 = (ring_t + 7) % 20;
                const r2_x = (bx + 11 + p2 * 0.6) * S;
                const r2_y = (by - 3 - p2 * 0.5) * S;
                ctx.beginPath();
                ctx.ellipse(r2_x, r2_y, 3.8 * S, 2.2 * S, 0, 0, Math.PI * 2);
                ctx.stroke();

                // Đồng hồ cát tinh xảo
                const hx = 45 * S, hy = 16 * S;
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.4, S * 0.3);
                ctx.beginPath();
                ctx.moveTo(hx - 6 * S, hy - 8 * S);
                ctx.lineTo(hx + 6 * S, hy - 8 * S);
                ctx.moveTo(hx - 6 * S, hy + 8 * S);
                ctx.lineTo(hx + 6 * S, hy + 8 * S);
                ctx.moveTo(hx - 4 * S, hy - 6 * S);
                ctx.lineTo(hx + 4 * S, hy - 6 * S);
                ctx.lineTo(hx, hy);
                ctx.lineTo(hx + 4 * S, hy + 6 * S);
                ctx.lineTo(hx - 4 * S, hy + 6 * S);
                ctx.lineTo(hx, hy);
                ctx.closePath();
                ctx.stroke();

                // Hạt cát chảy
                ctx.fillStyle = '#f59e0b';
                ctx.beginPath();
                ctx.arc(hx, hy + (2 + (f % 4) * 1.2) * S, 0.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Chân
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 20) * S);
                ctx.lineTo((bx - 3) * S, 53 * S);
                ctx.moveTo((bx + 2) * S, (by + 20) * S);
                ctx.lineTo((bx + 2) * S, 53 * S);
                ctx.stroke();

            }} else if (action === 3) {{
                // ACTION 3: XE THỂ THAO JDM LAO TRONG ĐÊM VỚI ĐÈN PHA RỌI SÁNG
                drawSportsCarSide(ctx, S);

                // Chàng trai bên trong xe
                ctx.fillStyle = '#181224';
                ctx.beginPath();
                ctx.arc(24 * S, 38 * S, 2.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Tay gác ra cửa sổ kẹp điếu thuốc
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 1.4;
                ctx.beginPath();
                ctx.moveTo(22 * S, 41 * S);
                ctx.lineTo(18 * S, 40 * S);
                ctx.stroke();
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc(17 * S, 40 * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Khói thuốc bay ngược về sau theo gió
                ctx.strokeStyle = 'rgba(0,0,0,0.4)';
                for (let k = 1; k < 6; k++) {{
                    const sx = (16 - k * 3) * S;
                    const sy = (40 - Math.sin(f * 0.6 + k) * 2) * S;
                    ctx.beginPath();
                    ctx.arc(sx, sy, 0.8 * S, 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Đèn pha rọi chùm sáng lớn cắt qua màn mưa
                const beamGrad = ctx.createLinearGradient(51 * S, 42 * S, 56 * S, 42 * S);
                beamGrad.addColorStop(0, 'rgba(255, 230, 180, 0.45)');
                beamGrad.addColorStop(1, 'rgba(255, 230, 180, 0.05)');
                ctx.fillStyle = beamGrad;
                ctx.beginPath();
                ctx.moveTo(51 * S, 42 * S);
                ctx.lineTo(56 * S, 36 * S);
                ctx.lineTo(56 * S, 48 * S);
                ctx.closePath();
                ctx.fill();

            }} else if (action === 4) {{
                // ACTION 4: COCKPIT POV - GƯƠNG CHIẾU HẬU, BÙA TIM ĐUNG ĐƯA & CẦN GẠT NƯỚC
                // Gương chiếu hậu ô tô
                ctx.fillStyle = '#ffffff';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.roundRect(17 * S, 5 * S, 20 * S, 10 * S, 3 * S);
                ctx.fill();
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(27 * S, 2 * S);
                ctx.lineTo(27 * S, 5 * S);
                ctx.stroke();

                // Bùa tim vỡ đung đưa dưới gương chiếu hậu
                const charm_sway = Math.sin(f * 0.3) * 2.5;
                const cx = (27 + charm_sway) * S;
                ctx.beginPath();
                ctx.moveTo(27 * S, 15 * S);
                ctx.lineTo(cx, 20 * S);
                ctx.stroke();
                drawHeart(ctx, 27 + charm_sway, 22, 2.5, S, true);

                // Taplo bên dưới & vô lăng 3 chấu
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(2 * S, 43 * S, 52 * S, 10 * S);
                ctx.strokeRect(2 * S, 43 * S, 52 * S, 10 * S);

                // Vô lăng
                ctx.beginPath();
                ctx.arc(19 * S, 44 * S, 7 * S, Math.PI, 0);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(19 * S, 44 * S);
                ctx.lineTo(13 * S, 46 * S);
                ctx.moveTo(19 * S, 44 * S);
                ctx.lineTo(25 * S, 46 * S);
                ctx.stroke();

                // Cần gạt nước gạt qua lại
                const wiper_phase = Math.sin(f * 0.45);
                const tip_x = (24 + wiper_phase * 16) * S;
                const tip_y = (24 - Math.abs(wiper_phase) * 4) * S;
                ctx.beginPath();
                ctx.moveTo(36 * S, 43 * S);
                ctx.lineTo(tip_x, tip_y);
                ctx.stroke();

                ctx.lineWidth = lw * 1.6;
                ctx.beginPath();
                ctx.moveTo(tip_x - 4 * S, tip_y - 2 * S);
                ctx.lineTo(tip_x + 4 * S, tip_y + 2 * S);
                ctx.stroke();
                ctx.lineWidth = lw;

            }} else if (action === 5) {{
                // ACTION 5: TỰA NẮP CAPO CHỤM TAY CHÂM THUỐC DƯỚI MƯA
                drawSportsCarSide(ctx, S);

                const bx = 34;
                const by = 28;

                drawAnimeHead(ctx, bx, by, S, 'down');

                // Nước mắt rơi
                ctx.fillStyle = '#00f2fe';
                ctx.beginPath();
                ctx.arc((bx + 2.5) * S, (by + 4) * S, 0.8 * S, 0, Math.PI * 2);
                ctx.fill();

                // Thân áo tựa nghiêng
                ctx.fillStyle = '#ffffff';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.moveTo((bx - 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 4) * S, (by + 6) * S);
                ctx.lineTo((bx + 3) * S, (by + 17) * S);
                ctx.lineTo((bx - 5) * S, (by + 17) * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Chụm hai bàn tay nâng niu ngọn lửa bật lửa
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.roundRect((bx + 1) * S, (by + 6) * S, 6 * S, 4 * S, 2 * S);
                ctx.fill();
                ctx.stroke();

                // Ngọn lửa nhỏ màu cam vàng ấm áp
                ctx.fillStyle = '#f59e0b';
                ctx.beginPath();
                ctx.arc((bx + 4) * S, (by + 7) * S, 1.4 * S, 0, Math.PI * 2);
                ctx.fill();

                // Khói thuốc bay lên từ kẽ ngón tay
                ctx.strokeStyle = 'rgba(0,0,0,0.45)';
                for (let k = 1; k < 8; k++) {{
                    const sy = (by + 5 - k * 2) * S;
                    const sx = (bx + 4 + Math.sin(f * 0.4 + k) * 1.8) * S;
                    ctx.beginPath();
                    ctx.arc(sx, sy, 0.7 * S, 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Chân bắt chéo tựa xe
                ctx.strokeStyle = '#000000';
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 18) * S);
                ctx.lineTo((bx - 6) * S, 53 * S);
                ctx.moveTo((bx + 1) * S, (by + 18) * S);
                ctx.lineTo((bx - 1) * S, 53 * S);
                ctx.stroke();

                // Trái tim rạn vỡ
                drawHeart(ctx, 44, 13, 3, S, false);

            }} else if (action === 6) {{
                // ACTION 6: NGỒI TRÊN NẮP CAPO, ÁNH SÁNG MÀN HÌNH ĐIỆN THOẠI
                // 1. Xe thể thao nhìn nghiêng
                drawSportsCarSide(ctx, S);

                // 2. Chàng trai ngồi trên mui xe tại bx=40, by=26
                const bx = 40;
                const by = 26 - beatBounce;

                // Đầu và tóc anime
                drawAnimeHead(ctx, bx, by, S, 'down');

                // Áo hoodie
                ctx.fillStyle = '#ffffff';
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.roundRect((bx - 4) * S, (by + 5.5) * S, 8 * S, 11 * S, 2 * S);
                ctx.fill();
                ctx.stroke();

                // Tay cầm điện thoại phát sáng
                ctx.beginPath();
                ctx.moveTo((bx + 2) * S, (by + 8) * S);
                ctx.lineTo((bx + 6) * S, (by + 11) * S);
                ctx.stroke();

                // Điện thoại smartphone
                ctx.fillStyle = '#0f172a';
                ctx.fillRect((bx + 6) * S, (by + 9) * S, 4.5 * S, 7 * S);
                ctx.fillStyle = '#00f2fe'; // Màn hình xanh ngọc phát sáng
                ctx.fillRect((bx + 6.8) * S, (by + 10) * S, 3 * S, 4.5 * S);
                // Icon khung chat trên màn hình
                ctx.fillStyle = '#ffffff';
                ctx.fillRect((bx + 7.5) * S, (by + 11.5) * S, 1.5 * S, 1 * S);

                // Vầng sáng dịu nhẹ hắt lên mặt và áo
                const grad = ctx.createLinearGradient((bx + 7) * S, (by + 10) * S, bx * S, by * S);
                grad.addColorStop(0, 'rgba(0, 242, 254, 0.28)');
                grad.addColorStop(1, 'rgba(0, 242, 254, 0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.moveTo((bx + 7) * S, (by + 10) * S);
                ctx.lineTo((bx - 1) * S, (by + 1) * S);
                ctx.lineTo((bx + 3) * S, (by - 1) * S);
                ctx.closePath();
                ctx.fill();

                // Tay trái kẹp điếu thuốc buông thõng
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 8) * S);
                ctx.lineTo((bx - 7) * S, (by + 13) * S);
                ctx.stroke();
                // Tàn thuốc hồng đỏ
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.arc((bx - 7.5) * S, (by + 13) * S, 1.2 * S, 0, Math.PI * 2);
                ctx.fill();

                // Làn khói uốn lượn
                ctx.strokeStyle = 'rgba(0,0,0,0.45)';
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo((bx - 7.5) * S, (by + 12) * S);
                ctx.bezierCurveTo((bx - 9) * S, (by + 9) * S, (bx - 7) * S, (by + 6) * S, (bx - 9) * S, (by + 3) * S);
                ctx.stroke();

                // Chân buông gác mui xe
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1.6, S * 0.35);
                ctx.beginPath();
                ctx.moveTo((bx - 1) * S, (by + 16) * S);
                ctx.lineTo((bx - 1) * S, 43 * S);
                ctx.lineTo((bx + 3) * S, 43 * S);
                ctx.stroke();

                // Trái tim rạn vỡ đập theo beat
                const heartSize = 4.8 + beatBounce * 1.5;
                drawHeart(ctx, 18, 13, heartSize, S, true);

            }} else if (action === 7) {{
                // ACTION 7: CAO TỐC VÔ CỰC, XE THỂ THAO ĐI XA DẦN VÀO MÀN ĐÊM
                drawHighwayLandscape(ctx, S, f);
                const carY = (37 + Math.sin(f * 0.1) * 1.5) * S;
                drawSportsCarRear(ctx, 28 * S, carY, S, f);
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
            iconPlay.style.display = 'none';
            iconPause.style.display = 'inline';

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
            iconPlay.style.display = 'inline';
            iconPause.style.display = 'none';

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

    print("\n=== HOÀN TẤT BỘ ANIMATION SIÊU CHI TIẾT & AUDIO EQUALIZER! ===")
    print("1. tellmewhy_frames.bin (Dữ liệu OLED SSD1306 có equalizer)")
    print("2. tellmewhy.gif (Ảnh GIF 384x192 khói thuốc, lái xe & thanh nhạc)")
    print("3. tell_me_why.cpp (C++ SFML độc lập)")
    print("4. run_tellmewhy.py + run_tellmewhy.bat (Trình phát Desktop native)")
    print("5. tell_me_why.html & index.html (Web Player siêu mượt Mobile Full-Height)")

if __name__ == "__main__":
    main()
