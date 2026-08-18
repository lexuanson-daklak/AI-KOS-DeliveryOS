from core.runtime import *
from core.export_center import (
    project_word_bytes,
    project_excel_bytes,
    project_json_bytes,
    raw_csv_zip_bytes,
    attachments_zip_bytes,
    project_full_zip_bytes,
    portfolio_word_bytes,
    portfolio_excel_bytes,
    portfolio_json_bytes,
    portfolio_full_zip_bytes,
)

VIEW_TITLE = "12. Xuất dữ liệu, báo cáo & sao lưu"


def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]

    st.subheader("Xuất dữ liệu, báo cáo & sao lưu")
    st.caption(
        "Mục tiêu: người dùng tải dữ liệu trực tiếp từ Streamlit, không phải vào GitHub để tìm file."
    )

    tab_project, tab_all, tab_restore = st.tabs([
        "Dự án đang chọn",
        "Toàn bộ danh mục",
        "Khôi phục dữ liệu",
    ])

    with tab_project:
        st.markdown(f"### Dự án: {project['project_name']}")
        st.info(
            "Có thể tải từng định dạng hoặc tải toàn bộ một lần. Gói toàn bộ gồm Word, Excel, JSON, CSV và hồ sơ đính kèm."
        )
        c1,c2,c3 = st.columns(3)
        c1.download_button(
            "⬇ Tải báo cáo Word",
            data=project_word_bytes(pid),
            file_name=f"{pid}_Bao_cao_DeliveryOS.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
        c2.download_button(
            "⬇ Tải dữ liệu Excel",
            data=project_excel_bytes(pid),
            file_name=f"{pid}_Du_lieu_DeliveryOS.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        c3.download_button(
            "⬇ Tải dữ liệu JSON",
            data=project_json_bytes(pid),
            file_name=f"{pid}_Du_lieu_DeliveryOS.json",
            mime="application/json",
            use_container_width=True,
        )

        d1,d2,d3 = st.columns(3)
        d1.download_button(
            "⬇ Tải dữ liệu thô CSV",
            data=raw_csv_zip_bytes(pid),
            file_name=f"{pid}_CSV.zip",
            mime="application/zip",
            use_container_width=True,
        )
        d2.download_button(
            "⬇ Tải hồ sơ đính kèm",
            data=attachments_zip_bytes(pid),
            file_name=f"{pid}_Ho_so_dinh_kem.zip",
            mime="application/zip",
            use_container_width=True,
        )
        d3.download_button(
            "⬇ TẢI TOÀN BỘ DỰ ÁN – ZIP",
            data=project_full_zip_bytes(pid),
            file_name=f"{pid}_FULL_EXPORT_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

    with tab_all:
        st.markdown("### Toàn bộ tất cả dự án")
        st.warning(
            "Gói TẢI TOÀN BỘ chứa báo cáo Word, Excel, JSON, toàn bộ CSV, hồ sơ đính kèm và bản sao SQLite deliveryos.db."
        )
        a1,a2,a3 = st.columns(3)
        a1.download_button(
            "⬇ Báo cáo danh mục Word",
            data=portfolio_word_bytes(),
            file_name=f"DeliveryOS_Bao_cao_danh_muc_{date.today()}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
        a2.download_button(
            "⬇ Toàn bộ dữ liệu Excel",
            data=portfolio_excel_bytes(),
            file_name=f"DeliveryOS_Toan_bo_du_lieu_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        a3.download_button(
            "⬇ Toàn bộ dữ liệu JSON",
            data=portfolio_json_bytes(),
            file_name=f"DeliveryOS_Toan_bo_du_lieu_{date.today()}.json",
            mime="application/json",
            use_container_width=True,
        )

        b1,b2,b3 = st.columns(3)
        b1.download_button(
            "⬇ Toàn bộ CSV",
            data=raw_csv_zip_bytes(None),
            file_name=f"DeliveryOS_Toan_bo_CSV_{date.today()}.zip",
            mime="application/zip",
            use_container_width=True,
        )
        b2.download_button(
            "⬇ Toàn bộ hồ sơ đính kèm",
            data=attachments_zip_bytes(None),
            file_name=f"DeliveryOS_Ho_so_dinh_kem_{date.today()}.zip",
            mime="application/zip",
            use_container_width=True,
        )
        if DB_PATH.exists():
            b3.download_button(
                "⬇ Sao lưu SQLite",
                data=DB_PATH.read_bytes(),
                file_name=f"deliveryos_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                mime="application/octet-stream",
                use_container_width=True,
            )

        st.download_button(
            "⬇⬇ TẢI ĐỒNG LOẠT TẤT CẢ DỮ LIỆU – FULL ZIP",
            data=portfolio_full_zip_bytes(),
            file_name=f"AI_KOS_DeliveryOS_FULL_EXPORT_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

        st.caption(
            "FULL ZIP là gói bàn giao/khôi phục thuận tiện nhất: Word + Excel + JSON + CSV + hồ sơ đính kèm + SQLite + MANIFEST."
        )

    with tab_restore:
        st.markdown("### Khôi phục từ bản sao lưu SQLite")
        st.warning(
            "Khôi phục sẽ thay toàn bộ dữ liệu hiện tại bằng file sao lưu. Chỉ dùng khi thật sự cần và nên tải FULL ZIP trước khi khôi phục."
        )
        restore = st.file_uploader("Chọn file deliveryos.db đã sao lưu", type=["db"])
        confirm = st.checkbox("Tôi xác nhận muốn thay dữ liệu hiện tại bằng bản sao lưu")
        if restore and confirm and st.button("Khôi phục dữ liệu", type="primary"):
            DB_PATH.write_bytes(restore.getvalue())
            st.success("Đã khôi phục. Ứng dụng sẽ tải lại.")
            st.rerun()

    st.info(
        "Chuẩn xuất dữ liệu V0.6.1: DOCX / XLSX / CSV / JSON / SQLite DB / ZIP. "
        "Các sản phẩm khác trong hệ sinh thái có thể bổ sung PDF, GeoJSON, KML, DXF/CAD... tùy nghiệp vụ."
    )
