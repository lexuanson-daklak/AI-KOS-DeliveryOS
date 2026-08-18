import importlib

from core.runtime import st, project_map, project_data

VIEW_REGISTRY = [
    ("00. Hôm nay cần làm gì?", "views.v00_today"),
    ("01. Danh mục dự án", "views.v01_portfolio"),
    ("02. Hồ sơ dự án", "views.v02_project_profile"),
    ("03. Tổng quan", "views.v03_dashboard"),
    ("04. Công việc & tiến độ", "views.v04_tasks"),
    ("05. Hợp đồng & đối tác", "views.v05_contracts"),
    ("06. Vật tư & nhân công", "views.v06_resources"),
    ("07. Chi phí & dòng tiền", "views.v07_cost_cashflow"),
    ("08. Nhật ký & hồ sơ", "views.v08_diary_files"),
    ("09. Phát sinh", "views.v09_changes"),
    ("10. Nghiệm thu & thanh toán", "views.v10_acceptance_payment"),
    ("11. Bảo hành & bảo trì", "views.v11_warranty"),
    ("12. Báo cáo & sao lưu", "views.v12_reports_backup"),
]

st.sidebar.title("AI-KOS DeliveryOS")
st.sidebar.caption("Quản trị thực hiện dự án, công trình và vận hành tài sản")

page = st.sidebar.radio("Chức năng", [x[0] for x in VIEW_REGISTRY])
projects = project_map()
if not projects:
    st.error("Chưa có dự án trong dữ liệu hiện tại.")
    st.stop()

pid = st.sidebar.selectbox("Dự án", list(projects.keys()), format_func=lambda x: f"{x} – {projects[x]}")
project, work, costs, changes = project_data(pid)

st.title("AI-KOS DeliveryOS V0.4.2")
st.caption("V0.4.2 FINAL – cấu trúc Views | GitHub → Streamlit → SQLite | AI hỗ trợ phân tích/cảnh báo, không tự sửa số liệu gốc.")

ctx = {"pid":pid, "project":project, "work":work, "costs":costs, "changes":changes}
module_name = dict(VIEW_REGISTRY)[page]
view_module = importlib.import_module(module_name)
view_module.render(ctx)

st.divider()
st.caption("AI-KOS DeliveryOS V0.4.2 FINAL | Cấu trúc Views ổn định | SQLite + sao lưu thủ công.")
