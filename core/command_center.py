import pandas as pd

from core.runtime import read_df, money, vi_date

TODAY = pd.Timestamp.today().normalize()

def _project_names():
    df = read_df("SELECT project_id, project_name FROM projects")
    if df.empty:
        return {}
    return dict(zip(df["project_id"], df["project_name"]))

def _scope_where(pid):
    return (" WHERE project_id=?", (pid,)) if pid else ("", ())

def command_actions(pid=None):
    """Tạo danh sách việc ưu tiên từ dữ liệu hiện có, không sửa dữ liệu gốc."""
    where, params = _scope_where(pid)
    names = _project_names()
    rows = []

    # 1) Công việc quá hạn / sắp đến hạn
    work = read_df(f"SELECT * FROM work_items{where}", params)
    if not work.empty:
        due = pd.to_datetime(work["planned_finish"], errors="coerce")
        active = work["status"].fillna("") != "Hoàn thành"

        for idx, r in work[active & (due < TODAY)].iterrows():
            d = pd.to_datetime(r["planned_finish"], errors="coerce")
            days = max((TODAY - d).days, 0) if pd.notna(d) else 0
            score = min(100, 90 + min(days, 10))
            rows.append({
                "Ưu tiên": score,
                "Mức": "🔴",
                "Nhóm": "Tiến độ",
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["work_name"],
                "Lý do": f"Quá hạn {days} ngày; hạn {vi_date(r['planned_finish'])}",
                "Giá trị": "",
            })

        soon = work[active & (due >= TODAY) & (due <= TODAY + pd.Timedelta(days=7))]
        for _, r in soon.iterrows():
            d = pd.to_datetime(r["planned_finish"], errors="coerce")
            days = max((d - TODAY).days, 0) if pd.notna(d) else 7
            score = 65 + max(0, 7-days)
            rows.append({
                "Ưu tiên": score,
                "Mức": "🟡",
                "Nhóm": "Tiến độ",
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["work_name"],
                "Lý do": f"Sắp đến hạn trong {days} ngày; hạn {vi_date(r['planned_finish'])}",
                "Giá trị": "",
            })

    # 2) Phát sinh chờ duyệt
    changes = read_df(f"SELECT * FROM changes{where}", params)
    if not changes.empty:
        pending = changes[changes["approval_status"].fillna("") == "Chờ duyệt"]
        for _, r in pending.iterrows():
            value = float(r["proposed_value"] or 0)
            rows.append({
                "Ưu tiên": 82,
                "Mức": "🟠",
                "Nhóm": "Phát sinh",
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["description"],
                "Lý do": "Phát sinh đang chờ duyệt",
                "Giá trị": money(value),
            })

    # 3) Thanh toán còn thiếu
    payments = read_df(f"SELECT * FROM payments{where}", params)
    if not payments.empty:
        payments = payments.copy()
        payments["remain"] = (
            payments["approved_value"].fillna(0) - payments["paid_value"].fillna(0)
        ).clip(lower=0)
        pending_pay = payments[payments["remain"] > 0]
        for _, r in pending_pay.iterrows():
            rows.append({
                "Ưu tiên": 85,
                "Mức": "🟠",
                "Nhóm": "Thanh toán",
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["tranche"] or r["payment_id"],
                "Lý do": "Khoản đã duyệt nhưng chưa thanh toán đủ",
                "Giá trị": money(r["remain"]),
            })

    # 4) Nghiệm thu có lỗi/tồn tại
    acc = read_df(f"SELECT * FROM acceptances{where}", params)
    if not acc.empty:
        defects = acc[acc["defects"].fillna("").str.strip() != ""]
        for _, r in defects.iterrows():
            due = pd.to_datetime(r["correction_due"], errors="coerce")
            overdue = pd.notna(due) and due < TODAY
            score = 96 if overdue else 78
            reason = (
                f"Quá hạn khắc phục; hạn {vi_date(r['correction_due'])}"
                if overdue else
                f"Còn lỗi/tồn tại; hạn khắc phục {vi_date(r['correction_due'])}"
            )
            rows.append({
                "Ưu tiên": score,
                "Mức": "🔴" if overdue else "🟠",
                "Nhóm": "Nghiệm thu",
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["defects"],
                "Lý do": reason,
                "Giá trị": money(r["accepted_value"]),
            })

    # 5) Bảo hành / bảo trì
    wm = read_df(f"SELECT * FROM warranty_maintenance{where}", params)
    if not wm.empty:
        due = pd.to_datetime(wm["due_date"], errors="coerce")
        active = wm["status"].fillna("") != "Hoàn thành"

        overdue_wm = wm[active & (due < TODAY)]
        for _, r in overdue_wm.iterrows():
            rows.append({
                "Ưu tiên": 92,
                "Mức": "🔴",
                "Nhóm": r["wm_type"],
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["asset_item"],
                "Lý do": f"Quá hạn; hạn {vi_date(r['due_date'])}",
                "Giá trị": money(r["cost"]),
            })

        soon_wm = wm[active & (due >= TODAY) & (due <= TODAY + pd.Timedelta(days=30))]
        for _, r in soon_wm.iterrows():
            days = max((pd.to_datetime(r["due_date"]) - TODAY).days, 0)
            score = 72 if days <= 7 else 55
            rows.append({
                "Ưu tiên": score,
                "Mức": "🟡",
                "Nhóm": r["wm_type"],
                "Mã dự án": r["project_id"],
                "Dự án": names.get(r["project_id"], ""),
                "Việc cần xử lý": r["asset_item"],
                "Lý do": f"Đến hạn trong {days} ngày; {vi_date(r['due_date'])}",
                "Giá trị": money(r["cost"]),
            })

    cols = ["Ưu tiên","Mức","Nhóm","Mã dự án","Dự án","Việc cần xử lý","Lý do","Giá trị"]
    if not rows:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(rows)
    return df.sort_values(["Ưu tiên","Mã dự án"], ascending=[False, True]).reset_index(drop=True)

def portfolio_metrics(pid=None):
    actions = command_actions(pid)
    if actions.empty:
        return {
            "total": 0, "red": 0, "overdue": 0, "soon": 0,
            "pending_changes": 0, "payment_due": 0, "defects": 0, "maintenance": 0
        }

    return {
        "total": len(actions),
        "red": int((actions["Mức"] == "🔴").sum()),
        "overdue": int(actions["Lý do"].str.contains("Quá hạn", na=False).sum()),
        "soon": int(actions["Lý do"].str.contains("Sắp đến hạn|Đến hạn trong", regex=True, na=False).sum()),
        "pending_changes": int((actions["Nhóm"] == "Phát sinh").sum()),
        "payment_due": int((actions["Nhóm"] == "Thanh toán").sum()),
        "defects": int((actions["Nhóm"] == "Nghiệm thu").sum()),
        "maintenance": int(actions["Nhóm"].isin(["Bảo hành","Bảo trì"]).sum()),
    }

def project_command_summary(pid, project, work, costs, changes):
    budget = float(project["budget"] or 0)
    forecast = float(costs["forecast_final"].sum()) if not costs.empty else 0
    planned = float(project["planned_progress"] or 0)
    actual = float(project["actual_progress"] or 0)
    gap = actual - planned

    pay = read_df("SELECT * FROM payments WHERE project_id=?", (pid,))
    outstanding = 0.0
    if not pay.empty:
        outstanding = float(
            (pay["approved_value"].fillna(0)-pay["paid_value"].fillna(0))
            .clip(lower=0).sum()
        )

    acc = read_df("SELECT * FROM acceptances WHERE project_id=?", (pid,))
    defect_count = 0
    overdue_defects = 0
    if not acc.empty:
        defect_mask = acc["defects"].fillna("").str.strip() != ""
        defect_count = int(defect_mask.sum())
        correction = pd.to_datetime(acc["correction_due"], errors="coerce")
        overdue_defects = int((defect_mask & (correction < TODAY)).sum())

    pending = changes[changes["approval_status"].fillna("") == "Chờ duyệt"] if not changes.empty else changes
    pending_change_value = float(pending["proposed_value"].sum()) if not pending.empty else 0

    wm = read_df("SELECT * FROM warranty_maintenance WHERE project_id=?", (pid,))
    maintenance_due = 0
    if not wm.empty:
        due = pd.to_datetime(wm["due_date"], errors="coerce")
        maintenance_due = int(
            ((wm["status"].fillna("")!="Hoàn thành") &
             (due >= TODAY) &
             (due <= TODAY + pd.Timedelta(days=30))).sum()
        )

    actions = command_actions(pid)

    # Xếp mức điều hành
    if overdue_defects > 0 or (budget > 0 and forecast > budget) or gap <= -10:
        health = "🔴 Cần xử lý ngay"
    elif len(actions) > 0 or gap < 0:
        health = "🟠 Cần theo dõi sát"
    else:
        health = "🟢 Trong tầm kiểm soát"

    return {
        "budget": budget,
        "forecast": forecast,
        "variance": forecast-budget,
        "planned": planned,
        "actual": actual,
        "gap": gap,
        "paid": float(project["paid"] or 0),
        "outstanding": outstanding,
        "pending_changes": len(pending),
        "pending_change_value": pending_change_value,
        "defect_count": defect_count,
        "overdue_defects": overdue_defects,
        "maintenance_due": maintenance_due,
        "health": health,
        "actions": actions,
    }

def operating_message(metrics):
    if metrics["total"] == 0:
        return "Không có việc ưu tiên nổi bật trong phạm vi đang xem."
    parts = []
    if metrics["red"]:
        parts.append(f"{metrics['red']} việc mức đỏ")
    if metrics["overdue"]:
        parts.append(f"{metrics['overdue']} việc quá hạn")
    if metrics["pending_changes"]:
        parts.append(f"{metrics['pending_changes']} phát sinh chờ duyệt")
    if metrics["payment_due"]:
        parts.append(f"{metrics['payment_due']} khoản còn phải thanh toán")
    if metrics["defects"]:
        parts.append(f"{metrics['defects']} nghiệm thu còn lỗi/tồn tại")
    if metrics["maintenance"]:
        parts.append(f"{metrics['maintenance']} lịch bảo hành/bảo trì cần theo dõi")
    return "Ưu tiên điều hành: " + "; ".join(parts) + "."
