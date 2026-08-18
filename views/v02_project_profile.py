from core.runtime import *

VIEW_TITLE = '02. Hồ sơ dự án'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Hồ sơ dự án")
    st.write(f"**Mã dự án:** `{pid}`")
    with st.form("edit_project"):
        a,b = st.columns(2)
        pname = a.text_input("Tên dự án",value=project["project_name"] or "")
        types = list(PROJECT_TEMPLATES.keys())+["Khác"]
        ptype = b.selectbox("Loại dự án",types,index=types.index(project["project_type"]) if project["project_type"] in types else len(types)-1)
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

# =========================================================
# 03. TỔNG QUAN
# =========================================================
