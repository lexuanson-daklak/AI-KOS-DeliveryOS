from core.runtime import *

VIEW_TITLE = '09. Phát sinh'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Phát sinh")
    changes = read_df("SELECT * FROM changes WHERE project_id=? ORDER BY found_date DESC",(pid,))

    if not changes.empty:
        show = changes[["change_id","work_id","found_date","change_type","description","reason","proposed_value","delay_days","approval_status","approved_value","approved_by"]].copy()
        show["found_date"] = show["found_date"].apply(vi_date)
        show["proposed_value"] = show["proposed_value"].apply(money)
        show["approved_value"] = show["approved_value"].apply(money)
        show = show.rename(columns={
            "change_id":"Mã phát sinh","work_id":"Mã việc","found_date":"Ngày","change_type":"Loại",
            "description":"Nội dung","reason":"Nguyên nhân","proposed_value":"Giá trị đề xuất",
            "delay_days":"Ảnh hưởng tiến độ (ngày)","approval_status":"Trạng thái",
            "approved_value":"Giá trị duyệt","approved_by":"Người duyệt"
        })
        st.dataframe(show,use_container_width=True,hide_index=True)

    st.markdown("### Tạo phát sinh mới")
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
            st.success("Đã tạo phát sinh ở trạng thái Chờ duyệt.")
            st.rerun()

    pending = changes[changes["approval_status"]=="Chờ duyệt"] if not changes.empty else pd.DataFrame()
    if not pending.empty:
        st.markdown("### Xử lý phát sinh chờ duyệt")
        cid = st.selectbox("Chọn phát sinh",pending["change_id"].tolist(),
                           format_func=lambda x: f"{x} – {pending.loc[pending['change_id']==x,'description'].iloc[0]} – {money(pending.loc[pending['change_id']==x,'proposed_value'].iloc[0])}")
        rr = pending[pending["change_id"]==cid].iloc[0]
        c1,c2 = st.columns(2)
        approved_value = c1.number_input("Giá trị được duyệt",value=float(rr["proposed_value"] or 0),step=100000.0)
        approved_by = c2.text_input("Người duyệt")
        note_approval = st.text_input("Ghi chú xử lý")
        b1,b2 = st.columns(2)
        if b1.button("✅ Duyệt phát sinh"):
            execute("UPDATE changes SET approval_status='Đã duyệt',approved_value=?,approved_by=?,note=? WHERE change_id=?",
                    (approved_value,approved_by,note_approval,cid))
            total = float(scalar("SELECT COALESCE(SUM(approved_value),0) FROM changes WHERE project_id=? AND approval_status='Đã duyệt'",(pid,),0))
            execute("UPDATE projects SET approved_changes=? WHERE project_id=?",(total,pid))
            st.success("Đã duyệt phát sinh.")
            st.rerun()
        if b2.button("❌ Từ chối phát sinh"):
            execute("UPDATE changes SET approval_status='Từ chối',approved_value=0,approved_by=?,note=? WHERE change_id=?",
                    (approved_by,note_approval,cid))
            total = float(scalar("SELECT COALESCE(SUM(approved_value),0) FROM changes WHERE project_id=? AND approval_status='Đã duyệt'",(pid,),0))
            execute("UPDATE projects SET approved_changes=? WHERE project_id=?",(total,pid))
            st.success("Đã từ chối phát sinh.")
            st.rerun()

# =========================================================
# 10. NGHIỆM THU & THANH TOÁN
# =========================================================
