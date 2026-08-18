from core.runtime import *

VIEW_TITLE = '03. Tổng quan'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader(project["project_name"])
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    budget = float(project["budget"] or 0)
    variance = forecast-budget

    a,b,c,d = st.columns(4)
    a.metric("Ngân sách",money(budget))
    b.metric("Đã thanh toán",money(project["paid"]))
    c.metric("Tiến độ thực tế",f"{float(project['actual_progress'] or 0):.0f}%",
             f"{float(project['actual_progress'] or 0)-float(project['planned_progress'] or 0):.0f} điểm %")
    if variance > 0:
        d.metric("Dự báo cuối kỳ",money(forecast),f"Vượt {money(variance)}",delta_color="inverse")
    else:
        d.metric("Dự báo cuối kỳ",money(forecast),f"Còn {money(abs(variance))}")

    st.progress(min(max(float(project["actual_progress"] or 0)/100,0),1))
    st.markdown("### Cảnh báo điều hành")
    for icon,title,msg in alerts(project,work,changes,costs):
        st.write(f"{icon} **{title}:** {msg}")

# =========================================================
# 04. CÔNG VIỆC & TIẾN ĐỘ
# =========================================================
