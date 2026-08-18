from core.runtime import *

VIEW_TITLE = '08. Nhật ký & hồ sơ'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Nhật ký & hồ sơ")
    logs = read_df("SELECT * FROM daily_logs WHERE project_id=? ORDER BY log_date DESC",(pid,))
    if not logs.empty:
        lshow = logs[["log_date","work_name","team","workers","quantity_done","weather","issue","note"]].copy()
        lshow["log_date"] = lshow["log_date"].apply(vi_date)
        lshow = lshow.rename(columns={"log_date":"Ngày","work_name":"Công việc","team":"Tổ đội","workers":"Nhân công",
                                      "quantity_done":"Khối lượng","weather":"Thời tiết","issue":"Vấn đề/Sự cố","note":"Ghi chú"})
        st.dataframe(lshow,use_container_width=True,hide_index=True)

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

    st.markdown("### Hồ sơ / Hình ảnh")
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

# =========================================================
# 09. PHÁT SINH – HIỂN THỊ + DUYỆT/TỪ CHỐI
# =========================================================
