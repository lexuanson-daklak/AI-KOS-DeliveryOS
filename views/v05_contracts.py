from core.runtime import *

VIEW_TITLE = '05. Hợp đồng & đối tác'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Hợp đồng & đối tác")
    partners = read_df("SELECT * FROM partners ORDER BY partner_name")
    contracts = read_df("SELECT * FROM contracts WHERE project_id=? ORDER BY signed_date DESC",(pid,))
    a,b = st.columns(2)

    with a:
        st.markdown("### Đối tác / Nhà thầu")
        if not partners.empty:
            pshow = partners[["partner_id","partner_name","partner_type","representative","phone","email"]].rename(columns={
                "partner_id":"Mã","partner_name":"Tên đơn vị","partner_type":"Loại","representative":"Đại diện","phone":"Điện thoại","email":"Email"})
            st.dataframe(pshow,use_container_width=True,hide_index=True)
        with st.form("new_partner"):
            pname = st.text_input("Tên đối tác/Nhà thầu")
            ptype = st.selectbox("Loại",["Nhà thầu","Tổ đội","Nhà cung cấp","Tư vấn","Khác"])
            rep = st.text_input("Người đại diện")
            phone = st.text_input("Điện thoại")
            email = st.text_input("Email")
            address = st.text_input("Địa chỉ")
            tax = st.text_input("Mã số thuế")
            note = st.text_input("Ghi chú")
            if st.form_submit_button("Thêm đối tác") and pname.strip():
                partner_id = new_id("PT","partners","partner_id")
                execute("INSERT INTO partners VALUES (?,?,?,?,?,?,?,?,?)",(partner_id,pname,ptype,rep,phone,email,address,tax,note))
                st.success("Đã thêm đối tác.")
                st.rerun()

    with b:
        st.markdown("### Hợp đồng của dự án")
        if not contracts.empty:
            cshow = contracts[["contract_id","partner_id","contract_name","contract_value","advance_value","signed_date","finish_date","warranty_months","status"]].copy()
            cshow["contract_value"] = cshow["contract_value"].apply(money)
            cshow["advance_value"] = cshow["advance_value"].apply(money)
            cshow["signed_date"] = cshow["signed_date"].apply(vi_date)
            cshow["finish_date"] = cshow["finish_date"].apply(vi_date)
            cshow = cshow.rename(columns={"contract_id":"Mã HĐ","partner_id":"Mã đối tác","contract_name":"Tên hợp đồng",
                "contract_value":"Giá trị HĐ","advance_value":"Tạm ứng","signed_date":"Ngày ký",
                "finish_date":"Ngày kết thúc","warranty_months":"Bảo hành (tháng)","status":"Trạng thái"})
            st.dataframe(cshow,use_container_width=True,hide_index=True)

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
            warranty_months = st.number_input("Bảo hành (tháng)",min_value=0,value=12)
            if st.form_submit_button("Thêm hợp đồng"):
                cid = new_id("HD","contracts","contract_id")
                execute("INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (cid,pid,partner,cname,value,advance,str(signed),str(start),str(finish),int(warranty_months),"Đang thực hiện",""))
                st.success("Đã thêm hợp đồng.")
                st.rerun()

# =========================================================
# 06. VẬT TƯ & NHÂN CÔNG
# =========================================================
