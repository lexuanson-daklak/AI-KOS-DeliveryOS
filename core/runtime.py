
import io
import base64
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "deliveryos.db"

st.set_page_config(
    page_title="AI-KOS DeliveryOS V0.4.2",
    page_icon="🏗️",
    layout="wide"
)

# =========================================================
# CSDL SQLITE
# =========================================================
def get_conn():
    return sqlite3.connect(DB_PATH)

def execute(sql, params=()):
    with get_conn() as con:
        con.execute(sql, params)
        con.commit()

def read_df(sql, params=()):
    with get_conn() as con:
        return pd.read_sql_query(sql, con, params=params)

def scalar(sql, params=(), default=0):
    df = read_df(sql, params)
    if df.empty:
        return default
    return df.iloc[0, 0]

def create_tables():
    schema = [
        """CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY, project_name TEXT, project_type TEXT, owner TEXT, location TEXT,
            planned_start TEXT, planned_finish TEXT, budget REAL DEFAULT 0, original_contract REAL DEFAULT 0,
            approved_changes REAL DEFAULT 0, paid REAL DEFAULT 0, planned_progress REAL DEFAULT 0,
            actual_progress REAL DEFAULT 0, status TEXT, alert_level TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS work_items (
            work_id TEXT PRIMARY KEY, project_id TEXT, work_group TEXT, work_name TEXT, unit TEXT,
            planned_qty REAL DEFAULT 0, planned_unit_price REAL DEFAULT 0, planned_value REAL DEFAULT 0,
            planned_start TEXT, planned_finish TEXT, planned_progress REAL DEFAULT 0, actual_progress REAL DEFAULT 0,
            assignee TEXT, status TEXT, accepted TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS costs (
            cost_id TEXT PRIMARY KEY, project_id TEXT, cost_group TEXT, description TEXT,
            planned_budget REAL DEFAULT 0, committed REAL DEFAULT 0, actual_cost REAL DEFAULT 0,
            forecast_final REAL DEFAULT 0, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS daily_logs (
            log_id TEXT PRIMARY KEY, project_id TEXT, log_date TEXT, work_name TEXT, team TEXT,
            workers INTEGER DEFAULT 0, quantity_done TEXT, weather TEXT, issue TEXT, status TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS changes (
            change_id TEXT PRIMARY KEY, project_id TEXT, work_id TEXT, found_date TEXT, change_type TEXT,
            description TEXT, reason TEXT, proposed_value REAL DEFAULT 0, delay_days INTEGER DEFAULT 0,
            approval_status TEXT, approved_value REAL DEFAULT 0, approved_by TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS acceptances (
            acceptance_id TEXT PRIMARY KEY, project_id TEXT, work_id TEXT, acceptance_date TEXT,
            accepted_quantity TEXT, accepted_value REAL DEFAULT 0, result TEXT, defects TEXT,
            correction_due TEXT, confirmed_by TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY, project_id TEXT, contract_id TEXT, tranche TEXT, request_date TEXT,
            requested_value REAL DEFAULT 0, approved_value REAL DEFAULT 0, paid_value REAL DEFAULT 0,
            payment_date TEXT, method TEXT, status TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS warranty_maintenance (
            wm_id TEXT PRIMARY KEY, project_id TEXT, asset_item TEXT, wm_type TEXT, start_date TEXT,
            due_date TEXT, contractor TEXT, tracking_content TEXT, status TEXT, cost REAL DEFAULT 0, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS attachments (
            attachment_id TEXT PRIMARY KEY, project_id TEXT, work_id TEXT, upload_date TEXT, category TEXT,
            stage TEXT, filename TEXT, mime_type TEXT, description TEXT, uploaded_by TEXT, content_b64 TEXT)""",
        """CREATE TABLE IF NOT EXISTS partners (
            partner_id TEXT PRIMARY KEY, partner_name TEXT, partner_type TEXT, representative TEXT,
            phone TEXT, email TEXT, address TEXT, tax_code TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS contracts (
            contract_id TEXT PRIMARY KEY, project_id TEXT, partner_id TEXT, contract_name TEXT,
            contract_value REAL DEFAULT 0, advance_value REAL DEFAULT 0, signed_date TEXT,
            start_date TEXT, finish_date TEXT, warranty_months INTEGER DEFAULT 0, status TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS materials (
            material_id TEXT PRIMARY KEY, project_id TEXT, material_name TEXT, unit TEXT,
            planned_qty REAL DEFAULT 0, purchased_qty REAL DEFAULT 0, used_qty REAL DEFAULT 0,
            unit_price REAL DEFAULT 0, supplier TEXT, note TEXT)""",
        """CREATE TABLE IF NOT EXISTS labour_logs (
            labour_id TEXT PRIMARY KEY, project_id TEXT, work_id TEXT, work_date TEXT, team TEXT,
            workers INTEGER DEFAULT 0, workdays REAL DEFAULT 0, unit_cost REAL DEFAULT 0,
            description TEXT, note TEXT)"""
    ]
    with get_conn() as con:
        for stmt in schema:
            con.execute(stmt)
        con.commit()

create_tables()

# =========================================================
# MẪU DỰ ÁN
# =========================================================
PROJECT_TEMPLATES = {
    "Xây nhà phố": [
        ("Chuẩn bị", "Khảo sát hiện trạng, yêu cầu và mặt bằng"),
        ("Thiết kế", "Hoàn thiện thiết kế và hồ sơ"),
        ("Phần thô", "Móng, kết cấu, xây tô"),
        ("Điện nước", "Thi công điện, nước và hệ thống kỹ thuật"),
        ("Hoàn thiện", "Ốp lát, sơn, cửa, thiết bị"),
        ("Bàn giao", "Nghiệm thu, thanh toán, bảo hành"),
    ],
    "Sửa chữa/cải tạo nhà": [
        ("Khảo sát", "Khảo sát hiện trạng và chụp ảnh"),
        ("Tháo dỡ", "Tháo dỡ hạng mục cũ/hư hỏng"),
        ("Kết cấu", "Sửa chữa/gia cường kết cấu"),
        ("Điện nước", "Sửa chữa điện nước"),
        ("Hoàn thiện", "Chống thấm, sơn, ốp lát, cửa"),
        ("Bàn giao", "Nghiệm thu, thanh toán, bảo hành"),
    ],
    "Xây dựng công trình": [
        ("Chuẩn bị", "Bàn giao mặt bằng, chuẩn bị thi công"),
        ("Nền móng", "Thi công nền, móng"),
        ("Kết cấu", "Thi công kết cấu chính"),
        ("Hệ thống kỹ thuật", "Thi công MEP/hạ tầng"),
        ("Hoàn thiện", "Hoàn thiện công trình"),
        ("Bàn giao", "Nghiệm thu, thanh toán, bàn giao"),
    ],
    "Cải tạo mặt bằng/đất": [
        ("Khảo sát", "Khảo sát cao độ, ranh giới, hiện trạng"),
        ("Chuẩn bị", "Dọn dẹp và chuẩn bị mặt bằng"),
        ("Đào đắp", "Đào, đắp và san nền"),
        ("Thoát nước", "Tổ chức thoát nước"),
        ("Hoàn thiện", "Lu lèn, chỉnh cao độ, nghiệm thu"),
        ("Theo dõi", "Theo dõi lún/sạt sau hoàn thành"),
    ],
    "Quản lý xưởng cơ khí": [
        ("Đơn hàng", "Tiếp nhận yêu cầu và báo giá"),
        ("Kế hoạch", "Lập lệnh sản xuất và kế hoạch vật tư"),
        ("Vật tư", "Mua/nhập/xuất vật tư"),
        ("Gia công", "Cắt, hàn, gia công, lắp ráp"),
        ("Kiểm tra", "Kiểm tra chất lượng"),
        ("Giao hàng", "Bàn giao, thanh toán, bảo hành"),
    ],
}

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
        if x is None or str(x).strip() == "":
            return ""
        return pd.to_datetime(x).strftime("%d/%m/%Y")
    except Exception:
        return str(x or "")

def fmt_money_columns(df, cols):
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].apply(money)
    return out

def fmt_date_columns(df, cols):
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].apply(vi_date)
    return out

def new_id(prefix, table, col):
    stamp = datetime.now().strftime("%Y%m%d")
    n = int(scalar(f"SELECT COUNT(*) FROM {table} WHERE {col} LIKE ?", (f"{prefix}-{stamp}-%",), 0)) + 1
    return f"{prefix}-{stamp}-{n:03d}"

def project_map():
    df = read_df("SELECT project_id, project_name FROM projects ORDER BY project_id")
    return {r["project_id"]: r["project_name"] for _, r in df.iterrows()}

def seed_tasks(project_id, template, start, finish):
    groups = PROJECT_TEMPLATES[template]
    total_days = max((finish - start).days, len(groups))
    step = max(total_days // len(groups), 1)
    for i, (grp, name) in enumerate(groups, start=1):
        s = start + timedelta(days=(i-1)*step)
        e = min(start + timedelta(days=i*step-1), finish)
        wid = f"{project_id}-W{i:02d}"
        execute(
            "INSERT INTO work_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (wid,project_id,grp,name,"gói",1,0,0,str(s),str(e),0,0,"","Chưa bắt đầu","Không",
             "Sinh tự động từ mẫu dự án V0.4.2")
        )

def project_data(pid):
    p = read_df("SELECT * FROM projects WHERE project_id=?", (pid,))
    w = read_df("SELECT * FROM work_items WHERE project_id=? ORDER BY planned_start", (pid,))
    c = read_df("SELECT * FROM costs WHERE project_id=?", (pid,))
    ch = read_df("SELECT * FROM changes WHERE project_id=? ORDER BY found_date DESC", (pid,))
    return p.iloc[0], w, c, ch

def alerts(project, work, changes, costs):
    out = []
    gap = float(project["actual_progress"] or 0) - float(project["planned_progress"] or 0)
    budget = float(project["budget"] or 0)
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0

    if gap <= -10:
        out.append(("🔴","Tiến độ",f"Tiến độ thực tế thấp hơn kế hoạch {abs(gap):.0f} điểm %."))
    elif gap < 0:
        out.append(("🟡","Tiến độ",f"Tiến độ thực tế thấp hơn kế hoạch {abs(gap):.0f} điểm %."))

    if budget > 0 and forecast > budget:
        out.append(("🔴","Chi phí",f"Dự báo vượt ngân sách {money(forecast-budget)}."))
    elif budget > 0 and forecast > budget*0.95:
        out.append(("🟡","Chi phí","Dự báo cuối kỳ đã vượt 95% ngân sách."))

    if not work.empty:
        due = pd.to_datetime(work["planned_finish"], errors="coerce")
        overdue = work[(work["status"]!="Hoàn thành") & (due < pd.Timestamp.today().normalize())]
        if len(overdue):
            out.append(("🟠","Công việc",f"Có {len(overdue)} công việc quá hạn."))

    if not changes.empty:
        pending = changes[changes["approval_status"]=="Chờ duyệt"]
        if len(pending):
            out.append(("🟡","Phát sinh",f"Có {len(pending)} phát sinh chờ duyệt, tổng {money(pending['proposed_value'].sum())}."))

    if not out:
        out.append(("🟢","Tổng thể","Chưa có cảnh báo đáng kể."))
    return out

def today_tasks(pid=None):
    cond = " WHERE project_id=?" if pid else ""
    params = (pid,) if pid else ()
    today = pd.Timestamp.today().normalize()
    d7 = today + pd.Timedelta(days=7)
    d30 = today + pd.Timedelta(days=30)
    rows = []

    w = read_df(f"SELECT * FROM work_items{cond}", params)
    if not w.empty:
        due = pd.to_datetime(w["planned_finish"], errors="coerce")
        for _, r in w[(w["status"]!="Hoàn thành") & (due < today)].iterrows():
            rows.append(("🔴","Quá hạn",r["project_id"],r["work_name"],f"Hạn {vi_date(r['planned_finish'])}"))
        for _, r in w[(w["status"]!="Hoàn thành") & (due >= today) & (due <= d7)].iterrows():
            rows.append(("🟡","Sắp đến hạn",r["project_id"],r["work_name"],f"Hạn {vi_date(r['planned_finish'])}"))

    ch = read_df(f"SELECT * FROM changes{cond}", params)
    if not ch.empty:
        for _, r in ch[ch["approval_status"]=="Chờ duyệt"].iterrows():
            rows.append(("🟡","Chờ duyệt",r["project_id"],r["description"],money(r["proposed_value"])))

    pay = read_df(f"SELECT * FROM payments{cond}", params)
    if not pay.empty:
        p = pay[pay["paid_value"].fillna(0) < pay["approved_value"].fillna(0)]
        for _, r in p.iterrows():
            remain = float(r["approved_value"] or 0)-float(r["paid_value"] or 0)
            rows.append(("🟡","Chờ thanh toán",r["project_id"],r["tranche"],money(remain)))

    wm = read_df(f"SELECT * FROM warranty_maintenance{cond}", params)
    if not wm.empty:
        due = pd.to_datetime(wm["due_date"], errors="coerce")
        for _, r in wm[(wm["status"]!="Hoàn thành") & (due >= today) & (due <= d30)].iterrows():
            rows.append(("🔵",r["wm_type"],r["project_id"],r["asset_item"],f"Đến hạn {vi_date(r['due_date'])}"))

    return pd.DataFrame(rows, columns=["Mức","Loại việc","Mã dự án","Nội dung","Thông tin"])

def export_project_excel(pid):
    output = io.BytesIO()
    data = {
        "Du_an": read_df("SELECT * FROM projects WHERE project_id=?", (pid,)),
        "Cong_viec": read_df("SELECT * FROM work_items WHERE project_id=?", (pid,)),
        "Hop_dong": read_df("SELECT * FROM contracts WHERE project_id=?", (pid,)),
        "Vat_tu": read_df("SELECT * FROM materials WHERE project_id=?", (pid,)),
        "Nhan_cong": read_df("SELECT * FROM labour_logs WHERE project_id=?", (pid,)),
        "Chi_phi": read_df("SELECT * FROM costs WHERE project_id=?", (pid,)),
        "Nhat_ky": read_df("SELECT * FROM daily_logs WHERE project_id=?", (pid,)),
        "Phat_sinh": read_df("SELECT * FROM changes WHERE project_id=?", (pid,)),
        "Nghiem_thu": read_df("SELECT * FROM acceptances WHERE project_id=?", (pid,)),
        "Thanh_toan": read_df("SELECT * FROM payments WHERE project_id=?", (pid,)),
        "Bao_hanh_Bao_tri": read_df("SELECT * FROM warranty_maintenance WHERE project_id=?", (pid,)),
    }
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in data.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    output.seek(0)
    return output.getvalue()

def export_portfolio_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        read_df("SELECT * FROM projects ORDER BY project_id").to_excel(writer, sheet_name="Danh_muc_du_an", index=False)
        read_df("SELECT * FROM work_items ORDER BY project_id, planned_start").to_excel(writer, sheet_name="Cong_viec", index=False)
        read_df("SELECT * FROM contracts ORDER BY project_id").to_excel(writer, sheet_name="Hop_dong", index=False)
        read_df("SELECT * FROM changes ORDER BY project_id").to_excel(writer, sheet_name="Phat_sinh", index=False)
    output.seek(0)
    return output.getvalue()

# =========================================================
# GIAO DIỆN
# =========================================================
