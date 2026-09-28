import matplotlib.pyplot as plt
import pandas as pd
import re

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=";")
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])  # string to pandas datetime
df['snapshot_date'] = df['snapshot_datetime'].dt.date  # datetime to date
latest_date = df['snapshot_date'].max()
df = df[df['snapshot_date'] == latest_date].copy()
df["reviews_count"] = pd.to_numeric(df["reviews_count"], errors="coerce").fillna(0)  # force reviews column to numeric, turn errors to NaN, replace NaN with 0

# calculating relative rank percentiles (method='first' breaks ties sequentially)
df["reviews_pct"] = df["reviews_count"].rank(method='first', pct=True) * 100
df["price_pct"] = df["price"].rank(method='first', pct=True) * 100

def categorize_resolution(res_string):
    if not isinstance(res_string, str): return "Other" # empty row/NaN
    match = re.search(r'(\d+)\s*[xXхХ]\s*(\d+)', res_string) # handling spaces and Latin/Cyrillic characters
    if not match: return "Other"
    w, h = int(match.group(1)), int(match.group(2))
    if h == 0: return "Other" # for division by zero errors
    aspect_ratio = w / h
    if aspect_ratio > 1.78: return "Ultrawide"  # 16:9 is ~1.777 so anything >1.78 is wider
    elif w == 1920: return "FHD"
    elif w == 2560: return "QHD"
    elif w >= 3840: return "4K+"
    else: return "Other"

df["res_category"] = df["resolution_str"].apply(categorize_resolution)
colors = {"FHD": "#1982c4", "QHD": "#8ac926", "4K+": "#ffca3a", "Ultrawide": "#ff595e", "Other": "#9d4edd"}
res_order = ["FHD", "QHD", "4K+", "Ultrawide", "Other"]

fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)

for res_type in res_order: # drawing scatter plot dots
    sub = df[df["res_category"] == res_type]
    ax.scatter(
        sub["reviews_pct"],  # reviews percentile as x-axis
        sub["price_pct"],  # price percentile as y-axis
        c=colors.get(res_type, "#cccccc"),
        label=res_type,
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
    "PRICE VS REVIEW VOLUME DISTRIBUTION BY RESOLUTION",
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
    title="resolution",
    title_fontsize=10,
)

plt.tight_layout()
plt.savefig("visualizations/price_reviews_resolution_scatter.png", dpi=300)
plt.close()