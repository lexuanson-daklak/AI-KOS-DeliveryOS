import pandas as pd

from core.runtime import read_df

TODAY = pd.Timestamp.today().normalize()

def money_short(x):
    try:
        value = float(x or 0)
    except Exception:
        value = 0.0

    sign = "-" if value < 0 else ""
    v = abs(value)

    if v >= 1_000_000_000:
        return f"{sign}{v/1_000_000_000:.2f}".replace(".", ",") + " tỷ"
    if v >= 1_000_000:
        m = v / 1_000_000
        txt = f"{m:.0f}" if abs(m-round(m)) < 1e-9 else f"{m:.1f}".replace(".", ",")
        return f"{sign}{txt} triệu"
    if v >= 1_000:
        return f"{sign}{v/1_000:.0f} nghìn"
    return f"{sign}{v:,.0f} đ".replace(",", ".")

def _risk_label(score):
    if score >= 70:
        return "🔴 Rất cao"
    if score >= 50:
        return "🟠 Cao"
    if score >= 30:
        return "🟡 Trung bình"
    return "🟢 Thấp"

def _risk_icon(score):
    if score >= 70:
        return "🔴"
    if score >= 50:
        return "🟠"
    if score >= 30:
        return "🟡"
    return "🟢"

def _one_project(project):
    pid = project["project_id"]

    costs = read_df("SELECT * FROM costs WHERE project_id=?", (pid,))
    work = read_df("SELECT * FROM work_items WHERE project_id=?", (pid,))
    changes = read_df("SELECT * FROM changes WHERE project_id=?", (pid,))
    payments = read_df("SELECT * FROM payments WHERE project_id=?", (pid,))
    acc = read_df("SELECT * FROM acceptances WHERE project_id=?", (pid,))
    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=?", (pid,))

    budget = float(project["budget"] or 0)
    forecast = float(costs["forecast_final"].fillna(0).sum()) if not costs.empty else 0
    variance = forecast - budget

    planned = float(project["planned_progress"] or 0)
    actual = float(project["actual_progress"] or 0)
    gap = actual - planned

    overdue_work = 0
    if not work.empty:
        due = pd.to_datetime(work["planned_finish"], errors="coerce")
        overdue_work = int(
            ((work["status"].fillna("") != "Hoàn thành") & (due < TODAY)).sum()
        )

    pending_changes = 0
    pending_change_value = 0.0
    if not changes.empty:
        pending = changes[changes["approval_status"].fillna("") == "Chờ duyệt"]
        pending_changes = len(pending)
        pending_change_value = float(pending["proposed_value"].fillna(0).sum())

    outstanding = 0.0
    if not payments.empty:
        outstanding = float(
            (
                payments["approved_value"].fillna(0)
                - payments["paid_value"].fillna(0)
            ).clip(lower=0).sum()
        )

    defect_count = 0
    overdue_defects = 0
    if not acc.empty:
        defect_mask = acc["defects"].fillna("").str.strip() != ""
        defect_count = int(defect_mask.sum())
        correction = pd.to_datetime(acc["correction_due"], errors="coerce")
        overdue_defects = int((defect_mask & (correction < TODAY)).sum())

    maintenance_due = 0
    overdue_maintenance = 0
    if not wm.empty:
        due = pd.to_datetime(wm["due_date"], errors="coerce")
        active = wm["status"].fillna("") != "Hoàn thành"
        maintenance_due = int(
            (active & (due >= TODAY) & (due <= TODAY + pd.Timedelta(days=30))).sum()
        )
        overdue_maintenance = int((active & (due < TODAY)).sum())

    # -----------------------------------------------------
    # Điểm rủi ro minh bạch, tối đa 100
    # -----------------------------------------------------
    score = 0.0

    # Tiến độ: tối đa 30
    if gap <= -20:
        score += 30
    elif gap <= -10:
        score += 25
    elif gap < 0:
        score += 10

    # Chi phí: tối đa 35
    if budget > 0 and variance > 0:
        over_ratio = variance / budget
        score += min(35, 25 + over_ratio * 100)
    elif budget > 0 and forecast > 0 and forecast >= budget * 0.95:
        score += 8

    # Công việc quá hạn: tối đa 20
    score += min(20, overdue_work * 5)

    # Phát sinh chờ duyệt: tối đa 10
    score += min(10, pending_changes * 3)

    # Thanh toán còn thiếu: tối đa 10
    if outstanding > 0:
        if budget > 0:
            score += min(10, 5 + 5 * outstanding / budget)
        else:
            score += 5

    # Nghiệm thu: tối đa khoảng 21
    score += min(15, overdue_defects * 7)
    remaining_defects = max(defect_count - overdue_defects, 0)
    score += min(6, remaining_defects * 2)

    # Bảo hành/bảo trì: tối đa 15
    score += min(10, overdue_maintenance * 5)
    score += min(5, maintenance_due * 2)

    score = int(round(min(score, 100)))

    return {
        "Mã dự án": pid,
        "Dự án": project["project_name"],
        "Loại dự án": project["project_type"],
        "Trạng thái": project["status"],
        "Điểm rủi ro": score,
        "Mức rủi ro": _risk_label(score),
        "Mức": _risk_icon(score),
        "Ngân sách": budget,
        "Dự báo": forecast,
        "Chênh dự báo": variance,
        "KH (%)": planned,
        "TT (%)": actual,
        "Chênh tiến độ": gap,
        "Đã thanh toán": float(project["paid"] or 0),
        "Còn phải trả": outstanding,
        "Việc quá hạn": overdue_work,
        "PS chờ duyệt": pending_changes,
        "Giá trị PS chờ": pending_change_value,
        "NT còn lỗi": defect_count,
        "NT quá hạn KP": overdue_defects,
        "BH/BT 30 ngày": maintenance_due,
        "BH/BT quá hạn": overdue_maintenance,
    }

def portfolio_ranking():
    projects = read_df("SELECT * FROM projects ORDER BY project_id")
    if projects.empty:
        return pd.DataFrame()

    rows = [_one_project(r) for _, r in projects.iterrows()]
    df = pd.DataFrame(rows)
    return df.sort_values(
        ["Điểm rủi ro", "Chênh tiến độ"],
        ascending=[False, True]
    ).reset_index(drop=True)

def portfolio_summary(ranking=None):
    df = ranking if ranking is not None else portfolio_ranking()
    if df.empty:
        return {
            "projects": 0,
            "budget": 0.0,
            "forecast": 0.0,
            "overrun": 0.0,
            "paid": 0.0,
            "outstanding": 0.0,
            "red": 0,
            "orange": 0,
            "yellow": 0,
            "green": 0,
            "overdue_work": 0,
            "pending_changes": 0,
            "defects": 0,
            "maintenance": 0,
        }

    return {
        "projects": len(df),
        "budget": float(df["Ngân sách"].sum()),
        "forecast": float(df["Dự báo"].sum()),
        "overrun": float(df["Chênh dự báo"].clip(lower=0).sum()),
        "paid": float(df["Đã thanh toán"].sum()),
        "outstanding": float(df["Còn phải trả"].sum()),
        "red": int((df["Điểm rủi ro"] >= 70).sum()),
        "orange": int(((df["Điểm rủi ro"] >= 50) & (df["Điểm rủi ro"] < 70)).sum()),
        "yellow": int(((df["Điểm rủi ro"] >= 30) & (df["Điểm rủi ro"] < 50)).sum()),
        "green": int((df["Điểm rủi ro"] < 30).sum()),
        "overdue_work": int(df["Việc quá hạn"].sum()),
        "pending_changes": int(df["PS chờ duyệt"].sum()),
        "defects": int(df["NT còn lỗi"].sum()),
        "maintenance": int((df["BH/BT 30 ngày"] + df["BH/BT quá hạn"]).sum()),
    }

def portfolio_message(summary, ranking):
    if summary["projects"] == 0:
        return "Chưa có dự án để điều hành."

    top = ranking.iloc[0]
    parts = [
        f"Danh mục có {summary['projects']} dự án",
        f"{summary['red']} dự án rủi ro rất cao",
        f"{summary['orange']} dự án rủi ro cao",
        f"{summary['overdue_work']} công việc quá hạn",
        f"{summary['pending_changes']} phát sinh chờ duyệt",
    ]
    if summary["overrun"] > 0:
        parts.append(f"dự báo vượt ngân sách cộng dồn {money_short(summary['overrun'])}")
    if summary["outstanding"] > 0:
        parts.append(f"còn phải thanh toán {money_short(summary['outstanding'])}")

    return (
        "; ".join(parts)
        + f". Dự án cần ưu tiên số 1: {top['Dự án']} – "
        + f"{top['Điểm rủi ro']}/100 điểm."
    )
