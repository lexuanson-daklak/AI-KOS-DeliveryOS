from core.runtime import *
from core.command_center import command_actions, portfolio_metrics, operating_message

VIEW_TITLE = "00. Hôm nay cần làm gì?"

def render(ctx):
    pid = ctx["pid"]

    st.subheader("Bảng điều hành hôm nay")
    st.caption(
        "Tự tổng hợp các việc cần chú ý từ tiến độ, phát sinh, thanh toán, "
        "nghiệm thu và bảo hành/bảo trì."
    )

    scope = st.radio(
        "Phạm vi điều hành",
        ["Tất cả dự án", "Dự án đang chọn"],
        horizontal=True
    )
    active_pid = pid if scope == "Dự án đang chọn" else None

    actions = command_actions(active_pid)
    m = portfolio_metrics(active_pid)

    a,b,c,d = st.columns(4)
    a.metric("Tổng việc cần chú ý", m["total"])
    b.metric("Mức đỏ", m["red"])
    c.metric("Quá hạn", m["overdue"])
    d.metric("Sắp đến hạn", m["soon"])

    e,f,g,h = st.columns(4)
    e.metric("Phát sinh chờ duyệt", m["pending_changes"])
    f.metric("Khoản còn phải trả", m["payment_due"])
    g.metric("Nghiệm thu còn lỗi", m["defects"])
    h.metric("Bảo hành/bảo trì", m["maintenance"])

    if m["red"] > 0:
        st.error(operating_message(m))
    elif m["total"] > 0:
        st.warning(operating_message(m))
    else:
        st.success(operating_message(m))

    st.markdown("### Việc ưu tiên theo thứ tự xử lý")
    if actions.empty:
        st.success("Hiện chưa có việc ưu tiên nổi bật.")
    else:
        display = actions.copy()
        display["Mức ưu tiên"] = display["Ưu tiên"].apply(
            lambda x: "Rất cao" if x >= 90 else ("Cao" if x >= 80 else ("Trung bình" if x >= 65 else "Theo dõi"))
        )
        display = display[
            ["Mức","Mức ưu tiên","Nhóm","Mã dự án","Dự án","Việc cần xử lý","Lý do","Giá trị"]
        ]
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.markdown("### 5 việc nên xử lý trước")
        for i, (_, r) in enumerate(actions.head(5).iterrows(), start=1):
            value = f" – {r['Giá trị']}" if str(r["Giá trị"]).strip() else ""
            st.write(
                f"**{i}. {r['Mức']} {r['Dự án']}** – {r['Việc cần xử lý']}{value}  \n"
                f"{r['Lý do']}"
            )

    st.info(
        "AI ở V0.5.0 mới làm nhiệm vụ tổng hợp, xếp ưu tiên và cảnh báo theo quy tắc. "
        "Không tự duyệt phát sinh, không tự nghiệm thu và không tự thay đổi số tiền."
    )
