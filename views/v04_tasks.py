from core.runtime import *

VIEW_TITLE = '04. Công việc & tiến độ'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Công việc & tiến độ")
    if work.empty:
        st.info("Chưa có công việc.")
    else:
        wshow = work[["work_id","work_group","work_name","planned_start","planned_finish","planned_progress","actual_progress","assignee","status","accepted","note"]].copy()
        wshow["planned_start"] = wshow["planned_start"].apply(vi_date)
        wshow["planned_finish"] = wshow["planned_finish"].apply(vi_date)
        wshow["Chênh lệch (%)"] = work["actual_progress"].fillna(0)-work["planned_progress"].fillna(0)
        wshow = wshow.rename(columns={
            "work_id":"Mã việc","work_group":"Nhóm việc","work_name":"Công việc","planned_start":"Bắt đầu KH",
            "planned_finish":"Kết thúc KH","planned_progress":"Tiến độ KH (%)","actual_progress":"Tiến độ TT (%)",
            "assignee":"Phụ trách","status":"Trạng thái","accepted":"Đã nghiệm thu","note":"Ghi chú"
        })
        st.dataframe(wshow,use_container_width=True,hide_index=True)

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

# =========================================================
# 05. HỢP ĐỒNG & ĐỐI TÁC
# =========================================================
