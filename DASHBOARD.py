import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Mini Dashboard", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def make_demo_data(seed: int = 7, days: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=days - 1)
    dates = pd.date_range(start, end, freq="D")

    categories = np.array(["A", "B", "C", "D"])
    channels = np.array(["Web", "Mobile", "Store"])

    n = len(dates) * 30
    df = pd.DataFrame(
        {
            "date": rng.choice(dates, size=n, replace=True),
            "category": rng.choice(categories, size=n, replace=True, p=[0.35, 0.25, 0.25, 0.15]),
            "channel": rng.choice(channels, size=n, replace=True, p=[0.55, 0.35, 0.10]),
            "orders": rng.integers(1, 6, size=n),
        }
    )
    df["revenue"] = (df["orders"] * rng.normal(45, 12, size=n)).clip(8, None).round(2)
    df["cost"] = (df["revenue"] * rng.uniform(0.45, 0.7, size=n)).round(2)
    df["profit"] = (df["revenue"] - df["cost"]).round(2)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


st.title("📊 Mini Dashboard (דוגמה)")
st.caption("דשבורד קטן לדוגמה עם נתוני דמה, פילטרים, מדדים וגרפים.")

df = make_demo_data()

with st.sidebar:
    st.header("פילטרים")

    min_d = df["date"].min()
    max_d = df["date"].max()

    date_range = st.date_input(
        "טווח תאריכים",
        value=(max_d - dt.timedelta(days=29), max_d),
        min_value=min_d,
        max_value=max_d,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_d, max_d

    chosen_categories = st.multiselect(
        "קטגוריות",
        options=sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )
    chosen_channels = st.multiselect(
        "ערוצים",
        options=sorted(df["channel"].unique()),
        default=sorted(df["channel"].unique()),
    )

    st.divider()
    st.download_button(
        "הורד CSV (אחרי פילטרים)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="demo_data.csv",
        mime="text/csv",
    )


filtered = df[
    (df["date"] >= start_d)
    & (df["date"] <= end_d)
    & (df["category"].isin(chosen_categories))
    & (df["channel"].isin(chosen_channels))
].copy()

if filtered.empty:
    st.warning("אין נתונים אחרי הסינון. נסה להרחיב טווח תאריכים או לבחור עוד קטגוריות/ערוצים.")
    st.stop()


total_orders = int(filtered["orders"].sum())
total_revenue = float(filtered["revenue"].sum())
total_profit = float(filtered["profit"].sum())
margin = (total_profit / total_revenue) if total_revenue else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("סה״כ הזמנות", f"{total_orders:,}")
col2.metric("סה״כ הכנסות", f"₪{total_revenue:,.0f}")
col3.metric("סה״כ רווח", f"₪{total_profit:,.0f}")
col4.metric("רווחיות", f"{margin:.1%}")

st.divider()

left, right = st.columns([1.35, 1.0], gap="large")

with left:
    by_day = (
        filtered.groupby("date", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("orders", "sum"))
        .sort_values("date")
    )
    fig = px.line(
        by_day,
        x="date",
        y=["revenue", "profit"],
        markers=True,
        title="מגמה יומית: הכנסות ורווח",
        labels={"value": "₪", "variable": "מדד", "date": "תאריך"},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    by_cat = (
        filtered.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("orders", "sum"))
        .sort_values("revenue", ascending=False)
    )
    fig2 = px.bar(
        by_cat,
        x="category",
        y="revenue",
        color="category",
        title="הכנסות לפי קטגוריה",
        labels={"revenue": "₪", "category": "קטגוריה"},
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("טבלת נתונים (דגימה)")
st.dataframe(
    filtered.sort_values(["date", "revenue"], ascending=[False, False]).head(200),
    use_container_width=True,
    hide_index=True,
)
