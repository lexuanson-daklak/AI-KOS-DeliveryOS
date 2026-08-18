from core.runtime import *

VIEW_TITLE = '10. Nghiệm thu & thanh toán'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Nghiệm thu & thanh toán")
    acc = read_df("SELECT * FROM acceptances WHERE project_id=? ORDER BY acceptance_date DESC",(pid,))
    pay = read_df("SELECT * FROM payments WHERE project_id=? ORDER BY request_date DESC",(pid,))
    contracts = read_df("SELECT * FROM contracts WHERE project_id=? ORDER BY contract_id",(pid,))

    tab1,tab2 = st.tabs(["Nghiệm thu","Thanh toán"])

    with tab1:
        st.markdown("### Nghiệm thu")
        if not acc.empty:
            ashow = acc[["acceptance_id","work_id","acceptance_date","accepted_quantity","accepted_value","result","defects","correction_due","confirmed_by"]].copy()
            ashow["acceptance_date"] = ashow["acceptance_date"].apply(vi_date)
            ashow["correction_due"] = ashow["correction_due"].apply(vi_date)
            ashow["accepted_value"] = ashow["accepted_value"].apply(money)
            ashow = ashow.rename(columns={
                "acceptance_id":"Mã NT","work_id":"Mã việc","acceptance_date":"Ngày nghiệm thu","accepted_quantity":"Khối lượng",
                "accepted_value":"Giá trị nghiệm thu","result":"Kết quả","defects":"Lỗi/Tồn tại",
                "correction_due":"Hạn khắc phục","confirmed_by":"Người xác nhận"
            })
            st.dataframe(ashow,use_container_width=True,hide_index=True)

            defects_count = int(acc["defects"].fillna("").str.strip().ne("").sum())
            if defects_count:
                st.warning(f"Có {defects_count} biên bản nghiệm thu còn lỗi/tồn tại phải theo dõi.")

        st.markdown("### Tạo nghiệm thu")
        with st.form("new_acceptance"):
            wid = st.selectbox("Mã công việc",work["work_id"].tolist() if not work.empty else [""])
            c1,c2 = st.columns(2)
            acc_date = c1.date_input("Ngày nghiệm thu",value=date.today())
            acc_value = c2.number_input("Giá trị nghiệm thu",min_value=0.0,value=0.0,step=100000.0)
            qty = st.text_input("Khối lượng nghiệm thu")
            result = st.selectbox("Kết quả",["Đạt","Đạt có điều kiện","Không đạt"])
            defects = st.text_area("Lỗi/Tồn tại")
            correction_due = st.date_input("Hạn khắc phục",value=date.today()+timedelta(days=7))
            confirmed = st.text_input("Người xác nhận")
            note = st.text_input("Ghi chú")
            if st.form_submit_button("Lưu nghiệm thu"):
                aid = new_id("ACC","acceptances","acceptance_id")
                execute("INSERT INTO acceptances VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (aid,pid,wid,str(acc_date),qty,acc_value,result,defects,str(correction_due),confirmed,note))
                if result=="Đạt" and wid:
                    execute("UPDATE work_items SET accepted='Có',status='Hoàn thành',actual_progress=100 WHERE work_id=?",(wid,))
                st.success("Đã lưu nghiệm thu.")
                st.rerun()

    with tab2:
        st.markdown("### Thanh toán")
        if not pay.empty:
            pshow = pay[["payment_id","contract_id","tranche","request_date","requested_value","approved_value","paid_value","payment_date","status","note"]].copy()
            pshow["Còn phải trả"] = pshow["approved_value"].fillna(0)-pshow["paid_value"].fillna(0)
            pshow["request_date"] = pshow["request_date"].apply(vi_date)
            pshow["payment_date"] = pshow["payment_date"].apply(vi_date)
            for col in ["requested_value","approved_value","paid_value","Còn phải trả"]:
                pshow[col] = pshow[col].apply(money)
            pshow = pshow.rename(columns={
                "payment_id":"Mã TT","contract_id":"Mã HĐ","tranche":"Đợt","request_date":"Ngày đề nghị",
                "requested_value":"Giá trị đề nghị","approved_value":"Giá trị duyệt","paid_value":"Đã thanh toán",
                "payment_date":"Ngày thanh toán","status":"Trạng thái","note":"Ghi chú"
            })
            st.dataframe(pshow,use_container_width=True,hide_index=True)

            remain_total = (pay["approved_value"].fillna(0)-pay["paid_value"].fillna(0)).clip(lower=0).sum()
            st.metric("Tổng còn phải thanh toán",money(remain_total))

        st.markdown("### Tạo khoản thanh toán")
        with st.form("new_payment"):
            contract_options = contracts["contract_id"].tolist() if not contracts.empty else [""]
            cid = st.selectbox("Mã hợp đồng",contract_options)
            tranche = st.text_input("Tên đợt thanh toán")
            c1,c2,c3 = st.columns(3)
            req_date = c1.date_input("Ngày đề nghị",value=date.today())
            req_value = c2.number_input("Giá trị đề nghị",min_value=0.0,value=0.0,step=100000.0)
            approved_value = c3.number_input("Giá trị duyệt",min_value=0.0,value=0.0,step=100000.0)
            c4,c5 = st.columns(2)
            paid_value = c4.number_input("Đã thanh toán",min_value=0.0,value=0.0,step=100000.0)
            method = c5.selectbox("Hình thức",["Chuyển khoản","Tiền mặt","Khác"])
            payment_date = st.date_input("Ngày thanh toán",value=date.today())
            note = st.text_input("Ghi chú")
            if st.form_submit_button("Lưu khoản thanh toán"):
                payid = new_id("PAY","payments","payment_id")
                status = "Đã thanh toán" if approved_value>0 and paid_value>=approved_value else ("Thanh toán một phần" if paid_value>0 else "Chờ thanh toán")
                execute("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (payid,pid,cid,tranche,str(req_date),req_value,approved_value,paid_value,str(payment_date) if paid_value>0 else "",method,status,note))
                total_paid = float(scalar("SELECT COALESCE(SUM(paid_value),0) FROM payments WHERE project_id=?",(pid,),0))
                execute("UPDATE projects SET paid=? WHERE project_id=?",(total_paid,pid))
                st.success("Đã lưu khoản thanh toán.")
                st.rerun()

        if not pay.empty:
            st.markdown("### Cập nhật khoản thanh toán hiện có")
            update_id = st.selectbox("Chọn khoản thanh toán",pay["payment_id"].tolist(),
                                     format_func=lambda x: f"{x} – {pay.loc[pay['payment_id']==x,'tranche'].iloc[0]}")
            pr = pay[pay["payment_id"]==update_id].iloc[0]
            u1,u2 = st.columns(2)
            new_paid = u1.number_input("Số tiền đã thanh toán cập nhật",min_value=0.0,value=float(pr["paid_value"] or 0),step=100000.0,key="update_paid")
            new_date = u2.date_input("Ngày thanh toán cập nhật",value=date.today(),key="update_date")
            if st.button("Cập nhật thanh toán"):
                appr = float(pr["approved_value"] or 0)
                status = "Đã thanh toán" if appr>0 and new_paid>=appr else ("Thanh toán một phần" if new_paid>0 else "Chờ thanh toán")
                execute("UPDATE payments SET paid_value=?,payment_date=?,status=? WHERE payment_id=?",(new_paid,str(new_date),status,update_id))
                total_paid = float(scalar("SELECT COALESCE(SUM(paid_value),0) FROM payments WHERE project_id=?",(pid,),0))
                execute("UPDATE projects SET paid=? WHERE project_id=?",(total_paid,pid))
                st.success("Đã cập nhật thanh toán.")
                st.rerun()

# =========================================================
# 11. BẢO HÀNH & BẢO TRÌ
# =========================================================
