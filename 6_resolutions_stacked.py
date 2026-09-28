import matplotlib.pyplot as plt
import pandas as pd
import re

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=";")
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
latest_date = df['snapshot_datetime'].dt.date.max()
df = df[df['snapshot_datetime'].dt.date == latest_date].copy()
_, bins = pd.qcut(df['price'].dropna(), q=4, retbins=True) # calc quartiles and extract bin values
dynamic_labels = [
    f"Budget\n(< {bins[1]:,.0f} ₽)",
    f"Lower-mid\n({bins[1]:,.0f} - {bins[2]:,.0f} ₽)",
    f"Upper-mid\n({bins[2]:,.0f} - {bins[3]:,.0f} ₽)",
    f"Premium\n(> {bins[3]:,.0f} ₽)"
]
df['price_tier'] = pd.qcut(df['price'].dropna(), q=4, labels=dynamic_labels)

def categorize_resolution(res_string):
    if not isinstance(res_string, str): return "Other"
    match = re.search(r'(\d+)\s*[xXхХ]\s*(\d+)', res_string)
    if not match: return "Other"
    w, h = int(match.group(1)), int(match.group(2))
    if h == 0: return "Other"
    aspect_ratio = w / h
    if aspect_ratio > 1.78: return "Ultrawide"
    elif w == 1920: return "FHD"
    elif w == 2560: return "QHD"
    elif w >= 3840: return "4K+"
    else: return "Other"

df['res_group'] = df['resolution_str'].apply(categorize_resolution)
res_order = ["FHD", "QHD", "4K+", "Ultrawide", "Other"]
res_matrix = (pd.crosstab(df['price_tier'], df['res_group'], normalize='index') * 100).reindex(columns=res_order, fill_value=0)
res_colors = {"FHD": "#1982c4", "QHD": "#8ac926", "4K+": "#ffca3a", "Ultrawide": "#ff595e", "Other": "#9d4edd"}

fig, ax = plt.subplots(figsize=(9, 7.5), dpi=300)
bottoms = [0.0] * len(dynamic_labels)

for cat in res_order:
    values = res_matrix[cat].tolist()
    ax.bar(dynamic_labels, values, width=0.55, bottom=bottoms, label=cat, color=res_colors[cat], edgecolor="white", linewidth=0.8)
    bottoms = [b + v for b, v in zip(bottoms, values)]

ax.set_title("RESOLUTIONS BY PRICE TIERS", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("percentage of SKUs in tier (%)", fontsize=12)
ax.set_xlabel("market price tier", fontsize=12, labelpad=10)
ax.tick_params(axis='both', labelsize=10)
ax.set_ylim(0, 100)
ax.grid(True, axis='y', linestyle=":", alpha=0.4)
ax.legend(title="screen resolution", loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=True)

plt.tight_layout()
plt.savefig("visualizations/resolutions_price_stacked.png", dpi=300)
plt.close()