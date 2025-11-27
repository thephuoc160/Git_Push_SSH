# 📊 Hướng Dẫn Tối Ưu Hóa Mô Hình Star Schema trong Power BI

## 📋 Mục Lục
1. [Giới thiệu về Star Schema](#giới-thiệu-về-star-schema)
2. [Phân tích mô hình hiện tại](#phân-tích-mô-hình-hiện-tại)
3. [Các bước tối ưu hóa](#các-bước-tối-ưu-hóa)
4. [Lợi ích của Star Schema](#lợi-ích-của-star-schema)
5. [Best Practices](#best-practices)

---

## 🌟 Giới thiệu về Star Schema

**Star Schema** (Mô hình sao) là một kiến trúc mô hình dữ liệu phổ biến nhất trong Data Warehouse và Power BI, bao gồm:

- **Dimension Tables (Bảng chiều)**: Chứa thông tin mô tả (như ngày tháng, địa điểm, sản phẩm)
- **Fact Tables (Bảng sự kiện)**: Chứa dữ liệu số liệu (như doanh thu, lưu lượng, mực nước)

### Đặc điểm của Star Schema:
- ✅ Dimension table ở trung tâm
- ✅ Fact tables kết nối trực tiếp với dimension tables
- ✅ Không có kết nối giữa các fact tables với nhau
- ✅ Lọc một chiều từ dimension → fact

---

## 🔍 Phân tích mô hình hiện tại

### Cấu trúc bảng của bạn:

#### **Dimension Table (Bảng chiều)**
| Bảng | Cột | Kiểu dữ liệu | Vai trò |
|------|-----|--------------|---------|
| `Calendar` | Date | DateTime | Bảng ngày tháng chính |

#### **Fact Tables (Bảng sự kiện)**
| Bảng | Các cột | Mô tả |
|------|---------|-------|
| `Htl` | Ngày, Htl, Hhl | Mực nước hồ thượng lưu và hạ lưu |
| `P277` | Ngày, P277, P277-nhan | Công suất P277 |
| `Qvh` | Ngày, Qvh.BT, Qvh.BD | Lưu lượng nước về hồ (bình thường & bão lũ) |
| `Qcm` | Ngày, Qcm H1, Qcm H2, Qcm H3, Qcm H4 | Lưu lượng cửa máy các tổ máy |
| `Qxt` | Ngày, Qxt BT, Qxt BD | Lưu lượng xả tràn |

### ❌ Vấn đề với mô hình hiện tại:

1. **Mối quan hệ hai chiều (BothDirections)**:
   - `Htl[Ngày]` ↔ `Calendar[Date]`
   - `P277[Ngày]` ↔ `Calendar[Date]`
   - `Qvh[Ngày]` ↔ `Calendar[Date]`
   
   ⚠️ **Vấn đề**: Làm chậm hiệu suất, gây nhầm lẫn trong DAX

2. **Mối quan hệ gián tiếp giữa các Fact Tables**:
   - `Qvh[Ngày]` ↔ `Qxt[Ngày]`
   - `P277[Ngày]` ↔ `Qcm[Ngày]`
   
   ⚠️ **Vấn đề**: Vi phạm nguyên tắc Star Schema, tạo đường đi mơ hồ

3. **LocalDateTable tự động**:
   - Power BI tự tạo các bảng ngày tháng ẩn
   
   ⚠️ **Vấn đề**: Lãng phí bộ nhớ khi đã có bảng Calendar

---

## 🛠️ Các bước tối ưu hóa

### **Bước 1: Mở Model View**

1. Trong Power BI Desktop, nhấn vào biểu tượng **Model** ở thanh bên trái
2. Bạn sẽ thấy sơ đồ các bảng và mối quan hệ

### **Bước 2: Xóa các mối quan hệ không tối ưu**

Xóa các mối quan hệ sau (click chuột phải vào đường kẻ → **Delete**):

#### 2.1. Xóa mối quan hệ giữa các Fact Tables:
- ❌ `Qvh[Ngày]` → `Qxt[Ngày]`
- ❌ `P277[Ngày]` → `Qcm[Ngày]`

> **Lý do**: Fact tables không nên kết nối trực tiếp với nhau, chỉ nên kết nối qua Dimension table

### **Bước 3: Cập nhật mối quan hệ với Calendar**

Đối với mỗi mối quan hệ giữa Fact table và Calendar, thực hiện:

#### 3.1. Click đúp vào đường kẻ mối quan hệ

#### 3.2. Cấu hình như sau:

**Cho mối quan hệ: `Htl[Ngày]` → `Calendar[Date]`**
```
┌─────────────────────────────────────────┐
│ Edit relationship                        │
├─────────────────────────────────────────┤
│ From: Htl                                │
│ Column: Ngày                             │
│                                          │
│ To: Calendar                             │
│ Column: Date                             │
│                                          │
│ Cardinality: Many to one (*:1)          │
│ Cross filter direction: Single          │
│ Make this relationship active: ✓        │
│ Assume referential integrity: ☐         │
└─────────────────────────────────────────┘
```

**Lặp lại cho các bảng còn lại:**
- `P277[Ngày]` → `Calendar[Date]`
- `Qvh[Ngày]` → `Calendar[Date]`
- `Qcm[Ngày]` → `Calendar[Date]`
- `Qxt[Ngày]` → `Calendar[Date]`

### **Bước 4: Tạo mối quan hệ mới (nếu chưa có)**

Nếu một Fact table chưa có mối quan hệ với Calendar:

1. Kéo cột `Ngày` từ Fact table
2. Thả vào cột `Date` của bảng `Calendar`
3. Cấu hình như Bước 3.2

### **Bước 5: Kiểm tra kết quả**

Sau khi hoàn thành, sơ đồ của bạn nên trông như thế này:

```
                    ┌─────────────┐
                    │  Calendar   │
                    │   (Date)    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────┬──────────────┐
        ↓                  ↓                  ↓              ↓              ↓
    ┌───────┐         ┌───────┐         ┌───────┐      ┌───────┐      ┌───────┐
    │  Htl  │         │ P277  │         │  Qvh  │      │  Qcm  │      │  Qxt  │
    │(Ngày) │         │(Ngày) │         │(Ngày) │      │(Ngày) │      │(Ngày) │
    └───────┘         └───────┘         └───────┘      └───────┘      └───────┘
     FACT              FACT              FACT           FACT           FACT
```

**Đặc điểm:**
- ✅ Calendar ở trung tâm
- ✅ Tất cả Fact tables kết nối với Calendar
- ✅ Không có kết nối giữa các Fact tables
- ✅ Mũi tên chỉ một chiều: Calendar → Fact tables

---

## 🎯 Lợi ích của Star Schema

### 1. **⚡ Hiệu suất cao hơn**
- Lọc một chiều nhanh hơn lọc hai chiều 30-50%
- Giảm tải cho DAX engine
- Query chạy mượt mà hơn

### 2. **📊 Dễ hiểu và bảo trì**
- Cấu trúc rõ ràng, logic
- Dễ dàng thêm bảng mới
- Người khác dễ hiểu mô hình

### 3. **🔍 DAX đơn giản hơn**
- Không cần xử lý ambiguity
- Context transition rõ ràng
- Ít lỗi hơn khi viết measure

### 4. **💾 Tối ưu bộ nhớ**
- Không cần lưu trữ mối quan hệ phức tạp
- Giảm kích thước file .pbix
- Load nhanh hơn

### 5. **🎨 Tương thích với Visuals**
- Slicer hoạt động tốt hơn
- Drill-down/up mượt mà
- Cross-filtering chính xác

---

## 💡 Best Practices

### ✅ Nên làm:

1. **Sử dụng một bảng Calendar duy nhất**
   - Tạo bảng Calendar đầy đủ với các cột: Năm, Tháng, Quý, Tuần, Ngày trong tuần
   - Đánh dấu là Date Table: `Table Tools` → `Mark as Date Table`

2. **Đặt tên mối quan hệ có ý nghĩa**
   - Ví dụ: `Htl_to_Calendar`, `Qvh_to_Calendar`
   - Giúp dễ debug và bảo trì

3. **Ẩn các cột khóa trong Fact tables**
   - Ẩn cột `Ngày` trong các Fact tables (vì đã có Calendar)
   - Chỉ hiển thị các cột số liệu cần thiết

4. **Tạo Hierarchies trong Calendar**
   ```
   Calendar
   └── Date Hierarchy
       ├── Năm
       ├── Quý
       ├── Tháng
       └── Ngày
   ```

5. **Sử dụng Display Folders**
   - Nhóm các measure liên quan vào các folder
   - Ví dụ: "Lưu lượng", "Mực nước", "Công suất"

### ❌ Không nên làm:

1. **Không tạo mối quan hệ hai chiều** trừ khi thực sự cần thiết
2. **Không kết nối Fact tables với nhau** trực tiếp
3. **Không sử dụng nhiều bảng Calendar** cho cùng một mục đích
4. **Không để Power BI tự tạo relationships** - luôn tạo thủ công để kiểm soát
5. **Không bỏ qua việc đánh dấu Date Table** - điều này quan trọng cho Time Intelligence

---

## 🔧 Troubleshooting

### Vấn đề 1: "Can't create relationship - ambiguous paths"
**Giải pháp**: Xóa các mối quan hệ gián tiếp giữa các Fact tables

### Vấn đề 2: Slicer không filter được visual
**Giải pháp**: 
- Kiểm tra Cross filter direction (phải là Single)
- Đảm bảo relationship đang Active

### Vấn đề 3: DAX measure trả về kết quả sai
**Giải pháp**:
- Kiểm tra có mối quan hệ hai chiều không
- Sử dụng `USERELATIONSHIP()` nếu cần

### Vấn đề 4: Performance chậm
**Giải pháp**:
- Chuyển tất cả mối quan hệ sang Single direction
- Xóa các LocalDateTable không cần thiết
- Tối ưu hóa DAX measures

---

## 📚 Tài liệu tham khảo

### Các hàm DAX hữu ích với Star Schema:

```dax
// Tính tổng theo ngày
Total Daily = 
    CALCULATE(
        SUM(Qvh[Qvh.BT]),
        Calendar[Date]
    )

// Tính trung bình động 7 ngày
Moving Average 7D = 
    CALCULATE(
        AVERAGE(Qvh[Qvh.BT]),
        DATESINPERIOD(
            Calendar[Date],
            MAX(Calendar[Date]),
            -7,
            DAY
        )
    )

// So sánh cùng kỳ năm trước
YoY Comparison = 
    VAR CurrentValue = SUM(Qvh[Qvh.BT])
    VAR PreviousYear = 
        CALCULATE(
            SUM(Qvh[Qvh.BT]),
            SAMEPERIODLASTYEAR(Calendar[Date])
        )
    RETURN
        CurrentValue - PreviousYear

// Tính tổng lũy kế
YTD Total = 
    TOTALYTD(
        SUM(Qvh[Qvh.BT]),
        Calendar[Date]
    )
```

---

## 📞 Hỗ trợ

Nếu bạn gặp vấn đề khi thực hiện các bước trên:

1. Kiểm tra lại từng bước một cách cẩn thận
2. Đảm bảo đã lưu file trước khi thay đổi
3. Có thể tạo bản sao file để test trước
4. Sử dụng Performance Analyzer để kiểm tra hiệu suất

---

## ✅ Checklist hoàn thành

- [ ] Đã xóa mối quan hệ giữa các Fact tables
- [ ] Tất cả Fact tables đã kết nối với Calendar
- [ ] Tất cả mối quan hệ là Many-to-One (*:1)
- [ ] Tất cả mối quan hệ là Single direction
- [ ] Đã đánh dấu Calendar là Date Table
- [ ] Đã ẩn các cột khóa không cần thiết
- [ ] Đã test các visual và measure
- [ ] Đã kiểm tra performance

---

**Chúc bạn thành công! 🎉**

*Tài liệu này được tạo tự động bởi Power BI Modeling Assistant*
*Ngày tạo: 26/11/2024*
