from core.runtime import *
from core.command_center import project_command_summary

VIEW_TITLE = "03. Tổng quan"

def money_short(x):
    """Hiển thị tiền gọn để KPI không bị cắt: tỷ / triệu / nghìn."""
    try:
        value = float(x or 0)
    except Exception:
        value = 0.0

    sign = "-" if value < 0 else ""
    v = abs(value)

    if v >= 1_000_000_000:
        text = f"{v/1_000_000_000:.2f}".replace(".", ",")
        return f"{sign}{text} tỷ"
    if v >= 1_000_000:
        value_m = v / 1_000_000
        if abs(value_m - round(value_m)) < 1e-9:
            text = f"{value_m:.0f}"
        else:
            text = f"{value_m:.1f}".replace(".", ",")
        return f"{sign}{text} triệu"
    if v >= 1_000:
        value_k = v / 1_000
        text = f"{value_k:.0f}"
        return f"{sign}{text} nghìn"
    return f"{sign}{v:,.0f} đ".replace(",", ".")

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]

    s = project_command_summary(pid, project, work, costs, changes)

    st.subheader(project["project_name"])
    st.caption(
        "Bảng điều hành dự án – nhìn một màn hình để biết dự án đang ở đâu và cần xử lý gì."
    )

    st.markdown(f"### {s['health']}")

    a,b,c,d = st.columns(4)
    a.metric("Ngân sách", money_short(s["budget"]))

    forecast_delta = (
        f"Vượt {money_short(s['variance'])}"
        if s["variance"] > 0
        else f"Còn {money_short(abs(s['variance']))}"
    )
    b.metric(
        "Dự báo cuối kỳ",
        money_short(s["forecast"]),
        forecast_delta,
        delta_color="inverse" if s["variance"] > 0 else "normal"
    )

    c.metric(
        "Tiến độ thực tế",
        f"{s['actual']:.0f}%",
        f"{s['gap']:.0f} điểm % so với KH"
    )
    d.metric("Đã thanh toán", money_short(s["paid"]))

    e,f,g,h = st.columns(4)
    e.metric("Còn phải thanh toán", money_short(s["outstanding"]))

    pending_delta = (
        f"{money_short(s['pending_change_value'])} đang chờ duyệt"
        if s["pending_changes"] > 0 else None
    )
    f.metric(
        "Phát sinh chờ duyệt",
        s["pending_changes"],
        pending_delta,
        delta_color="inverse"
    )

    defects_delta = (
        f"{s['overdue_defects']} quá hạn khắc phục"
        if s["overdue_defects"] > 0
        else ("Còn tồn tại cần xử lý" if s["defect_count"] > 0 else None)
    )
    g.metric(
        "Nghiệm thu còn lỗi",
        s["defect_count"],
        defects_delta,
        delta_color="inverse"
    )

    h.metric("BH/BT trong 30 ngày", s["maintenance_due"])

    st.markdown("### Tiến độ kế hoạch – thực tế")
    p1,p2,p3 = st.columns(3)
    p1.metric("Kế hoạch", f"{s['planned']:.0f}%")
    p2.metric("Thực tế", f"{s['actual']:.0f}%")
    p3.metric("Chênh lệch", f"{s['gap']:.0f} điểm %")
    st.progress(min(max(s["actual"]/100, 0), 1))

    st.markdown("### Cảnh báo điều hành hiện có")
    for icon,title,msg in alerts(project,work,changes,costs):
        st.write(f"{icon} **{title}:** {msg}")

    st.markdown("### Việc cần xử lý của dự án")
    actions = s["actions"]
    if actions.empty:
        st.success("Chưa có việc ưu tiên nổi bật.")
    else:
        show = actions[
            ["Mức","Nhóm","Việc cần xử lý","Lý do","Giá trị"]
        ].head(10)
        st.dataframe(show, use_container_width=True, hide_index=True)

        top = actions.iloc[0]
        st.warning(
            f"**Ưu tiên số 1:** {top['Nhóm']} – {top['Việc cần xử lý']}. "
            f"{top['Lý do']}"
        )

    st.caption(
        "Quy ước màu V0.5.1: số tăng ở các mục rủi ro như “Phát sinh chờ duyệt” "
        "và “Nghiệm thu còn lỗi” được hiển thị theo màu cảnh báo, không coi là tín hiệu tích cực."
    )
