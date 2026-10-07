# SỔ ĐIỂM LỚP HỌC

## 1. Danh sách Routes

Lệnh kiểm tra:

```powershell
flask --app sodiem routes
```

Kết quả:

```text
Endpoint             Methods           Rule
-------------------  ----------------  --------------------------------------------
api_score            DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
api_student_detail   GET               /api/students/<mssv>
api_students         GET               /api/students
export_scores        GET               /students/<mssv>/export
home                 GET               /
search               GET               /search
short_student        GET               /sv/<mssv>
static               GET               /static/<path:filename>
student_detail       GET               /students/<mssv>
student_list         GET               /students
```

Tổng cộng: 10 routes, bao gồm route `static`.


## 2. Kiểm thử bằng curl

Địa chỉ server:

```text
http://127.0.0.1:8000
```

### 2.1 Redirect 301

Lệnh:

```powershell
curl.exe -i http://127.0.0.1:8000/sv/23T1020001
```

Kết quả quan trọng:

```text
HTTP/1.1 301 MOVED PERMANENTLY
Location: /students/23T1020001
```


### 2.2 Xuất bảng điểm CSV

Lệnh:

```powershell
curl.exe -i http://127.0.0.1:8000/students/23T1020001/export
```

Kết quả quan trọng:

```text
HTTP/1.1 200 OK
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename=diem_23T1020001.csv
```

Nội dung:

```text
hoc_phan,diem
PMMNM,8.5
CSDL,7.0
MMT,9.0
```


### 2.3 Lọc lớp và điểm trung bình

Lệnh:

```powershell
curl.exe "http://127.0.0.1:8000/api/students?lop=k47a&min_avg=7"
```

Kết quả:

```text
Trả về JSON chứa các sinh viên thuộc lớp K47A
và có điểm trung bình từ 7 trở lên.
```


### 2.4 min_avg không hợp lệ

Lệnh:

```powershell
curl.exe -i "http://127.0.0.1:8000/api/students?min_avg=abc"
```

Kết quả:

```text
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json
```

Body:

```json
{
    "detail": "min_avg phải là số.",
    "error": "Dữ liệu không hợp lệ"
}
```


### 2.5 Sinh viên không tồn tại

Lệnh:

```powershell
curl.exe -i http://127.0.0.1:8000/api/students/999
```

Kết quả:

```text
HTTP/1.1 404 NOT FOUND
Content-Type: application/json
```

Body:

```json
{
    "detail": "Không có sinh viên với MSSV = 999.",
    "error": "Không tìm thấy"
}
```


### 2.6 Thêm điểm mới

Lệnh:

```powershell
curl.exe -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/web?score=9"
```

Kết quả:

```text
HTTP/1.1 201 CREATED
Content-Type: application/json
Location: /api/students/23T1020005/scores/WEB
```

Body:

```json
{
    "average": 9.0,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 9.0
}
```


### 2.7 Cập nhật điểm

Lệnh:

```powershell
curl.exe -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=7.5"
```

Kết quả:

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

Body:

```json
{
    "average": 7.5,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 7.5
}
```


### 2.8 Điểm không hợp lệ

Lệnh:

```powershell
curl.exe -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=11"
```

Kết quả:

```text
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json
```

Body:

```json
{
    "detail": "score phải nằm trong khoảng từ 0 đến 10.",
    "error": "Dữ liệu không hợp lệ"
}
```


### 2.9 Xóa điểm

Lệnh:

```powershell
curl.exe -i -X DELETE "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB"
```

Kết quả:

```text
HTTP/1.1 204 NO CONTENT
```

Body rỗng.


### 2.10 POST vào API

Lệnh:

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB"
```

Kết quả:

```text
HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: application/json
```

API trả lỗi dưới dạng JSON.


### 2.11 POST vào trang Web

Lệnh:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/students
```

Kết quả:

```text
HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: text/html; charset=utf-8
```

Trang Web trả lỗi dưới dạng HTML.


## 3. Trả lời câu hỏi

### Câu 1

**Tại sao Câu 4 sử dụng 301 còn Câu 8 sử dụng 201 + Location?**

Câu 4 dùng `301 Moved Permanently` vì `/sv/<mssv>` là địa chỉ rút gọn và được chuyển hướng vĩnh viễn sang địa chỉ chính `/students/<mssv>`.

Câu 8 dùng `201 Created` khi thêm một điểm học phần mới vì một tài nguyên mới vừa được tạo. Header `Location` cho biết URL của tài nguyên vừa tạo.


### Câu 2

**Thêm điểm cho sinh viên 23T1020005 rồi khởi động lại server, điểm có còn không? Vì sao?**

Không.

Điểm chỉ được thay đổi trong biến `STUDENTS` đang lưu trong bộ nhớ RAM. Khi server được khởi động lại, chương trình chạy lại từ đầu và biến `STUDENTS` được tạo lại từ dữ liệu ban đầu trong file `sodiem.py`.

Ứng dụng chưa sử dụng cơ sở dữ liệu hoặc file để lưu thay đổi nên điểm mới không được lưu vĩnh viễn.

## 4. Hoàn tất

Đã kiểm thử các chức năng Web, API và xử lý lỗi của ứng dụng.