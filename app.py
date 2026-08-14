
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
DB_PATH = DATA_DIR / "deliveryos.db"

st.set_page_config(
    page_title="AI-KOS DeliveryOS V0.4",
    page_icon="🏗️",
    layout="wide"
)

# =========================================================
# CSDL SQLITE – ĐƠN GIẢN, KHÔNG CẦN NGUỒN DỮ LIỆU BÊN NGOÀI
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
        """,
        """
        CREATE TABLE IF NOT EXISTS partners (
            partner_id TEXT PRIMARY KEY,
            partner_name TEXT,
            partner_type TEXT,
            representative TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            tax_code TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id TEXT PRIMARY KEY,
            project_id TEXT,
            partner_id TEXT,
            contract_name TEXT,
            contract_value REAL DEFAULT 0,
            advance_value REAL DEFAULT 0,
            signed_date TEXT,
            start_date TEXT,
            finish_date TEXT,
            warranty_months INTEGER DEFAULT 0,
            status TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS materials (
            material_id TEXT PRIMARY KEY,
            project_id TEXT,
            material_name TEXT,
            unit TEXT,
            planned_qty REAL DEFAULT 0,
            purchased_qty REAL DEFAULT 0,
            used_qty REAL DEFAULT 0,
            unit_price REAL DEFAULT 0,
            supplier TEXT,
            note TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS labour_logs (
            labour_id TEXT PRIMARY KEY,
            project_id TEXT,
            work_id TEXT,
            work_date TEXT,
            team TEXT,
            workers INTEGER DEFAULT 0,
            workdays REAL DEFAULT 0,
            unit_cost REAL DEFAULT 0,
            description TEXT,
            note TEXT
        )
        """
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
            """INSERT INTO work_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (wid,project_id,grp,name,"gói",1,0,0,str(s),str(e),0,0,"","Chưa bắt đầu","Không",
             "Sinh tự động từ mẫu dự án V0.4")
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
st.sidebar.title("AI-KOS DeliveryOS")
st.sidebar.caption("Quản trị thực hiện dự án, công trình và vận hành tài sản")

pages = [
    "00. Hôm nay cần làm gì?",
    "01. Danh mục dự án",
    "02. Hồ sơ dự án",
    "03. Tổng quan",
    "04. Công việc & tiến độ",
    "05. Hợp đồng & đối tác",
    "06. Vật tư & nhân công",
    "07. Chi phí & dòng tiền",
    "08. Nhật ký & hồ sơ",
    "09. Phát sinh",
    "10. Nghiệm thu & thanh toán",
    "11. Bảo hành & bảo trì",
    "12. Báo cáo & sao lưu",
]
page = st.sidebar.radio("Chức năng", pages)

projects = project_map()
if not projects:
    st.error("Chưa có dự án. Hãy tạo dự án ở mục 01. Danh mục dự án.")
    st.stop()

pid = st.sidebar.selectbox("Dự án", list(projects.keys()), format_func=lambda x: f"{x} – {projects[x]}")
project, work, costs, changes = project_data(pid)

st.title("AI-KOS DeliveryOS V0.4")
st.caption("V0.4 – Dùng SQLite đơn giản | Có sao lưu/khôi phục dữ liệu | AI chỉ phân tích/cảnh báo, không tự sửa số liệu gốc.")

# 00
if page == "00. Hôm nay cần làm gì?":
    st.subheader("Hôm nay cần làm gì?")
    scope = st.radio("Phạm vi", ["Tất cả dự án","Dự án đang chọn"], horizontal=True)
    todo = today_tasks(pid if scope=="Dự án đang chọn" else None)
    a,b,c,d = st.columns(4)
    a.metric("Tổng việc cần chú ý",len(todo))
    b.metric("Quá hạn",int((todo["Loại việc"]=="Quá hạn").sum()) if not todo.empty else 0)
    c.metric("Chờ duyệt/thanh toán",int(todo["Loại việc"].isin(["Chờ duyệt","Chờ thanh toán"]).sum()) if not todo.empty else 0)
    d.metric("Bảo hành/bảo trì sắp đến hạn",int(todo["Loại việc"].isin(["Bảo hành","Bảo trì"]).sum()) if not todo.empty else 0)
    if todo.empty:
        st.success("Không có việc khẩn cấp hoặc sắp đến hạn.")
    else:
        st.dataframe(todo, use_container_width=True, hide_index=True)

# 01
elif page == "01. Danh mục dự án":
    st.subheader("Danh mục dự án")
    allp = read_df("SELECT * FROM projects ORDER BY project_id")
    allp["Chênh lệch tiến độ (%)"] = allp["actual_progress"].fillna(0)-allp["planned_progress"].fillna(0)
    show = allp.rename(columns={
        "project_id":"Mã dự án","project_name":"Tên dự án","project_type":"Loại dự án","owner":"Chủ đầu tư/Đơn vị",
        "location":"Địa điểm","budget":"Ngân sách","planned_progress":"Tiến độ KH (%)",
        "actual_progress":"Tiến độ TT (%)","status":"Trạng thái","alert_level":"Cảnh báo"
    })
    st.dataframe(show[["Mã dự án","Tên dự án","Loại dự án","Địa điểm","Ngân sách","Tiến độ KH (%)","Tiến độ TT (%)","Trạng thái","Cảnh báo","Chênh lệch tiến độ (%)"]],
                 use_container_width=True, hide_index=True)

    st.markdown("### Tạo dự án mới theo mẫu")
    with st.form("create_project"):
        a,b = st.columns(2)
        template = a.selectbox("Mẫu dự án",list(PROJECT_TEMPLATES.keys()))
        name = b.text_input("Tên dự án")
        c,d,e = st.columns(3)
        owner = c.text_input("Chủ đầu tư/Đơn vị")
        location = d.text_input("Địa điểm",value="Đắk Lắk")
        budget = e.number_input("Ngân sách",min_value=0.0,value=0.0,step=1_000_000.0)
        f,g = st.columns(2)
        start = f.date_input("Bắt đầu kế hoạch",value=date.today())
        finish = g.date_input("Kết thúc kế hoạch",value=date.today()+timedelta(days=60))
        custom_id = st.text_input("Mã dự án (để trống để hệ thống tự tạo)")
        if st.form_submit_button("Tạo dự án và sinh khung công việc"):
            if not name.strip():
                st.error("Tên dự án là bắt buộc.")
            elif finish < start:
                st.error("Ngày kết thúc phải sau ngày bắt đầu.")
            else:
                prefix_map = {"Xây nhà phố":"HOUSE","Sửa chữa/cải tạo nhà":"REPAIR","Xây dựng công trình":"CONST","Cải tạo mặt bằng/đất":"LAND","Quản lý xưởng cơ khí":"WORKSHOP"}
                project_id = custom_id.strip() or f"{prefix_map[template]}-{datetime.now().strftime('%Y')}-{int(scalar('SELECT COUNT(*) FROM projects',default=0))+1:03d}"
                if int(scalar("SELECT COUNT(*) FROM projects WHERE project_id=?",(project_id,),0)):
                    st.error("Mã dự án đã tồn tại.")
                else:
                    execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (project_id,name.strip(),template,owner,location,str(start),str(finish),budget,0,0,0,0,0,"Chuẩn bị","Xanh","Tạo từ V0.4"))
                    seed_tasks(project_id,template,start,finish)
                    st.success(f"Đã tạo {project_id}.")
                    st.rerun()

# 02
elif page == "02. Hồ sơ dự án":
    st.subheader("Hồ sơ dự án")
    st.write(f"**Mã dự án:** `{pid}`")
    with st.form("edit_project"):
        a,b = st.columns(2)
        pname = a.text_input("Tên dự án",value=project["project_name"] or "")
        ptype = b.selectbox("Loại dự án",list(PROJECT_TEMPLATES.keys())+["Khác"],
                            index=(list(PROJECT_TEMPLATES.keys())+["Khác"]).index(project["project_type"]) if project["project_type"] in list(PROJECT_TEMPLATES.keys())+["Khác"] else len(PROJECT_TEMPLATES))
        c,d = st.columns(2)
        owner = c.text_input("Chủ đầu tư/Đơn vị",value=project["owner"] or "")
        location = d.text_input("Địa điểm",value=project["location"] or "")
        e,f,g = st.columns(3)
        budget = e.number_input("Ngân sách",min_value=0.0,value=float(project["budget"] or 0),step=1_000_000.0)
        planned = f.number_input("Tiến độ kế hoạch (%)",0.0,100.0,float(project["planned_progress"] or 0),1.0)
        actual = g.number_input("Tiến độ thực tế (%)",0.0,100.0,float(project["actual_progress"] or 0),1.0)
        h,i = st.columns(2)
        status_opts = ["Chuẩn bị","Đang thi công","Đang vận hành","Tạm dừng","Hoàn thành"]
        status = h.selectbox("Trạng thái",status_opts,index=status_opts.index(project["status"]) if project["status"] in status_opts else 0)
        alert_opts = ["Xanh","Vàng","Cam","Đỏ"]
        alert = i.selectbox("Cảnh báo",alert_opts,index=alert_opts.index(project["alert_level"]) if project["alert_level"] in alert_opts else 0)
        note = st.text_area("Ghi chú",value=project["note"] or "")
        if st.form_submit_button("Lưu hồ sơ dự án"):
            execute("""UPDATE projects SET project_name=?,project_type=?,owner=?,location=?,budget=?,
                       planned_progress=?,actual_progress=?,status=?,alert_level=?,note=? WHERE project_id=?""",
                    (pname,ptype,owner,location,budget,planned,actual,status,alert,note,pid))
            st.success("Đã cập nhật hồ sơ.")
            st.rerun()

# 03
elif page == "03. Tổng quan":
    st.subheader(project["project_name"])
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    a,b,c,d = st.columns(4)
    a.metric("Ngân sách",money(project["budget"]))
    b.metric("Đã thanh toán",money(project["paid"]))
    c.metric("Tiến độ thực tế",f"{float(project['actual_progress'] or 0):.0f}%",
             f"{float(project['actual_progress'] or 0)-float(project['planned_progress'] or 0):.0f} điểm %")
    d.metric("Dự báo cuối kỳ",money(forecast),money(float(project["budget"] or 0)-forecast))
    st.progress(min(max(float(project["actual_progress"] or 0)/100,0),1))
    st.markdown("### Cảnh báo điều hành")
    for icon,title,msg in alerts(project,work,changes,costs):
        st.write(f"{icon} **{title}:** {msg}")

# 04
elif page == "04. Công việc & tiến độ":
    st.subheader("Công việc & tiến độ")
    if work.empty:
        st.info("Chưa có công việc.")
    else:
        wshow = work.copy()
        wshow["Chênh lệch (%)"] = wshow["actual_progress"].fillna(0)-wshow["planned_progress"].fillna(0)
        st.dataframe(wshow.rename(columns={
            "work_id":"Mã việc","work_group":"Nhóm việc","work_name":"Công việc","planned_start":"Bắt đầu KH",
            "planned_finish":"Kết thúc KH","planned_progress":"Tiến độ KH (%)","actual_progress":"Tiến độ TT (%)",
            "assignee":"Phụ trách","status":"Trạng thái","accepted":"Đã nghiệm thu","note":"Ghi chú"
        }),use_container_width=True,hide_index=True)
        wid = st.selectbox("Chọn công việc để cập nhật",work["work_id"].tolist())
        r = work[work["work_id"]==wid].iloc[0]
        a,b,c = st.columns(3)
        prog = a.number_input("Tiến độ thực tế (%)",0.0,100.0,float(r["actual_progress"] or 0),1.0)
        states = ["Chưa bắt đầu","Đang thực hiện","Chờ nghiệm thu","Hoàn thành"]
        state = b.selectbox("Trạng thái",states,index=states.index(r["status"]) if r["status"] in states else 0)
        assignee = c.text_input("Người/Tổ phụ trách",value=r["assignee"] or "")
        note = st.text_input("Ghi chú",value=r["note"] or "")
        if st.button("Lưu cập nhật công việc"):
            execute("UPDATE work_items SET actual_progress=?,status=?,assignee=?,note=? WHERE work_id=?",(prog,state,assignee,note,wid))
            st.success("Đã lưu.")
            st.rerun()

# 05
elif page == "05. Hợp đồng & đối tác":
    st.subheader("Hợp đồng & đối tác")
    partners = read_df("SELECT * FROM partners ORDER BY partner_name")
    contracts = read_df("SELECT * FROM contracts WHERE project_id=? ORDER BY signed_date DESC",(pid,))
    a,b = st.columns(2)
    with a:
        st.markdown("### Đối tác / Nhà thầu")
        st.dataframe(partners.rename(columns={"partner_id":"Mã","partner_name":"Tên đơn vị","partner_type":"Loại","representative":"Đại diện","phone":"Điện thoại","email":"Email"}),use_container_width=True,hide_index=True)
        with st.form("new_partner"):
            pname = st.text_input("Tên đối tác/Nhà thầu")
            ptype = st.selectbox("Loại",["Nhà thầu","Tổ đội","Nhà cung cấp","Tư vấn","Khác"])
            rep = st.text_input("Người đại diện")
            phone = st.text_input("Điện thoại")
            email = st.text_input("Email")
            address = st.text_input("Địa chỉ")
            tax = st.text_input("Mã số thuế")
            note = st.text_input("Ghi chú")
            if st.form_submit_button("Thêm đối tác"):
                if pname.strip():
                    partner_id = new_id("PT","partners","partner_id")
                    execute("INSERT INTO partners VALUES (?,?,?,?,?,?,?,?,?)",(partner_id,pname,ptype,rep,phone,email,address,tax,note))
                    st.success("Đã thêm đối tác.")
                    st.rerun()
    with b:
        st.markdown("### Hợp đồng của dự án")
        st.dataframe(contracts.rename(columns={
            "contract_id":"Mã HĐ","partner_id":"Mã đối tác","contract_name":"Tên hợp đồng","contract_value":"Giá trị HĐ",
            "advance_value":"Tạm ứng","signed_date":"Ngày ký","finish_date":"Ngày kết thúc","warranty_months":"Bảo hành (tháng)","status":"Trạng thái"
        }),use_container_width=True,hide_index=True)
        with st.form("new_contract"):
            partner_options = [""] + partners["partner_id"].tolist()
            partner = st.selectbox("Đối tác",partner_options,format_func=lambda x: x if not x else f"{x} – {partners.loc[partners['partner_id']==x,'partner_name'].iloc[0]}")
            cname = st.text_input("Tên/Nội dung hợp đồng")
            c1,c2 = st.columns(2)
            value = c1.number_input("Giá trị hợp đồng",min_value=0.0,value=0.0,step=1_000_000.0)
            advance = c2.number_input("Tạm ứng",min_value=0.0,value=0.0,step=1_000_000.0)
            c3,c4,c5 = st.columns(3)
            signed = c3.date_input("Ngày ký",value=date.today())
            start = c4.date_input("Bắt đầu",value=date.today())
            finish = c5.date_input("Kết thúc",value=date.today()+timedelta(days=60))
            warranty = st.number_input("Bảo hành (tháng)",min_value=0,value=12)
            if st.form_submit_button("Thêm hợp đồng"):
                cid = new_id("HD","contracts","contract_id")
                execute("INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (cid,pid,partner,cname,value,advance,str(signed),str(start),str(finish),int(warranty),"Đang thực hiện",""))
                st.success("Đã thêm hợp đồng.")
                st.rerun()

# 06
elif page == "06. Vật tư & nhân công":
    st.subheader("Vật tư & nhân công")
    mats = read_df("SELECT * FROM materials WHERE project_id=? ORDER BY material_name",(pid,))
    labs = read_df("SELECT * FROM labour_logs WHERE project_id=? ORDER BY work_date DESC",(pid,))
    a,b = st.columns(2)
    with a:
        st.markdown("### Vật tư")
        if not mats.empty:
            m = mats.copy()
            m["Tồn"] = m["purchased_qty"].fillna(0)-m["used_qty"].fillna(0)
            m["Giá trị đã mua"] = m["purchased_qty"].fillna(0)*m["unit_price"].fillna(0)
            st.dataframe(m.rename(columns={"material_id":"Mã","material_name":"Vật tư","unit":"ĐVT","planned_qty":"KH","purchased_qty":"Đã mua","used_qty":"Đã dùng","unit_price":"Đơn giá","supplier":"Nhà cung cấp"}),use_container_width=True,hide_index=True)
        with st.form("new_material"):
            name = st.text_input("Tên vật tư")
            c1,c2,c3 = st.columns(3)
            unit = c1.text_input("ĐVT")
            planned = c2.number_input("Khối lượng KH",min_value=0.0,value=0.0)
            purchased = c3.number_input("Đã mua",min_value=0.0,value=0.0)
            c4,c5 = st.columns(2)
            used = c4.number_input("Đã sử dụng",min_value=0.0,value=0.0)
            price = c5.number_input("Đơn giá",min_value=0.0,value=0.0,step=1000.0)
            supplier = st.text_input("Nhà cung cấp")
            if st.form_submit_button("Thêm vật tư"):
                mid = new_id("MAT","materials","material_id")
                execute("INSERT INTO materials VALUES (?,?,?,?,?,?,?,?,?,?)",(mid,pid,name,unit,planned,purchased,used,price,supplier,""))
                st.success("Đã thêm vật tư.")
                st.rerun()
    with b:
        st.markdown("### Nhân công")
        if not labs.empty:
            l = labs.copy()
            l["Thành tiền"] = l["workdays"].fillna(0)*l["unit_cost"].fillna(0)
            st.dataframe(l.rename(columns={"labour_id":"Mã","work_id":"Mã việc","work_date":"Ngày","team":"Tổ đội","workers":"Số người","workdays":"Số công","unit_cost":"Đơn giá/công","description":"Nội dung"}),use_container_width=True,hide_index=True)
        with st.form("new_labour"):
            wid = st.selectbox("Mã công việc",[""]+work["work_id"].tolist())
            c1,c2 = st.columns(2)
            wdate = c1.date_input("Ngày",value=date.today())
            team = c2.text_input("Tổ đội")
            c3,c4,c5 = st.columns(3)
            workers = c3.number_input("Số người",min_value=0,value=0)
            workdays = c4.number_input("Số công",min_value=0.0,value=0.0)
            unit_cost = c5.number_input("Đơn giá/công",min_value=0.0,value=0.0,step=10000.0)
            desc = st.text_input("Nội dung")
            if st.form_submit_button("Thêm nhật ký nhân công"):
                lid = new_id("LAB","labour_logs","labour_id")
                execute("INSERT INTO labour_logs VALUES (?,?,?,?,?,?,?,?,?,?)",(lid,pid,wid,str(wdate),team,int(workers),workdays,unit_cost,desc,""))
                st.success("Đã thêm nhân công.")
                st.rerun()

# 07
elif page == "07. Chi phí & dòng tiền":
    st.subheader("Chi phí & dòng tiền")
    budget = float(project["budget"] or 0)
    committed = float(costs["committed"].sum()) if not costs.empty else 0
    actual = float(costs["actual_cost"].sum()) if not costs.empty else 0
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    a,b,c,d = st.columns(4)
    a.metric("Ngân sách",money(budget)); b.metric("Cam kết/Hợp đồng",money(committed)); c.metric("Chi thực tế",money(actual)); d.metric("Dự báo cuối kỳ",money(forecast),money(budget-forecast))
    if not costs.empty:
        st.dataframe(costs.rename(columns={"cost_group":"Nhóm chi phí","description":"Nội dung","planned_budget":"Ngân sách KH","committed":"Cam kết","actual_cost":"Chi thực tế","forecast_final":"Dự báo cuối kỳ"}),use_container_width=True,hide_index=True)

# 08
elif page == "08. Nhật ký & hồ sơ":
    st.subheader("Nhật ký & hồ sơ")
    logs = read_df("SELECT * FROM daily_logs WHERE project_id=? ORDER BY log_date DESC",(pid,))
    if not logs.empty:
        st.dataframe(logs.rename(columns={"log_date":"Ngày","work_name":"Công việc","team":"Tổ đội","workers":"Nhân công","quantity_done":"Khối lượng","weather":"Thời tiết","issue":"Vấn đề/Sự cố","note":"Ghi chú"}),use_container_width=True,hide_index=True)
    with st.form("new_log"):
        c1,c2,c3 = st.columns(3)
        log_date = c1.date_input("Ngày",value=date.today())
        work_name = c2.text_input("Công việc")
        team = c3.text_input("Tổ đội")
        workers = st.number_input("Nhân công",min_value=0,value=0)
        qty = st.text_input("Khối lượng thực hiện")
        issue = st.text_input("Vấn đề/Sự cố")
        note = st.text_area("Ghi chú")
        if st.form_submit_button("Lưu nhật ký"):
            lid = new_id("LOG","daily_logs","log_id")
            execute("INSERT INTO daily_logs VALUES (?,?,?,?,?,?,?,?,?,?,?)",(lid,pid,str(log_date),work_name,team,int(workers),qty,"",issue,"Đang thực hiện",note))
            st.success("Đã lưu.")
            st.rerun()

    uploaded = st.file_uploader("Tải hồ sơ/ảnh (tối đa 5 MB)",type=["jpg","jpeg","png","pdf","docx","xlsx"])
    if uploaded:
        size = len(uploaded.getvalue())/(1024*1024)
        if size > 5:
            st.error("Tệp lớn hơn 5 MB.")
        else:
            category = st.selectbox("Loại hồ sơ",["Ảnh hiện trường","Hợp đồng","Nghiệm thu","Thanh toán","Bản vẽ","Khác"])
            desc = st.text_input("Mô tả")
            if st.button("Lưu hồ sơ"):
                aid = new_id("ATT","attachments","attachment_id")
                content = base64.b64encode(uploaded.getvalue()).decode("ascii")
                execute("INSERT INTO attachments VALUES (?,?,?,?,?,?,?,?,?,?,?)",(aid,pid,"",str(date.today()),category,"",uploaded.name,uploaded.type,desc,"",content))
                st.success("Đã lưu hồ sơ.")
                st.rerun()

# 09
elif page == "09. Phát sinh":
    st.subheader("Phát sinh")
    if not changes.empty:
        st.dataframe(changes.rename(columns={"change_id":"Mã phát sinh","work_id":"Mã việc","found_date":"Ngày","change_type":"Loại","description":"Nội dung","reason":"Nguyên nhân","proposed_value":"Giá trị đề xuất","approval_status":"Trạng thái duyệt","approved_value":"Giá trị duyệt"}),use_container_width=True,hide_index=True)
    with st.form("new_change"):
        wid = st.selectbox("Mã công việc",[""]+work["work_id"].tolist())
        ctype = st.selectbox("Loại",["Tăng khối lượng","Thay đổi vật liệu","Bổ sung công việc","Giảm trừ"])
        desc = st.text_input("Nội dung")
        reason = st.text_area("Nguyên nhân")
        value = st.number_input("Giá trị đề xuất",min_value=0.0,value=0.0,step=100000.0)
        delay = st.number_input("Ảnh hưởng tiến độ (ngày)",min_value=0,value=0)
        if st.form_submit_button("Tạo phát sinh"):
            cid = new_id("CHG","changes","change_id")
            execute("INSERT INTO changes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(cid,pid,wid,str(date.today()),ctype,desc,reason,value,int(delay),"Chờ duyệt",0,"",""))
            st.success("Đã tạo phát sinh.")
            st.rerun()

# 10
elif page == "10. Nghiệm thu & thanh toán":
    st.subheader("Nghiệm thu & thanh toán")
    acc = read_df("SELECT * FROM acceptances WHERE project_id=? ORDER BY acceptance_date DESC",(pid,))
    pay = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date DESC",(pid,))
    a,b = st.columns(2)
    with a:
        st.markdown("### Nghiệm thu")
        st.dataframe(acc,use_container_width=True,hide_index=True)
    with b:
        st.markdown("### Thanh toán")
        st.dataframe(pay,use_container_width=True,hide_index=True)

# 11
elif page == "11. Bảo hành & bảo trì":
    st.subheader("Bảo hành & bảo trì")
    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=? ORDER BY due_date",(pid,))
    st.dataframe(wm.rename(columns={"wm_id":"Mã","asset_item":"Hạng mục/Tài sản","wm_type":"Loại","start_date":"Bắt đầu","due_date":"Đến hạn","contractor":"Đơn vị phụ trách","tracking_content":"Nội dung","status":"Trạng thái","cost":"Chi phí"}),use_container_width=True,hide_index=True)
    with st.form("new_wm"):
        item = st.text_input("Hạng mục/Tài sản")
        wtype = st.selectbox("Loại",["Bảo hành","Bảo trì"])
        due = st.date_input("Ngày đến hạn",value=date.today()+timedelta(days=30))
        contractor = st.text_input("Đơn vị phụ trách")
        content = st.text_area("Nội dung theo dõi")
        if st.form_submit_button("Tạo lịch"):
            wid = new_id("WM","warranty_maintenance","wm_id")
            execute("INSERT INTO warranty_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)",(wid,pid,item,wtype,str(date.today()),str(due),contractor,content,"Lên lịch",0,""))
            st.success("Đã tạo lịch.")
            st.rerun()

# 12
elif page == "12. Báo cáo & sao lưu":
    st.subheader("Báo cáo & sao lưu")
    st.markdown("### Báo cáo Excel")
    st.download_button("Tải báo cáo dự án đang chọn",data=export_project_excel(pid),
                       file_name=f"{pid}_Bao_cao_DeliveryOS_V0.4.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Tải danh mục toàn bộ dự án",data=export_portfolio_excel(),
                       file_name=f"AI_KOS_DeliveryOS_Danh_muc_{date.today()}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("### Sao lưu toàn bộ dữ liệu")
    st.info("Cách đơn giản nhất: tải file `deliveryos.db` về máy. Đây là bản sao toàn bộ dữ liệu SQLite của ứng dụng.")
    if DB_PATH.exists():
        st.download_button("Tải bản sao lưu deliveryos.db",data=DB_PATH.read_bytes(),
                           file_name=f"deliveryos_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                           mime="application/octet-stream")

    st.markdown("### Khôi phục từ bản sao lưu")
    st.warning("Khôi phục sẽ thay toàn bộ dữ liệu hiện tại bằng file sao lưu. Chỉ dùng khi thật sự cần.")
    restore = st.file_uploader("Chọn file deliveryos.db đã sao lưu",type=["db"])
    confirm = st.checkbox("Tôi xác nhận muốn thay dữ liệu hiện tại bằng bản sao lưu")
    if restore and confirm and st.button("Khôi phục dữ liệu"):
        DB_PATH.write_bytes(restore.getvalue())
        st.success("Đã khôi phục. Ứng dụng sẽ tải lại.")
        st.rerun()

st.divider()
st.caption("AI-KOS DeliveryOS V0.4 | SQLite + sao lưu thủ công | Dữ liệu demo công khai không chứa thông tin bí mật.")
