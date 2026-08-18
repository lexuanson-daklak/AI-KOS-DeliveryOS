from core.runtime import *

VIEW_TITLE = '07. Chi phí & dòng tiền'

def render(ctx):
    pid = ctx["pid"]
    project = ctx["project"]
    work = ctx["work"]
    costs = ctx["costs"]
    changes = ctx["changes"]
    st.subheader("Chi phí & dòng tiền")
    budget = float(project["budget"] or 0)
    committed = float(costs["committed"].sum()) if not costs.empty else 0
    actual = float(costs["actual_cost"].sum()) if not costs.empty else 0
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    a,b,c,d = st.columns(4)
    a.metric("Ngân sách",money(budget))
    b.metric("Cam kết/Hợp đồng",money(committed))
    c.metric("Chi thực tế",money(actual))
    if forecast > budget:
        d.metric("Dự báo cuối kỳ",money(forecast),f"Vượt {money(forecast-budget)}",delta_color="inverse")
    else:
        d.metric("Dự báo cuối kỳ",money(forecast),f"Còn {money(budget-forecast)}")

    if not costs.empty:
        cshow = costs[["cost_group","description","planned_budget","committed","actual_cost","forecast_final"]].copy()
        cshow = fmt_money_columns(cshow,["planned_budget","committed","actual_cost","forecast_final"])
        cshow = cshow.rename(columns={"cost_group":"Nhóm chi phí","description":"Nội dung","planned_budget":"Ngân sách KH",
                                      "committed":"Cam kết","actual_cost":"Chi thực tế","forecast_final":"Dự báo cuối kỳ"})
        st.dataframe(cshow,use_container_width=True,hide_index=True)

# =========================================================
# 08. NHẬT KÝ & HỒ SƠ
# =========================================================
