from core.runtime import *
from core.portfolio_center import (
    portfolio_ranking,
    portfolio_summary,
    portfolio_message,
    money_short,
)

VIEW_TITLE = "00A. Trung tâm điều hành danh mục"

def render(ctx):
    st.subheader("Trung tâm điều hành nhiều dự án")
    st.caption(
        "So sánh toàn bộ danh mục trên một màn hình: tiến độ, chi phí, phát sinh, "
        "thanh toán, nghiệm thu và bảo hành/bảo trì."
    )

    ranking = portfolio_ranking()
    summary = portfolio_summary(ranking)

    if ranking.empty:
        st.info("Chưa có dự án để tổng hợp.")
        return

    # -----------------------------------------------------
    # KPI toàn danh mục
    # -----------------------------------------------------
    a,b,c,d = st.columns(4)
    a.metric("Số dự án", summary["projects"])
    b.metric("Tổng ngân sách", money_short(summary["budget"]))
    c.metric("Tổng dự báo cuối kỳ", money_short(summary["forecast"]))
    d.metric(
        "Dự báo vượt ngân sách",
        money_short(summary["overrun"]),
        "Cần kiểm soát" if summary["overrun"] > 0 else "Trong ngân sách",
        delta_color="inverse" if summary["overrun"] > 0 else "normal"
    )

    e,f,g,h = st.columns(4)
    e.metric("Rủi ro rất cao", summary["red"])
    f.metric("Rủi ro cao", summary["orange"])
    g.metric("Việc quá hạn", summary["overdue_work"])
    h.metric(
        "Còn phải thanh toán",
        money_short(summary["outstanding"]),
        delta_color="inverse"
    )

    if summary["red"] > 0:
        st.error(portfolio_message(summary, ranking))
    elif summary["orange"] > 0:
        st.warning(portfolio_message(summary, ranking))
    else:
        st.success(portfolio_message(summary, ranking))

    # -----------------------------------------------------
    # Xếp hạng
    # -----------------------------------------------------
    st.markdown("### Xếp hạng rủi ro dự án")

    display = ranking.copy()
    display.insert(0, "Xếp hạng", range(1, len(display)+1))

    for col in ["Ngân sách","Dự báo","Chênh dự báo","Còn phải trả","Giá trị PS chờ"]:
        display[col] = display[col].apply(money_short)

    display["KH (%)"] = display["KH (%)"].apply(lambda x: f"{x:.0f}%")
    display["TT (%)"] = display["TT (%)"].apply(lambda x: f"{x:.0f}%")
    display["Chênh tiến độ"] = display["Chênh tiến độ"].apply(lambda x: f"{x:.0f} điểm %")

    display = display[
        [
            "Xếp hạng","Mức","Điểm rủi ro","Mức rủi ro","Mã dự án","Dự án",
            "KH (%)","TT (%)","Chênh tiến độ",
            "Ngân sách","Dự báo","Chênh dự báo",
            "Việc quá hạn","PS chờ duyệt","NT còn lỗi",
            "BH/BT 30 ngày","Còn phải trả"
        ]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # Biểu đồ rủi ro
    # -----------------------------------------------------
    st.markdown("### So sánh điểm rủi ro")
    chart = ranking[["Dự án","Điểm rủi ro"]].copy().set_index("Dự án")
    st.bar_chart(chart)

    # -----------------------------------------------------
    # Top 3
    # -----------------------------------------------------
    st.markdown("### 3 dự án cần ưu tiên điều hành")
    for i, (_, r) in enumerate(ranking.head(3).iterrows(), start=1):
        reasons = []
        if r["Chênh tiến độ"] < 0:
            reasons.append(f"chậm {abs(r['Chênh tiến độ']):.0f} điểm %")
        if r["Chênh dự báo"] > 0:
            reasons.append(f"dự báo vượt {money_short(r['Chênh dự báo'])}")
        if r["Việc quá hạn"] > 0:
            reasons.append(f"{int(r['Việc quá hạn'])} việc quá hạn")
        if r["PS chờ duyệt"] > 0:
            reasons.append(f"{int(r['PS chờ duyệt'])} phát sinh chờ duyệt")
        if r["NT còn lỗi"] > 0:
            reasons.append(f"{int(r['NT còn lỗi'])} nghiệm thu còn lỗi")
        if r["Còn phải trả"] > 0:
            reasons.append(f"còn phải trả {money_short(r['Còn phải trả'])}")
        reason_text = "; ".join(reasons) if reasons else "chưa có rủi ro nổi bật"

        st.write(
            f"**{i}. {r['Mức']} {r['Dự án']} – {r['Điểm rủi ro']}/100 điểm**  \n"
            f"{reason_text}."
        )

    # -----------------------------------------------------
    # Chi tiết một dự án trong bảng xếp hạng
    # -----------------------------------------------------
    st.markdown("### Soi nhanh một dự án")
    selected = st.selectbox(
        "Chọn dự án trong bảng xếp hạng",
        ranking["Mã dự án"].tolist(),
        format_func=lambda x: (
            f"{x} – "
            + ranking.loc[ranking["Mã dự án"]==x, "Dự án"].iloc[0]
        )
    )
    r = ranking[ranking["Mã dự án"] == selected].iloc[0]

    p1,p2,p3,p4 = st.columns(4)
    p1.metric("Điểm rủi ro", f"{r['Điểm rủi ro']}/100")
    p2.metric("Chênh tiến độ", f"{r['Chênh tiến độ']:.0f} điểm %")
    p3.metric(
        "Chênh dự báo",
        money_short(r["Chênh dự báo"]),
        delta_color="inverse"
    )
    p4.metric("Còn phải trả", money_short(r["Còn phải trả"]))

    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Việc quá hạn", int(r["Việc quá hạn"]))
    q2.metric("Phát sinh chờ duyệt", int(r["PS chờ duyệt"]))
    q3.metric("Nghiệm thu còn lỗi", int(r["NT còn lỗi"]))
    q4.metric(
        "BH/BT cần theo dõi",
        int(r["BH/BT 30 ngày"] + r["BH/BT quá hạn"])
    )

    with st.expander("Cách tính điểm rủi ro – để người dùng kiểm tra được"):
        st.markdown(
            """
Điểm rủi ro là **chỉ báo quản trị**, tối đa 100 điểm. Hệ thống đọc dữ liệu hiện có và cộng điểm theo các nhóm:

- **Tiến độ:** tối đa 30 điểm, dự án càng chậm kế hoạch càng tăng điểm.
- **Chi phí:** tối đa 35 điểm, dự báo vượt ngân sách làm tăng mạnh điểm.
- **Công việc quá hạn:** tối đa 20 điểm.
- **Phát sinh chờ duyệt:** tối đa 10 điểm.
- **Thanh toán còn thiếu:** tối đa 10 điểm.
- **Nghiệm thu còn lỗi/quá hạn khắc phục:** tăng điểm theo mức độ.
- **Bảo hành/bảo trì đến hạn hoặc quá hạn:** tăng điểm theo số lượng.

Một vấn đề có thể ảnh hưởng nhiều chiều quản trị. Điểm này dùng để **xếp thứ tự chú ý**, không thay thế quyết định của người có thẩm quyền.
            """
        )

    st.info(
        "V0.6.0 chỉ đọc và tổng hợp dữ liệu để xếp hạng. "
        "Không tự thay đổi tiến độ, ngân sách, phát sinh, nghiệm thu hoặc thanh toán."
    )
