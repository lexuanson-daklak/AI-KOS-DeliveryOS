from core.runtime import *

VIEW_TITLE = '12. Báo cáo & sao lưu'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Báo cáo & sao lưu")
    st.markdown("### Báo cáo Excel")
    st.download_button("Tải báo cáo dự án đang chọn",data=export_project_excel(pid),
                       file_name=f"{pid}_Bao_cao_DeliveryOS_V0.4.2.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Tải danh mục toàn bộ dự án",data=export_portfolio_excel(),
                       file_name=f"AI_KOS_DeliveryOS_Danh_muc_{date.today()}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("### Sao lưu toàn bộ dữ liệu")
    st.info("Tải file `deliveryos.db` về máy. Đây là bản sao toàn bộ dữ liệu SQLite của ứng dụng.")
    if DB_PATH.exists():
        st.download_button("Tải bản sao lưu deliveryos.db",data=DB_PATH.read_bytes(),
                           file_name=f"deliveryos_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                           mime="application/octet-stream")

    st.markdown("### Khôi phục từ bản sao lưu")
    st.warning("Khôi phục sẽ thay toàn bộ dữ liệu hiện tại bằng file sao lưu. Chỉ dùng khi thật sự cần.")
    restore = st.file_uploader("Chọn file deliveryos.db đã sao lưu",type=["db"])
    confirm = st.checkbox("Tôi xác nhận muốn thay dữ liệu hiện tại bằng bản sao lưu")
    if restore and confirm and st.button("Khôi phục dữ liệu"):
        DB_PATH.write_bytes(restore.getvalue())
        st.success("Đã khôi phục. Ứng dụng sẽ tải lại.")
        st.rerun()

