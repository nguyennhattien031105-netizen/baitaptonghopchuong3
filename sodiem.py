from flask import (
    Flask,
    url_for,
    request,
    abort,
    redirect,
    make_response,
    jsonify
)
from markupsafe import escape


app = Flask(__name__)

# JSON hiển thị tiếng Việt có dấu
app.json.ensure_ascii = False


# ==================================================
# DỮ LIỆU SINH VIÊN
# ==================================================

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },

    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },

    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },

    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },

    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },

    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


# ==================================================
# PHẦN 0 - HÀM PHỤ
# ==================================================

def average(scores):
    if not scores:
        return None

    return round(
        sum(scores.values()) / len(scores),
        2
    )


def rank(avg):
    if avg is None:
        return "Chưa có điểm"

    if avg >= 8.5:
        return "Giỏi"

    if avg >= 7.0:
        return "Khá"

    if avg >= 5.0:
        return "Trung bình"

    return "Yếu"


def student_summary(mssv):
    student = STUDENTS[mssv]

    avg = average(student["scores"])

    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }


# ==================================================
# KHUNG HTML
# ==================================================

def layout(title, body):
    return f"""
    <!DOCTYPE html>

    <html lang="vi">

    <head>
        <meta charset="UTF-8">
        <title>{escape(title)} - Sổ điểm</title>
    </head>

    <body>

        <nav>

            <a href="{url_for('home')}">
                Trang chủ
            </a>

            |

            <a href="{url_for('student_list')}">
                Sinh viên
            </a>

            |

            <a href="{url_for('search')}">
                Tìm kiếm sinh viên
            </a>

        </nav>

        <hr>

        {body}

    </body>

    </html>
    """


# ==================================================
# CÂU 1 - TRANG CHỦ
# ==================================================

@app.route("/")
def home():

    total_students = len(STUDENTS)

    classes = {
        student["lop"]
        for student in STUDENTS.values()
    }

    total_classes = len(classes)

    body = f"""
        <h1>Sổ điểm lớp học</h1>

        <p>
            Tổng số sinh viên:
            <strong>{total_students}</strong>
        </p>

        <p>
            Số lớp:
            <strong>{total_classes}</strong>
        </p>

        <p>
            <a href="{url_for('student_list')}">
                Xem danh sách sinh viên
            </a>
        </p>

        <p>
            <a href="{url_for('api_students')}">
                API danh sách sinh viên
            </a>
        </p>
    """

    return layout(
        "Trang chủ",
        body
    )


# ==================================================
# CÂU 2 - DANH SÁCH SINH VIÊN
# ==================================================

@app.route("/students")
def student_list():

    selected_class = request.args.get(
        "lop",
        ""
    )

    classes = sorted({
        student["lop"]
        for student in STUDENTS.values()
    })

    if selected_class:

        student_ids = [
            mssv
            for mssv, student in STUDENTS.items()
            if student["lop"].lower()
            == selected_class.lower()
        ]

    else:

        student_ids = list(
            STUDENTS.keys()
        )

    body = """
        <h1>Danh sách sinh viên</h1>
    """

    # Thanh lọc
    body += f"""
        <p>

            <a href="{url_for('student_list')}">
                Tất cả
            </a>
    """

    for lop in classes:

        body += f"""
            |

            <a href="{url_for(
                'student_list',
                lop=lop
            )}">
                {escape(lop)}
            </a>
        """

    body += "</p>"

    # Không có kết quả
    if not student_ids:

        body += """
            <p>
                Không có sinh viên phù hợp.
            </p>
        """

        return layout(
            "Danh sách sinh viên",
            body
        )

    # Bảng sinh viên
    body += """
        <table border="1">

            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
    """

    for mssv in student_ids:

        summary = student_summary(
            mssv
        )

        if summary["average"] is None:
            avg_text = "—"
        else:
            avg_text = str(
                summary["average"]
            )

        body += f"""
            <tr>

                <td>
                    <a href="{url_for(
                        'student_detail',
                        mssv=mssv
                    )}">
                        {escape(mssv)}
                    </a>
                </td>

                <td>
                    {escape(summary["name"])}
                </td>

                <td>
                    {escape(summary["lop"])}
                </td>

                <td>
                    {escape(avg_text)}
                </td>

                <td>
                    {escape(summary["rank"])}
                </td>

            </tr>
        """

    body += "</table>"

    return layout(
        "Danh sách sinh viên",
        body
    )


# ==================================================
# CÂU 3 - CHI TIẾT SINH VIÊN
# ==================================================

@app.route("/students/<mssv>")
def student_detail(mssv):

    if mssv not in STUDENTS:

        abort(
            404,
            description=(
                f"Không có sinh viên "
                f"với MSSV = {mssv}."
            )
        )

    summary = student_summary(
        mssv
    )

    if summary["average"] is None:
        avg_text = "—"
    else:
        avg_text = str(
            summary["average"]
        )

    body = f"""
        <h1>Chi tiết sinh viên</h1>

        <p>
            <strong>Họ tên:</strong>
            {escape(summary["name"])}
        </p>

        <p>
            <strong>MSSV:</strong>
            {escape(summary["mssv"])}
        </p>

        <p>
            <strong>Lớp:</strong>

            <a href="{url_for(
                'student_list',
                lop=summary['lop']
            )}">
                {escape(summary["lop"])}
            </a>
        </p>

        <p>
            <strong>Điểm trung bình:</strong>
            {escape(avg_text)}
        </p>

        <p>
            <strong>Xếp loại:</strong>
            {escape(summary["rank"])}
        </p>

        <h2>Bảng điểm</h2>
    """

    if not summary["scores"]:

        body += """
            <p>Chưa có điểm.</p>
        """

    else:

        body += """
            <table border="1">

                <tr>
                    <th>Học phần</th>
                    <th>Điểm</th>
                </tr>
        """

        for course, score in summary["scores"].items():

            body += f"""
                <tr>
                    <td>{escape(course)}</td>
                    <td>{escape(str(score))}</td>
                </tr>
            """

        body += "</table>"

    # Link CSV
    body += f"""
        <p>

            <a href="{url_for(
                'export_scores',
                mssv=mssv
            )}">
                Tải bảng điểm (CSV)
            </a>

        </p>
    """

    # Link rút gọn
    short_url = url_for(
        "short_student",
        mssv=mssv
    )

    body += f"""
        <p>
            Link rút gọn:

            <a href="{short_url}">
                {escape(short_url)}
            </a>

        </p>
    """

    return layout(
        "Chi tiết sinh viên",
        body
    )


# ==================================================
# CÂU 4 - REDIRECT 301
# ==================================================

@app.route("/sv/<mssv>")
def short_student(mssv):

    return redirect(
        url_for(
            "student_detail",
            mssv=mssv
        ),
        code=301
    )


# ==================================================
# CÂU 5 - EXPORT CSV
# ==================================================

@app.route("/students/<mssv>/export")
def export_scores(mssv):

    if mssv not in STUDENTS:

        abort(
            404,
            description=(
                f"Không có sinh viên "
                f"với MSSV = {mssv}."
            )
        )

    student = STUDENTS[mssv]

    csv_content = "hoc_phan,diem\n"

    for course, score in student["scores"].items():

        csv_content += (
            f"{course},{score}\n"
        )

    response = make_response(
        csv_content
    )

    response.headers[
        "Content-Type"
    ] = "text/csv; charset=utf-8"

    response.headers[
        "Content-Disposition"
    ] = (
        f"attachment; "
        f"filename=diem_{mssv}.csv"
    )

    return response


# ==================================================
# CÂU 6 - TÌM KIẾM
# ==================================================

@app.route("/search")
def search():

    q = request.args.get(
        "q",
        ""
    )

    results = []

    if q:

        q_lower = q.lower()

        for mssv, student in STUDENTS.items():

            name_match = (
                q_lower
                in student["name"].lower()
            )

            mssv_match = (
                q_lower
                in mssv.lower()
            )

            if name_match or mssv_match:

                results.append(
                    mssv
                )

    body = f"""
        <h1>Tìm kiếm sinh viên</h1>

        <form
            method="GET"
            action="{url_for('search')}"
        >

            <input
                type="text"
                name="q"
                value="{escape(q)}"
                placeholder="Nhập tên hoặc MSSV"
            >

            <button type="submit">
                Tìm kiếm
            </button>

        </form>
    """

    if q:

        body += f"""
            <h2>
                Tìm thấy
                {len(results)}
                kết quả cho
                “{escape(q)}”
            </h2>
        """

        if results:

            body += "<ul>"

            for mssv in results:

                student = STUDENTS[mssv]

                body += f"""
                    <li>

                        <a href="{url_for(
                            'student_detail',
                            mssv=mssv
                        )}">

                            {escape(mssv)}
                            -
                            {escape(student["name"])}

                        </a>

                    </li>
                """

            body += "</ul>"

    return layout(
        "Tìm kiếm sinh viên",
        body
    )


# ==================================================
# CÂU 7 - GET /api/students
# ==================================================

@app.route("/api/students")
def api_students():

    lop = request.args.get(
        "lop"
    )

    # ----------------------------------------------
    # Xử lý min_avg
    # ----------------------------------------------

    min_avg = None

    # Phải kiểm tra xem tham số có thực sự xuất hiện
    if "min_avg" in request.args:

        min_avg_raw = request.args.get(
            "min_avg"
        )

        try:
            min_avg = float(
                min_avg_raw
            )

        except (TypeError, ValueError):

            abort(
                400,
                description=(
                    "min_avg phải là số."
                )
            )

    results = []

    for mssv, student in STUDENTS.items():

        summary = student_summary(
            mssv
        )

        # ------------------------------------------
        # Lọc theo lớp
        # ------------------------------------------

        if lop is not None:

            if (
                student["lop"].lower()
                != lop.lower()
            ):
                continue

        # ------------------------------------------
        # Lọc theo điểm trung bình
        # ------------------------------------------

        if min_avg is not None:

            # Không có điểm TB thì bỏ qua
            if summary["average"] is None:
                continue

            if summary["average"] < min_avg:
                continue

        results.append(
            summary
        )

    return jsonify(
        results
    )


# ==================================================
# CÂU 7 - GET /api/students/<mssv>
# ==================================================

@app.route("/api/students/<mssv>")
def api_student_detail(mssv):

    if mssv not in STUDENTS:

        abort(
            404,
            description=(
                f"Không có sinh viên "
                f"với MSSV = {mssv}."
            )
        )

    return jsonify(
        student_summary(mssv)
    )


# ==================================================
# CÂU 8
#
# GET    : xem điểm
# PUT    : thêm / sửa điểm
# DELETE : xóa điểm
# ==================================================

@app.route(
    "/api/students/<mssv>/scores/<course>",
    methods=[
        "GET",
        "PUT",
        "DELETE"
    ]
)
def api_score(mssv, course):

    # ----------------------------------------------
    # Kiểm tra MSSV
    # ----------------------------------------------

    if mssv not in STUDENTS:

        abort(
            404,
            description=(
                f"Không có sinh viên "
                f"với MSSV = {mssv}."
            )
        )

    # Tên môn luôn chuyển thành chữ HOA
    course = course.upper()

    scores = STUDENTS[mssv][
        "scores"
    ]

    # ==================================================
    # GET
    # ==================================================

    if request.method == "GET":

        if course not in scores:

            abort(
                404,
                description=(
                    f"Sinh viên {mssv} "
                    f"chưa có điểm học phần "
                    f"{course}."
                )
            )

        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": scores[course]
        })

    # ==================================================
    # PUT
    # ==================================================

    if request.method == "PUT":

        # Kiểm tra score có xuất hiện không
        if "score" not in request.args:

            abort(
                400,
                description=(
                    "Thiếu tham số score."
                )
            )

        score_raw = request.args.get(
            "score"
        )

        # Chuyển score sang float
        try:

            score = float(
                score_raw
            )

        except (TypeError, ValueError):

            abort(
                400,
                description=(
                    "score phải là số."
                )
            )

        # Điểm phải từ 0 đến 10
        # score = 0 vẫn hợp lệ
        if score < 0 or score > 10:

            abort(
                400,
                description=(
                    "score phải nằm "
                    "trong khoảng từ 0 đến 10."
                )
            )

        # Kiểm tra môn đã tồn tại chưa
        existed = (
            course in scores
        )

        # Thêm hoặc cập nhật
        scores[course] = score

        # Tính lại điểm trung bình
        avg = average(
            scores
        )

        data = {
            "mssv": mssv,
            "course": course,
            "score": score,
            "average": avg
        }

        # ------------------------------------------
        # Nếu đã tồn tại -> cập nhật -> 200
        # ------------------------------------------

        if existed:

            return jsonify(
                data
            ), 200

        # ------------------------------------------
        # Nếu chưa tồn tại -> tạo mới -> 201
        # + Location
        # ------------------------------------------

        response = make_response(
            jsonify(data),
            201
        )

        response.headers[
            "Location"
        ] = url_for(
            "api_score",
            mssv=mssv,
            course=course
        )

        return response

    # ==================================================
    # DELETE
    # ==================================================

    if request.method == "DELETE":

        if course not in scores:

            abort(
                404,
                description=(
                    f"Sinh viên {mssv} "
                    f"chưa có điểm học phần "
                    f"{course}."
                )
            )

        del scores[course]

        # 204 = thành công nhưng không có body
        return "", 204

# ==================================================
# CÂU 9 - XỬ LÝ LỖI
# ==================================================

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):

    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ"
    }

    title = titles.get(
        error.code,
        "Có lỗi xảy ra"
    )

    # Nếu là API -> trả JSON
    if request.path.startswith("/api/"):

        return jsonify({
            "error": title,
            "detail": error.description
        }), error.code

    # Nếu là trang web -> trả HTML
    body = f"""
        <h1>
            {error.code} - {escape(title)}
        </h1>

        <p>
            {escape(error.description)}
        </p>
    """

    return layout(
        title,
        body
    ), error.code    