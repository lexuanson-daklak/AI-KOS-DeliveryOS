from core.runtime import *
from core.command_center import project_command_summary

VIEW_TITLE = "03. Tổng quan"

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]

    s = project_command_summary(pid, project, work, costs, changes)

    st.subheader(project["project_name"])
    st.caption("Bảng điều hành dự án – nhìn một màn hình để biết dự án đang ở đâu và cần xử lý gì.")

    st.markdown(f"### {s['health']}")

    a,b,c,d = st.columns(4)
    a.metric("Ngân sách", money(s["budget"]))
    b.metric("Dự báo cuối kỳ", money(s["forecast"]),
             f"Vượt {money(s['variance'])}" if s["variance"] > 0 else f"Còn {money(abs(s['variance']))}",
             delta_color="inverse" if s["variance"] > 0 else "normal")
    c.metric("Tiến độ thực tế", f"{s['actual']:.0f}%",
             f"{s['gap']:.0f} điểm % so với KH")
    d.metric("Đã thanh toán", money(s["paid"]))

    e,f,g,h = st.columns(4)
    e.metric("Còn phải thanh toán", money(s["outstanding"]))
    f.metric("Phát sinh chờ duyệt", s["pending_changes"], money(s["pending_change_value"]))
    g.metric("Nghiệm thu còn lỗi", s["defect_count"],
             f"{s['overdue_defects']} quá hạn khắc phục")
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
