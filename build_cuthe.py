"""
Trình tạo animation CỨ THẾ (Orange x Hoàng Dũng) - Bố cục chuẩn bản gốc
- Trái: Hoạt ảnh nhân vật phong phú, thay đổi động tác theo từng câu hát.
- Phải: Chữ chạy Karaoke từng từ theo nhịp bài hát.
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
    print("=== TAO ANIMATION 'CU THE' BO CUC CHUAN BAN GOC ===")

    wav_path = "cuthe_chorus.wav"
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Khong tim thay {wav_path}!")

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
    print(f"Tong so frame: {NUM_FRAMES} (~{NUM_FRAMES * FRAME_MS / 1000:.1f}s)")

    energies = []
    for i in range(NUM_FRAMES):
        chunk = left[i * frame_samples : (i + 1) * frame_samples]
        rms = math.sqrt(sum(s*s for s in chunk) / len(chunk)) if chunk else 0
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

    # 10 câu hát với mốc thời gian chi tiết từng dòng bên phải (Pre-chorus + Điệp khúc Cứ Thế)
    KARAOKE_TIMED_PHRASES = [
        # Câu 1 (Pre-chorus): (0.0s đến 4.3s)
        {
            "start_f": 0, "end_f": s_to_f(4.3), "action": 1,
            "lines": [
                [(0.1, "Tình"), (0.5, "yêu"), (0.9, "là")],
                [(1.3, "giấc"), (1.7, "mộng"), (2.1, "đẹp")],
                [(2.6, "và"), (2.9, "anh"), (3.2, "vốn")],
                [(3.5, "chẳng"), (3.8, "muốn"), (4.1, "tỉnh"), (4.3, "dậy...")]
            ]
        },
        # Câu 2 (Pre-chorus): (4.4s đến 8.7s)
        {
            "start_f": s_to_f(4.4), "end_f": s_to_f(8.7), "action": 2,
            "lines": [
                [(4.7, "Trừ"), (5.1, "khi"), (5.5, "sớm"), (5.8, "mai")],
                [(6.2, "mở"), (6.6, "mắt")],
                [(7.0, "thấy"), (7.4, "em"), (7.8, "ở"), (8.2, "đây..."), (8.5, "✨")]
            ]
        },
        # Câu 3: (8.8s đến 12.8s)
        {
            "start_f": s_to_f(8.8), "end_f": s_to_f(12.8), "action": 3,
            "lines": [
                [(9.3, "Ta"), (9.7, "cứ"), (10.1, "thế,")],
                [(10.6, "cứ"), (11.0, "thế")],
                [(11.4, "yêu"), (11.8, "nhiều"), (12.2, "thêm"), (12.4, "♥")]
            ]
        },
        # Câu 4: (12.9s đến 16.7s)
        {
            "start_f": s_to_f(12.9), "end_f": s_to_f(16.7), "action": 4,
            "lines": [
                [(13.0, "Ai"), (13.4, "không"), (13.8, "vui,")],
                [(14.3, "ta"), (14.7, "cứ"), (15.1, "cho")],
                [(15.5, "họ"), (15.9, "xem!")]
            ]
        },
        # Câu 5: (16.8s đến 20.8s)
        {
            "start_f": s_to_f(16.8), "end_f": s_to_f(20.8), "action": 5,
            "lines": [
                [(16.8, "Đã"), (17.2, "có")],
                [(17.6, "nhau"), (18.0, "rồi")],
                [(18.6, "thì"), (19.0, "nhất"), (19.4, "quyết")],
                [(19.8, "không"), (20.2, "rời!")]
            ]
        },
        # Câu 6: (20.9s đến 24.8s)
        {
            "start_f": s_to_f(20.9), "end_f": s_to_f(24.8), "action": 6,
            "lines": [
                [(21.1, "Don't"), (21.5, "stop")],
                [(21.9, "this"), (22.3, "feeling,")],
                [(22.9, "it"), (23.3, "won't")],
                [(23.7, "go"), (24.1, "away..."), (24.4, "✨")]
            ]
        },
        # Câu 7: (24.9s đến 28.8s)
        {
            "start_f": s_to_f(24.9), "end_f": s_to_f(28.8), "action": 7,
            "lines": [
                [(25.1, "Yêu"), (25.5, "đi,")],
                [(25.9, "yêu"), (26.3, "vui"), (26.7, "lắm,")],
                [(27.3, "yêu"), (27.8, "nhiều"), (28.2, "lên!"), (28.5, "💐")]
            ]
        },
        # Câu 8: (28.9s đến 32.8s)
        {
            "start_f": s_to_f(28.9), "end_f": s_to_f(32.8), "action": 8,
            "lines": [
                [(29.1, "Đâu"), (29.5, "ai"), (29.9, "mong")],
                [(30.4, "cứ"), (30.8, "đớn"), (31.2, "đau")],
                [(31.6, "triền"), (32.0, "miên...")]
            ]
        },
        # Câu 9: (32.9s đến 36.8s)
        {
            "start_f": s_to_f(32.9), "end_f": s_to_f(36.8), "action": 9,
            "lines": [
                [(32.9, "Đã"), (33.3, "có")],
                [(33.7, "nhau"), (34.1, "rồi")],
                [(34.7, "thì"), (35.1, "nhất"), (35.5, "quyết")],
                [(35.9, "không"), (36.3, "rời"), (36.5, "♥")]
            ]
        },
        # Câu 10: (36.9s đến 41.0s - Finale 20/10)
        {
            "start_f": s_to_f(36.9), "end_f": NUM_FRAMES, "action": 10,
            "lines": [
                [(37.1, "💖"), (37.4, "CHÚC"), (37.7, "MỪNG"), (38.0, "💖")],
                [(38.3, "NGÀY"), (38.7, "20/10")],
                [(39.1, "Cứ"), (39.5, "thế"), (39.8, "yêu")],
                [(40.1, "thương"), (40.4, "nha!"), (40.7, "✨")]
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

    print("Đang vẽ hoạt ảnh chi tiết (Nhân vật bên trái - Chữ bên phải)...")
    frame_images = []
    raw_all_bytes = bytearray()

    for f in range(NUM_FRAMES):
        img = Image.new('1', (128, 64), 1) # 1 = Nền trắng
        draw = ImageDraw.Draw(img)
        energy = norm_energies[f]
        beat_bounce = int(energy * 2.5) # 0 đến 2 pixel nhún nhảy

        # 1. Đường đất & Dải phân cách dọc nhẹ nhàng
        draw.line([(0, 54), (127, 54)], fill=0) # Mặt đất
        for dy in range(6, 50, 4):
            draw.point((56, dy), fill=0) # Dấu phân chia vùng trái/phải

        # Cỏ hoa dưới chân
        for fx in [6, 18, 42, 50, 115, 122]:
            draw.point([(fx, 53), (fx, 52)], fill=0)

        # 2. VẼ CHỮ BÊN PHẢI (X: 58 đến 126, tâm tại X=92)
        action, lines = get_karaoke_data(f)
        text_x = 92
        num_l = len(lines)
        if num_l == 3:
            y_starts = [16, 28, 40]
        else: # 4 dòng
            y_starts = [10, 20, 30, 40]

        for i, text_str in enumerate(lines):
            if text_str and i < len(y_starts):
                draw.text((text_x, y_starts[i]), text_str, font=font_lyrics, fill=0, anchor='mm')

        # 3. VẼ HOẠT ẢNH BÊN TRÁI THEO TỪNG CÂU HÁT (X: 0 đến 54)
        is_blinking = (f % 40 in [0, 1])

        if action == 1:
            # --- CÂU 1 (PRE-CHORUS): GIẤC MỘNG ĐẸP CHẲNG MUỐN TỈNH DẬY ---
            bx = 26
            by = 31 - beat_bounce

            # Đầu & Tóc
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            # Mắt nhắm ngủ mơ màng ^ ^
            draw.line([(bx-4, by), (bx-2, by-1)], fill=0)
            draw.line([(bx-2, by-1), (bx, by)], fill=0)
            draw.line([(bx+1, by), (bx+3, by-1)], fill=0)
            draw.line([(bx+3, by-1), (bx+5, by)], fill=0)
            # Miệng mỉm cười ngọt ngào
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)

            # Thân & Tay buông thả lỏng
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+8), (bx-7, by+13)], fill=0)
            draw.line([(bx+4, by+8), (bx+7, by+13)], fill=0)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Đám mây giấc mơ (Dream cloud) bồng bềnh
            cloud_float = int(math.sin(f * 0.2) * 1.5)
            cy = 13 + cloud_float
            cx = 30
            draw.ellipse([cx-12, cy-5, cx+12, cy+5], outline=0, fill=1)
            draw.ellipse([cx-8, cy-8, cx+2, cy+2], outline=0, fill=1)
            draw.ellipse([cx, cy-9, cx+9, cy+1], outline=0, fill=1)
            # Trái tim mơ mộng bên trong
            draw.polygon([(cx, cy+2), (cx-3, cy-1), (cx-2, cy-3), (cx, cy-2), (cx+2, cy-3), (cx+3, cy-1)], fill=0)
            # Bọt bóng suy nghĩ từ đầu lên mây
            draw.point([(bx+2, by-8), (bx+4, by-10), (bx+6, by-12)], fill=0)

        elif action == 2:
            # --- CÂU 2 (PRE-CHORUS): SỚM MAI MỞ MẮT THẤY EM Ở ĐÂY ---
            bx = 18
            gx = 38
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            # Mặt trời ban mai góc trái trên
            draw.arc([3, 3, 13, 13], start=0, end=360, fill=0)
            draw.line([(8, 1), (8, 0)], fill=0)
            draw.line([(8, 15), (8, 16)], fill=0)
            draw.line([(1, 8), (0, 8)], fill=0)
            draw.line([(15, 8), (16, 8)], fill=0)
            draw.line([(12, 4), (14, 2)], fill=0)
            draw.line([(12, 12), (14, 14)], fill=0)

            # Nam mở mắt tươi cười ngạc nhiên
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+8), (bx-7, by+13)], fill=0)
            draw.line([(bx+4, by+8), (bx+7, by+10)], fill=0) # Đưa tay chào
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ xuất hiện mỉm cười và vẫy tay
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            # Nơ tóc
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            # Mắt cười
            draw.line([(gx-4, gy), (gx-2, gy-1)], fill=0)
            draw.line([(gx-2, gy-1), (gx, gy)], fill=0)
            draw.line([(gx+1, gy), (gx+3, gy-1)], fill=0)
            draw.line([(gx+3, gy-1), (gx+5, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            # Tay vẫy
            wave_y = int(math.sin(f * 0.5) * 3)
            draw.line([(gx-4, gy+8), (gx-7, gy+13)], fill=0)
            draw.line([(gx+4, gy+8), (gx+8, gy+2 + wave_y)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Lấp lánh giữa 2 người
            draw.point([(28, 20), (27, 20), (29, 20), (28, 19), (28, 21)], fill=0)

        elif action == 3:
            # --- CÂU 3: BẠN NAM SẢI BƯỚC TỰ TIN (WALK CYCLE) ---
            bx = int(10 + (f / 54.0) * 22)
            by = 30 - beat_bounce
            walk = (f // 3) % 4
            
            # Đầu & Tóc
            draw.ellipse([bx-6, by-6, bx+6, by+6], outline=0, fill=1)
            draw.polygon([(bx-6, by-2), (bx-7, by-6), (bx-3, by-8), (bx+2, by-7), (bx+6, by-3), (bx+6, by-1)], outline=0, fill=0)
            if is_blinking:
                draw.line([(bx-4, by), (bx-2, by)], fill=0)
                draw.line([(bx+2, by), (bx+4, by)], fill=0)
            else:
                draw.point([(bx-3, by), (bx+3, by)], fill=0)
            # Miệng huýt sáo
            draw.ellipse([bx-1, by+2, bx+2, by+4], outline=0, fill=1)

            # Thân
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            # Tay vung theo bước đi
            if walk in [0, 1]:
                draw.line([(bx-4, by+8), (bx-8, by+13)], fill=0)
                draw.line([(bx+4, by+8), (bx+8, by+11)], fill=0)
                # Chân bước
                draw.line([(bx-2, by+15), (bx-5, 53)], fill=0)
                draw.line([(bx+2, by+15), (bx+5, 53)], fill=0)
            else:
                draw.line([(bx-4, by+8), (bx-8, by+11)], fill=0)
                draw.line([(bx+4, by+8), (bx+8, by+13)], fill=0)
                draw.line([(bx-2, by+15), (bx+4, 53)], fill=0)
                draw.line([(bx+2, by+15), (bx-4, 53)], fill=0)

            # Nốt nhạc bay phía sau
            ny = 25 - ((f * 1.5) % 22)
            nx = max(4, bx - 14 + int(math.sin(f * 0.3) * 2))
            draw.point([(nx, ny), (nx+1, ny), (nx+1, ny-1), (nx+1, ny-2), (nx+2, ny-2)], fill=0)

        elif action == 4:
            # --- CÂU 4: BẠN NỮ XUẤT HIỆN, TẠO DÁNG CHỮ V & NGẦU ---
            bx = 18
            gx = 38
            by = 30 - beat_bounce
            gy = 30 - beat_bounce

            # Nam: khoanh tay / cool ngầu
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.line([(bx-3, by), (bx-1, by)], fill=0) # Mắt nháy
            draw.point([(bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+9), (bx+4, by+11)], fill=0) # Khoanh tay
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ: tay giơ chữ V (Peace)
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            # Nơ tóc
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            if is_blinking:
                draw.line([(gx-4, gy), (gx-2, gy)], fill=0)
                draw.line([(gx+2, gy), (gx+4, gy)], fill=0)
            else:
                draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-4, gy+9), (gx-7, gy+14)], fill=0)
            # Tay chữ V
            draw.line([(gx+4, gy+8), (gx+8, gy+2)], fill=0)
            draw.line([(gx+8, gy+2), (gx+7, gy-3)], fill=0)
            draw.line([(gx+8, gy+2), (gx+10, gy-3)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Ngôi sao lấp lánh cạnh bạn nữ
            draw.point([(gx+14, gy-2), (gx+13, gy-2), (gx+15, gy-2), (gx+14, gy-3), (gx+14, gy-1)], fill=0)

        elif action == 5:
            # --- CÂU 5: NẮM TAY NHAU & TRÁI TIM ĐẬP THÌNH THỊCH ---
            bx = 20
            gx = 36
            by = 30 - beat_bounce
            gy = 30 - beat_bounce

            # Nam
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+9), (bx-7, by+14)], fill=0)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Nữ
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx+4, gy+9), (gx+7, gy+14)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            # Nắm tay nhau ở giữa (X=28, Y=39)
            draw.line([(bx+4, by+9), (28, 39)], fill=0)
            draw.line([(gx-4, gy+9), (28, 39)], fill=0)
            draw.point([(28, 39), (28, 40)], fill=0)

            # Trái tim to ở giữa phập phồng theo beat
            hw = 4 + beat_bounce
            hx = 28
            hy = 20 - int(math.sin(f * 0.3) * 2)
            draw.polygon([(hx, hy+hw), (hx-hw, hy), (hx-hw+1, hy-hw//2), (hx, hy-hw//3), (hx+hw-1, hy-hw//2), (hx+hw, hy)], fill=0)

        elif action == 6:
            # --- CÂU 6: KHIÊU VŨ XOAY VÒNG (SWING DANCE) ---
            sway = int(math.sin(f * 0.4) * 3)
            bx = 18 + sway
            gx = 36 + sway
            by = 30 - beat_bounce
            gy = 30 - beat_bounce

            # Nam
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-4, by+9), (bx-8, by+12)], fill=0)
            draw.line([(bx-2, by+15), (bx-4, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx, 53)], fill=0)

            # Nữ
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.polygon([(gx+4, gy-5), (gx+8, gy-7), (gx+8, gy-2)], outline=0, fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            # Váy xòe bay theo điệu nhảy
            draw.polygon([(gx, gy+7), (gx-7, gy+15), (gx+7, gy+15)], outline=0, fill=1)
            draw.line([(gx+4, gy+9), (gx+8, gy+12)], fill=0)
            draw.line([(gx-2, gy+16), (gx, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+4, 53)], fill=0)

            # Tay giơ cao nắm nhau xoay tròn
            draw.line([(bx+4, by+8), (27 + sway, 20)], fill=0)
            draw.line([(gx-4, gy+8), (27 + sway, 20)], fill=0)
            draw.point([(27 + sway, 20)], fill=0)

            # Sao lấp lánh xung quanh
            sy = 14 + int(math.sin(f * 0.5) * 3)
            draw.point([(10, sy), (10, sy-1), (9, sy), (11, sy), (10, sy+1)], fill=0)
            draw.point([(46, sy+4), (46, sy+3), (45, sy+4), (47, sy+4), (46, sy+5)], fill=0)

        elif action == 7:
            # --- CÂU 7: TẶNG BÓ HOA & BẠN NỮ NHẢY CẪNG VUI SƯỚNG ---
            bx = 16
            gx = 40
            by = 31
            jump = int(abs(math.sin(f * 0.45)) * 6)
            gy = 28 - jump

            # Nam dâng hoa
            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            # Bó hoa rực rỡ
            draw.line([(bx+4, by+9), (bx+11, by+7)], fill=0)
            # Hoa
            draw.polygon([(bx+11, by+7), (bx+14, by+3), (bx+17, by+6), (bx+14, by+9)], outline=0, fill=0)
            draw.point([(bx+13, by+5), (bx+15, by+5)], fill=1)

            # Nữ vui mừng
            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.line([(gx-4, gy), (gx-2, gy-1)], fill=0)
            draw.line([(gx-2, gy-1), (gx, gy)], fill=0)
            draw.line([(gx+1, gy), (gx+3, gy-1)], fill=0)
            draw.line([(gx+3, gy-1), (gx+5, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.line([(gx-4, gy+8), (gx-8, gy+2)], fill=0)
            draw.line([(gx+4, gy+8), (gx+8, gy+2)], fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-2, gy+16), (gx-3, gy+23)], fill=0)
            draw.line([(gx+2, gy+16), (gx+3, gy+23)], fill=0)

            # Tim bay lên từ bạn nữ
            hy = gy - 12 - (f % 16)
            draw.polygon([(gx, hy+3), (gx-3, hy), (gx-2, hy-2), (gx, hy-1), (gx+2, hy-2), (gx+3, hy)], fill=0)

        elif action == 8:
            # --- CÂU 8: CHIẾC Ô CHE MƯA (CHỞ CHE ẤM ÁP) ---
            bx = 20
            gx = 34
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            # Đám mây mưa ở trên (Y: 8..13)
            draw.ellipse([18, 6, 38, 14], outline=0, fill=1)
            draw.ellipse([14, 8, 26, 15], outline=0, fill=1)
            draw.ellipse([30, 8, 42, 15], outline=0, fill=1)
            # Hạt mưa rơi
            for rx in [12, 16, 26, 38, 44]:
                ry = (f * 2 + rx * 3) % 25 + 14
                if ry < 53:
                    draw.line([(rx, ry), (rx-1, ry+2)], fill=0)

            # Chiếc ô bạn nam cầm che cả 2
            draw.chord([14, 14, 42, 28], start=180, end=360, outline=0, fill=1)
            draw.line([(28, 21), (28, 36)], fill=0)
            draw.arc([25, 34, 28, 39], start=0, end=180, fill=0)

            draw.ellipse([bx-4, by-6, bx+4, by+6], outline=0, fill=1)
            draw.polygon([(bx-4, by-3), (bx-5, by-6), (bx, by-8), (bx+4, by-5), (bx+4, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-3, by+7, bx+3, by+14], outline=0, fill=1)
            draw.line([(bx+3, by+9), (28, 35)], fill=0)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            draw.ellipse([gx-4, gy-6, gx+4, gy+6], outline=0, fill=1)
            draw.arc([gx-5, gy-7, gx+5, gy], start=180, end=360, fill=0)
            draw.line([(gx-5, gy-3), (gx-6, gy+8)], fill=0)
            draw.line([(gx+5, gy-3), (gx+6, gy+8)], fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.polygon([(gx, gy+7), (gx-4, gy+15), (gx+4, gy+15)], outline=0, fill=1)
            draw.line([(gx-3, gy+10), (bx+2, by+11)], fill=0)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

        elif action == 9:
            # --- CÂU 9: ÔM NHAU ẤM ÁP & BÓNG BAY TRÁI TIM ---
            bx = 24
            gx = 32
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            draw.ellipse([bx-4, by-6, bx+4, by+6], outline=0, fill=1)
            draw.polygon([(bx-4, by-3), (bx-5, by-6), (bx, by-8), (bx+4, by-5), (bx+4, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+1, by+4], start=0, end=180, fill=0)

            draw.ellipse([gx-4, gy-6, gx+4, gy+6], outline=0, fill=1)
            draw.arc([gx-5, gy-7, gx+5, gy], start=180, end=360, fill=0)
            draw.line([(gx+5, gy-3), (gx+6, gy+8)], fill=0)
            draw.point([(gx+1, gy)], fill=0)
            draw.arc([gx-1, gy+1, gx+2, gy+4], start=0, end=180, fill=0)

            draw.rectangle([bx-3, by+7, gx+3, by+15], outline=0, fill=1)
            draw.line([(bx-3, by+9), (gx+2, by+10)], fill=0)
            draw.line([(gx+3, gy+9), (bx-2, by+10)], fill=0)
            draw.line([(bx-1, by+16), (bx-1, 53)], fill=0)
            draw.line([(gx+1, gy+16), (gx+1, 53)], fill=0)

            blx = 28 + int(math.sin(f * 0.2) * 3)
            bly = 12
            draw.polygon([(blx, bly+5), (blx-5, bly), (blx-4, bly-3), (blx, bly-2), (blx+4, bly-3), (blx+5, bly)], fill=0)
            draw.line([(blx, bly+5), (28, 22)], fill=0)

        elif action == 10:
            # --- CÂU 10: ĐẠI KẾT 20/10 RỰC RỠ - VẪY TAY CHÀO & PHÁO HOA ---
            bx = 18
            gx = 38
            by = 31 - beat_bounce
            gy = 31 - beat_bounce

            draw.ellipse([bx-5, by-6, bx+5, by+6], outline=0, fill=1)
            draw.polygon([(bx-5, by-3), (bx-6, by-6), (bx, by-8), (bx+5, by-5), (bx+5, by-1)], outline=0, fill=0)
            draw.point([(bx-2, by), (bx+2, by)], fill=0)
            draw.arc([bx-2, by+1, bx+2, by+4], start=0, end=180, fill=0)
            draw.rectangle([bx-4, by+7, bx+4, by+14], outline=0, fill=1)
            draw.line([(bx-2, by+15), (bx-2, 53)], fill=0)
            draw.line([(bx+2, by+15), (bx+2, 53)], fill=0)

            draw.ellipse([gx-5, gy-6, gx+5, gy+6], outline=0, fill=1)
            draw.arc([gx-6, gy-7, gx+6, gy], start=180, end=360, fill=0)
            draw.line([(gx-6, gy-3), (gx-7, gy+8)], fill=0)
            draw.line([(gx+6, gy-3), (gx+7, gy+8)], fill=0)
            draw.point([(gx-2, gy), (gx+2, gy)], fill=0)
            draw.arc([gx-2, gy+1, gx+2, gy+4], start=0, end=180, fill=0)
            draw.polygon([(gx, gy+7), (gx-5, gy+15), (gx+5, gy+15)], outline=0, fill=1)
            draw.line([(gx-2, gy+16), (gx-2, 53)], fill=0)
            draw.line([(gx+2, gy+16), (gx+2, 53)], fill=0)

            wave_arm = int(math.sin(f * 0.6) * 3)
            draw.line([(bx-4, by+8), (bx-8, by+2 + wave_arm)], fill=0)
            draw.line([(bx+4, by+8), (bx+8, by+2 - wave_arm)], fill=0)
            draw.line([(gx-4, gy+8), (gx-8, gy+2 - wave_arm)], fill=0)
            draw.line([(gx+4, gy+8), (gx+8, gy+2 + wave_arm)], fill=0)

            fx_y = 10 + (f % 5)
            draw.point([(8, fx_y), (7, fx_y), (9, fx_y), (8, fx_y-1), (8, fx_y+1)], fill=0)
            draw.point([(48, fx_y+3), (47, fx_y+3), (49, fx_y+3), (48, fx_y+2), (48, fx_y+4)], fill=0)

        # 4. CHUYỂN THÀNH 1024 BYTE ĐỊNH DẠNG C++
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

    # Ghi file binary
    with open("cuthe_frames.bin", "wb") as f:
        f.write(raw_all_bytes)
    print(f"Đã lưu cuthe_frames.bin ({len(raw_all_bytes)} bytes)")

    # Xuất file ảnh GIF
    print("Đang tạo cuthe_20_10.gif...")
    gif_frames = []
    for im in frame_images:
        scaled = im.resize((384, 192), Image.Resampling.NEAREST).convert('P')
        gif_frames.append(scaled)
    gif_frames[0].save("cuthe_20_10.gif", save_all=True, append_images=gif_frames[1:], duration=FRAME_MS, loop=0)
    print("Đã tạo cuthe_20_10.gif!")

    # C++ SFML
    print("Đang cập nhật cu_the.cpp...")
    cpp_chunks = [f"""#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
using namespace std;

constexpr int WIDTH = 128;
constexpr int HEIGHT = 64;
constexpr int FRAME_SIZE = (WIDTH * HEIGHT) / 8;
constexpr int NUM_FRAMES = {NUM_FRAMES};

constexpr uint8_t allFrames[NUM_FRAMES][FRAME_SIZE] = {{
"""]
    for fi in range(NUM_FRAMES):
        fb = raw_all_bytes[fi * 1024 : (fi + 1) * 1024]
        cpp_chunks.append("{\n")
        for row in range(64):
            line_bytes = fb[row * 16 : (row + 1) * 16]
            hex_str = ", ".join(f"0x{b:02x}" for b in line_bytes)
            comma = "," if (row < 63 or fi < NUM_FRAMES - 1) else ""
            cpp_chunks.append(f"{hex_str}{comma}\n")
        cpp_chunks.append("}" + (",\n" if fi < NUM_FRAMES - 1 else "\n};\n"))

    cpp_chunks.append(f"""
int main()
{{
    sf::RenderWindow window(sf::VideoMode({{384, 192}}), "Cu The - Orange x Hoang Dung [20-10]");
    sf::Music music;
    if (music.openFromFile("cuthe_chorus.wav"))
    {{
        music.setLooping(true);
        music.play();
    }}

    int cnt = 0;
    while (window.isOpen())
    {{
        while (const std::optional<sf::Event> event = window.pollEvent())
        {{
            if (event->is<sf::Event::Closed>())
                window.close();
        }}

        sf::Image image;
        image.resize({{128, 64}}, sf::Color::White);
        for (unsigned int y = 0; y < 64; ++y)
        {{
            for (unsigned int x = 0; x < 128; ++x)
            {{
                int byteIndex = y * 16 + (x / 8);
                int bitIndex = 7 - (x % 8);
                bool pixelOn = (allFrames[cnt][byteIndex] >> bitIndex) & 1;
                if (pixelOn) image.setPixel({{x, y}}, sf::Color::White);
                else image.setPixel({{x, y}}, sf::Color::Black);
            }}
        }}

        sf::Texture texture;
        texture.loadFromImage(image);
        sf::Sprite sprite(texture);
        sprite.setScale({{3.f, 3.f}});
        sprite.setPosition({{0, 0}});

        window.clear(sf::Color::White);
        window.draw(sprite);
        window.display();

        sf::sleep(sf::milliseconds(70));
        cnt = (cnt + 1) % NUM_FRAMES;
    }}
    return 0;
}}
""")
    with open("cu_the.cpp", "w", encoding="utf-8") as f:
        f.write("".join(cpp_chunks))
    print("Đã cập nhật cu_the.cpp!")

    # Cập nhật run_cuthe.py
    print("Đang tạo run_cuthe.py...")
    player_py = f'''"""
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
NUM_FRAMES = {NUM_FRAMES}

WHITE = b'\\xff\\xff\\xff'
BLACK = b'\\x00\\x00\\x00'

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
    hdr = f"P6\\n{{FRAME_W * SCALE}} {{FRAME_H * SCALE}}\\n255\\n".encode("ascii")
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
        self.root.geometry(f"{{WINDOW_WIDTH}}x{{WINDOW_HEIGHT}}")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        pos_x = (screen_w - WINDOW_WIDTH) // 2
        pos_y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{{WINDOW_WIDTH}}x{{WINDOW_HEIGHT}}+{{pos_x}}+{{pos_y}}")

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
        status_text = f"Frame: {{self.current_frame + 1}}/{{self.num_frames}} | {{music_text}} [M] | [Space] Play/Pause | [R] Restart"
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
        self.status_var.set(f"Chế độ lặp lại: {{'BẬT' if self.loop else 'TẮT'}}")

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
'''
    with open("run_cuthe.py", "w", encoding="utf-8") as f:
        f.write(player_py)

    # Cập nhật Web Player index.html
    print("Đang tạo index.html...")
    frames_b64 = base64.b64encode(raw_all_bytes).decode('ascii')
    with open("cuthe_chorus.mp3", "rb") as af:
        audio_b64 = base64.b64encode(af.read()).decode('ascii')

    html_code = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>CỨ THẾ 💖 - 20/10 Animation (Orange x Hoàng Dũng)</title>
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
            background: radial-gradient(ellipse at 50% 30%, #1e1035 0%, #080512 100%);
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
            background: rgba(24, 16, 44, 0.78);
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
            0%, 100% {{
                transform: scale(1);
                box-shadow: 0 0 22px rgba(255, 77, 141, 0.7);
            }}
            50% {{
                transform: scale(1.08);
                box-shadow: 0 0 38px rgba(255, 77, 141, 0.95), 0 0 16px rgba(157, 78, 221, 0.8);
            }}
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
    </style>
</head>
<body>
    <div class="glow-1"></div>
    <div class="glow-2"></div>

    <div class="app-card">
        <div class="header">
            <div class="badge">🌸 20 • 10 • Yêu Thương 🌸</div>
            <div class="song-title">CỨ THẾ</div>
            <div class="song-artist">Orange x Hoàng Dũng</div>
        </div>

        <div class="screen-wrapper" id="screenWrapper">
            <canvas id="screenCanvas"></canvas>
            <div class="play-overlay" id="playOverlay">
                <div class="play-btn-circle">
                    <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </div>
                <div class="play-btn-text" id="playBtnText">Chạm để mở quà 💖</div>
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
                <div class="time-tag" id="timeDisplay">00:00 / 00:41</div>
                <button class="mode-toggle-btn" id="btnToggleMode">✨ HD Sắc Nét</button>
                <button class="icon-action-btn" id="btnMute" aria-label="Mute/Unmute">
                    <span id="muteEmoji">🔊</span>
                </button>
            </div>
        </div>
    </div>

    <audio id="bgMusic" loop preload="auto" playsinline>
        <source src="cuthe_chorus.mp3" type="audio/mpeg">
        <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
    </audio>

    <script>
        const FRAMES_BASE64 = "{frames_b64}";
        let allBytes = null;
        try {{
            const rawString = atob(FRAMES_BASE64);
            allBytes = new Uint8Array(rawString.length);
            for (let i = 0; i < rawString.length; i++) allBytes[i] = rawString.charCodeAt(i);
        }} catch(e) {{
            console.warn("Base64 frames load error:", e);
        }}

        const KARAOKE_TIMED_PHRASES = [
            {{
                start_t: 0.0, end_t: 4.3, action: 1,
                lines: [
                    [{{t: 0.1, w: "Tình"}}, {{t: 0.5, w: "yêu"}}, {{t: 0.9, w: "là"}}],
                    [{{t: 1.3, w: "giấc"}}, {{t: 1.7, w: "mộng"}}, {{t: 2.1, w: "đẹp"}}],
                    [{{t: 2.6, w: "và"}}, {{t: 2.9, w: "anh"}}, {{t: 3.2, w: "vốn"}}],
                    [{{t: 3.5, w: "chẳng"}}, {{t: 3.8, w: "muốn"}}, {{t: 4.1, w: "tỉnh"}}, {{t: 4.3, w: "dậy..."}}]
                ]
            }},
            {{
                start_t: 4.4, end_t: 8.7, action: 2,
                lines: [
                    [{{t: 4.7, w: "Trừ"}}, {{t: 5.1, w: "khi"}}, {{t: 5.5, w: "sớm"}}, {{t: 5.8, w: "mai"}}],
                    [{{t: 6.2, w: "mở"}}, {{t: 6.6, w: "mắt"}}],
                    [{{t: 7.0, w: "thấy"}}, {{t: 7.4, w: "em"}}, {{t: 7.8, w: "ở"}}, {{t: 8.2, w: "đây..."}}, {{t: 8.5, w: "✨"}}]
                ]
            }},
            {{
                start_t: 8.8, end_t: 12.8, action: 3,
                lines: [
                    [{{t: 9.3, w: "Ta"}}, {{t: 9.7, w: "cứ"}}, {{t: 10.1, w: "thế,"}}],
                    [{{t: 10.6, w: "cứ"}}, {{t: 11.0, w: "thế"}}],
                    [{{t: 11.4, w: "yêu"}}, {{t: 11.8, w: "nhiều"}}, {{t: 12.2, w: "thêm"}}, {{t: 12.4, w: "♥"}}]
                ]
            }},
            {{
                start_t: 12.9, end_t: 16.7, action: 4,
                lines: [
                    [{{t: 13.0, w: "Ai"}}, {{t: 13.4, w: "không"}}, {{t: 13.8, w: "vui,"}}],
                    [{{t: 14.3, w: "ta"}}, {{t: 14.7, w: "cứ"}}, {{t: 15.1, w: "cho"}}],
                    [{{t: 15.5, w: "họ"}}, {{t: 15.9, w: "xem!"}}]
                ]
            }},
            {{
                start_t: 16.8, end_t: 20.8, action: 5,
                lines: [
                    [{{t: 16.8, w: "Đã"}}, {{t: 17.2, w: "có"}}],
                    [{{t: 17.6, w: "nhau"}}, {{t: 18.0, w: "rồi"}}],
                    [{{t: 18.6, w: "thì"}}, {{t: 19.0, w: "nhất"}}, {{t: 19.4, w: "quyết"}}],
                    [{{t: 19.8, w: "không"}}, {{t: 20.2, w: "rời!"}}]
                ]
            }},
            {{
                start_t: 20.9, end_t: 24.8, action: 6,
                lines: [
                    [{{t: 21.1, w: "Don't"}}, {{t: 21.5, w: "stop"}}],
                    [{{t: 21.9, w: "this"}}, {{t: 22.3, w: "feeling,"}}],
                    [{{t: 22.9, w: "it"}}, {{t: 23.3, w: "won't"}}],
                    [{{t: 23.7, w: "go"}}, {{t: 24.1, w: "away..."}}, {{t: 24.4, w: "✨"}}]
                ]
            }},
            {{
                start_t: 24.9, end_t: 28.8, action: 7,
                lines: [
                    [{{t: 25.1, w: "Yêu"}}, {{t: 25.5, w: "đi,"}}],
                    [{{t: 25.9, w: "yêu"}}, {{t: 26.3, w: "vui"}}, {{t: 26.7, w: "lắm,"}}],
                    [{{t: 27.3, w: "yêu"}}, {{t: 27.8, w: "nhiều"}}, {{t: 28.2, w: "lên!"}}, {{t: 28.5, w: "💐"}}]
                ]
            }},
            {{
                start_t: 28.9, end_t: 32.8, action: 8,
                lines: [
                    [{{t: 29.1, w: "Đâu"}}, {{t: 29.5, w: "ai"}}, {{t: 29.9, w: "mong"}}],
                    [{{t: 30.4, w: "cứ"}}, {{t: 30.8, w: "đớn"}}, {{t: 31.2, w: "đau"}}],
                    [{{t: 31.6, w: "triền"}}, {{t: 32.0, w: "miên..."}}]
                ]
            }},
            {{
                start_t: 32.9, end_t: 36.8, action: 9,
                lines: [
                    [{{t: 32.9, w: "Đã"}}, {{t: 33.3, w: "có"}}],
                    [{{t: 33.7, w: "nhau"}}, {{t: 34.1, w: "rồi"}}],
                    [{{t: 34.7, w: "thì"}}, {{t: 35.1, w: "nhất"}}, {{t: 35.5, w: "quyết"}}],
                    [{{t: 35.9, w: "không"}}, {{t: 36.3, w: "rời"}}, {{t: 36.5, w: "♥"}}]
                ]
            }},
            {{
                start_t: 36.9, end_t: 41.0, action: 10,
                lines: [
                    [{{t: 37.1, w: "💖"}}, {{t: 37.4, w: "CHÚC"}}, {{t: 37.7, w: "MỪNG"}}, {{t: 38.0, w: "💖"}}],
                    [{{t: 38.3, w: "NGÀY"}}, {{t: 38.7, w: "20/10"}}],
                    [{{t: 39.1, w: "Cứ"}}, {{t: 39.5, w: "thế"}}, {{t: 39.8, w: "yêu"}}],
                    [{{t: 40.1, w: "thương"}}, {{t: 40.4, w: "nha!"}}, {{t: 40.7, w: "✨"}}]
                ]
            }}
        ];

        const TOTAL_DURATION = 41.0;
        const NUM_FRAMES = {NUM_FRAMES};
        const FRAME_DURATION = 0.070;

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
        let isHDMode = true; // Mặc định HD Sắc Nét

        function resizeCanvas() {{
            const rect = screenWrapper.getBoundingClientRect();
            const dpr = Math.max(2, window.devicePixelRatio || 1);
            canvas.width = Math.round(rect.width * dpr);
            canvas.height = Math.round(rect.width * 0.5 * dpr);
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
            return {{ action: active.action, lines: lines }};
        }}

        function drawBoy(ctx, bx, by, S, options = {{}}) {{
            const {{ hair = 'spiky', eye = 'dot', mouth = 'smile', armL = null, armR = null, legL = null, legR = null }} = options;

            // Head
            ctx.beginPath();
            ctx.arc(bx * S, by * S, 4.8 * S, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.stroke();

            // Hair
            ctx.beginPath();
            ctx.moveTo((bx - 4.5) * S, (by - 2.5) * S);
            ctx.lineTo((bx - 5.5) * S, (by - 5.5) * S);
            ctx.lineTo((bx - 1.0) * S, (by - 7.5) * S);
            ctx.lineTo((bx + 4.0) * S, (by - 5.0) * S);
            ctx.lineTo((bx + 4.5) * S, (by - 1.0) * S);
            ctx.closePath();
            ctx.fillStyle = '#000000';
            ctx.fill();

            // Eyes
            ctx.fillStyle = '#000000';
            if (eye === 'wink') {{
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, by * S);
                ctx.stroke();
                ctx.beginPath();
                ctx.arc((bx + 2) * S, by * S, S * 0.45, 0, Math.PI * 2);
                ctx.fill();
            }} else if (eye === 'sleep') {{
                ctx.beginPath();
                ctx.moveTo((bx - 3.5) * S, by * S);
                ctx.lineTo((bx - 2.0) * S, (by - 1.2) * S);
                ctx.lineTo((bx - 0.5) * S, by * S);
                ctx.moveTo((bx + 0.5) * S, by * S);
                ctx.lineTo((bx + 2.0) * S, (by - 1.2) * S);
                ctx.lineTo((bx + 3.5) * S, by * S);
                ctx.stroke();
            }} else if (eye === 'blink') {{
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, by * S);
                ctx.lineTo((bx - 1) * S, by * S);
                ctx.moveTo((bx + 1) * S, by * S);
                ctx.lineTo((bx + 3) * S, by * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.arc((bx - 2) * S, by * S, S * 0.45, 0, Math.PI * 2);
                ctx.arc((bx + 2) * S, by * S, S * 0.45, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Mouth
            if (mouth === 'whistle') {{
                ctx.beginPath();
                ctx.arc((bx + 0.5) * S, (by + 2.5) * S, S * 0.9, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.arc(bx * S, (by + 1.5) * S, 2 * S, 0, Math.PI);
                ctx.stroke();
            }}

            // Body
            ctx.beginPath();
            ctx.rect((bx - 3.5) * S, (by + 7) * S, 7 * S, 7.5 * S);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.stroke();

            // Arms
            if (armL) {{
                ctx.beginPath();
                ctx.moveTo(armL[0][0] * S, armL[0][1] * S);
                ctx.lineTo(armL[1][0] * S, armL[1][1] * S);
                ctx.stroke();
            }}
            if (armR) {{
                ctx.beginPath();
                ctx.moveTo(armR[0][0] * S, armR[0][1] * S);
                ctx.lineTo(armR[1][0] * S, armR[1][1] * S);
                ctx.stroke();
            }}

            // Legs
            if (legL) {{
                ctx.beginPath();
                ctx.moveTo(legL[0][0] * S, legL[0][1] * S);
                ctx.lineTo(legL[1][0] * S, legL[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((bx - 2) * S, (by + 14.5) * S);
                ctx.lineTo((bx - 2) * S, 53 * S);
                ctx.stroke();
            }}

            if (legR) {{
                ctx.beginPath();
                ctx.moveTo(legR[0][0] * S, legR[0][1] * S);
                ctx.lineTo(legR[1][0] * S, legR[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((bx + 2) * S, (by + 14.5) * S);
                ctx.lineTo((bx + 2) * S, 53 * S);
                ctx.stroke();
            }}
        }}

        function drawGirl(ctx, gx, gy, S, options = {{}}) {{
            const {{ hair = 'side', eye = 'dot', bow = true, armL = null, armR = null, legL = null, legR = null }} = options;

            // Head
            ctx.beginPath();
            ctx.arc(gx * S, gy * S, 4.8 * S, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.stroke();

            // Hair arc
            ctx.beginPath();
            ctx.arc(gx * S, (gy - 0.5) * S, 5.2 * S, Math.PI, 0);
            ctx.stroke();
            // Side strands
            ctx.beginPath();
            ctx.moveTo((gx - 5.0) * S, (gy - 2.5) * S);
            ctx.lineTo((gx - 6.2) * S, (gy + 8.0) * S);
            ctx.moveTo((gx + 5.0) * S, (gy - 2.5) * S);
            ctx.lineTo((gx + 6.2) * S, (gy + 8.0) * S);
            ctx.stroke();

            // Hair Bow
            if (bow) {{
                ctx.beginPath();
                ctx.moveTo((gx + 4) * S, (gy - 4.5) * S);
                ctx.lineTo((gx + 8.5) * S, (gy - 7.5) * S);
                ctx.lineTo((gx + 8.5) * S, (gy - 2.0) * S);
                ctx.closePath();
                ctx.fillStyle = '#000000';
                ctx.fill();
            }}

            // Eyes
            ctx.fillStyle = '#000000';
            if (eye === 'happy') {{
                ctx.beginPath();
                ctx.moveTo((gx - 3.5) * S, gy * S);
                ctx.lineTo((gx - 2.0) * S, (gy - 1.2) * S);
                ctx.lineTo((gx - 0.5) * S, gy * S);
                ctx.moveTo((gx + 0.5) * S, gy * S);
                ctx.lineTo((gx + 2.0) * S, (gy - 1.2) * S);
                ctx.lineTo((gx + 3.5) * S, gy * S);
                ctx.stroke();
            }} else if (eye === 'blink') {{
                ctx.beginPath();
                ctx.moveTo((gx - 3) * S, gy * S);
                ctx.lineTo((gx - 1) * S, gy * S);
                ctx.moveTo((gx + 1) * S, gy * S);
                ctx.lineTo((gx + 3) * S, gy * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.arc((gx - 2) * S, gy * S, S * 0.45, 0, Math.PI * 2);
                ctx.arc((gx + 2) * S, gy * S, S * 0.45, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Smile
            ctx.beginPath();
            ctx.arc(gx * S, (gy + 1.5) * S, 2 * S, 0, Math.PI);
            ctx.stroke();

            // Dress
            ctx.beginPath();
            ctx.moveTo(gx * S, (gy + 7) * S);
            ctx.lineTo((gx - 4.5) * S, (gy + 15) * S);
            ctx.lineTo((gx + 4.5) * S, (gy + 15) * S);
            ctx.closePath();
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.stroke();

            // Arms
            if (armL) {{
                ctx.beginPath();
                ctx.moveTo(armL[0][0] * S, armL[0][1] * S);
                ctx.lineTo(armL[1][0] * S, armL[1][1] * S);
                ctx.stroke();
            }}
            if (armR) {{
                ctx.beginPath();
                ctx.moveTo(armR[0][0] * S, armR[0][1] * S);
                ctx.lineTo(armR[1][0] * S, armR[1][1] * S);
                ctx.stroke();
            }}

            // Legs
            if (legL) {{
                ctx.beginPath();
                ctx.moveTo(legL[0][0] * S, legL[0][1] * S);
                ctx.lineTo(legL[1][0] * S, legL[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((gx - 2) * S, (gy + 15.5) * S);
                ctx.lineTo((gx - 2) * S, 53 * S);
                ctx.stroke();
            }}

            if (legR) {{
                ctx.beginPath();
                ctx.moveTo(legR[0][0] * S, legR[0][1] * S);
                ctx.lineTo(legR[1][0] * S, legR[1][1] * S);
                ctx.stroke();
            }} else {{
                ctx.beginPath();
                ctx.moveTo((gx + 2) * S, (gy + 15.5) * S);
                ctx.lineTo((gx + 2) * S, 53 * S);
                ctx.stroke();
            }}
        }}

        function drawHeart(ctx, hx, hy, size, S) {{
            ctx.beginPath();
            ctx.moveTo(hx * S, (hy + size * 0.7) * S);
            ctx.bezierCurveTo((hx - size) * S, hy * S, (hx - size) * S, (hy - size * 0.7) * S, hx * S, (hy - size * 0.3) * S);
            ctx.bezierCurveTo((hx + size) * S, (hy - size * 0.7) * S, (hx + size) * S, hy * S, hx * S, (hy + size * 0.7) * S);
            ctx.closePath();
            ctx.fillStyle = '#ff3366';
            ctx.fill();
            ctx.stroke();
        }}

        function drawStar(ctx, sx, sy, r, S) {{
            ctx.beginPath();
            ctx.moveTo(sx * S, (sy - r) * S);
            ctx.lineTo((sx + r * 0.3) * S, (sy - r * 0.3) * S);
            ctx.lineTo((sx + r) * S, sy * S);
            ctx.lineTo((sx + r * 0.3) * S, (sy + r * 0.3) * S);
            ctx.lineTo(sx * S, (sy + r) * S);
            ctx.lineTo((sx - r * 0.3) * S, (sy + r * 0.3) * S);
            ctx.lineTo((sx - r) * S, sy * S);
            ctx.lineTo((sx - r * 0.3) * S, (sy - r * 0.3) * S);
            ctx.closePath();
            ctx.fillStyle = '#ffbb00';
            ctx.fill();
            ctx.stroke();
        }}

        function renderPixelFrame(cur_t) {{
            if (!allBytes) return;
            const S = canvas.width / 128.0;
            const frameIdx = Math.min(NUM_FRAMES - 1, Math.floor(cur_t / FRAME_DURATION));

            ctx.imageSmoothingEnabled = false;
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

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
            updateProgress(cur_t);
        }}

        function render(cur_t) {{
            if (!isHDMode) {{
                renderPixelFrame(cur_t);
                return;
            }}

            const S = canvas.width / 128.0;
            const f = Math.floor(cur_t / 0.070);
            const isBlinking = (f % 40 === 0 || f % 40 === 1);
            const beatBounce = Math.abs(Math.sin(cur_t * Math.PI * 2.1)) * 1.5;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Styling
            const lw = Math.max(1.8, S * 0.38);
            ctx.lineWidth = lw;
            ctx.strokeStyle = '#000000';
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            // 1. Ground line
            ctx.beginPath();
            ctx.moveTo(0, 54 * S);
            ctx.lineTo(canvas.width, 54 * S);
            ctx.stroke();

            // 2. Grass tufts
            [6, 18, 42, 50, 115, 122].forEach(gx => {{
                ctx.beginPath();
                ctx.moveTo(gx * S, 53.5 * S);
                ctx.lineTo(gx * S, 50.5 * S);
                ctx.stroke();
            }});

            // 3. Middle Dashed Divider (X = 56)
            ctx.fillStyle = '#000000';
            for (let dy = 6; dy < 50; dy += 4) {{
                ctx.beginPath();
                ctx.arc(56 * S, dy * S, S * 0.28, 0, Math.PI * 2);
                ctx.fill();
            }}

            // 4. Karaoke Lyrics on the right side (Center X = 92)
            const {{ action, lines }} = getActiveKaraoke(cur_t);
            const text_x = 92 * S;
            const y_starts = lines.length === 3 
                ? [17 * S, 29 * S, 41 * S] 
                : [11 * S, 21 * S, 31 * S, 41 * S];

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

            // 5. Actions on the left side (10 Actions synced with 41s audio)
            if (action === 1) {{
                // ACTION 1 (PRE-CHORUS): GIẤC MỘNG ĐẸP CHẲNG MUỐN TỈNH DẬY
                const bx = 26;
                const by = 31 - beatBounce;

                // Cloud floating
                const cloudFloat = Math.sin(f * 0.18) * 2;
                const cx = 31;
                const cy = 13 + cloudFloat;

                // Dream Cloud puffs
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc((cx - 8) * S, (cy + 1) * S, 6 * S, 0, Math.PI * 2);
                ctx.arc((cx + 1) * S, (cy - 3) * S, 7 * S, 0, Math.PI * 2);
                ctx.arc((cx + 9) * S, (cy + 1) * S, 5.5 * S, 0, Math.PI * 2);
                ctx.arc(cx * S, (cy + 3) * S, 6.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Heart inside dream
                drawHeart(ctx, cx, cy, 3.2, S);

                // Thought bubbles leading to boy's head
                [
                    {{ x: bx + 1.5, y: by - 7, r: 0.9 }},
                    {{ x: bx + 3.5, y: by - 9.5, r: 1.3 }},
                    {{ x: bx + 6.0, y: by - 12.5, r: 1.8 }}
                ].forEach(b => {{
                    ctx.beginPath();
                    ctx.arc(b.x * S, b.y * S, b.r * S, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                    ctx.stroke();
                }});

                // Boy sleeping peacefully
                drawBoy(ctx, bx, by, S, {{
                    eye: 'sleep',
                    mouth: 'smile',
                    armL: [[bx - 3.5, by + 8], [bx - 6.5, by + 13]],
                    armR: [[bx + 3.5, by + 8], [bx + 6.5, by + 13]],
                }});

            }} else if (action === 2) {{
                // ACTION 2 (PRE-CHORUS): SỚM MAI MỞ MẮT THẤY EM Ở ĐÂY
                const bx = 18;
                const gx = 38;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Morning sun rays top-left
                ctx.fillStyle = '#ffbb00';
                ctx.beginPath();
                ctx.arc(8 * S, 8 * S, 4.5 * S, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                for (let ang = 0; ang <= 90; ang += 22.5) {{
                    const rad = ang * Math.PI / 180;
                    ctx.beginPath();
                    ctx.moveTo((8 + Math.cos(rad) * 6.5) * S, (8 + Math.sin(rad) * 6.5) * S);
                    ctx.lineTo((8 + Math.cos(rad) * 9.5) * S, (8 + Math.sin(rad) * 9.5) * S);
                    ctx.stroke();
                }}

                // Boy looking at girl happily
                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    mouth: 'smile',
                    armL: [[bx - 3.5, by + 8], [bx - 6.5, by + 13]],
                    armR: [[bx + 3.5, by + 8], [bx + 6.5, by + 10]],
                }});

                // Girl waving at boy
                const waveY = Math.sin(f * 0.5) * 3;
                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy',
                    armL: [[gx - 3.5, gy + 8], [gx - 6.5, gy + 13]],
                    armR: [[gx + 3.5, gy + 8], [gx + 7.5, gy + 2 + waveY]],
                }});

                // Star sparkle between them
                drawStar(ctx, 28, 20, 2.5, S);

            }} else if (action === 3) {{
                // WALK CYCLE
                const walk = Math.floor(cur_t / 0.14) % 4;
                const bx = 26;
                const by = 30 - beatBounce;

                let legL, legR, armL, armR;
                if (walk === 0 || walk === 1) {{
                    armL = [[bx - 3.5, by + 8], [bx - 7.5, by + 13]];
                    armR = [[bx + 3.5, by + 8], [bx + 7.5, by + 11]];
                    legL = [[bx - 2, by + 14.5], [bx - 5, 53]];
                    legR = [[bx + 2, by + 14.5], [bx + 5, 53]];
                }} else {{
                    armL = [[bx - 3.5, by + 8], [bx - 7.5, by + 11]];
                    armR = [[bx + 3.5, by + 8], [bx + 7.5, by + 13]];
                    legL = [[bx - 2, by + 14.5], [bx + 4, 53]];
                    legR = [[bx + 2, by + 14.5], [bx - 4, 53]];
                }}

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    mouth: 'whistle',
                    armL: armL, armR: armR,
                    legL: legL, legR: legR
                }});

                // Floating musical notes
                const ny = 25 - ((f * 1.5) % 22);
                const nx = Math.max(4, bx - 14 + Math.sin(f * 0.3) * 2);
                ctx.beginPath();
                ctx.arc(nx * S, ny * S, S * 1.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo((nx + 1.2) * S, ny * S);
                ctx.lineTo((nx + 1.2) * S, (ny - 4) * S);
                ctx.lineTo((nx + 3.0) * S, (ny - 3) * S);
                ctx.stroke();

            }} else if (action === 4) {{
                // GIRL V SIGN & BOY COOL POSE
                const bx = 18;
                const gx = 38;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: 'wink',
                    armL: [[bx - 3.5, by + 9], [bx + 3.5, by + 11]],
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    armR: [[gx + 3.5, gy + 8], [gx + 8.5, gy + 2]],
                }});

                // V fingers
                ctx.beginPath();
                ctx.moveTo((gx + 8.5) * S, (gy + 2) * S);
                ctx.lineTo((gx + 7.0) * S, (gy - 3) * S);
                ctx.moveTo((gx + 8.5) * S, (gy + 2) * S);
                ctx.lineTo((gx + 10.5) * S, (gy - 3) * S);
                ctx.stroke();

                // Sparkle
                drawStar(ctx, gx + 14, gy - 2, 2.5, S);

            }} else if (action === 5) {{
                // HOLDING HANDS & PULSING HEART
                const bx = 20;
                const gx = 36;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [28, 39]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 9], [28, 39]]
                }});

                // Clasp dot
                ctx.beginPath();
                ctx.arc(28 * S, 39 * S, S * 1.2, 0, Math.PI * 2);
                ctx.fill();

                // Pulsing heart
                const heartSize = 3.5 + beatBounce * 1.5;
                const hy = 20 - Math.sin(f * 0.3) * 2;
                drawHeart(ctx, 28, hy, heartSize, S);

            }} else if (action === 6) {{
                // SWING DANCE
                const sway = Math.sin(f * 0.4) * 3;
                const bx = 18 + sway;
                const gx = 36 + sway;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 8], [27 + sway, 20]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 8], [27 + sway, 20]]
                }});

                // Twinkling stars
                const sy = 14 + Math.sin(f * 0.5) * 3;
                drawStar(ctx, 10, sy, 2.2, S);
                drawStar(ctx, 46, sy + 4, 2.2, S);

            }} else if (action === 7) {{
                // GIVING FLOWERS & GIRL JUMPING
                const bx = 16;
                const gx = 40;
                const by = 31;
                const jump = Math.abs(Math.sin(f * 0.45)) * 6;
                const gy = 28 - jump;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [bx + 11, by + 7]]
                }});

                // Flower bouquet
                ctx.beginPath();
                ctx.moveTo((bx + 11) * S, (by + 7) * S);
                ctx.lineTo((bx + 14) * S, (by + 3) * S);
                ctx.lineTo((bx + 17) * S, (by + 6) * S);
                ctx.lineTo((bx + 14) * S, (by + 9) * S);
                ctx.closePath();
                ctx.fillStyle = '#ff4d8d';
                ctx.fill();
                ctx.stroke();

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy',
                    armL: [[gx - 3.5, gy + 8], [gx - 8, gy + 2]],
                    armR: [[gx + 3.5, gy + 8], [gx + 8, gy + 2]]
                }});

                // Rising heart
                const hy = gy - 12 - (f % 16);
                drawHeart(ctx, gx, hy, 2.5, S);

            }} else if (action === 8) {{
                // UMBRELLA IN RAIN
                const bx = 20;
                const gx = 34;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Cloud
                ctx.beginPath();
                ctx.ellipse(28 * S, 10 * S, 10 * S, 4 * S, 0, 0, Math.PI * 2);
                ctx.ellipse(20 * S, 11 * S, 6 * S, 3.5 * S, 0, 0, Math.PI * 2);
                ctx.ellipse(36 * S, 11 * S, 6 * S, 3.5 * S, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Falling raindrops
                ctx.strokeStyle = '#3b82f6';
                [12, 16, 26, 38, 44].forEach((rx) => {{
                    const ry = ((f * 2 + rx * 3) % 25) + 14;
                    if (ry < 53) {{
                        ctx.beginPath();
                        ctx.moveTo(rx * S, ry * S);
                        ctx.lineTo((rx - 1) * S, (ry + 2) * S);
                        ctx.stroke();
                    }}
                }});
                ctx.strokeStyle = '#000000';

                // Umbrella Dome
                ctx.beginPath();
                ctx.arc(28 * S, 21 * S, 14 * S, Math.PI, 0);
                ctx.closePath();
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Umbrella Handle
                ctx.beginPath();
                ctx.moveTo(28 * S, 21 * S);
                ctx.lineTo(28 * S, 36 * S);
                ctx.arc(26.5 * S, 36.5 * S, 1.5 * S, 0, Math.PI);
                ctx.stroke();

                // Boy
                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [28, 35]]
                }});

                // Girl nestled close
                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 10], [bx + 2, by + 11]]
                }});

            }} else if (action === 9) {{
                // WARM HUG & HEART BALLOON
                const bx = 24;
                const gx = 32;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Shared body
                ctx.beginPath();
                ctx.rect((bx - 3) * S, (by + 7) * S, (gx - bx + 6) * S, 8 * S);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Arms around each other's backs
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 9) * S);
                ctx.lineTo((gx + 2) * S, (by + 10) * S);
                ctx.moveTo((gx + 3) * S, (gy + 9) * S);
                ctx.lineTo((bx - 2) * S, (by + 10) * S);
                ctx.stroke();

                // Heads
                drawBoy(ctx, bx, by, S, {{ eye: isBlinking ? 'blink' : 'dot' }});
                drawGirl(ctx, gx, gy, S, {{ bow: true, eye: isBlinking ? 'blink' : 'dot' }});

                // Heart Balloon
                const blx = 28 + Math.sin(f * 0.2) * 3;
                const bly = 12;
                drawHeart(ctx, blx, bly, 4.5, S);

                // Balloon string
                ctx.beginPath();
                ctx.moveTo(blx * S, (bly + 4.5) * S);
                ctx.bezierCurveTo((blx - 2) * S, (bly + 9) * S, (blx + 2) * S, 17 * S, 28 * S, 22 * S);
                ctx.stroke();

            }} else if (action === 10) {{
                // FINALE 20/10 CELEBRATION
                const bx = 18;
                const gx = 38;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;
                const waveArm = Math.sin(f * 0.6) * 3;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[bx - 3.5, by + 8], [bx - 7.5, by + 2 + waveArm]],
                    armR: [[bx + 3.5, by + 8], [bx + 7.5, by + 2 - waveArm]],
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy',
                    armL: [[gx - 3.5, gy + 8], [gx - 7.5, gy + 2 - waveArm]],
                    armR: [[gx + 3.5, gy + 8], [gx + 7.5, gy + 2 + waveArm]],
                }});

                // Fireworks / Starbursts
                const fx_y = 10 + (f % 5);
                drawStar(ctx, 8, fx_y, 3.5, S);
                drawStar(ctx, 48, fx_y + 3, 3.5, S);
            }}

            updateProgress(cur_t);
        }}

        function render(cur_t) {{
            if (!isHDMode) {{
                renderPixelFrame(cur_t);
                return;
            }}

            const S = canvas.width / 128.0;
            const f = Math.floor(cur_t / 0.070);
            const isBlinking = (f % 40 === 0 || f % 40 === 1);
            const beatBounce = Math.abs(Math.sin(cur_t * Math.PI * 2.1)) * 1.5;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Styling
            const lw = Math.max(1.8, S * 0.38);
            ctx.lineWidth = lw;
            ctx.strokeStyle = '#000000';
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            // 1. Ground line
            ctx.beginPath();
            ctx.moveTo(0, 54 * S);
            ctx.lineTo(canvas.width, 54 * S);
            ctx.stroke();

            // 2. Grass tufts
            [6, 18, 42, 50, 115, 122].forEach(gx => {{
                ctx.beginPath();
                ctx.moveTo(gx * S, 53.5 * S);
                ctx.lineTo(gx * S, 50.5 * S);
                ctx.stroke();
            }});

            // 3. Middle Dashed Divider (X = 56)
            ctx.fillStyle = '#000000';
            for (let dy = 6; dy < 50; dy += 4) {{
                ctx.beginPath();
                ctx.arc(56 * S, dy * S, S * 0.28, 0, Math.PI * 2);
                ctx.fill();
            }}

            // 4. Karaoke Lyrics on the right side (Center X = 92)
            const {{ action, lines }} = getActiveKaraoke(cur_t);
            const text_x = 92 * S;
            const y_starts = lines.length === 3 
                ? [17 * S, 29 * S, 41 * S] 
                : [11 * S, 21 * S, 31 * S, 41 * S];

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

            // 5. Actions on the left side
            if (action === 1) {{
                // WALK CYCLE
                const walk = Math.floor(cur_t / 0.14) % 4;
                const bx = 26;
                const by = 30 - beatBounce;

                let legL, legR, armL, armR;
                if (walk === 0 || walk === 1) {{
                    armL = [[bx - 3.5, by + 8], [bx - 7.5, by + 13]];
                    armR = [[bx + 3.5, by + 8], [bx + 7.5, by + 11]];
                    legL = [[bx - 2, by + 14.5], [bx - 5, 53]];
                    legR = [[bx + 2, by + 14.5], [bx + 5, 53]];
                }} else {{
                    armL = [[bx - 3.5, by + 8], [bx - 7.5, by + 11]];
                    armR = [[bx + 3.5, by + 8], [bx + 7.5, by + 13]];
                    legL = [[bx - 2, by + 14.5], [bx + 4, 53]];
                    legR = [[bx + 2, by + 14.5], [bx - 4, 53]];
                }}

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    mouth: 'whistle',
                    armL: armL, armR: armR,
                    legL: legL, legR: legR
                }});

                // Floating musical notes
                const ny = 25 - ((f * 1.5) % 22);
                const nx = Math.max(4, bx - 14 + Math.sin(f * 0.3) * 2);
                ctx.beginPath();
                ctx.arc(nx * S, ny * S, S * 1.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo((nx + 1.2) * S, ny * S);
                ctx.lineTo((nx + 1.2) * S, (ny - 4) * S);
                ctx.lineTo((nx + 3.0) * S, (ny - 3) * S);
                ctx.stroke();

            }} else if (action === 2) {{
                // GIRL V SIGN & BOY COOL POSE
                const bx = 18;
                const gx = 38;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: 'wink',
                    armL: [[bx - 3.5, by + 9], [bx + 3.5, by + 11]],
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    armR: [[gx + 3.5, gy + 8], [gx + 8.5, gy + 2]],
                }});

                // V fingers
                ctx.beginPath();
                ctx.moveTo((gx + 8.5) * S, (gy + 2) * S);
                ctx.lineTo((gx + 7.0) * S, (gy - 3) * S);
                ctx.moveTo((gx + 8.5) * S, (gy + 2) * S);
                ctx.lineTo((gx + 10.5) * S, (gy - 3) * S);
                ctx.stroke();

                // Sparkle
                drawStar(ctx, gx + 14, gy - 2, 2.5, S);

            }} else if (action === 3) {{
                // HOLDING HANDS & PULSING HEART
                const bx = 20;
                const gx = 36;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [28, 39]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 9], [28, 39]]
                }});

                // Clasp dot
                ctx.beginPath();
                ctx.arc(28 * S, 39 * S, S * 1.2, 0, Math.PI * 2);
                ctx.fill();

                // Pulsing heart
                const heartSize = 3.5 + beatBounce * 1.5;
                const hy = 20 - Math.sin(f * 0.3) * 2;
                drawHeart(ctx, 28, hy, heartSize, S);

            }} else if (action === 4) {{
                // SWING DANCE
                const sway = Math.sin(f * 0.4) * 3;
                const bx = 18 + sway;
                const gx = 36 + sway;
                const by = 30 - beatBounce;
                const gy = 30 - beatBounce;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 8], [27 + sway, 20]]
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 8], [27 + sway, 20]]
                }});

                // Twinkling stars
                const sy = 14 + Math.sin(f * 0.5) * 3;
                drawStar(ctx, 10, sy, 2.2, S);
                drawStar(ctx, 46, sy + 4, 2.2, S);

            }} else if (action === 5) {{
                // GIVING FLOWERS & GIRL JUMPING
                const bx = 16;
                const gx = 40;
                const by = 31;
                const jump = Math.abs(Math.sin(f * 0.45)) * 6;
                const gy = 28 - jump;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [bx + 11, by + 7]]
                }});

                // Flower bouquet
                ctx.beginPath();
                ctx.moveTo((bx + 11) * S, (by + 7) * S);
                ctx.lineTo((bx + 14) * S, (by + 3) * S);
                ctx.lineTo((bx + 17) * S, (by + 6) * S);
                ctx.lineTo((bx + 14) * S, (by + 9) * S);
                ctx.closePath();
                ctx.fillStyle = '#ff4d8d';
                ctx.fill();
                ctx.stroke();

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy',
                    armL: [[gx - 3.5, gy + 8], [gx - 8, gy + 2]],
                    armR: [[gx + 3.5, gy + 8], [gx + 8, gy + 2]]
                }});

                // Rising heart
                const hy = gy - 12 - (f % 16);
                drawHeart(ctx, gx, hy, 2.5, S);

            }} else if (action === 6) {{
                // UMBRELLA IN RAIN
                const bx = 20;
                const gx = 34;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Cloud
                ctx.beginPath();
                ctx.ellipse(28 * S, 10 * S, 10 * S, 4 * S, 0, 0, Math.PI * 2);
                ctx.ellipse(20 * S, 11 * S, 6 * S, 3.5 * S, 0, 0, Math.PI * 2);
                ctx.ellipse(36 * S, 11 * S, 6 * S, 3.5 * S, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Falling raindrops
                ctx.strokeStyle = '#3b82f6';
                [12, 16, 26, 38, 44].forEach((rx) => {{
                    const ry = ((f * 2 + rx * 3) % 25) + 14;
                    if (ry < 53) {{
                        ctx.beginPath();
                        ctx.moveTo(rx * S, ry * S);
                        ctx.lineTo((rx - 1) * S, (ry + 2) * S);
                        ctx.stroke();
                    }}
                }});
                ctx.strokeStyle = '#000000';

                // Umbrella Dome
                ctx.beginPath();
                ctx.arc(28 * S, 21 * S, 14 * S, Math.PI, 0);
                ctx.closePath();
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Umbrella Handle
                ctx.beginPath();
                ctx.moveTo(28 * S, 21 * S);
                ctx.lineTo(28 * S, 36 * S);
                ctx.arc(26.5 * S, 36.5 * S, 1.5 * S, 0, Math.PI);
                ctx.stroke();

                // Boy
                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armR: [[bx + 3.5, by + 9], [28, 35]]
                }});

                // Girl nestled close
                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[gx - 3.5, gy + 10], [bx + 2, by + 11]]
                }});

            }} else if (action === 7) {{
                // WARM HUG & HEART BALLOON
                const bx = 24;
                const gx = 32;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;

                // Shared body
                ctx.beginPath();
                ctx.rect((bx - 3) * S, (by + 7) * S, (gx - bx + 6) * S, 8 * S);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.stroke();

                // Arms around each other's backs
                ctx.beginPath();
                ctx.moveTo((bx - 3) * S, (by + 9) * S);
                ctx.lineTo((gx + 2) * S, (by + 10) * S);
                ctx.moveTo((gx + 3) * S, (gy + 9) * S);
                ctx.lineTo((bx - 2) * S, (by + 10) * S);
                ctx.stroke();

                // Heads
                drawBoy(ctx, bx, by, S, {{ eye: isBlinking ? 'blink' : 'dot' }});
                drawGirl(ctx, gx, gy, S, {{ bow: true, eye: isBlinking ? 'blink' : 'dot' }});

                // Heart Balloon
                const blx = 28 + Math.sin(f * 0.2) * 3;
                const bly = 12;
                drawHeart(ctx, blx, bly, 4.5, S);

                // Balloon string
                ctx.beginPath();
                ctx.moveTo(blx * S, (bly + 4.5) * S);
                ctx.bezierCurveTo((blx - 2) * S, (bly + 9) * S, (blx + 2) * S, 17 * S, 28 * S, 22 * S);
                ctx.stroke();

            }} else if (action === 8) {{
                // FINALE 20/10 CELEBRATION
                const bx = 18;
                const gx = 38;
                const by = 31 - beatBounce;
                const gy = 31 - beatBounce;
                const waveArm = Math.sin(f * 0.6) * 3;

                drawBoy(ctx, bx, by, S, {{
                    eye: isBlinking ? 'blink' : 'dot',
                    armL: [[bx - 3.5, by + 8], [bx - 7.5, by + 2 + waveArm]],
                    armR: [[bx + 3.5, by + 8], [bx + 7.5, by + 2 - waveArm]],
                }});

                drawGirl(ctx, gx, gy, S, {{
                    bow: true,
                    eye: 'happy',
                    armL: [[gx - 3.5, gy + 8], [gx - 7.5, gy + 2 - waveArm]],
                    armR: [[gx + 3.5, gy + 8], [gx + 7.5, gy + 2 + waveArm]],
                }});

                // Fireworks / Starbursts
                const fx_y = 10 + (f % 5);
                drawStar(ctx, 8, fx_y, 3.5, S);
                drawStar(ctx, 48, fx_y + 3, 3.5, S);
            }}

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

            if (bgMusic.currentTime >= TOTAL_DURATION) {{
                bgMusic.currentTime = 0;
            }}

            bgMusic.play().catch(e => {{
                console.log('Autoplay requires user gesture:', e);
            }});

            requestAnimationFrame(step);
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

        // Render ban đầu khi mở trang
        render(0);
    </script>
</body>
</html>
'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("Đã tạo index.html thành công!")

    print("\n=== HOÀN TẤT TẤT CẢ CÁC BƯỚC THÀNH CÔNG! ===")

if __name__ == "__main__":
    main()
