# 🗺️ Bản đồ Ánh xạ Phương pháp nén và Mã nguồn (SOTA Repositories Map)

Tài liệu này lưu trữ thông tin đối chiếu giữa **14 Phương pháp SOTA (State-of-the-Art)** được liệt kê trong Kế hoạch và **12 Kho mã nguồn (Repositories)** tương ứng đã được tải về hệ thống.

> [!NOTE]
> Số lượng Repositories ít hơn số lượng Phương pháp vì một số Repository (như `cords` hay `DatasetCondensation`) chứa lõi thuật toán của nhiều phương pháp cùng lúc. Phương pháp C2TC đã được ẩn đi khỏi danh sách đánh giá.

---

## 1. Danh sách Ánh xạ Chi tiết

| STT | Tên Phương pháp (Trong Kế hoạch) | Nguồn Mã nguồn (GitHub Repository) | Ghi chú Giải thích |
|:---:|:---|:---|:---|
| 1 | **Random Selection** | *(Không có)* | Là hàm toán học cơ bản (`np.random.choice`), không cần tải mã nguồn. |
| 2 | **RECON** | `for0nething/RECON` | Viết bằng C++. Yêu cầu đọc file CSV để chạy độc lập. |
| 3 | **CoreTab** | `avivhadar33/coretab` | Phương pháp nền tảng cho Tabular data. |
| 4 | **SubStrat** | `teddy4445/SubStrat` | Tối ưu hóa tập con dựa trên hàm lợi ích. |
| 5 | **CRAIG** | `baharanm/craig` (Gốc)<br>`decile-team/cords` (Thư viện) | Ưu tiên dùng thư viện `cords` để tích hợp chung cho dễ. Tải thêm bản gốc để backup. |
| 6 | **GradMatch** | `decile-team/cords` | Nằm chung bộ công cụ của CORDS. |
| 7 | **GLISTER** | `dssresearch/GLISTER` (Gốc)<br>`decile-team/cords` (Thư viện) | Ưu tiên dùng thư viện `cords`. Có bản gốc dự phòng. |
| 8 | **Data Maps (Cartography)**| `allenai/cartography` | Thiết kế gốc dùng cho NLP, sẽ được điều chỉnh cho Tabular. |
| 9 | **Forgetting Events** | `mtoneva/example_forgetting` | Theo dõi sự thay đổi dự đoán qua các Epochs. |
| 10| **SVP (Selection via Proxy)**| `stanford-futuredata/selection-via-proxy` | Dùng mô hình nhỏ (proxy) để chọn dữ liệu nhanh hơn. |
| 11| **Moderate-DS** | `tmllab/2023_ICLR_Moderate-DS` | Chọn điểm dữ liệu ở gần biên quyết định (margin). |
| 12| **Dataset Condensation** | `VICO-UoE/DatasetCondensation` | **Gộp chung repo với số 13**. Nén dữ liệu thông qua tối ưu Gradient. |
| 13| **Distribution Matching** | `VICO-UoE/DatasetCondensation` | Khớp phân phối không gian ẩn giữa tập nhỏ và tập lớn. |
| 14| **TDColER** | `inwonakng/tdbench` | Benchmarking Tabular Deep Learning. |

---

## 2. Các Biến Thể Đề Xuất (Dự án Tự Phát Triển)

Các phương pháp sau đây **KHÔNG** tải từ GitHub, mà được viết hoàn toàn mới trong thư mục `src/coreset/methods/variants_coretab.py` (Lấy cảm hứng từ CoreTab và DataMaps):

1.  **CoreSynth**: Nhấn mạnh vùng Hard + Tổng hợp dữ liệu.
2.  **CoreFair**: Nhấn mạnh sự công bằng (Fairness) và cân bằng Class.
3.  **CoreNeural**: Dùng Neural Network Proxy thay vì XGBoost.
4.  **CoreCRAIG**: Kết hợp CoreTab với Gradient Matching của CRAIG.
5.  **CoreEnsemble**: Chọn tỷ lệ pha trộn (VD: 50% Hard, 30% Ambiguous, 20% Easy).

---

## 3. Kiến trúc Tích hợp (Wrapper Strategy)

Tất cả các kho mã nguồn tải về ở trên **sẽ không chạy trực tiếp** để tránh xung đột hệ thống. Thay vào đó, chúng sẽ được gọi ngầm thông qua **Wrapper Class** do chúng ta tự viết trong thư mục `src/coreset/methods/`.

*Trạng thái hiện tại: Đã clone đủ 13 thư mục. Sẵn sàng tích hợp Giai đoạn 2.*
