"""Unit tests for the cleaning and validation logic (synthetic data) plus one real-data check."""
from __future__ import annotations

import config
import etl_lib
import pandas as pd
import pytest

SECTION = "B. Payment Systems"
MONTHS = pd.date_range("2024-01-01", periods=6, freq="MS")


def make_raw(series: dict[str, dict[str, list]], section: str = SECTION) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build (raw_long, header_meta) from {label: {"volume": [...], "value": [...]}}; None -> '-'."""
    rows, heads = [], []
    for col, (label, metrics) in enumerate(series.items(), start=2):
        code = etl_lib.make_slug(label)
        for metric, values in metrics.items():
            heads.append({"source_col": col, "section": section, "sub_section": "", "indicator_label": label,
                          "indicator_code": code, "metric": metric, "unit_raw": config.EXPECTED_UNITS[metric]})
            for m, v in zip(MONTHS, values):
                rows.append({"source_row": 1, "source_col": col, "month_date": m.date().isoformat(),
                             "section": section, "sub_section": "", "indicator_label": label,
                             "indicator_code": code, "metric": metric,
                             "unit_raw": config.EXPECTED_UNITS[metric], "value_raw": "-" if v is None else v})
    return pd.DataFrame(rows), pd.DataFrame(heads)


def test_parse_month_and_bad_input():
    assert etl_lib.parse_month("Aug-2026") == pd.Timestamp("2026-08-01")
    assert pd.isna(etl_lib.parse_month("not a month"))


def test_parse_label_code_name_marker():
    assert etl_lib.parse_label("2.7 UPI @") == ("2.7", "UPI", "@")
    assert etl_lib.parse_label("1   CCIL Operated Systems (1.1 to 1.3)")[:2] == ("1", "CCIL Operated Systems (1.1 to 1.3)")
    assert etl_lib.parse_label("Total Payments (1+2+3+4+5+6)")[0] is None
    assert etl_lib.make_slug("2.7 UPI @") == "2_7_upi"
    assert len(etl_lib.make_slug("x" * 200)) == 60


def test_hierarchy_levels_parents_and_section_collision():
    ind = pd.DataFrame({
        "section": [SECTION, SECTION, SECTION, "B. ATMs"],
        "sub_section": [""] * 4,
        "indicator_label": ["2 Credit Transfers (2.1 to 2.7)", "2.7 UPI @", "2.7.1 of which USSD @", "2 Other thing"],
    })
    ind["indicator_code"] = ind["indicator_label"].map(etl_lib.make_slug)
    out = etl_lib.add_hierarchy(ind).set_index("code_number", drop=False)
    assert list(out["hierarchy_level"]) == [1, 2, 3, 1]
    ussd = out[out["indicator_name"].str.contains("USSD")].iloc[0]
    assert ussd["parent_code_number"] == "2.7" and ussd["is_of_which"]
    upi = out[out["indicator_name"] == "UPI"].iloc[0]
    assert upi["has_children"] and upi["analysis_role"] == "instrument"
    # code "2" exists in two sections; each must resolve to its own section
    assert out["kpi_scope"].tolist().count("channel_view") == 1


def test_clean_long_explains_every_dash_and_keeps_zero():
    raw, heads = make_raw({"1 Alpha": {"volume": [None, 1.0, 0.0, 2.0, None, None], "value": [5, 6, 7, 8, 9, 10]}})
    clean, rejected, stats = etl_lib.clean_long(raw, heads)
    assert stats["raw_rows_in"] == len(raw) == 12
    assert stats["rows_after_cleaning"] + stats["rows_rejected"] == 12
    reasons = rejected["reject_reason"].value_counts().to_dict()
    assert reasons == {"leading_gap_not_yet_reported": 1, "trailing_gap_series_ended": 2}
    assert int(clean["is_zero"].sum()) == 1          # zero kept and flagged, not dropped
    assert set(clean["unit"]) == {"lakh", "INR crore"}


def test_clean_long_removes_duplicate_keys():
    raw, heads = make_raw({"1 Alpha": {"volume": [1, 2, 3, 4, 5, 6]}})
    raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    clean, _rejected, stats = etl_lib.clean_long(raw, heads)
    assert stats["duplicates_removed"] == 1 and len(clean) == 6


def _hierarchy_fixture(break_month: int | None):
    child_a, child_b = [10.0] * 6, [5.0] * 6
    parent = [15.0] * 6
    if break_month is not None:
        parent[break_month] = 18.0
    raw, heads = make_raw({"2 Parent (2.1 to 2.2)": {"value": parent},
                           "2.1 Child A": {"value": child_a}, "2.2 Child B": {"value": child_b},
                           "2.2.1 of which sub": {"value": [99.0] * 6}})
    clean, _, _ = etl_lib.clean_long(raw, heads)
    return clean


def test_hierarchy_check_passes_on_consistent_data_and_ignores_of_which():
    parents, comparisons, viol = etl_lib.hierarchy_violations(_hierarchy_fixture(None), config.SUM_TOLERANCE)
    assert parents >= 1 and comparisons == 6 and viol.empty


def test_hierarchy_check_detects_injected_error():
    _, _, viol = etl_lib.hierarchy_violations(_hierarchy_fixture(3), config.SUM_TOLERANCE)
    assert len(viol) == 1 and viol.iloc[0]["difference"] == pytest.approx(3.0)


def test_totals_check_flags_group_missing_from_sum():
    """Mirrors the real Sep-2023 case: a group is '-' but the reported total still includes it."""
    groups = {f"{n} Group {n}": {"volume": [10.0] * 6} for n in range(1, 7)}
    groups["5 Group 5"] = {"volume": [10.0, 10.0, None, 10.0, 10.0, 10.0]}
    groups["Total Payments (1+2+3+4+5+6)"] = {"volume": [60.0] * 6}
    raw, heads = make_raw(groups)
    clean, _, _ = etl_lib.clean_long(raw, heads)
    comparisons, viol = etl_lib.totals_violations(clean, config.SUM_TOLERANCE)
    assert comparisons == 6 and len(viol) == 1
    assert viol.iloc[0]["difference"] == pytest.approx(10.0)


def test_outlier_flag_catches_shock_but_not_trend():
    values = [100 * 1.02 ** i for i in range(30)]
    values[15] = values[14] * 0.4                      # sudden 60 percent drop
    df = pd.DataFrame({"indicator_code": "x", "metric": "volume",
                       "month_date": [d.date().isoformat() for d in pd.date_range("2020-01-01", periods=30, freq="MS")],
                       "value": values})
    flags = etl_lib.flag_outliers(df, z_threshold=6.0, min_points=12)
    assert flags.sum() >= 1 and flags.iloc[15]


@pytest.mark.skipif(not config.RAW_EXCEL.exists(), reason="raw RBI file not present")
def test_real_rbi_file_end_to_end_counts():
    raw, heads, info = etl_lib.read_raw_excel(config.RAW_EXCEL)
    clean, rejected, _stats = etl_lib.clean_long(raw, heads)
    assert info["months"] == 82 and info["indicators"] == 70 and len(raw) == 11480
    assert len(clean) + len(rejected) == len(raw)
    assert (set(clean["unit"]) == {"lakh", "INR crore"}) and not clean.duplicated(etl_lib.KEY_COLS).any()
    parents, _comparisons, viol = etl_lib.hierarchy_violations(clean, config.SUM_TOLERANCE)
    assert parents == 19 and viol.empty
