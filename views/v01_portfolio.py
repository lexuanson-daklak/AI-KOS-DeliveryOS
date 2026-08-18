from core.runtime import *

VIEW_TITLE = '01. Danh mục dự án'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Danh mục dự án")
    allp = read_df("SELECT * FROM projects ORDER BY project_id")
    allp["Chênh lệch tiến độ (%)"] = allp["actual_progress"].fillna(0)-allp["planned_progress"].fillna(0)
    show = allp[["project_id","project_name","project_type","location","budget","planned_progress","actual_progress","status","alert_level","Chênh lệch tiến độ (%)"]].copy()
    show["budget"] = show["budget"].apply(money)
    show = show.rename(columns={
        "project_id":"Mã dự án","project_name":"Tên dự án","project_type":"Loại dự án","location":"Địa điểm",
        "budget":"Ngân sách","planned_progress":"Tiến độ KH (%)","actual_progress":"Tiến độ TT (%)",
        "status":"Trạng thái","alert_level":"Cảnh báo"
    })
    st.dataframe(show, use_container_width=True, hide_index=True)

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
                            (project_id,name.strip(),template,owner,location,str(start),str(finish),budget,0,0,0,0,0,"Chuẩn bị","Xanh","Tạo từ V0.4.2"))
                    seed_tasks(project_id,template,start,finish)
                    st.success(f"Đã tạo {project_id}.")
                    st.rerun()

# =========================================================
# 02. HỒ SƠ DỰ ÁN
# =========================================================
