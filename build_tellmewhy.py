"""
Trình tạo trọn bộ Animation đồng bộ bài hát "TELL ME WHY" (Dương Domic)
Theo quy chuẩn AGENTS.md / Agent.md:
- 128x64 OLED monochrome 1-bit frames (tellmewhy_frames.bin)
- GIF preview 384x192 (tellmewhy.gif)
- C++ SFML source code (tell_me_why.cpp)
- Native Python Tkinter Desktop player (run_tellmewhy.py + run_tellmewhy.bat)
- Web Player chuẩn Mobile Full-Height (tell_me_why.html)
"""

import os
import sys
import wave
import struct
import math
import base64
from PIL import Image, ImageDraw, ImageFont

def main():
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("=== TẠO BỘ ANIMATION ĐỒNG BỘ: TELL ME WHY (DƯƠNG DOMIC) ===")

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

    samples = struct.unpack_from(f'<{nframes * nchannels}h', data)
    left = samples[0::nchannels]

    FRAME_MS = 70
    frame_samples = int(rate * (FRAME_MS / 1000.0))
    NUM_FRAMES = len(left) // frame_samples
    print(f"Tổng số frame: {NUM_FRAMES} (~{NUM_FRAMES * FRAME_MS / 1000:.1f}s)")

    energies = []
    for i in range(NUM_FRAMES):
        chunk = left[i * frame_samples : (i + 1) * frame_samples]
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) if chunk else 0
        energies.append(rms)

    max_e = max(energies) or 1
    norm_energies = [e / max_e for e in energies]

    try:
        font_lyrics = ImageFont.truetype('segoeuib.ttf', 8)
        font_finale = ImageFont.truetype('segoeuib.ttf', 8)
    except Exception:
        font_lyrics = font_finale = ImageFont.load_default()

    def s_to_f(s):
        return round(s / 0.070)

    # 7 Phân đoạn lời bài hát đồng bộ từng từ theo giây (Tell Me Why - Dương Domic)
    KARAOKE_TIMED_PHRASES = [
        # Câu 1 (0.0s -> 3.8s) - Action 1: Ôm gối ngắm trăng khuyết
        {
            "start_f": 0, "end_f": s_to_f(3.8), "action": 1,
            "lines": [
                [(0.2, "Từng"), (0.8, "cơn"), (1.4, "đau")],
                [(2.0, "tăng"), (2.6, "dần"), (3.1, "lên..."), (3.5, "🌧")]
            ]
        },
        # Câu 2 (3.8s -> 7.5s) - Action 2: Bước đi một mình, đồng hồ cát
        {
            "start_f": s_to_f(3.8), "end_f": s_to_f(7.5), "action": 2,
            "lines": [
                [(3.9, "Thời"), (4.5, "gian"), (5.0, "trôi")],
                [(5.6, "âm"), (6.2, "thầm"), (6.8, "đếm..."), (7.2, "⏳")]
            ]
        },
        # Câu 3 (7.5s -> 10.8s) - Action 3: Nỗi cô đơn, bóng hình em
        {
            "start_f": s_to_f(7.5), "end_f": s_to_f(10.8), "action": 3,
            "lines": [
                [(7.6, "Nỗi"), (8.1, "cô"), (8.6, "đơn")],
                [(9.1, "ghé"), (9.5, "qua"), (9.9, "đêm"), (10.3, "nay..."), (10.6, "🌙")]
            ]
        },
        # Câu 4 (10.8s -> 14.0s) - Action 4: Quay lưng trong gió đêm
        {
            "start_f": s_to_f(10.8), "end_f": s_to_f(14.0), "action": 4,
            "lines": [
                [(10.8, "Đêm"), (11.2, "qua,"), (11.6, "đêm"), (12.0, "nay")],
                [(12.4, "anh"), (12.8, "chẳng"), (13.2, "muốn")],
                [(13.5, "quay"), (13.8, "lại...")]
            ]
        },
        # Câu 5 (14.0s -> 17.5s) - Action 5: Phải xa em anh nào muốn
        {
            "start_f": s_to_f(14.0), "end_f": s_to_f(17.5), "action": 5,
            "lines": [
                [(14.1, "Phải"), (14.6, "xa"), (15.1, "em")],
                [(15.6, "anh"), (16.2, "nào"), (16.8, "muốn..."), (17.2, "💔")]
            ]
        },
        # Câu 6 (17.5s -> 21.5s) - Action 6: Vì chia đôi vẫn còn thương (chạm tay, tim hàn gắn)
        {
            "start_f": s_to_f(17.5), "end_f": s_to_f(21.5), "action": 6,
            "lines": [
                [(17.6, "Vì"), (18.1, "chia"), (18.6, "đôi")],
                [(19.2, "vẫn"), (19.8, "còn")],
                [(20.3, "thương..."), (20.8, "♥"), (21.2, "✨")]
            ]
        },
        # Câu 7 (21.5s -> 26.04s) - Action 7: Outro & Finale ấm áp
        {
            "start_f": s_to_f(21.5), "end_f": NUM_FRAMES, "action": 7,
            "lines": [
                [(21.6, "✨"), (22.0, "TELL"), (22.4, "ME"), (22.8, "WHY"), (23.2, "✨")],
                [(23.6, "Dương"), (24.0, "Domic")],
                [(24.5, "Vẫn"), (24.9, "còn"), (25.3, "thương"), (25.7, "nhau!"), (25.9, "💖")]
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

    print("Đang vẽ hoạt ảnh 128x64 chuẩn Pixel Art...")
    frame_images = []
    raw_all_bytes = bytearray()

    for f in range(NUM_FRAMES):
        img = Image.new('1', (128, 64), 1)  # 1 = Nền trắng
        draw = ImageDraw.Draw(img)
        energy = norm_energies[f]
        beat_bounce = int(energy * 2.5)

        # 1. Mặt đất & Dải phân cách dọc nhẹ nhàng
        draw.line([(0, 54), (127, 54)], fill=0)
        for dy in range(6, 50, 4):
            draw.point((56, dy), fill=0)

        # Cỏ hoa dưới chân
        for fx in [6, 18, 42, 50, 115, 122]:
            draw.point([(fx, 53), (fx, 52)], fill=0)

        # 2. VẼ CHỮ BÊN PHẢI (X: 58 đến 126, tâm tại X=92)
        action, lines = get_karaoke_data(f)
        text_x = 92
        num_l = len(lines)
        if num_l == 2:
            y_starts = [22, 36]
        elif num_l == 3:
            y_starts = [16, 28, 40]
        else:
            y_starts = [10, 20, 30, 40]

        for i, text_str in enumerate(lines):
            if text_str and i < len(y_starts):
                draw.text((text_x, y_starts[i]), text_str, font=font_lyrics, fill=0, anchor='mm')

        # 3. VẼ HOẠT CẢNH BÊN TRÁI (X: 0 đến 55)
        is_blinking = (f % 40 in [0, 1])

        if action == 1:
            # --- ACTION 1: TỪNG CƠN ĐAU TĂNG DẦN LÊN ---
            # Nam ngồi ôm gối, trăng khuyết & giọt sầu rơi
            bx = 26
            by = 38 - beat_bounce

            # Trăng khuyết trên bầu trời
            draw.arc([10, 8, 22, 20], start=45, end=270, fill=0)
            draw.arc([13, 8, 22, 20], start=60, end=250, fill=0)

            # Sao lấp lánh buồn
            if f % 10 < 6:
                draw.point([(38, 12), (37, 12), (39, 12), (38, 11), (38, 13)], fill=0)
                draw.point([(18, 22), (18, 21), (18, 23)], fill=0)

            # Chàng trai ngồi co ro
            draw.ellipse([bx-4, by-5, bx+4, by+5], outline=0, fill=1)
            draw.line([(bx-4, by-2), (bx+4, by-3)], fill=0)  # Tóc
            # Mắt nhắm buồn
            draw.line([(bx-3, by), (bx-1, by+1)], fill=0)
            draw.line([(bx+1, by), (bx+3, by+1)], fill=0)
            # Thân ngồi cuộn tròn
            draw.ellipse([bx-5, by+5, bx+5, by+15], outline=0, fill=1)
            # Tay ôm gối
            draw.arc([bx-5, by+7, bx+5, by+13], start=0, end=180, fill=0)
            # Tim rạn nứt
            draw.polygon([(bx+8, by-2), (bx+6, by-5), (bx+10, by-5)], outline=0, fill=0)
            draw.line([(bx+8, by-5), (bx+8, by-2)], fill=1)

        elif action == 2:
            # --- ACTION 2: THỜI GIAN TRÔI ÂM THẦM ĐẾM ---
            # Đồng hồ cát & Chàng trai bước đi trong đêm
            walk = (f // 2) % 4
            bx = 22
            by = 31 - beat_bounce

            # Đồng hồ cát ở góc trên
            hx = 38
            hy = 14
            draw.polygon([(hx-5, hy-6), (hx+5, hy-6), (hx, hy), (hx+5, hy+6), (hx-5, hy+6), (hx, hy)], outline=0, fill=1)
            draw.line([(hx-6, hy-6), (hx+6, hy-6)], fill=0)
            draw.line([(hx-6, hy+6), (hx+6, hy+6)], fill=0)
            # Hạt cát rơi
            if (f % 4) < 2:
                draw.point([(hx, hy+2), (hx, hy+4)], fill=0)

            # Nam bước đi
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            eye_y = by if not is_blinking else by + 1
            draw.point([(bx-2, eye_y), (bx+2, eye_y)], fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            # Khăn len bay trong gió
            scarf_wave = int(math.sin(f * 0.4) * 2)
            draw.line([(bx-4, by+8), (bx-9, by+9 + scarf_wave)], fill=0)
            # Chân bước
            if walk in [0, 2]:
                draw.line([(bx-2, by+15), (bx-4, 53)], fill=0)
                draw.line([(bx+2, by+15), (bx+4, 53)], fill=0)
            else:
                draw.line([(bx-2, by+15), (bx, 53)], fill=0)
                draw.line([(bx+2, by+15), (bx+1, 53)], fill=0)

        elif action == 3:
            # --- ACTION 3: NỖI CÔ ĐƠN GHÉ QUA ĐÊM NAY ---
            # Nam với tay tìm bóng hình Nữ mờ ảo
            bx = 18
            gx = 42
            by = 31 - beat_bounce
            gy = 31

            # Đám mây đêm xám
            draw.ellipse([20, 6, 36, 14], outline=0, fill=1)
            draw.ellipse([26, 4, 42, 12], outline=0, fill=1)

            # Nam với tay
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx+4, by+9), (bx+10, by+7)], fill=0)  # Tay với
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ nhìn lại xa xăm
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)  # Nơ
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

        elif action == 4:
            # --- ACTION 4: QUAY LƯNG TRONG ĐÊM ---
            # Nam và Nữ đứng quay lưng, vạt áo lay động
            bx = 20
            gx = 36
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            # Nam nhìn sang trái
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-3, by)], fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+9), (bx-7, by+13)], fill=0)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ nhìn sang phải
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx+3, gy)], fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx+4, gy+9), (gx+7, gy+13)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Cơn gió thổi giữa 2 người
            wind_x = 28 + int(math.sin(f * 0.5) * 3)
            draw.arc([wind_x-4, 25, wind_x+4, 35], start=45, end=180, fill=0)

        elif action == 5:
            # --- ACTION 5: PHẢI XA EM ANH NÀO MUỐN ---
            # Nam che ô / chìa tay, Nữ ngấn lệ
            bx = 18
            gx = 36
            by = 31
            gy = 31

            # Nam cầm ô
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx+4, by+9), (28, 30)], fill=0)  # Cán ô
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Chiếc ô che cho cả hai
            draw.arc([16, 12, 40, 32], start=180, end=360, fill=0)
            draw.line([(16, 22), (40, 22)], fill=0)
            draw.line([(28, 22), (28, 34)], fill=0)

            # Nữ ngước nhìn, giọt lệ rơi
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            # Giọt lệ rơi
            tear_y = gy + 2 + (f % 5)
            draw.point([(gx-1, tear_y)], fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

        elif action == 6:
            # --- ACTION 6: VÌ CHIA ĐÔI VẪN CÒN THƯƠNG ---
            # Chạm tay nhau, trái tim hàn gắn phập phồng
            bx = 20
            gx = 36
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            # Nam
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx+4, by+9), (28, 39)], fill=0)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-4, gy+9), (28, 39)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Nắm tay nhau tại X=28, Y=39
            draw.point([(28, 39), (28, 40)], fill=0)

            # Trái tim to ở giữa phập phồng theo beat
            hw = 4 + beat_bounce
            hx = 28
            hy = 18 - int(math.sin(f * 0.3) * 2)
            draw.polygon([(hx, hy+hw), (hx-hw, hy), (hx-hw+1, hy-hw//2), (hx, hy-hw//3), (hx+hw-1, hy-hw//2), (hx+hw, hy)], fill=0)

        elif action == 7:
            # --- ACTION 7: OUTRO & FINALE ---
            # Cặp đôi ôm ấm áp & Bắn pháo hoa sao lấp lánh
            bx = 24
            gx = 32
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            # Thân ôm nhau
            draw.rectangle([bx-4, by+7, gx+4, by+15], outline=0, fill=1)
            draw.line([(bx-4, by+9), (gx+2, by+10)], fill=0)
            draw.line([(gx+4, gy+9), (bx-2, by+10)], fill=0)
            draw.line([(bx-2, by+16), (bx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Đầu Nam
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+3], start=0, end=180, fill=0)

            # Đầu Nữ
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+3], start=0, end=180, fill=0)

            # Bóng bay trái tim bay bổng
            blx = 28 + int(math.sin(f * 0.25) * 3)
            bly = 10
            draw.polygon([(blx, bly+4), (blx-4, bly), (blx-3, bly-2), (blx, bly-1), (blx+3, bly-2), (blx+4, bly)], fill=0)
            draw.line([(blx, bly+4), (28, 24)], fill=0)

            # Pháo hoa sao lấp lánh hai bên
            fx_y = 12 + (f % 5)
            draw.point([(8, fx_y), (7, fx_y), (9, fx_y), (8, fx_y-1), (8, fx_y+1)], fill=0)
            draw.point([(48, fx_y+2), (47, fx_y+2), (49, fx_y+2), (48, fx_y+1), (48, fx_y+3)], fill=0)

        # 4. CHUYỂN THÀNH 1024 BYTES (1 bit/pixel MSB-first)
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
    sf::RenderWindow window(sf::VideoMode(WIDTH * SCALE, HEIGHT * SCALE), "TELL ME WHY - Duong Domic [SFML OLED Player]");
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
        self.root.title("TELL ME WHY 💖 - Dương Domic (Animation Player)")
        self.root.geometry(f"{{WINDOW_WIDTH}}x{{WINDOW_HEIGHT}}")
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
    print("Đang tạo tell_me_why.html chuẩn Mobile Full-Height...")
    frames_b64 = base64.b64encode(raw_all_bytes).decode('ascii')
    with open(mp3_path, "rb") as af:
        audio_b64 = base64.b64encode(af.read()).decode('ascii')

    html_code = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>TELL ME WHY 💖 - Dương Domic (Animation Player)</title>
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
            background: radial-gradient(ellipse at 50% 30%, #171026 0%, #07040d 100%);
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
            background: rgba(22, 14, 38, 0.82);
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
            <div class="badge">✨ TELL ME WHY ✨</div>
            <div class="song-title">TELL ME WHY</div>
            <div class="song-artist">Dương Domic</div>
        </div>

        <div class="screen-wrapper" id="screenWrapper">
            <canvas id="screenCanvas"></canvas>
            <div class="play-overlay" id="playOverlay">
                <div class="play-btn-circle">
                    <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </div>
                <div class="play-btn-text" id="playBtnText">Chạm để lắng nghe 💖</div>
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
                    [{{t: 24.5, w: "Vẫn"}}, {{t: 24.9, w: "còn"}}, {{t: 25.3, w: "thương"}}, {{t: 25.7, w: "nhau!"}}, {{t: 25.9, w: "💖"}}]
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

        // Helper vẽ nhân vật vector HD
        function drawBoy(ctx, bx, by, S, opts = {{}}) {{
            const eye = opts.eye || 'dot';
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(bx * S, by * S, 5 * S, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Tóc ngắn
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.moveTo((bx - 5) * S, (by - 2) * S);
            ctx.lineTo((bx - 6) * S, (by - 6) * S);
            ctx.lineTo(bx * S, (by - 7.5) * S);
            ctx.lineTo((bx + 5) * S, (by - 5) * S);
            ctx.lineTo((bx + 5) * S, (by - 1) * S);
            ctx.closePath();
            ctx.fill();

            // Mắt
            if (eye === 'blink') {{
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, (by + 1) * S);
                ctx.moveTo((bx + 1) * S, by * S);
                ctx.lineTo((bx + 3) * S, (by + 1) * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.arc((bx - 2) * S, by * S, S * 0.85, 0, Math.PI * 2);
                ctx.arc((bx + 2) * S, by * S, S * 0.85, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Thân
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.roundRect((bx - 4) * S, (by + 7) * S, 8 * S, 7.5 * S, 2 * S);
            ctx.fill();
            ctx.stroke();

            // Tay
            if (opts.armR) {{
                ctx.beginPath();
                ctx.moveTo(opts.armR[0][0] * S, opts.armR[0][1] * S);
                ctx.lineTo(opts.armR[1][0] * S, opts.armR[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((bx + 4) * S, (by + 9) * S);
                ctx.lineTo((bx + 7) * S, (by + 14) * S);
                ctx.stroke();
            }}

            if (opts.armL) {{
                ctx.beginPath();
                ctx.moveTo(opts.armL[0][0] * S, opts.armL[0][1] * S);
                ctx.lineTo(opts.armL[1][0] * S, opts.armL[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((bx - 4) * S, (by + 9) * S);
                ctx.lineTo((bx - 7) * S, (by + 14) * S);
                ctx.stroke();
            }}

            // Chân
            ctx.beginPath();
            ctx.moveTo((bx - 2) * S, (by + 15) * S);
            ctx.lineTo((bx - 2) * S, 53.5 * S);
            ctx.moveTo((bx + 2) * S, (by + 15) * S);
            ctx.lineTo((bx + 2) * S, 53.5 * S);
            ctx.stroke();
        }}

        function drawGirl(ctx, gx, gy, S, opts = {{}}) {{
            const eye = opts.eye || 'dot';
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(gx * S, gy * S, 5 * S, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // Tóc dài hai bên
            ctx.beginPath();
            ctx.arc(gx * S, (gy - 2) * S, 5.5 * S, Math.PI, 0);
            ctx.moveTo((gx - 5.5) * S, (gy - 2) * S);
            ctx.lineTo((gx - 6.5) * S, (gy + 7) * S);
            ctx.moveTo((gx + 5.5) * S, (gy - 2) * S);
            ctx.lineTo((gx + 6.5) * S, (gy + 7) * S);
            ctx.stroke();

            // Nơ cài tóc
            if (opts.bow) {{
                ctx.fillStyle = '#ff4d8d';
                ctx.beginPath();
                ctx.moveTo((gx + 4) * S, (gy - 5) * S);
                ctx.lineTo((gx + 8) * S, (gy - 7) * S);
                ctx.lineTo((gx + 8) * S, (gy - 2) * S);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }}

            // Mắt
            ctx.fillStyle = '#000000';
            if (eye === 'blink') {{
                ctx.beginPath();
                ctx.moveTo((gx - 3) * S, gy * S);
                ctx.lineTo((gx - 1) * S, (gy + 1) * S);
                ctx.moveTo((gx + 1) * S, gy * S);
                ctx.lineTo((gx + 3) * S, (gy + 1) * S);
                ctx.stroke();
            }} else if (eye === 'happy') {{
                ctx.beginPath();
                ctx.arc((gx - 2) * S, gy * S, S * 1.5, Math.PI, 0);
                ctx.arc((gx + 2) * S, gy * S, S * 1.5, Math.PI, 0);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.arc((gx - 2) * S, gy * S, S * 0.85, 0, Math.PI * 2);
                ctx.arc((gx + 2) * S, gy * S, S * 0.85, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Váy xòe
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.moveTo(gx * S, (gy + 7) * S);
            ctx.lineTo((gx - 5.5) * S, (gy + 15) * S);
            ctx.lineTo((gx + 5.5) * S, (gy + 15) * S);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Tay
            if (opts.armL) {{
                ctx.beginPath();
                ctx.moveTo(opts.armL[0][0] * S, opts.armL[0][1] * S);
                ctx.lineTo(opts.armL[1][0] * S, opts.armL[1][1] * S);
                ctx.stroke();
            }}
            if (opts.armR) {{
                ctx.beginPath();
                ctx.moveTo(opts.armR[0][0] * S, opts.armR[0][1] * S);
                ctx.lineTo(opts.armR[1][0] * S, opts.armR[1][1] * S);
                ctx.stroke();
            }}

            // Chân
            ctx.beginPath();
            ctx.moveTo((gx - 2) * S, (gy + 15.5) * S);
            ctx.lineTo((gx - 2) * S, 53.5 * S);
            ctx.moveTo((gx + 2) * S, (gy + 15.5) * S);
            ctx.lineTo((gx + 2) * S, 53.5 * S);
            ctx.stroke();
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
            const f = Math.floor(cur_t / 0.070);
            const isBlinking = (f % 40 === 0 || f % 40 === 1);
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

            // 1. Đường đất chạy ngang tràn viền
            ctx.beginPath();
            ctx.moveTo(-offsetX, 54 * S);
            ctx.lineTo(canvas.width - offsetX, 54 * S);
            ctx.stroke();

            // 2. Cỏ hoa
            [6, 18, 42, 50, 115, 122].forEach(gx => {{
                ctx.beginPath();
                ctx.moveTo(gx * S, 53.5 * S);
                ctx.lineTo(gx * S, 50.5 * S);
                ctx.stroke();
            }});

            // 3. Vách ngăn dải chấm
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
                ? [22 * S, 36 * S]
                : (lines.length === 3 ? [17 * S, 29 * S, 41 * S] : [11 * S, 21 * S, 31 * S, 41 * S]);

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

            // 5. Diễn hoạt nhân vật bên trái (X: 0..55)
            if (action === 1) {{
                // ACTION 1: Từng cơn đau tăng dần lên (Ôm gối, trăng khuyết)
                const bx = 26;
                const by = 38 - beatBounce;

                // Trăng khuyết
                ctx.beginPath();
                ctx.arc(16 * S, 14 * S, 6 * S, Math.PI * 0.3, Math.PI * 1.5);
                ctx.arc(19 * S, 14 * S, 5 * S, Math.PI * 1.4, Math.PI * 0.4, true);
                ctx.stroke();

                // Nam ngồi ôm gối
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(bx * S, by * S, 4.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Tóc
                ctx.beginPath();
                ctx.moveTo((bx - 4.5) * S, (by - 2) * S);
                ctx.lineTo((bx + 4.5) * S, (by - 3) * S);
                ctx.stroke();

                // Mắt nhắm buồn
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, (by + 1) * S);
                ctx.moveTo((bx + 1) * S, by * S);
                ctx.lineTo((bx + 3) * S, (by + 1) * S);
                ctx.stroke();

                // Thân cuộn tròn
                ctx.beginPath();
                ctx.ellipse(bx * S, (by + 9) * S, 5 * S, 5.5 * S, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Tim rạn nứt
                drawHeart(ctx, bx + 9, by - 2, 2.5, S);

            }} else if (action === 2) {{
                // ACTION 2: Thời gian trôi âm thầm đếm (Bước đi, đồng hồ cát)
                const bx = 22;
                const by = 31 - beatBounce;

                // Đồng hồ cát
                ctx.beginPath();
                ctx.moveTo(33 * S, 8 * S);
                ctx.lineTo(43 * S, 8 * S);
                ctx.lineTo(38 * S, 14 * S);
                ctx.lineTo(43 * S, 20 * S);
                ctx.lineTo(33 * S, 20 * S);
                ctx.lineTo(38 * S, 14 * S);
                ctx.closePath();
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                drawBoy(ctx, bx, by, S, {{ eye: isBlinking ? 'blink' : 'dot' }});

                // Khăn len bay
                const scarf_wave = Math.sin(f * 0.4) * 2;
                ctx.beginPath();
                ctx.moveTo((bx - 4) * S, (by + 8) * S);
                ctx.lineTo((bx - 9) * S, (by + 9 + scarf_wave) * S);
                ctx.stroke();

            }} else if (action === 3) {{
                // ACTION 3: Nỗi cô đơn ghé qua đêm nay (Với tay tìm bóng hình)
                const bx = 18;
                const gx = 42;
                const by = 31 - beatBounce;
                const gy = 31;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 4, by + 9], [bx + 11, by + 7]]
                }});

                // Nữ xa xăm
                drawGirl(ctx, gx, gy, S, {{ bow: true, eye: 'blink' }});

                // Mây đêm
                ctx.beginPath();
                ctx.ellipse(28 * S, 10 * S, 8 * S, 4 * S, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

            }} else if (action === 4) {{
                // ACTION 4: Đêm qua đêm nay anh chẳng muốn quay lại (Quay lưng trong gió)
                const bx = 20;
                const gx = 36;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: 'dot',
                    armL: [[bx - 4, by + 9], [bx - 7, by + 13]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'dot',
                    armR: [[gx + 4, gy + 9], [gx + 7, gy + 13]]
                }});

                // Gió thổi ở giữa
                const wind_x = 28 + Math.sin(f * 0.5) * 3;
                drawStar(ctx, wind_x, 24, 2.2, S);

            }} else if (action === 5) {{
                // ACTION 5: Phải xa em anh nào muốn (Che ô, giọt lệ rơi)
                const bx = 18;
                const gx = 36;
                const by = 31;
                const gy = 31;

                // Ô che
                ctx.beginPath();
                ctx.arc(28 * S, 21 * S, 14 * S, Math.PI, 0);
                ctx.closePath();
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(28 * S, 21 * S);
                ctx.lineTo(28 * S, 36 * S);
                ctx.stroke();

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 4, by + 9], [28, 33]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy'
                }});

                // Trái tim vỡ lơ lửng
                drawHeart(ctx, 28, 9, 3.2, S);

            }} else if (action === 6) {{
                // ACTION 6: Vì chia đôi vẫn còn thương (Chạm tay, tim hàn gắn)
                const bx = 20;
                const gx = 36;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 4, by + 9], [28, 39]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 4, gy + 9], [28, 39]]
                }});

                // Nắm tay
                ctx.beginPath();
                ctx.arc(28 * S, 39 * S, S * 1.2, 0, Math.PI * 2);
                ctx.fill();

                // Trái tim lớn đập rộn ràng
                const heartSize = 3.8 + beatBounce * 1.4;
                const hy = 18 - Math.sin(f * 0.3) * 2;
                drawHeart(ctx, 28, hy, heartSize, S);

            }} else if (action === 7) {{
                // ACTION 7: OUTRO & FINALE (Ôm ấm áp, pháo hoa)
                const bx = 24;
                const gx = 32;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Thân ôm
                ctx.beginPath();
                ctx.rect((bx - 4) * S, (by + 7) * S, 16 * S, 8 * S);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Đầu Nam & Nữ
                drawBoy(ctx, bx, by, S, {{ eye: isBlinking ? 'blink' : 'dot' }});
                drawGirl(ctx, gx, gy, S, {{ bow: true, eye: isBlinking ? 'blink' : 'dot' }});

                // Bóng bay trái tim
                const blx = 28 + Math.sin(f * 0.25) * 3;
                const bly = 10;
                drawHeart(ctx, blx, bly, 4.2, S);
                ctx.beginPath();
                ctx.moveTo(blx * S, (bly + 4.2) * S);
                ctx.lineTo(28 * S, 24 * S);
                ctx.stroke();

                // Pháo hoa sao lấp lánh
                const fx_y = 12 + (f % 5);
                drawStar(ctx, 8, fx_y, 3.5, S);
                drawStar(ctx, 48, fx_y + 2, 3.5, S);
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
            playBtnText.textContent = 'Tiếp tục 💖';
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

    # Cập nhật index.html để có thể mở ngay Tell Me Why
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("Đã cập nhật index.html để phát Tell Me Why mặc định!")

    print("\n=== HOÀN TẤT TOÀN BỘ SẢN PHẨM 'TELL ME WHY' (DƯƠNG DOMIC) ===")
    print("1. tellmewhy_frames.bin (Dữ liệu OLED SSD1306)")
    print("2. tellmewhy.gif (Ảnh GIF 384x192)")
    print("3. tell_me_why.cpp (C++ SFML độc lập)")
    print("4. run_tellmewhy.py + run_tellmewhy.bat (Trình phát Desktop native)")
    print("5. tell_me_why.html & index.html (Web Player siêu mượt Mobile Full-Height)")

if __name__ == "__main__":
    main()
