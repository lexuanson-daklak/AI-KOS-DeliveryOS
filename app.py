
import sqlite3
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "deliveryos.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="AI-KOS DeliveryOS V0.2",
    page_icon="🏗️",
    layout="wide"
)

def money(x):
    try:
        return f"{float(x):,.0f} đ".replace(",", ".")
    except:
        return "0 đ"

def get_conn():
    return sqlite3.connect(DB_PATH)

def read_df(sql, params=None):
    with get_conn() as con:
        return pd.read_sql_query(sql, con, params=params or ())

def execute(sql, params=()):
    with get_conn() as con:
        con.execute(sql, params)
        con.commit()

def project_ids():
    df = read_df("SELECT project_id, project_name FROM projects ORDER BY project_id")
    return {r["project_id"]: r["project_name"] for _, r in df.iterrows()}

def selected_project():
    projects = project_ids()
    pid = st.sidebar.selectbox(
        "Dự án / Project",
        list(projects.keys()),
        format_func=lambda x: f"{x} – {projects[x]}"
    )
    return pid

def alert_rules(project, work, changes, costs):
    alerts = []
    gap = float(project["actual_progress"]) - float(project["planned_progress"])
    forecast = float(costs["forecast_final"].sum()) if len(costs) else 0
    budget = float(project["budget"])

    if gap <= -10:
        alerts.append(("🔴", "Tiến độ", f"Tiến độ thực tế thấp hơn kế hoạch {abs(gap):.0f} điểm %."))
    elif gap < 0:
        alerts.append(("🟡", "Tiến độ", f"Tiến độ đang thấp hơn kế hoạch {abs(gap):.0f} điểm %."))

    if forecast > budget:
        alerts.append(("🔴", "Chi phí", f"Dự báo cuối kỳ vượt ngân sách {money(forecast-budget)}."))
    elif forecast > budget * 0.95:
        alerts.append(("🟡", "Chi phí", "Dự báo cuối kỳ đã sử dụng trên 95% ngân sách."))

    overdue = work[(work["status"] != "Hoàn thành") & (pd.to_datetime(work["planned_finish"], errors="coerce") < pd.Timestamp.today())]
    if len(overdue):
        alerts.append(("🟠", "Công việc", f"Có {len(overdue)} công việc quá hạn chưa hoàn thành."))

    pending_change = changes[changes["approval_status"] == "Chờ duyệt"]
    if len(pending_change):
        alerts.append(("🟡", "Phát sinh", f"Có {len(pending_change)} phát sinh đang chờ duyệt, tổng đề xuất {money(pending_change['proposed_value'].sum())}."))

    if not alerts:
        alerts.append(("🟢", "Tổng thể", "Dự án chưa có cảnh báo đáng kể theo bộ quy tắc V0.1."))

    return alerts

st.sidebar.title("AI-KOS DeliveryOS")
st.sidebar.caption("Quản trị thực hiện dự án, công trình và vận hành tài sản")
page = st.sidebar.radio(
    "Chức năng / Module",
    [
        "00. Danh mục dự án",
        "01. Tổng quan",
        "02. Công việc & tiến độ",
        "03. Chi phí & dòng tiền",
        "04. Nhật ký & hình ảnh",
        "05. Phát sinh",
        "06. Nghiệm thu & thanh toán",
        "07. Bảo hành & bảo trì",
    ]
)
pid = selected_project()

project_df = read_df("SELECT * FROM projects WHERE project_id=?", (pid,))
project = project_df.iloc[0]
work = read_df("SELECT * FROM work_items WHERE project_id=? ORDER BY planned_start", (pid,))
costs = read_df("SELECT * FROM costs WHERE project_id=?", (pid,))
changes = read_df("SELECT * FROM changes WHERE project_id=? ORDER BY found_date DESC", (pid,))

st.title("AI-KOS DeliveryOS V0.2")
st.caption("MVP V0.2 – Quản lý nhiều dự án. AI cảnh báo V0.1 sử dụng quy tắc nghiệp vụ; chưa tự ý thay đổi số liệu gốc.")

if page == "00. Danh mục dự án":
    st.subheader("Danh mục dự án / Project Portfolio")
    all_projects = read_df("SELECT * FROM projects ORDER BY project_id")
    all_projects["Chênh lệch tiến độ"] = all_projects["actual_progress"] - all_projects["planned_progress"]
    st.dataframe(
        all_projects[[
            "project_id","project_name","project_type","location","budget",
            "planned_progress","actual_progress","Chênh lệch tiến độ","status","alert_level"
        ]],
        use_container_width=True,
        hide_index=True
    )

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Số dự án", len(all_projects))
    c2.metric("Tổng ngân sách", money(all_projects["budget"].sum()))
    c3.metric("Đang thi công/vận hành", int(all_projects["status"].isin(["Đang thi công","Đang vận hành"]).sum()))
    c4.metric("Cảnh báo vàng/đỏ", int(all_projects["alert_level"].isin(["Vàng","Cam","Đỏ"]).sum()))

    st.markdown("### Tạo dự án mới")
    with st.form("create_project"):
        p1,p2 = st.columns(2)
        new_id = p1.text_input("PROJECT_ID", placeholder="LXS-REPAIR-2026-002")
        new_name = p2.text_input("Tên dự án")
        p3,p4,p5 = st.columns(3)
        new_type = p3.selectbox("Loại dự án", ["Sửa chữa – cải tạo","Công trình sửa chữa","Quản lý xưởng","Khác"])
        new_owner = p4.text_input("Chủ đầu tư/Đơn vị")
        new_location = p5.text_input("Địa điểm", value="Đắk Lắk")
        p6,p7,p8 = st.columns(3)
        new_budget = p6.number_input("Ngân sách", min_value=0.0, value=0.0, step=1000000.0)
        start = p7.date_input("Bắt đầu kế hoạch")
        finish = p8.date_input("Kết thúc kế hoạch")
        submitted = st.form_submit_button("Tạo dự án")
        if submitted:
            if not new_id.strip() or not new_name.strip():
                st.error("PROJECT_ID và Tên dự án là bắt buộc.")
            else:
                exists = read_df("SELECT project_id FROM projects WHERE project_id=?", (new_id.strip(),))
                if len(exists):
                    st.error("PROJECT_ID đã tồn tại.")
                else:
                    execute(
                        "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            new_id.strip(),new_name.strip(),new_type,new_owner,new_location,
                            str(start),str(finish),new_budget,0,0,0,0,0,
                            "Chuẩn bị","Xanh","Dự án được tạo từ DeliveryOS V0.2"
                        )
                    )
                    st.success("Đã tạo dự án mới.")
                    st.rerun()

elif page == "01. Tổng quan":
    st.subheader(project["project_name"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ngân sách", money(project["budget"]))
    c2.metric("Đã thanh toán", money(project["paid"]))
    c3.metric("Tiến độ thực tế", f"{project['actual_progress']:.0f}%", f"{project['actual_progress']-project['planned_progress']:.0f} điểm %")
    forecast = costs["forecast_final"].sum()
    c4.metric("Dự báo chi phí cuối kỳ", money(forecast), money(project["budget"]-forecast))

    st.progress(min(max(float(project["actual_progress"])/100, 0), 1))
    st.write(f"**Kế hoạch:** {project['planned_progress']:.0f}%  |  **Thực tế:** {project['actual_progress']:.0f}%  |  **Trạng thái:** {project['status']}  |  **Cảnh báo:** {project['alert_level']}")

    st.markdown("### Cảnh báo điều hành")
    for icon, title, msg in alert_rules(project, work, changes, costs):
        st.write(f"{icon} **{title}:** {msg}")

    left, right = st.columns(2)
    with left:
        st.markdown("### Công việc theo trạng thái")
        s = work.groupby("status").size().reset_index(name="Số lượng")
        st.bar_chart(s.set_index("status"))
        st.dataframe(work[["work_id","work_group","work_name","planned_progress","actual_progress","status"]], use_container_width=True)
    with right:
        st.markdown("### Cơ cấu chi phí dự báo")
        c = costs[["cost_group","forecast_final"]].set_index("cost_group")
        st.bar_chart(c)
        st.dataframe(costs[["cost_group","planned_budget","actual_cost","forecast_final"]], use_container_width=True)

elif page == "02. Công việc & tiến độ":
    st.subheader("Công việc & tiến độ / Schedule & Tasks")
    st.info("Nguyên tắc: mỗi công việc phải có mã, khối lượng, giá trị, mốc thời gian, người phụ trách và trạng thái nghiệm thu.")
    show = work.copy()
    show["Chênh lệch tiến độ"] = show["actual_progress"] - show["planned_progress"]
    st.dataframe(
        show[["work_id","work_group","work_name","planned_start","planned_finish","planned_progress","actual_progress","Chênh lệch tiến độ","assignee","status","accepted"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Cập nhật một công việc")
    work_id = st.selectbox("WORK_ID", work["work_id"].tolist())
    r = work[work["work_id"]==work_id].iloc[0]
    col1, col2, col3 = st.columns(3)
    new_progress = col1.number_input("Tiến độ thực tế (%)", 0.0, 100.0, float(r["actual_progress"]), 1.0)
    new_status = col2.selectbox("Trạng thái", ["Chưa bắt đầu","Đang thực hiện","Chờ nghiệm thu","Hoàn thành"], index=["Chưa bắt đầu","Đang thực hiện","Chờ nghiệm thu","Hoàn thành"].index(r["status"]) if r["status"] in ["Chưa bắt đầu","Đang thực hiện","Chờ nghiệm thu","Hoàn thành"] else 0)
    new_note = col3.text_input("Ghi chú", value=r["note"] or "")
    if st.button("Lưu cập nhật công việc"):
        execute("UPDATE work_items SET actual_progress=?, status=?, note=? WHERE work_id=?", (new_progress,new_status,new_note,work_id))
        st.success("Đã lưu.")
        st.rerun()

elif page == "03. Chi phí & dòng tiền":
    st.subheader("Chi phí & dòng tiền / Cost & Cash Flow")
    budget = float(project["budget"])
    committed = float(costs["committed"].sum())
    actual = float(costs["actual_cost"].sum())
    forecast = float(costs["forecast_final"].sum())
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Ngân sách", money(budget))
    c2.metric("Cam kết chi", money(committed))
    c3.metric("Chi thực tế", money(actual))
    c4.metric("Dự báo cuối kỳ", money(forecast), money(budget-forecast))

    df = costs.copy()
    df["Chênh lệch dự báo"] = df["forecast_final"] - df["planned_budget"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    payments = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date", (pid,))
    st.markdown("### Dòng tiền thanh toán")
    st.dataframe(payments, use_container_width=True, hide_index=True)
    st.write(f"**Đã thanh toán theo các đợt:** {money(payments['paid_value'].sum())}")

elif page == "04. Nhật ký & hình ảnh":
    st.subheader("Nhật ký & hình ảnh / Site Diary & Photos")
    logs = read_df("SELECT * FROM daily_logs WHERE project_id=? ORDER BY log_date DESC", (pid,))
    st.dataframe(logs, use_container_width=True, hide_index=True)

    st.markdown("### Thêm nhật ký ngày")
    with st.form("new_log"):
        c1,c2,c3 = st.columns(3)
        log_date = c1.date_input("Ngày", value=date.today())
        work_name = c2.text_input("Công việc")
        team = c3.text_input("Tổ đội")
        c4,c5,c6 = st.columns(3)
        workers = c4.number_input("Nhân công", min_value=0, value=0)
        quantity_done = c5.text_input("Khối lượng thực hiện")
        weather = c6.text_input("Thời tiết")
        issue = st.text_input("Vấn đề/Sự cố")
        note = st.text_area("Ghi chú")
        submitted = st.form_submit_button("Lưu nhật ký")
        if submitted:
            next_id = f"LOG-{len(logs)+1:03d}"
            execute("INSERT INTO daily_logs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (next_id,pid,str(log_date),work_name,team,int(workers),quantity_done,weather,issue,"Đang thực hiện",note))
            st.success("Đã lưu nhật ký.")
            st.rerun()

    st.markdown("### Tải ảnh hiện trường")
    uploaded = st.file_uploader("Ảnh JPG/PNG", type=["jpg","jpeg","png"])
    if uploaded:
        safe_name = f"{pid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded.name}"
        target = UPLOAD_DIR / safe_name
        target.write_bytes(uploaded.getbuffer())
        st.success(f"Đã lưu ảnh cục bộ: {safe_name}")
        st.image(str(target), width=500)
        st.caption("V0.2 sẽ bổ sung metadata bắt buộc: WORK_ID, khu vực, Trước/Trong/Sau, mô tả và người tải.")

elif page == "05. Phát sinh":
    st.subheader("Phát sinh / Change Management")
    st.warning("Nguyên tắc: phát sinh phải có mã riêng, nguyên nhân, giá trị, ảnh hưởng tiến độ và trạng thái phê duyệt.")
    st.dataframe(changes, use_container_width=True, hide_index=True)

    st.markdown("### Thêm phát sinh")
    with st.form("new_change"):
        c1,c2,c3 = st.columns(3)
        work_id = c1.selectbox("WORK_ID", work["work_id"].tolist())
        change_type = c2.selectbox("Loại", ["Tăng khối lượng","Thay đổi vật liệu","Bổ sung công việc","Giảm trừ"])
        found_date = c3.date_input("Ngày phát hiện", value=date.today())
        desc = st.text_input("Nội dung")
        reason = st.text_area("Nguyên nhân")
        c4,c5 = st.columns(2)
        value = c4.number_input("Giá trị đề xuất", min_value=0.0, value=0.0, step=100000.0)
        delay = c5.number_input("Ảnh hưởng tiến độ (ngày)", min_value=0, value=0)
        submitted = st.form_submit_button("Tạo phát sinh")
        if submitted:
            next_id = f"CHG-{len(changes)+1:03d}"
            execute("INSERT INTO changes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (next_id,pid,work_id,str(found_date),change_type,desc,reason,value,int(delay),"Chờ duyệt",0,"",""))
            st.success("Đã tạo phát sinh ở trạng thái Chờ duyệt.")
            st.rerun()

    pending = changes[changes["approval_status"]=="Chờ duyệt"]
    if len(pending):
        st.markdown("### Duyệt phát sinh")
        cid = st.selectbox("CHANGE_ID cần xử lý", pending["change_id"].tolist())
        rr = pending[pending["change_id"]==cid].iloc[0]
        approved_value = st.number_input("Giá trị được duyệt", min_value=0.0, value=float(rr["proposed_value"]), step=100000.0)
        approved_by = st.text_input("Người duyệt")
        c1,c2 = st.columns(2)
        if c1.button("Duyệt phát sinh"):
            execute("UPDATE changes SET approval_status='Đã duyệt', approved_value=?, approved_by=? WHERE change_id=?",
                    (approved_value, approved_by, cid))
            # Synchronize total approved changes in project
            total = read_df("SELECT COALESCE(SUM(approved_value),0) AS total FROM changes WHERE project_id=? AND approval_status='Đã duyệt'", (pid,)).iloc[0]["total"]
            execute("UPDATE projects SET approved_changes=? WHERE project_id=?", (float(total),pid))
            st.success("Đã duyệt.")
            st.rerun()
        if c2.button("Từ chối"):
            execute("UPDATE changes SET approval_status='Từ chối', approved_value=0, approved_by=? WHERE change_id=?",
                    (approved_by, cid))
            st.success("Đã từ chối.")
            st.rerun()

elif page == "06. Nghiệm thu & thanh toán":
    st.subheader("Nghiệm thu & thanh toán / Acceptance & Payment")
    acc = read_df("SELECT * FROM acceptances WHERE project_id=? ORDER BY acceptance_date DESC", (pid,))
    pay = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date DESC", (pid,))
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Nghiệm thu")
        st.dataframe(acc, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("### Thanh toán")
        st.dataframe(pay, use_container_width=True, hide_index=True)

    st.markdown("### Thêm biên bản nghiệm thu")
    with st.form("new_acc"):
        c1,c2,c3 = st.columns(3)
        work_id = c1.selectbox("WORK_ID", work["work_id"].tolist(), key="acc_work")
        acc_date = c2.date_input("Ngày nghiệm thu", value=date.today())
        accepted_value = c3.number_input("Giá trị nghiệm thu", min_value=0.0, value=0.0, step=100000.0)
        quantity = st.text_input("Khối lượng nghiệm thu")
        result = st.selectbox("Kết quả", ["Đạt","Đạt có điều kiện","Không đạt"])
        defects = st.text_area("Lỗi/tồn tại")
        confirmed_by = st.text_input("Người xác nhận")
        submitted = st.form_submit_button("Lưu nghiệm thu")
        if submitted:
            next_id = f"ACC-{len(acc)+1:03d}"
            execute("INSERT INTO acceptances VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (next_id,pid,work_id,str(acc_date),quantity,accepted_value,result,defects,"",confirmed_by,""))
            if result == "Đạt":
                execute("UPDATE work_items SET accepted='Có', status='Hoàn thành', actual_progress=100 WHERE work_id=?", (work_id,))
            st.success("Đã lưu nghiệm thu.")
            st.rerun()

elif page == "07. Bảo hành & bảo trì":
    st.subheader("Bảo hành & bảo trì / Warranty & Maintenance")
    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=? ORDER BY due_date", (pid,))
    st.dataframe(wm, use_container_width=True, hide_index=True)

    st.markdown("### Thêm lịch bảo hành/bảo trì")
    with st.form("new_wm"):
        c1,c2,c3 = st.columns(3)
        asset_item = c1.text_input("Hạng mục/Tài sản")
        wm_type = c2.selectbox("Loại", ["Bảo hành","Bảo trì"])
        due = c3.date_input("Ngày đến hạn", value=date.today())
        contractor = st.text_input("Đơn vị/Nhà thầu phụ trách")
        tracking = st.text_area("Nội dung theo dõi")
        submitted = st.form_submit_button("Tạo lịch")
        if submitted:
            next_id = f"WM-{len(wm)+1:03d}"
            execute("INSERT INTO warranty_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (next_id,pid,asset_item,wm_type,str(date.today()),str(due),contractor,tracking,"Lên lịch",0,""))
            st.success("Đã thêm lịch.")
            st.rerun()

st.divider()
st.caption("AI-KOS DeliveryOS MVP V0.2 | Dự án mẫu 01: Sửa chữa nhà cũ | Không sử dụng dữ liệu công vụ hoặc thông tin bí mật trong bản demo công khai.")
