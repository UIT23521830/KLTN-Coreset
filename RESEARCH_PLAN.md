# Kế hoạch Nghiên cứu Đồ án: Mô hình CTR với KAN & NAFI

## PHẦN 1: Ý TƯỞNG BÀI BÁO (NAFI) VÀ LOGIC CODE CHUẨN BIG DATA

### 1. Bài báo NAFI giải quyết chuyện gì?
- **Vấn đề CTR:** Dự đoán click quảng cáo cần 2 thứ: **Chính xác** (nhờ học sự tương tác giữa các đặc trưng, ví dụ `iPhone` + `Ban đêm`) và **Giải thích được** (để biết tại sao lại gợi ý quảng cáo này). Các mô hình cũ (Deep Neural Network) thì chính xác nhưng là "hộp đen". Mô hình tuyến tính thì giải thích được nhưng kém chính xác.
- **Giải pháp NAFI:** Ghép 2 module lại:
  - **NAM (Neural Additive Model):** Mỗi đặc trưng (feature) chạy qua 1 mạng MLP độc lập. Điều này giúp tính được chính xác *sức mạnh đơn lẻ* của từng đặc trưng (Giải thích được).
  - **FIN (Feature Interaction Network):** Dùng Multi-Head Attention (giống Transformer) để học *sự tương tác chéo* giữa các đặc trưng (Tăng độ chính xác).

### 2. Logic của đoạn Code (Kỹ thuật Big Data)
- **Out-of-Core Learning (Chunking):** Data Avazu nặng 6GB (40 triệu dòng). Thay vì đẩy hết vào RAM gây tràn bộ nhớ, hệ thống cắt file thành từng khối 500k-1M dòng (`chunksize=1_000_000`). Xử lý xong khối nào, xóa RAM khối đó.
- **Hashing Trick:** Không thể tạo từ điển Mapping String -> ID cho 40 triệu dòng vì tốn RAM. Hệ thống dùng hàm `hash(chuỗi) % VOCAB_SIZE` để ép mọi chữ thành 1 số nguyên cố định theo thời gian thực.
- **Tại sao hợp lý?** Mọi kỹ sư Big Data đều dùng cách này. Nó cho phép hệ thống train dữ liệu cực lớn (hàng trăm GB) trên máy có RAM rất yếu (2GB - 4GB), tối đa hóa sức mạnh của GPU.

---

## PHẦN 2: TÌM RESEARCH GAP (KHOẢNG TRỐNG NGHIÊN CỨU) CHO ĐỒ ÁN

Việc bạn định dùng mạng **KAN (Kolmogorov-Arnold Networks)** là một ý tưởng bắt trend cực tốt. Mặc dù bài báo **KarSein** đã áp dụng KAN cho CTR, bạn vẫn có 3 "Khoảng trống nghiên cứu" (Research Gap) rất mạnh để làm đồ án:

### Ý tưởng 1: "KAN-NAFI" (Thay thế MLP trong NAM bằng KAN) - 🔥 KHUYÊN DÙNG
- **Hạn chế của NAFI:** Nhánh NAM của NAFI dùng MLP. Dù tính ra được con số đóng góp của từng đặc trưng, nhưng bản thân MLP vẫn là "hộp đen" ở mức vi mô, không ra được công thức toán học.
- **Hạn chế của KarSein:** Dùng KAN chủ yếu để học Tương tác đặc trưng (Feature Interaction).
- **Khoảng trống (Gap):** Bạn giữ lại kiến trúc 2 nhánh của NAFI, nhưng **đá bay nhánh MLP của NAM, thay bằng 1D-KAN**.
- **Đóng góp khoa học:** Tính chất biểu tượng hóa (Symbolification) của KAN cho phép trích xuất ra hẳn một **công thức toán học chính xác** (ví dụ: `Tác động = sin(x) + x^2`) cho từng đặc trưng. Mô hình của bạn mang tính "Interpretable" ở cấp độ Toán học sâu sắc nhất, ăn đứt NAFI ban đầu. Đặt tên mô hình là **KAN-AM**.

### Ý tưởng 2: Knowledge Distillation trên nền KarSein (KD-KarSein)
- **Hạn chế của KAN:** Nhược điểm chí mạng của KAN là tốc độ suy luận (inference speed) cực kỳ chậm do phải tính toán các hàm B-spline. Trong quảng cáo, mô hình phải trả kết quả trong vài mili-giây.
- **Khoảng trống (Gap):** Áp dụng **Knowledge Distillation**. Dùng mạng KarSein khổng lồ làm "Teacher", dạy cho một mạng MLP nhỏ, tốc độ cao làm "Student". Giải quyết bài toán độ trễ (Latency) khi đưa KAN vào thực tế.

### Ý tưởng 3: Kết hợp KAN với bài toán CTR chuỗi thời gian (Sequential CTR)
- **Khoảng trống (Gap):** Criteo và Avazu là dữ liệu Tabular tĩnh. Bạn có thể mang KAN áp dụng vào dữ liệu chuỗi hành vi lịch sử (Sequential) như mô hình DIN (Deep Interest Network) để dự đoán sở thích thay đổi theo thời gian của người dùng.
