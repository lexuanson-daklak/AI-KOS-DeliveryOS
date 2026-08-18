from core.runtime import *

VIEW_TITLE = '11. Bảo hành & bảo trì'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Bảo hành & bảo trì")
    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=? ORDER BY due_date",(pid,))
    if not wm.empty:
        today = pd.Timestamp.today().normalize()
        due = pd.to_datetime(wm["due_date"],errors="coerce")
        wmshow = wm[["wm_id","asset_item","wm_type","start_date","due_date","contractor","tracking_content","status","cost","note"]].copy()
        wmshow["Cảnh báo hạn"] = ""
        wmshow.loc[(due < today) & (wm["status"]!="Hoàn thành"),"Cảnh báo hạn"] = "🔴 Quá hạn"
        wmshow.loc[(due >= today) & (due <= today+pd.Timedelta(days=30)) & (wm["status"]!="Hoàn thành"),"Cảnh báo hạn"] = "🟡 Sắp đến hạn"
        wmshow["start_date"] = wmshow["start_date"].apply(vi_date)
        wmshow["due_date"] = wmshow["due_date"].apply(vi_date)
        wmshow["cost"] = wmshow["cost"].apply(money)
        wmshow = wmshow.rename(columns={
            "wm_id":"Mã","asset_item":"Hạng mục/Tài sản","wm_type":"Loại","start_date":"Bắt đầu","due_date":"Đến hạn",
            "contractor":"Đơn vị phụ trách","tracking_content":"Nội dung theo dõi","status":"Trạng thái","cost":"Chi phí","note":"Ghi chú"
        })
        st.dataframe(wmshow,use_container_width=True,hide_index=True)

    with st.form("new_wm"):
        item = st.text_input("Hạng mục/Tài sản")
        wtype = st.selectbox("Loại",["Bảo hành","Bảo trì"])
        due_date = st.date_input("Ngày đến hạn",value=date.today()+timedelta(days=30))
        contractor = st.text_input("Đơn vị phụ trách")
        content = st.text_area("Nội dung theo dõi")
        cost = st.number_input("Chi phí dự kiến",min_value=0.0,value=0.0,step=100000.0)
        if st.form_submit_button("Tạo lịch"):
            wid = new_id("WM","warranty_maintenance","wm_id")
            execute("INSERT INTO warranty_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (wid,pid,item,wtype,str(date.today()),str(due_date),contractor,content,"Lên lịch",cost,""))
            st.success("Đã tạo lịch.")
            st.rerun()

# =========================================================
# 12. BÁO CÁO & SAO LƯU
# =========================================================
