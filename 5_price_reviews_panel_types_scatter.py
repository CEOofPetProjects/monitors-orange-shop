import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=";")
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"]) # string to pandas datetime
df['snapshot_date'] = df['snapshot_datetime'].dt.date # datetime to date
latest_date = df['snapshot_date'].max()
df = df[df['snapshot_date'] == latest_date].copy()
df["reviews_count"] = pd.to_numeric(df["reviews_count"], errors="coerce").fillna(0) # force reviews column to numeric, turn errors to NaN, replace NaN with 0

# calculating relative rank percentiles (method='first' breaks ties sequentially)
df["reviews_pct"] = df["reviews_count"].rank(method='first', pct=True) * 100
df["price_pct"] = df["price"].rank(method='first', pct=True) * 100

def categorize_panel(panel_string):
    if not isinstance(panel_string, str): return "Other"
    p = panel_string.upper()
    if "OLED" in p: return "OLED"
    elif "IPS" in p: return "IPS"
    elif "VA" in p: return "VA"
    elif "TN" in p: return "TN"
    else: return "Other"

df["panel_category"] = df["panel_type"].apply(categorize_panel)
colors = {"IPS": "#1982c4", "VA": "#ff595e", "OLED": "#8ac926", "TN": "#ffca3a", "Other": "#9d4edd"}
panel_order = ["IPS", "VA", "OLED", "TN", "Other"]

fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)

for m_type in panel_order: # drawing scatter plot dots
    sub = df[df["panel_type"] == m_type]
    ax.scatter(
        sub["reviews_pct"], # reviews percentile as x-axis
        sub["price_pct"], # price percentile as y-axis
        c=colors.get(m_type, "#cccccc"),
        label=m_type,
        alpha=0.55,
        s=35,
        edgecolors="white",
        linewidths=0.5,
        zorder=2,
    )

quartiles = [0.25, 0.50, 0.75]
for q in quartiles:
    pct_val = q * 100
    price_val = df["price"].quantile(q)  # price to quantile-quartile value
    ax.axhline(y=pct_val, color="gray", linestyle="--", alpha=0.6, linewidth=1, zorder=1) # horizontal quantile border
    ax.text(
        99,
        pct_val + 0.8,
        f"{price_val:,.0f} ₽",
        color="dimgray",
        fontsize=9,
        fontweight="bold",
        ha="right",
        va="bottom",
        bbox=dict(
            boxstyle="square,pad=0.1",
            facecolor="white",
            edgecolor="none",
            alpha=0.8,
        ),
    )

ax.set_xlabel("reviews percentile rank (% of market volume)", fontsize=11, labelpad=8)
ax.set_ylabel("price percentile rank (% of market volume)", fontsize=11, labelpad=8)
ax.set_title(
    "PRICE VS REVIEW VOLUME DISTRIBUTION BY PANEL TYPE",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.grid(True, linestyle=":", alpha=0.4)
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12),
    ncol=5,
    frameon=True,
    facecolor="white",
    edgecolor="lightgray",
    fontsize=10,
    title="panel type",
    title_fontsize=10,
)

plt.tight_layout()
plt.savefig("visualizations/price_reviews_panel_scatter.png", dpi=300)
plt.close()
