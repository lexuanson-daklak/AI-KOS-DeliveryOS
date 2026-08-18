from core.runtime import *

VIEW_TITLE = '00. Hôm nay cần làm gì?'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Hôm nay cần làm gì?")
    scope = st.radio("Phạm vi", ["Tất cả dự án","Dự án đang chọn"], horizontal=True)
    todo = today_tasks(pid if scope=="Dự án đang chọn" else None)

    total = len(todo)
    overdue_n = int((todo["Loại việc"]=="Quá hạn").sum()) if not todo.empty else 0
    soon_n = int((todo["Loại việc"]=="Sắp đến hạn").sum()) if not todo.empty else 0
    waiting_n = int(todo["Loại việc"].isin(["Chờ duyệt","Chờ thanh toán"]).sum()) if not todo.empty else 0
    wm_n = int(todo["Loại việc"].isin(["Bảo hành","Bảo trì"]).sum()) if not todo.empty else 0

    a,b,c,d,e = st.columns(5)
    a.metric("Tổng việc cần chú ý", total)
    b.metric("Quá hạn", overdue_n)
    c.metric("Sắp đến hạn", soon_n)
    d.metric("Chờ duyệt/thanh toán", waiting_n)
    e.metric("Bảo hành/bảo trì", wm_n)

    if todo.empty:
        st.success("Không có việc khẩn cấp hoặc sắp đến hạn.")
    else:
        st.dataframe(todo, use_container_width=True, hide_index=True)

# =========================================================
# 01. DANH MỤC DỰ ÁN
# =========================================================
