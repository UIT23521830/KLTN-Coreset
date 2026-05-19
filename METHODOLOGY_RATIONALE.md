# Lý do Lựa chọn Phương pháp (Methodology Rationale)

Tài liệu này giải thích lý do (justification) đằng sau việc lựa chọn các thuật toán nén dữ liệu (Coresets) và các mô hình huấn luyện (Training Models) cho Khóa Luận Tốt Nghiệp. Đây là cơ sở khoa học để trả lời phản biện trước Hội đồng bảo vệ.

## 1. Cơ sở lựa chọn Thuật toán Nén (Coreset Methods)

Chúng ta không chọn bừa thuật toán, mà phân bổ 15 phương pháp SOTA thành 4 nhóm chiến lược cốt lõi để so sánh:

1. **Nhóm Baseline (Ngẫu nhiên):**
   *   `Random Selection`: Điểm chuẩn (Baseline) tối thiểu. Mọi thuật toán SOTA bắt buộc phải chứng minh chúng tốt hơn Random.

2. **Nhóm Hình học & Khoảng cách (Geometry-based):**
   *   `CoreTab` (2024), `ModerateDS`: Dựa trên không gian đặc trưng. CoreTab đặc biệt quan trọng vì nó là SOTA sinh ra dành riêng cho dữ liệu dạng bảng (Tabular).

3. **Nhóm Tối ưu hóa Gradient & Loss (Gradient-based):**
   *   `CRAIG`, `GradMatch`, `GLISTER`: Đại diện cho tư duy tối ưu hóa Gradient trong Deep Learning. Các phương pháp này chọn ra một tập con sao cho Gradient của chúng xấp xỉ Gradient của toàn bộ tập dữ liệu gốc.

4. **Nhóm Động lực học Huấn luyện (Training Dynamics) & Proxy:**
   *   `DataMaps` (2020), `Forgetting` (2018), `SVP`: Dựa trên hành vi của dữ liệu qua các Epoch (Mẫu nào hay bị mô hình quên? Mẫu nào có độ tự tin thấp?). Đây là các hướng tiếp cận hành vi học máy rất hiện đại.

5. **Nhóm Sinh dữ liệu / Phân phối (Generative/Distribution):**
   *   `Dataset Condensation` (DC), `TabKDE` (2024-2025): Không chỉ trích xuất, mà dùng ước lượng phân phối để tìm ra lõi dữ liệu hoặc tổng hợp nên dữ liệu mới mang đặc trưng của phân phối gốc.

**Kết luận:** Sự đa dạng này giúp khóa luận chứng minh được một cái nhìn toàn cảnh: "Giữa Gradient, Geometry, và Training Dynamics, hướng tiếp cận nào thực sự phù hợp nhất cho Tabular Data?"

## 2. Cơ sở lựa chọn Mô hình Huấn luyện (Training Models)

Dữ liệu dạng bảng (Tabular) có tính chất cực kỳ đặc thù (các cột không có thứ tự không gian như Ảnh, hay thứ tự thời gian như Text). Do đó, sự lựa chọn mô hình trải dài từ Cổ điển đến Mạng Nơ-ron Foundation:

1. **Nhóm Tree-based (Vua của Tabular Data):**
   *   `XGBoost`, `Random Forest`, `HistGradientBoosting (HGB)`: Theo các nghiên cứu khoa học, Gradient Boosting Trees hiện tại vẫn là SOTA thống trị dữ liệu Tabular. Đưa các mô hình này vào là bắt buộc để có được Benchmark chính xác nhất.
   
2. **Nhóm Cổ điển & Tuyến tính (Linear/Classic):**
   *   `Logistic Regression (LR)`, `SVM`, `KNN`, `Naive Bayes`: Đây là nhóm Lightweight. Giúp đo lường xem liệu tập dữ liệu nén (Coreset) có giữ được ranh giới quyết định (Decision Boundary) tuyến tính cơ bản hay không. 

3. **Nhóm Deep Learning (Neural Networks):**
   *   `MLP`: Mạng nơ-ron đa lớp tiêu chuẩn. Thường học kém hơn Tree trên Tabular nếu không tinh chỉnh (tune) kỹ.
   *   `TabNet` (Google - 2019): Mạng nơ-ron áp dụng cơ chế Sequential Attention chuyên biệt cho dữ liệu bảng, cố gắng mô phỏng sức mạnh của Decision Tree nhưng có thể học vi phân (differentiable).
   *   `TabPFN` (ICLR 2023): Một bước đột phá lớn - Foundation Model dựa trên Transformer. Có khả năng zero-shot classification siêu việt trên các tập dữ liệu nhỏ (điều kiện hoàn hảo khi ta đã nén dữ liệu thành tập Coreset siêu nhỏ).

**Kết luận:** Việc phủ rộng từ Tree-based đến Transformer (TabPFN) đập tan mọi hoài nghi của giảng viên về việc "thiếu sót tính hiện đại" và giúp khẳng định tính khách quan của tập Coreset khi kiểm thử chéo trên đa dạng cấu trúc mô hình.
