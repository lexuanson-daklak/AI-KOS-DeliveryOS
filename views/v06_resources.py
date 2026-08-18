from core.runtime import *

VIEW_TITLE = '06. Vật tư & nhân công'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Vật tư & nhân công")
    mats = read_df("SELECT * FROM materials WHERE project_id=? ORDER BY material_name",(pid,))
    labs = read_df("SELECT * FROM labour_logs WHERE project_id=? ORDER BY work_date DESC",(pid,))

    a,b = st.columns(2)
    with a:
        st.markdown("### Vật tư")
        if not mats.empty:
            m = mats.copy()
            m["Chênh lệch mua"] = m["purchased_qty"].fillna(0)-m["planned_qty"].fillna(0)
            m["Tồn kho"] = m["purchased_qty"].fillna(0)-m["used_qty"].fillna(0)
            m["Giá trị đã mua"] = m["purchased_qty"].fillna(0)*m["unit_price"].fillna(0)

            mshow = m[["material_id","material_name","unit","planned_qty","purchased_qty","used_qty","Chênh lệch mua","Tồn kho","Giá trị đã mua"]].copy()
            mshow["Giá trị đã mua"] = mshow["Giá trị đã mua"].apply(money)
            mshow = mshow.rename(columns={"material_id":"Mã","material_name":"Vật tư","unit":"ĐVT","planned_qty":"KH",
                                          "purchased_qty":"Đã mua","used_qty":"Đã dùng"})
            st.dataframe(mshow,use_container_width=True,hide_index=True)

            over = m[m["Chênh lệch mua"]>0]
            if len(over):
                st.warning("Vật tư mua vượt kế hoạch:")
                for _, r in over.iterrows():
                    st.write(f"🟠 **{r['material_name']}**: vượt {r['Chênh lệch mua']:,.0f} {r['unit']}; tồn {r['Tồn kho']:,.0f} {r['unit']}.".replace(",", "."))

        with st.form("new_material"):
            name = st.text_input("Tên vật tư")
            c1,c2,c3 = st.columns(3)
            unit = c1.text_input("ĐVT")
            planned = c2.number_input("Khối lượng KH",min_value=0.0,value=0.0)
            purchased = c3.number_input("Đã mua",min_value=0.0,value=0.0)
            c4,c5 = st.columns(2)
            used = c4.number_input("Đã sử dụng",min_value=0.0,value=0.0)
            price = c5.number_input("Đơn giá",min_value=0.0,value=0.0,step=1000.0)
            supplier = st.text_input("Nhà cung cấp")
            if st.form_submit_button("Thêm vật tư"):
                mid = new_id("MAT","materials","material_id")
                execute("INSERT INTO materials VALUES (?,?,?,?,?,?,?,?,?,?)",(mid,pid,name,unit,planned,purchased,used,price,supplier,""))
                st.success("Đã thêm vật tư.")
                st.rerun()

    with b:
        st.markdown("### Nhân công")
        if not labs.empty:
            l = labs.copy()
            l["Thành tiền"] = l["workdays"].fillna(0)*l["unit_cost"].fillna(0)
            lshow = l[["labour_id","work_id","work_date","team","workers","workdays","unit_cost","Thành tiền","description"]].copy()
            lshow["work_date"] = lshow["work_date"].apply(vi_date)
            lshow["unit_cost"] = lshow["unit_cost"].apply(money)
            lshow["Thành tiền"] = lshow["Thành tiền"].apply(money)
            lshow = lshow.rename(columns={"labour_id":"Mã","work_id":"Mã việc","work_date":"Ngày","team":"Tổ đội",
                                          "workers":"Số người","workdays":"Số công","unit_cost":"Đơn giá/công","description":"Nội dung"})
            st.dataframe(lshow,use_container_width=True,hide_index=True)
            total_lab = (labs["workdays"].fillna(0)*labs["unit_cost"].fillna(0)).sum()
            st.metric("Tổng chi phí nhân công đã ghi nhận",money(total_lab))

        with st.form("new_labour"):
            wid = st.selectbox("Mã công việc",[""]+work["work_id"].tolist())
            c1,c2 = st.columns(2)
            wdate = c1.date_input("Ngày",value=date.today())
            team = c2.text_input("Tổ đội")
            c3,c4,c5 = st.columns(3)
            workers = c3.number_input("Số người",min_value=0,value=0)
            workdays = c4.number_input("Số công",min_value=0.0,value=0.0)
            unit_cost = c5.number_input("Đơn giá/công",min_value=0.0,value=0.0,step=10000.0)
            desc = st.text_input("Nội dung")
            if st.form_submit_button("Thêm nhật ký nhân công"):
                lid = new_id("LAB","labour_logs","labour_id")
                execute("INSERT INTO labour_logs VALUES (?,?,?,?,?,?,?,?,?,?)",(lid,pid,wid,str(wdate),team,int(workers),workdays,unit_cost,desc,""))
                st.success("Đã thêm nhân công.")
                st.rerun()

# =========================================================
# 07. CHI PHÍ & DÒNG TIỀN
# =========================================================
