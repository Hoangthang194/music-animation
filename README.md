# Tuyển tập Animation Pixel Art & Music Visualizer 💖

Dự án tự động chuyển đổi file nhạc MP3 thành bộ tác phẩm animation pixel art (128x64 Monochrome OLED SSD1306) và trình phát Web HD Vector:

---

## 🌟 Bộ 1: "TELL ME WHY" - Dương Domic (Bản Nâng Cấp Siêu Chi Tiết ✨)
Tác phẩm được tạo tự động từ file âm thanh `audio_Feeling Soundzz_download.mp3` theo quy chuẩn [Agent.md](file:///c:/Users/ThangHoang/Documents/20-10/Agent.md).
- **Thời lượng:** ~26.04 giây (372 frames, 70ms/frame).
- **Nội dung cảm xúc (Sad Boy Lo-Fi & Sports Car Drive):**
  - *"Từng cơn đau tăng dần lên..."* - Đứng dưới cột đèn đường cổ điển đêm mưa, áo khoác dài, ngậm điếu thuốc với làn khói uốn lượn bay lên.
  - *"Thời gian trôi âm thầm đếm..."* - Cận cảnh thở các vòng khói tròn (smoke rings) bay lên tan dần cạnh chiếc đồng hồ cát chảy từng hạt.
  - *"Nỗi cô đơn ghé qua đêm nay..."* - Chiếc coupe thể thao JDM chạy trong mưa, bánh xe 5 chấu xoay tròn, đèn pha rọi sáng đường, người lái gác tay ra cửa sổ kẹp điếu thuốc khói bay lùi về sau.
  - *"Đêm qua đêm nay anh chẳng muốn quay lại..."* - Góc nhìn từ buồng lái (Cockpit POV): Cần gạt nước quét nước mưa qua lại, gương chiếu hậu có bùa trái tim đung đưa, taplo và vô lăng 3 chấu.
  - *"Phải xa em anh nào muốn..."* - Xe đỗ ven đường, chàng trai tựa mui xe chụm hai bàn tay che gió châm thuốc, ngấn lệ rơi dưới mưa lạnh.
  - *"Vì chia đôi vẫn còn thương..."* - Ngồi trên nắp capo, ánh sáng màn hình điện thoại le lói rọi lên khuôn mặt, điếu thuốc tàn tro rơi bên dưới trái tim rạn vỡ đập thắt lại theo nhịp bass.
  - **Finale:** Đường cao tốc hun hút về chân trời, chiếc xe thể thao với dải đèn LED đỏ rực lăn bánh xa dần vào màn đêm dưới ánh trăng khuyết và trời đầy sao.
- **Dưới chân hoạt cảnh:** 24 thanh nhạc Equalizer nhảy nhịp nhàng theo tần số âm thanh thực tế (phân tích bằng biến đổi Fourier FFT).

### 🚀 Cách xem bộ "Tell Me Why":
1. **Xem trên Web:** Mở file [index.html](file:///c:/Users/ThangHoang/Documents/20-10/index.html) hoặc [tell_me_why.html](file:///c:/Users/ThangHoang/Documents/20-10/tell_me_why.html) (Web Player Full-Height chuẩn Mobile & Desktop).
2. **Xem Native Desktop:** Nhấp đúp vào [run_tellmewhy.bat](file:///c:/Users/ThangHoang/Documents/20-10/run_tellmewhy.bat) hoặc chạy:
   ```bash
   python run_tellmewhy.py
   ```
3. **Ảnh GIF gửi tặng ngay:** File [tellmewhy.gif](file:///c:/Users/ThangHoang/Documents/20-10/tellmewhy.gif) (chuẩn 384x192 sắc nét).
4. **Mã nguồn C++ SFML:** File [tell_me_why.cpp](file:///c:/Users/ThangHoang/Documents/20-10/tell_me_why.cpp).
5. **File nhị phân OLED:** File [tellmewhy_frames.bin](file:///c:/Users/ThangHoang/Documents/20-10/tellmewhy_frames.bin) nạp trực tiếp vào ESP32 / Arduino màn hình 0.96".

---

## 🌸 Bộ 2: "CỨ THẾ" - Orange x Hoàng Dũng (Special Edition 20/10)
- **Thời lượng:** ~32.2 giây (460 frames, 70ms/frame).
- **Xem trên Web:** Mở file [cu_the.html](file:///c:/Users/ThangHoang/Documents/20-10/cu_the.html) (Web Player Full-Height, có nút chuyển nhanh qua lại với Tell Me Why).
- **Xem trên Desktop:** Nhấp đúp [run_cuthe.bat](file:///c:/Users/ThangHoang/Documents/20-10/run_cuthe.bat) hoặc `python run_cuthe.py`.
- **Ảnh GIF:** [cuthe_20_10.gif](file:///c:/Users/ThangHoang/Documents/20-10/cuthe_20_10.gif).
- **Mã nguồn C++:** [cu_the.cpp](file:///c:/Users/ThangHoang/Documents/20-10/cu_the.cpp).
- **File nhị phân OLED:** [cuthe_frames.bin](file:///c:/Users/ThangHoang/Documents/20-10/cuthe_frames.bin).

---

## 🎬 Bộ 3: "I miss you..." (Rex Orange County - Best Friend)
Bản animation kinh điển tải về từ repository [baodeptraihihi/lmao-code](https://github.com/baodeptraihihi/lmao-code).
- **Mã nguồn C++:** [bestfriends.cpp](file:///c:/Users/ThangHoang/Documents/20-10/bestfriends.cpp)
- **Xem trên Desktop:** Nhấp đúp [run.bat](file:///c:/Users/ThangHoang/Documents/20-10/run.bat) hoặc chạy `python run.py`.
- **File GIF:** [animation.gif](file:///c:/Users/ThangHoang/Documents/20-10/animation.gif).

---

## 🤖 Hướng dẫn tạo bài hát mới tự động
Xem tài liệu đóng gói kỹ năng [Agent.md](file:///c:/Users/ThangHoang/Documents/20-10/Agent.md) hoặc [AGENTS.md](file:///c:/Users/ThangHoang/Documents/20-10/AGENTS.md).

### ⌨️ Phím tắt chung khi chạy Desktop:
- `Space`: Tạm dừng / Tiếp tục
- `M`: Tắt / Bật tiếng (Mute/Unmute)
- `R`: Xem lại từ đầu
- `L`: Bật/Tắt lặp lại
- `I`: Chuyển đổi Dark / Light mode
- `Esc`: Thoát
