
import os
import io
import base64
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SQLITE_PATH = DATA_DIR / "deliveryos.db"

st.set_page_config(
    page_title="AI-KOS DeliveryOS V0.3",
    page_icon="🏗️",
    layout="wide"
)

# =========================================================
# CẤU HÌNH CSDL: PostgreSQL nếu có DATABASE_URL, ngược lại SQLite
# =========================================================
def get_database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url
    try:
        url = str(st.secrets.get("DATABASE_URL", "")).strip()
    except Exception:
        url = ""
    return url

DATABASE_URL = get_database_url()
DB_KIND = "postgres" if DATABASE_URL.startswith(("postgres://", "postgresql://")) else "sqlite"

def get_conn():
    if DB_KIND == "postgres":
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_PATH)

def adapt_sql(sql):
    return sql.replace("?", "%s") if DB_KIND == "postgres" else sql

def execute(sql, params=()):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(adapt_sql(sql), params)
        con.commit()
    finally:
        con.close()

def read_df(sql, params=()):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(adapt_sql(sql), params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return pd.DataFrame(rows, columns=cols)
    finally:
        con.close()

def scalar(sql, params=(), default=0):
    df = read_df(sql, params)
    if df.empty:
        return default
    return df.iloc[0, 0]

def create_tables():
    statements = [
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            project_name TEXT,
            project_type TEXT,
            owner TEXT,
            location TEXT,
            planned_start TEXT,
            planned_finish TEXT,
            budget REAL DEFAULT 0,
            original_contract REAL DEFAULT 0,
            approved_changes REAL DEFAULT 0,
            paid REAL DEFAULT 0,
            planned_progress REAL DEFAULT 0,
            actual_progress REAL DEFAULT 0,
            status TEXT,
            alert_level TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS work_items (
            work_id TEXT PRIMARY KEY,
            project_id TEXT,
            work_group TEXT,
            work_name TEXT,
            unit TEXT,
            planned_qty REAL DEFAULT 0,
            planned_unit_price REAL DEFAULT 0,
            planned_value REAL DEFAULT 0,
            planned_start TEXT,
            planned_finish TEXT,
            planned_progress REAL DEFAULT 0,
            actual_progress REAL DEFAULT 0,
            assignee TEXT,
            status TEXT,
            accepted TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS costs (
            cost_id TEXT PRIMARY KEY,
            project_id TEXT,
            cost_group TEXT,
            description TEXT,
            planned_budget REAL DEFAULT 0,
            committed REAL DEFAULT 0,
            actual_cost REAL DEFAULT 0,
            forecast_final REAL DEFAULT 0,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_id TEXT PRIMARY KEY,
            project_id TEXT,
            log_date TEXT,
            work_name TEXT,
            team TEXT,
            workers INTEGER DEFAULT 0,
            quantity_done TEXT,
            weather TEXT,
            issue TEXT,
            status TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS changes (
            change_id TEXT PRIMARY KEY,
            project_id TEXT,
            work_id TEXT,
            found_date TEXT,
            change_type TEXT,
            description TEXT,
            reason TEXT,
            proposed_value REAL DEFAULT 0,
            delay_days INTEGER DEFAULT 0,
            approval_status TEXT,
            approved_value REAL DEFAULT 0,
            approved_by TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS acceptances (
            acceptance_id TEXT PRIMARY KEY,
            project_id TEXT,
            work_id TEXT,
            acceptance_date TEXT,
            accepted_quantity TEXT,
            accepted_value REAL DEFAULT 0,
            result TEXT,
            defects TEXT,
            correction_due TEXT,
            confirmed_by TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            project_id TEXT,
            contract_id TEXT,
            tranche TEXT,
            request_date TEXT,
            requested_value REAL DEFAULT 0,
            approved_value REAL DEFAULT 0,
            paid_value REAL DEFAULT 0,
            payment_date TEXT,
            method TEXT,
            status TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS warranty_maintenance (
            wm_id TEXT PRIMARY KEY,
            project_id TEXT,
            asset_item TEXT,
            wm_type TEXT,
            start_date TEXT,
            due_date TEXT,
            contractor TEXT,
            tracking_content TEXT,
            status TEXT,
            cost REAL DEFAULT 0,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS attachments (
            attachment_id TEXT PRIMARY KEY,
            project_id TEXT,
            work_id TEXT,
            upload_date TEXT,
            category TEXT,
            stage TEXT,
            filename TEXT,
            mime_type TEXT,
            description TEXT,
            uploaded_by TEXT,
            content_b64 TEXT
        )
        """
    ]
    con = get_conn()
    try:
        cur = con.cursor()
        for stmt in statements:
            cur.execute(stmt)
        con.commit()
    finally:
        con.close()

# =========================================================
# DỮ LIỆU MẪU & 5 MẪU DỰ ÁN
# =========================================================
PROJECT_TEMPLATES = {
    "Xây nhà phố": {
        "prefix": "HOUSE",
        "groups": [
            ("Chuẩn bị", "Khảo sát hiện trạng, xác định yêu cầu"),
            ("Pháp lý/Thiết kế", "Hoàn thiện thiết kế và hồ sơ cần thiết"),
            ("Phần thô", "Móng, kết cấu, xây tô"),
            ("MEP", "Điện, nước và hệ thống kỹ thuật"),
            ("Hoàn thiện", "Ốp lát, sơn, cửa, thiết bị"),
            ("Bàn giao", "Nghiệm thu, bàn giao, bảo hành"),
        ]
    },
    "Sửa chữa/cải tạo nhà": {
        "prefix": "REPAIR",
        "groups": [
            ("Khảo sát", "Khảo sát hiện trạng và chụp ảnh trước sửa chữa"),
            ("Tháo dỡ", "Tháo dỡ các hạng mục cũ/hư hỏng"),
            ("Kết cấu", "Gia cường/sửa chữa kết cấu nếu có"),
            ("Điện nước", "Sửa chữa/thay thế điện nước"),
            ("Hoàn thiện", "Chống thấm, sơn, ốp lát, cửa"),
            ("Bàn giao", "Nghiệm thu, thanh toán, bảo hành"),
        ]
    },
    "Xây dựng công trình": {
        "prefix": "CONST",
        "groups": [
            ("Chuẩn bị", "Bàn giao mặt bằng và chuẩn bị thi công"),
            ("Nền móng", "Thi công nền, móng"),
            ("Kết cấu", "Thi công kết cấu chính"),
            ("Hạ tầng/MEP", "Hệ thống kỹ thuật và hạ tầng"),
            ("Hoàn thiện", "Hoàn thiện công trình"),
            ("Nghiệm thu", "Nghiệm thu, thanh toán, bàn giao"),
        ]
    },
    "Cải tạo mặt bằng/đất": {
        "prefix": "LAND",
        "groups": [
            ("Khảo sát", "Khảo sát hiện trạng, cao độ, ranh giới"),
            ("Chuẩn bị", "Dọn dẹp và chuẩn bị mặt bằng"),
            ("Đào đắp", "Đào, đắp, san nền"),
            ("Thoát nước", "Tổ chức thoát nước và bảo vệ mặt bằng"),
            ("Hoàn thiện", "Lu lèn, chỉnh cao độ, nghiệm thu"),
            ("Bảo trì", "Theo dõi lún/sạt và bảo trì sau hoàn thành"),
        ]
    },
    "Quản lý xưởng cơ khí": {
        "prefix": "WORKSHOP",
        "groups": [
            ("Đơn hàng", "Tiếp nhận yêu cầu và lập báo giá"),
            ("Kế hoạch", "Lập lệnh sản xuất và kế hoạch vật tư"),
            ("Vật tư", "Mua/nhập/xuất vật tư"),
            ("Gia công", "Cắt, hàn, gia công, lắp ráp"),
            ("Kiểm tra", "Kiểm tra chất lượng và hoàn thiện"),
            ("Giao hàng", "Bàn giao, thanh toán và theo dõi bảo hành"),
        ]
    }
}

def new_id(prefix, table, id_col):
    today = datetime.now().strftime("%Y%m%d")
    n = int(scalar(f"SELECT COUNT(*) FROM {table} WHERE {id_col} LIKE ?", (f"{prefix}-{today}-%",), 0)) + 1
    return f"{prefix}-{today}-{n:03d}"

def seed_project_tasks(project_id, template_name, start_date, finish_date):
    template = PROJECT_TEMPLATES.get(template_name)
    if not template:
        return
    groups = template["groups"]
    total_days = max((finish_date - start_date).days, len(groups))
    step = max(total_days // len(groups), 1)

    for idx, (grp, work_name) in enumerate(groups, start=1):
        s = start_date + timedelta(days=(idx - 1) * step)
        e = min(start_date + timedelta(days=idx * step - 1), finish_date)
        wid = f"{project_id}-W{idx:02d}"
        execute(
            """INSERT INTO work_items
            (work_id,project_id,work_group,work_name,unit,planned_qty,planned_unit_price,planned_value,
             planned_start,planned_finish,planned_progress,actual_progress,assignee,status,accepted,note)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (wid, project_id, grp, work_name, "gói", 1, 0, 0, str(s), str(e), 0, 0, "",
             "Chưa bắt đầu", "Không", "Sinh tự động từ mẫu dự án V0.3")
        )

def seed_demo_if_empty():
    if int(scalar("SELECT COUNT(*) FROM projects", default=0)) > 0:
        return

    projects = [
        ("LXS-REPAIR-2026-001","Sửa chữa, cải tạo nhà ở cũ – Dự án mẫu 01","Sửa chữa/cải tạo nhà",
         "Chủ đầu tư mẫu","Đắk Lắk","2026-09-01","2026-10-30",500_000_000,420_000_000,
         15_000_000,220_000_000,70,62,"Đang thi công","Vàng","Dữ liệu demo V0.3"),
        ("LXS-WORKSHOP-2026-001","Quản lý xưởng cơ khí mẫu","Quản lý xưởng cơ khí",
         "Doanh nghiệp mẫu","Đắk Lắk","2026-08-01","2026-12-31",800_000_000,0,
         0,180_000_000,65,58,"Đang vận hành","Vàng","Dữ liệu demo V0.3"),
        ("LXS-CONST-2026-001","Công trình sửa chữa văn phòng mẫu","Xây dựng công trình",
         "Chủ đầu tư mẫu","Đắk Lắk","2026-08-15","2026-11-15",1_200_000_000,980_000_000,
         25_000_000,350_000_000,55,50,"Đang thi công","Vàng","Dữ liệu demo V0.3"),
    ]
    for p in projects:
        execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", p)

    work_rows = [
        ("W-001","LXS-REPAIR-2026-001","Tháo dỡ","Tháo mái cũ","m2",120,120000,14400000,"2026-09-01","2026-09-04",100,100,"Tổ A","Hoàn thành","Có",""),
        ("W-002","LXS-REPAIR-2026-001","Kết cấu","Gia cường dầm","md",24,850000,20400000,"2026-09-05","2026-09-12",100,100,"Tổ B","Hoàn thành","Có",""),
        ("W-003","LXS-REPAIR-2026-001","Mái","Chống thấm mái","m2",100,180000,18000000,"2026-09-13","2026-09-18",90,70,"Tổ A","Đang thực hiện","Không","Mưa ảnh hưởng tiến độ"),
        ("W-004","LXS-REPAIR-2026-001","Điện","Thay dây điện cũ","gói",1,28000000,28000000,"2026-09-15","2026-09-25",70,55,"Tổ điện","Đang thực hiện","Không",""),
        ("WW-001","LXS-WORKSHOP-2026-001","Đơn hàng","Gia công khung thép đơn hàng A","bộ",10,15000000,150000000,"2026-08-05","2026-08-30",100,100,"Tổ gia công","Hoàn thành","Có",""),
        ("WW-002","LXS-WORKSHOP-2026-001","Sản xuất","Gia công lan can đơn hàng B","md",120,850000,102000000,"2026-09-01","2026-09-20",80,65,"Tổ hàn","Đang thực hiện","Không","Thiếu thép hộp"),
        ("WC-001","LXS-CONST-2026-001","Tháo dỡ","Tháo trần cũ","m2",250,95000,23750000,"2026-08-15","2026-08-20",100,100,"Tổ 1","Hoàn thành","Có",""),
        ("WC-002","LXS-CONST-2026-001","Hoàn thiện","Thi công trần mới","m2",250,320000,80000000,"2026-09-01","2026-09-15",90,70,"Tổ 2","Đang thực hiện","Không",""),
    ]
    for r in work_rows:
        execute("INSERT INTO work_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", r)

    costs = [
        ("C-001","LXS-REPAIR-2026-001","Xây lắp","Thi công chính",380000000,360000000,185000000,390000000,""),
        ("C-002","LXS-REPAIR-2026-001","Vật tư","Vật tư bổ sung",40000000,35000000,18000000,42000000,""),
        ("CW-001","LXS-WORKSHOP-2026-001","Vật tư","Thép và vật tư sản xuất",500000000,320000000,210000000,470000000,""),
        ("CC-001","LXS-CONST-2026-001","Xây lắp","Thi công sửa chữa",900000000,850000000,320000000,930000000,""),
    ]
    for r in costs:
        execute("INSERT INTO costs VALUES (?,?,?,?,?,?,?,?,?)", r)

    changes = [
        ("CHG-001","LXS-REPAIR-2026-001","W-003","2026-09-15","Tăng khối lượng",
         "Bổ sung xử lý chân tường mái","Hư hỏng phát hiện sau tháo dỡ",15000000,2,"Đã duyệt",15000000,"Chủ đầu tư",""),
        ("CHG-002","LXS-REPAIR-2026-001","W-004","2026-09-16","Bổ sung công việc",
         "Bổ sung ống gen khu bếp","Hệ thống cũ không bảo đảm",6500000,1,"Chờ duyệt",0,"",""),
    ]
    for r in changes:
        execute("INSERT INTO changes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", r)

    execute("INSERT INTO acceptances VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("ACC-001","LXS-REPAIR-2026-001","W-001","2026-09-04","120 m2",14400000,"Đạt","","","Chủ đầu tư/NT",""))

    execute("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("PAY-001","LXS-REPAIR-2026-001","HD-001","Tạm ứng","2026-08-29",100000000,100000000,100000000,
             "2026-08-30","Chuyển khoản","Đã thanh toán",""))

    execute("INSERT INTO warranty_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("WM-001","LXS-REPAIR-2026-001","Chống thấm mái","Bảo hành","2026-11-01","2027-10-31",
             "Nhà thầu mẫu","Bảo hành 12 tháng","Chưa bắt đầu",0,""))

create_tables()
seed_demo_if_empty()

# =========================================================
# HÀM TIỆN ÍCH
# =========================================================
def money(x):
    try:
        return f"{float(x):,.0f} đ".replace(",", ".")
    except Exception:
        return "0 đ"

def vi_date(x):
    try:
        return pd.to_datetime(x).strftime("%d/%m/%Y")
    except Exception:
        return str(x or "")

def project_map():
    df = read_df("SELECT project_id, project_name FROM projects ORDER BY project_id")
    return {r["project_id"]: r["project_name"] for _, r in df.iterrows()}

DISPLAY_PROJECT = {
    "project_id":"Mã dự án","project_name":"Tên dự án","project_type":"Loại dự án","owner":"Chủ đầu tư/Đơn vị",
    "location":"Địa điểm","budget":"Ngân sách","planned_progress":"Tiến độ KH (%)",
    "actual_progress":"Tiến độ TT (%)","status":"Trạng thái","alert_level":"Cảnh báo"
}
DISPLAY_WORK = {
    "work_id":"Mã việc","work_group":"Nhóm việc","work_name":"Công việc","planned_start":"Bắt đầu KH",
    "planned_finish":"Kết thúc KH","planned_progress":"Tiến độ KH (%)","actual_progress":"Tiến độ TT (%)",
    "assignee":"Phụ trách","status":"Trạng thái","accepted":"Đã nghiệm thu","note":"Ghi chú"
}
DISPLAY_COST = {
    "cost_group":"Nhóm chi phí","description":"Nội dung","planned_budget":"Ngân sách KH",
    "committed":"Cam kết/Hợp đồng","actual_cost":"Chi thực tế","forecast_final":"Dự báo cuối kỳ"
}

def current_project_data(pid):
    p = read_df("SELECT * FROM projects WHERE project_id=?", (pid,))
    w = read_df("SELECT * FROM work_items WHERE project_id=? ORDER BY planned_start", (pid,))
    c = read_df("SELECT * FROM costs WHERE project_id=?", (pid,))
    ch = read_df("SELECT * FROM changes WHERE project_id=? ORDER BY found_date DESC", (pid,))
    return p.iloc[0], w, c, ch

def alert_rules(project, work, changes, costs):
    alerts = []
    gap = float(project["actual_progress"] or 0) - float(project["planned_progress"] or 0)
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    budget = float(project["budget"] or 0)

    if gap <= -10:
        alerts.append(("🔴","Tiến độ",f"Thực tế thấp hơn kế hoạch {abs(gap):.0f} điểm %."))
    elif gap < 0:
        alerts.append(("🟡","Tiến độ",f"Thực tế thấp hơn kế hoạch {abs(gap):.0f} điểm %."))

    if budget > 0 and forecast > budget:
        alerts.append(("🔴","Chi phí",f"Dự báo vượt ngân sách {money(forecast-budget)}."))
    elif budget > 0 and forecast > budget * 0.95:
        alerts.append(("🟡","Chi phí","Dự báo cuối kỳ đã vượt 95% ngân sách."))

    if not work.empty:
        finish = pd.to_datetime(work["planned_finish"], errors="coerce")
        overdue = work[(work["status"] != "Hoàn thành") & (finish < pd.Timestamp.today().normalize())]
        if len(overdue):
            alerts.append(("🟠","Công việc",f"Có {len(overdue)} công việc quá hạn chưa hoàn thành."))

    if not changes.empty:
        pending = changes[changes["approval_status"]=="Chờ duyệt"]
        if len(pending):
            alerts.append(("🟡","Phát sinh",f"Có {len(pending)} phát sinh chờ duyệt, tổng {money(pending['proposed_value'].sum())}."))

    if not alerts:
        alerts.append(("🟢","Tổng thể","Chưa có cảnh báo đáng kể theo bộ quy tắc V0.3."))
    return alerts

def tasks_today(pid=None):
    today = pd.Timestamp.today().normalize()
    horizon7 = today + pd.Timedelta(days=7)
    horizon30 = today + pd.Timedelta(days=30)
    params = (pid,) if pid else ()
    cond = " WHERE project_id=?" if pid else ""

    works = read_df(f"SELECT * FROM work_items{cond}", params)
    changes = read_df(f"SELECT * FROM changes{cond}", params)
    acc = read_df(f"SELECT * FROM acceptances{cond}", params)
    pay = read_df(f"SELECT * FROM payments{cond}", params)
    wm = read_df(f"SELECT * FROM warranty_maintenance{cond}", params)

    result = []

    if not works.empty:
        finish = pd.to_datetime(works["planned_finish"], errors="coerce")
        overdue = works[(works["status"]!="Hoàn thành") & (finish < today)]
        for _, r in overdue.iterrows():
            result.append(("🔴","Quá hạn",r["project_id"],r["work_name"],f"Hạn {vi_date(r['planned_finish'])}"))

        upcoming = works[(works["status"]!="Hoàn thành") & (finish >= today) & (finish <= horizon7)]
        for _, r in upcoming.iterrows():
            result.append(("🟡","Sắp đến hạn",r["project_id"],r["work_name"],f"Hạn {vi_date(r['planned_finish'])}"))

    if not changes.empty:
        pending = changes[changes["approval_status"]=="Chờ duyệt"]
        for _, r in pending.iterrows():
            result.append(("🟡","Chờ duyệt",r["project_id"],r["description"],money(r["proposed_value"])))

    if not acc.empty and "defects" in acc.columns:
        acc2 = acc[acc["defects"].fillna("").str.strip()!=""]
        for _, r in acc2.iterrows():
            result.append(("🟠","Tồn tại nghiệm thu",r["project_id"],r["defects"],f"Khắc phục: {vi_date(r['correction_due'])}"))

    if not pay.empty:
        pending_pay = pay[pay["paid_value"].fillna(0) < pay["approved_value"].fillna(0)]
        for _, r in pending_pay.iterrows():
            remain = float(r["approved_value"] or 0) - float(r["paid_value"] or 0)
            result.append(("🟡","Chờ thanh toán",r["project_id"],r["tranche"],money(remain)))

    if not wm.empty:
        due = pd.to_datetime(wm["due_date"], errors="coerce")
        upcoming_wm = wm[(wm["status"]!="Hoàn thành") & (due >= today) & (due <= horizon30)]
        for _, r in upcoming_wm.iterrows():
            result.append(("🔵",r["wm_type"],r["project_id"],r["asset_item"],f"Đến hạn {vi_date(r['due_date'])}"))

    return pd.DataFrame(result, columns=["Mức","Loại việc","Mã dự án","Nội dung","Thông tin"])

def export_project_excel(pid):
    output = io.BytesIO()
    tables = {
        "Du_an": read_df("SELECT * FROM projects WHERE project_id=?", (pid,)),
        "Cong_viec": read_df("SELECT * FROM work_items WHERE project_id=?", (pid,)),
        "Chi_phi": read_df("SELECT * FROM costs WHERE project_id=?", (pid,)),
        "Nhat_ky": read_df("SELECT * FROM daily_logs WHERE project_id=?", (pid,)),
        "Phat_sinh": read_df("SELECT * FROM changes WHERE project_id=?", (pid,)),
        "Nghiem_thu": read_df("SELECT * FROM acceptances WHERE project_id=?", (pid,)),
        "Thanh_toan": read_df("SELECT * FROM payments WHERE project_id=?", (pid,)),
        "Bao_hanh_Bao_tri": read_df("SELECT * FROM warranty_maintenance WHERE project_id=?", (pid,)),
    }
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    output.seek(0)
    return output.getvalue()

# =========================================================
# GIAO DIỆN
# =========================================================
st.sidebar.title("AI-KOS DeliveryOS")
st.sidebar.caption("Quản trị thực hiện dự án, công trình và vận hành tài sản")

page = st.sidebar.radio(
    "Chức năng",
    [
        "00. Hôm nay cần làm gì?",
        "01. Danh mục dự án",
        "02. Tổng quan",
        "03. Công việc & tiến độ",
        "04. Chi phí & dòng tiền",
        "05. Nhật ký & hồ sơ",
        "06. Phát sinh",
        "07. Nghiệm thu & thanh toán",
        "08. Bảo hành & bảo trì",
        "09. Báo cáo",
    ]
)

projects = project_map()
pid = st.sidebar.selectbox(
    "Dự án",
    list(projects.keys()),
    format_func=lambda x: f"{x} – {projects[x]}"
)

project, work, costs, changes = current_project_data(pid)

st.title("AI-KOS DeliveryOS V0.3")
db_label = "PostgreSQL – lưu bền" if DB_KIND == "postgres" else "SQLite – chế độ demo"
st.caption(f"Quản lý nhiều dự án | CSDL: {db_label} | AI chỉ phân tích/cảnh báo, không tự sửa số liệu gốc.")

if DB_KIND == "sqlite":
    st.info("ℹ️ Bản đang chạy dùng SQLite. Trên Streamlit Community Cloud, dữ liệu mới nhập có thể mất khi ứng dụng được khởi tạo lại. V0.3 đã sẵn sàng chuyển sang PostgreSQL bằng DATABASE_URL.")

# 00. HÔM NAY
if page == "00. Hôm nay cần làm gì?":
    st.subheader("Hôm nay cần làm gì?")
    scope = st.radio("Phạm vi", ["Tất cả dự án","Dự án đang chọn"], horizontal=True)
    todo = tasks_today(pid if scope=="Dự án đang chọn" else None)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Tổng việc cần chú ý", len(todo))
    c2.metric("Quá hạn", int((todo["Loại việc"]=="Quá hạn").sum()) if not todo.empty else 0)
    c3.metric("Chờ duyệt/thanh toán", int(todo["Loại việc"].isin(["Chờ duyệt","Chờ thanh toán"]).sum()) if not todo.empty else 0)
    c4.metric("Bảo hành/bảo trì sắp đến hạn", int(todo["Loại việc"].isin(["Bảo hành","Bảo trì"]).sum()) if not todo.empty else 0)

    if todo.empty:
        st.success("Không có việc khẩn cấp hoặc sắp đến hạn theo dữ liệu hiện tại.")
    else:
        st.dataframe(todo, use_container_width=True, hide_index=True)

    st.markdown("### Gợi ý điều hành")
    if not todo.empty:
        if (todo["Loại việc"]=="Quá hạn").any():
            st.error("Ưu tiên xử lý các công việc quá hạn trước.")
        if (todo["Loại việc"]=="Chờ duyệt").any():
            st.warning("Xem xét phát sinh đang chờ duyệt để tránh kéo dài tiến độ.")
        if (todo["Loại việc"]=="Chờ thanh toán").any():
            st.warning("Kiểm tra hồ sơ nghiệm thu và điều kiện thanh toán.")
    else:
        st.write("Tiếp tục cập nhật nhật ký và tiến độ thực tế để hệ thống cảnh báo chính xác.")

# 01. DANH MỤC
elif page == "01. Danh mục dự án":
    st.subheader("Danh mục dự án")
    all_projects = read_df("SELECT * FROM projects ORDER BY project_id")
    all_projects["Chênh lệch tiến độ (%)"] = all_projects["actual_progress"].fillna(0) - all_projects["planned_progress"].fillna(0)

    show_cols = ["project_id","project_name","project_type","location","budget","planned_progress","actual_progress","status","alert_level","Chênh lệch tiến độ (%)"]
    show = all_projects[show_cols].rename(columns=DISPLAY_PROJECT)
    st.dataframe(show, use_container_width=True, hide_index=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Số dự án", len(all_projects))
    c2.metric("Tổng ngân sách", money(all_projects["budget"].sum()))
    c3.metric("Đang thi công/vận hành", int(all_projects["status"].isin(["Đang thi công","Đang vận hành"]).sum()))
    c4.metric("Cảnh báo vàng/cam/đỏ", int(all_projects["alert_level"].isin(["Vàng","Cam","Đỏ"]).sum()))

    st.markdown("### Tạo dự án mới theo mẫu")
    with st.form("create_project"):
        a,b = st.columns(2)
        template_name = a.selectbox("Mẫu dự án", list(PROJECT_TEMPLATES.keys()))
        new_name = b.text_input("Tên dự án")
        c,d,e = st.columns(3)
        owner = c.text_input("Chủ đầu tư/Đơn vị")
        location = d.text_input("Địa điểm", value="Đắk Lắk")
        budget = e.number_input("Ngân sách", min_value=0.0, value=0.0, step=1_000_000.0)
        f,g = st.columns(2)
        start = f.date_input("Bắt đầu kế hoạch", value=date.today())
        finish = g.date_input("Kết thúc kế hoạch", value=date.today()+timedelta(days=60))
        custom_id = st.text_input("Mã dự án (để trống để hệ thống tự tạo)")
        submitted = st.form_submit_button("Tạo dự án và sinh khung công việc")

        if submitted:
            if not new_name.strip():
                st.error("Tên dự án là bắt buộc.")
            elif finish < start:
                st.error("Ngày kết thúc phải sau ngày bắt đầu.")
            else:
                prefix = PROJECT_TEMPLATES[template_name]["prefix"]
                project_id = custom_id.strip() or f"{prefix}-{datetime.now().strftime('%Y')}-{int(scalar('SELECT COUNT(*) FROM projects', default=0))+1:03d}"
                if int(scalar("SELECT COUNT(*) FROM projects WHERE project_id=?", (project_id,), 0)) > 0:
                    st.error("Mã dự án đã tồn tại.")
                else:
                    execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (project_id,new_name.strip(),template_name,owner,location,str(start),str(finish),budget,0,0,0,0,0,
                             "Chuẩn bị","Xanh","Tạo từ mẫu AI-KOS DeliveryOS V0.3"))
                    seed_project_tasks(project_id, template_name, start, finish)
                    st.success(f"Đã tạo {project_id} và sinh khung công việc từ mẫu “{template_name}”.")
                    st.rerun()

# 02. TỔNG QUAN
elif page == "02. Tổng quan":
    st.subheader(project["project_name"])
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Ngân sách", money(project["budget"]))
    c2.metric("Đã thanh toán", money(project["paid"]))
    c3.metric("Tiến độ thực tế", f"{float(project['actual_progress'] or 0):.0f}%",
              f"{float(project['actual_progress'] or 0)-float(project['planned_progress'] or 0):.0f} điểm %")
    c4.metric("Dự báo chi phí cuối kỳ", money(forecast), money(float(project["budget"] or 0)-forecast))

    st.progress(min(max(float(project["actual_progress"] or 0)/100, 0), 1))
    st.write(f"**Loại dự án:** {project['project_type']}  |  **Trạng thái:** {project['status']}  |  **Cảnh báo:** {project['alert_level']}")

    st.markdown("### Cảnh báo điều hành")
    for icon,title,msg in alert_rules(project, work, changes, costs):
        st.write(f"{icon} **{title}:** {msg}")

    left,right = st.columns(2)
    with left:
        st.markdown("### Công việc theo trạng thái")
        if work.empty:
            st.info("Chưa có công việc.")
        else:
            s = work.groupby("status").size()
            st.bar_chart(s)
            cols = ["work_id","work_group","work_name","planned_progress","actual_progress","status"]
            st.dataframe(work[cols].rename(columns=DISPLAY_WORK), use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Chi phí dự báo")
        if costs.empty:
            st.info("Chưa có dữ liệu chi phí.")
        else:
            st.bar_chart(costs.set_index("cost_group")["forecast_final"])
            st.dataframe(costs[["cost_group","planned_budget","actual_cost","forecast_final"]].rename(columns=DISPLAY_COST),
                         use_container_width=True, hide_index=True)

# 03. CÔNG VIỆC
elif page == "03. Công việc & tiến độ":
    st.subheader("Công việc & tiến độ")
    if work.empty:
        st.info("Dự án chưa có công việc.")
    else:
        show = work.copy()
        show["Chênh lệch tiến độ (%)"] = show["actual_progress"].fillna(0)-show["planned_progress"].fillna(0)
        cols = ["work_id","work_group","work_name","planned_start","planned_finish","planned_progress","actual_progress",
                "Chênh lệch tiến độ (%)","assignee","status","accepted","note"]
        st.dataframe(show[cols].rename(columns=DISPLAY_WORK), use_container_width=True, hide_index=True)

        st.markdown("### Cập nhật công việc")
        wid = st.selectbox("Mã công việc", work["work_id"].tolist())
        r = work[work["work_id"]==wid].iloc[0]
        a,b,c = st.columns(3)
        prog = a.number_input("Tiến độ thực tế (%)", 0.0, 100.0, float(r["actual_progress"] or 0), 1.0)
        status_opts = ["Chưa bắt đầu","Đang thực hiện","Chờ nghiệm thu","Hoàn thành"]
        status = b.selectbox("Trạng thái", status_opts,
                             index=status_opts.index(r["status"]) if r["status"] in status_opts else 0)
        assignee = c.text_input("Người/Tổ phụ trách", value=r["assignee"] or "")
        note = st.text_input("Ghi chú", value=r["note"] or "")
        if st.button("Lưu cập nhật công việc"):
            execute("UPDATE work_items SET actual_progress=?,status=?,assignee=?,note=? WHERE work_id=?",
                    (prog,status,assignee,note,wid))
            st.success("Đã lưu.")
            st.rerun()

# 04. CHI PHÍ
elif page == "04. Chi phí & dòng tiền":
    st.subheader("Chi phí & dòng tiền")
    budget = float(project["budget"] or 0)
    committed = float(costs["committed"].sum()) if not costs.empty else 0
    actual = float(costs["actual_cost"].sum()) if not costs.empty else 0
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    a,b,c,d = st.columns(4)
    a.metric("Ngân sách", money(budget))
    b.metric("Cam kết/Hợp đồng", money(committed))
    c.metric("Chi thực tế", money(actual))
    d.metric("Dự báo cuối kỳ", money(forecast), money(budget-forecast))

    if not costs.empty:
        show = costs.copy()
        show["Chênh lệch dự báo"] = show["forecast_final"]-show["planned_budget"]
        st.dataframe(show.rename(columns=DISPLAY_COST), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu chi phí.")

    payments = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date", (pid,))
    st.markdown("### Thanh toán")
    if payments.empty:
        st.info("Chưa có khoản thanh toán.")
    else:
        st.dataframe(payments.rename(columns={
            "payment_id":"Mã thanh toán","tranche":"Đợt","request_date":"Ngày đề nghị",
            "requested_value":"Giá trị đề nghị","approved_value":"Giá trị duyệt",
            "paid_value":"Đã thanh toán","status":"Trạng thái"
        }), use_container_width=True, hide_index=True)

# 05. NHẬT KÝ & HỒ SƠ
elif page == "05. Nhật ký & hồ sơ":
    st.subheader("Nhật ký & hồ sơ")
    logs = read_df("SELECT * FROM daily_logs WHERE project_id=? ORDER BY log_date DESC", (pid,))
    if not logs.empty:
        st.dataframe(logs.rename(columns={
            "log_date":"Ngày","work_name":"Công việc","team":"Tổ đội","workers":"Nhân công",
            "quantity_done":"Khối lượng","weather":"Thời tiết","issue":"Vấn đề/Sự cố","note":"Ghi chú"
        }), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có nhật ký.")

    st.markdown("### Thêm nhật ký")
    with st.form("new_log"):
        a,b,c = st.columns(3)
        log_date = a.date_input("Ngày", value=date.today())
        work_name = b.text_input("Công việc")
        team = c.text_input("Tổ đội")
        d,e,f = st.columns(3)
        workers = d.number_input("Nhân công", min_value=0, value=0)
        qty = e.text_input("Khối lượng thực hiện")
        weather = f.text_input("Thời tiết")
        issue = st.text_input("Vấn đề/Sự cố")
        note = st.text_area("Ghi chú")
        if st.form_submit_button("Lưu nhật ký"):
            lid = new_id("LOG","daily_logs","log_id")
            execute("INSERT INTO daily_logs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (lid,pid,str(log_date),work_name,team,int(workers),qty,weather,issue,"Đang thực hiện",note))
            st.success("Đã lưu nhật ký.")
            st.rerun()

    st.markdown("### Hồ sơ / Hình ảnh")
    uploaded = st.file_uploader("Tải tệp (MVP giới hạn 5 MB/tệp)", type=["jpg","jpeg","png","pdf","docx","xlsx"])
    if uploaded:
        size_mb = len(uploaded.getvalue())/(1024*1024)
        if size_mb > 5:
            st.error("Tệp lớn hơn 5 MB. V0.3 chỉ lưu tệp nhỏ trực tiếp trong CSDL.")
        else:
            a,b,c = st.columns(3)
            work_id = a.selectbox("Gắn với công việc", [""] + work["work_id"].tolist())
            category = b.selectbox("Loại hồ sơ", ["Ảnh hiện trường","Hợp đồng","Nghiệm thu","Thanh toán","Bản vẽ","Khác"])
            stage = c.selectbox("Giai đoạn", ["Trước","Trong khi thực hiện","Sau","Không áp dụng"])
            desc = st.text_input("Mô tả hồ sơ")
            uploader = st.text_input("Người tải")
            if st.button("Lưu hồ sơ"):
                aid = new_id("ATT","attachments","attachment_id")
                b64 = base64.b64encode(uploaded.getvalue()).decode("ascii")
                execute("INSERT INTO attachments VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (aid,pid,work_id,str(date.today()),category,stage,uploaded.name,uploaded.type,desc,uploader,b64))
                st.success("Đã lưu hồ sơ vào CSDL.")
                st.rerun()

    attachments = read_df("SELECT * FROM attachments WHERE project_id=? ORDER BY upload_date DESC", (pid,))
    if not attachments.empty:
        st.markdown("### Hồ sơ đã lưu")
        for _,r in attachments.iterrows():
            with st.expander(f"{r['category']} – {r['filename']} – {r['upload_date']}"):
                st.write(r["description"] or "")
                data = base64.b64decode(r["content_b64"])
                if str(r["mime_type"]).startswith("image/"):
                    st.image(data, width=600)
                st.download_button("Tải tệp", data=data, file_name=r["filename"], mime=r["mime_type"],
                                   key=f"dl_{r['attachment_id']}")

# 06. PHÁT SINH
elif page == "06. Phát sinh":
    st.subheader("Phát sinh")
    if not changes.empty:
        st.dataframe(changes.rename(columns={
            "change_id":"Mã phát sinh","work_id":"Mã việc","found_date":"Ngày phát hiện","change_type":"Loại",
            "description":"Nội dung","reason":"Nguyên nhân","proposed_value":"Giá trị đề xuất",
            "delay_days":"Ảnh hưởng tiến độ (ngày)","approval_status":"Trạng thái duyệt",
            "approved_value":"Giá trị duyệt","approved_by":"Người duyệt"
        }), use_container_width=True, hide_index=True)

    with st.form("new_change"):
        a,b,c = st.columns(3)
        wid = a.selectbox("Mã công việc", [""]+work["work_id"].tolist())
        ctype = b.selectbox("Loại phát sinh", ["Tăng khối lượng","Thay đổi vật liệu","Bổ sung công việc","Giảm trừ"])
        found = c.date_input("Ngày phát hiện", value=date.today())
        desc = st.text_input("Nội dung")
        reason = st.text_area("Nguyên nhân")
        d,e = st.columns(2)
        value = d.number_input("Giá trị đề xuất", min_value=0.0, value=0.0, step=100000.0)
        delay = e.number_input("Ảnh hưởng tiến độ (ngày)", min_value=0, value=0)
        if st.form_submit_button("Tạo phát sinh"):
            cid = new_id("CHG","changes","change_id")
            execute("INSERT INTO changes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid,pid,wid,str(found),ctype,desc,reason,value,int(delay),"Chờ duyệt",0,"",""))
            st.success("Đã tạo phát sinh ở trạng thái Chờ duyệt.")
            st.rerun()

    pending = changes[changes["approval_status"]=="Chờ duyệt"] if not changes.empty else pd.DataFrame()
    if not pending.empty:
        st.markdown("### Xử lý phát sinh chờ duyệt")
        cid = st.selectbox("Mã phát sinh", pending["change_id"].tolist())
        rr = pending[pending["change_id"]==cid].iloc[0]
        a,b = st.columns(2)
        approved_value = a.number_input("Giá trị được duyệt", min_value=0.0, value=float(rr["proposed_value"] or 0), step=100000.0)
        approved_by = b.text_input("Người duyệt")
        x,y = st.columns(2)
        if x.button("Duyệt"):
            execute("UPDATE changes SET approval_status='Đã duyệt',approved_value=?,approved_by=? WHERE change_id=?",
                    (approved_value,approved_by,cid))
            total = float(scalar("SELECT COALESCE(SUM(approved_value),0) FROM changes WHERE project_id=? AND approval_status='Đã duyệt'", (pid,), 0))
            execute("UPDATE projects SET approved_changes=? WHERE project_id=?", (total,pid))
            st.success("Đã duyệt phát sinh.")
            st.rerun()
        if y.button("Từ chối"):
            execute("UPDATE changes SET approval_status='Từ chối',approved_value=0,approved_by=? WHERE change_id=?",
                    (approved_by,cid))
            st.success("Đã từ chối.")
            st.rerun()

# 07. NGHIỆM THU & THANH TOÁN
elif page == "07. Nghiệm thu & thanh toán":
    st.subheader("Nghiệm thu & thanh toán")
    acc = read_df("SELECT * FROM acceptances WHERE project_id=? ORDER BY acceptance_date DESC", (pid,))
    pay = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date DESC", (pid,))
    a,b = st.columns(2)
    with a:
        st.markdown("### Nghiệm thu")
        st.dataframe(acc, use_container_width=True, hide_index=True)
    with b:
        st.markdown("### Thanh toán")
        st.dataframe(pay, use_container_width=True, hide_index=True)

    with st.form("new_acc"):
        a,b,c = st.columns(3)
        wid = a.selectbox("Mã công việc", work["work_id"].tolist() if not work.empty else [""])
        acc_date = b.date_input("Ngày nghiệm thu", value=date.today())
        value = c.number_input("Giá trị nghiệm thu", min_value=0.0, value=0.0, step=100000.0)
        qty = st.text_input("Khối lượng nghiệm thu")
        result = st.selectbox("Kết quả", ["Đạt","Đạt có điều kiện","Không đạt"])
        defects = st.text_area("Lỗi/tồn tại")
        correction_due = st.date_input("Hạn khắc phục", value=date.today()+timedelta(days=7))
        confirmed = st.text_input("Người xác nhận")
        if st.form_submit_button("Lưu nghiệm thu"):
            aid = new_id("ACC","acceptances","acceptance_id")
            execute("INSERT INTO acceptances VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (aid,pid,wid,str(acc_date),qty,value,result,defects,str(correction_due),confirmed,""))
            if result=="Đạt" and wid:
                execute("UPDATE work_items SET accepted='Có',status='Hoàn thành',actual_progress=100 WHERE work_id=?", (wid,))
            st.success("Đã lưu nghiệm thu.")
            st.rerun()

# 08. BẢO HÀNH
elif page == "08. Bảo hành & bảo trì":
    st.subheader("Bảo hành & bảo trì")
    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=? ORDER BY due_date", (pid,))
    st.dataframe(wm.rename(columns={
        "wm_id":"Mã","asset_item":"Hạng mục/Tài sản","wm_type":"Loại","start_date":"Bắt đầu",
        "due_date":"Đến hạn","contractor":"Đơn vị phụ trách","tracking_content":"Nội dung theo dõi",
        "status":"Trạng thái","cost":"Chi phí"
    }), use_container_width=True, hide_index=True)

    with st.form("new_wm"):
        a,b,c = st.columns(3)
        item = a.text_input("Hạng mục/Tài sản")
        wtype = b.selectbox("Loại", ["Bảo hành","Bảo trì"])
        due = c.date_input("Ngày đến hạn", value=date.today()+timedelta(days=30))
        contractor = st.text_input("Đơn vị/Nhà thầu phụ trách")
        tracking = st.text_area("Nội dung theo dõi")
        if st.form_submit_button("Tạo lịch"):
            wid = new_id("WM","warranty_maintenance","wm_id")
            execute("INSERT INTO warranty_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (wid,pid,item,wtype,str(date.today()),str(due),contractor,tracking,"Lên lịch",0,""))
            st.success("Đã thêm lịch.")
            st.rerun()

# 09. BÁO CÁO
elif page == "09. Báo cáo":
    st.subheader("Báo cáo dự án")
    st.write(f"**Dự án:** {project['project_name']}")
    st.write(f"**Mã dự án:** {pid}")
    st.write(f"**Ngân sách:** {money(project['budget'])}")
    st.write(f"**Tiến độ kế hoạch / thực tế:** {float(project['planned_progress'] or 0):.0f}% / {float(project['actual_progress'] or 0):.0f}%")

    st.markdown("### Cảnh báo")
    for icon,title,msg in alert_rules(project, work, changes, costs):
        st.write(f"{icon} **{title}:** {msg}")

    report_bytes = export_project_excel(pid)
    st.download_button(
        "Tải báo cáo Excel toàn bộ dự án",
        data=report_bytes,
        file_name=f"{pid}_Bao_cao_DeliveryOS_V0.3.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()
st.caption("AI-KOS DeliveryOS V0.3 | Dữ liệu demo công khai không chứa thông tin bí mật. Các phê duyệt tài chính, nghiệm thu và thanh toán phải do người có trách nhiệm xác nhận.")
