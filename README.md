# DATA ANALYST ASSISSTANT 🤖💾

## Tổng quan
Trợ lý này được hỗ trợ bởi Streamlit và sử dụng Gemini AI của Google để giúp các nhà phát triển và chuyên gia dữ liệu nhanh chóng tạo ra các truy vấn SQL, biểu đồ , tạo báo cáo dựa trên mô tả bằng ngôn ngữ tự nhiên.

## 🌟 Tính năng
- Tạo truy vấn SQL từ đầu vào ngôn ngữ tự nhiên
- Hỗ trợ nhiều định dạng file CSV/EXCEL
- Tạo biểu đồ để trực quan hóa tương tác
- Giao diện Streamlit thân thiện với người dùng
- Được hỗ trợ bởi AI sinh thành tiên tiến của Google
- Xác thực truy vấn và đề xuất tối ưu hóa

## 🛠 Yêu cầu tiên quyết
- Python 3.8+
- Streamlit
- Google Generative AI SDK
- Google Cloud API Key
- pandasai

## 📦 Cài đặt
### 1. Sao chép Kho lưu trữ
```bash
git clone https://github.com/your-username/DATA-ASSISTANT.git
cd DATA-ASSISTANT
```

### 2. Tạo Môi trường Ảo
```bash
python -m venv venv
source venv/bin/activate  # Trên Windows, sử dụng `venv\Scripts\activate`
```

### 3. Cài đặt Các Gói Phụ thuộc
```bash
pip install -r requirements.txt
```

### 4. Thiết lập Thông tin Xác thực Google Cloud
1. Tạo một dự án Google Cloud
2. Kích hoạt API Generative AI
3. Tạo tài khoản dịch vụ và tải xuống khóa JSON
4. Thiết lập biến môi trường:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## 🚀 Chạy Ứng dụng
```bash
streamlit run SQL.py
```

## 🔧 Cấu hình
ai_settings:
  max_query_length: 500
  temperature: 0.7
  safety_threshold: moderate

## 📝 Ví dụ Sử dụng
### 1. Tạo Truy vấn Cơ bản
- Đầu vào: "Lấy tất cả khách hàng từ New York"
- Đầu ra: 
  ```sql
  SELECT * FROM customers WHERE city = 'New York';
  ```

### 2. Tạo Truy vấn Phức tạp
- Đầu vào: "Tìm 5 sản phẩm bán chạy nhất trong quý vừa qua"
- Đầu ra:
  ```sql
  SELECT 
    product_id, 
    product_name, 
    SUM(sales_amount) as total_sales
  FROM sales
  WHERE sale_date BETWEEN '2023-10-01' AND '2023-12-31'
  GROUP BY product_id, product_name
  ORDER BY total_sales DESC
  LIMIT 5;
  ```

## 🛡️ Bảo mật
- Không bao giờ commit khóa API hoặc thông tin xác thực nhạy cảm vào kho lưu trữ
- Sử dụng biến môi trường hoặc quản lý bí mật an toàn
- Triển khai kiểm tra đầu vào để ngăn chặn SQL injection

## 📊 Chỉ số Hiệu suất
- Thời gian tạo truy vấn trung bình: 2-10s ( Tùy vào độ phức tạp theo truy vấn)

## 🚧 Hạn chế
- Phụ thuộc vào chất lượng và độ cụ thể của mô tả đầu vào
- Yêu cầu hiểu biết cơ bản về cấu trúc cơ sở dữ liệu
- Không có chức năng kết nối với cơ sở dữ liệu của bạn
- Biểu đồ không linh hoạt (chỉ hỗ trợ biểu đồ Line, Bar, Hist, heatmap và pie chart)
- Chỉ hỗ trợ file CSV/EXCEL dưới 200MB
- Viết prompt phải rõ ràng và cụ thể
- Google Gemini không phải một model tối ưu nhất , có thể cân nhắc sử dụng OPENAI nếu có bản Premium , không giới hạn quotaquota

## 🙏 Lời cảm ơn
- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://cloud.google.com/ai)
- Cộng đồng mã nguồn mở

---
**Tuyên bố miễn trừ trách nhiệm**: Công cụ này là một trợ lý AI và nên được sử dụng với sự xem xét cẩn thận. Luôn xác thực các truy vấn SQL được tạo ra trước khi thực thi.
