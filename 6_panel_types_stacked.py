import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=";")
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
latest_date = df['snapshot_datetime'].dt.date.max()
df = df[df['snapshot_datetime'].dt.date == latest_date].copy()
_, bins = pd.qcut(df['price'].dropna(), q=4, retbins=True) # calc quartiles and extract bin values
dynamic_labels = [
    f"Budget\n(< {bins[1]:,.0f}₽)",
    f"Lower-mid\n({bins[1]:,.0f} - {bins[2]:,.0f}₽)",
    f"Upper-mid\n({bins[2]:,.0f} - {bins[3]:,.0f}₽)",
    f"Premium\n(> {bins[3]:,.0f}₽)"
]
df['price_tier'] = pd.qcut(df['price'].dropna(), q=4, labels=dynamic_labels)

def categorize_panel(panel_string):
    if not isinstance(panel_string, str): return "VA"
    p = panel_string.upper()
    if "OLED" in p: return "OLED"
    elif "IPS" in p: return "IPS"
    elif "VA" in p: return "VA"
    elif "TN" in p: return "TN"
    else: return "IPS"

df['panel_group'] = df['panel_type'].apply(categorize_panel)
panel_order = ["IPS", "VA", "OLED", "TN"]
panel_matrix = (pd.crosstab(df['price_tier'], df['panel_group'], normalize='index') * 100).reindex(columns=panel_order, fill_value=0)
panel_colors = {"VA": "#ff595e", "IPS": "#1982c4", "OLED": "#8ac926", "TN": "#ffca3a"}

fig, ax = plt.subplots(figsize=(9, 7.5), dpi=300)
bottoms = [0.0] * len(dynamic_labels)

for cat in panel_order:
    values = panel_matrix[cat].tolist()
    ax.bar(dynamic_labels, values, width=0.55, bottom=bottoms, label=cat, color=panel_colors[cat], edgecolor="white", linewidth=0.8)
    bottoms = [b + v for b, v in zip(bottoms, values)]

ax.set_title("PANEL TYPES BY PRICE TIERS", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("percentage of SKUs in tier (%)", fontsize=12)
ax.set_xlabel("market price tier", fontsize=12, labelpad=10)
ax.tick_params(axis='both', labelsize=10)
ax.set_ylim(0, 100)
ax.grid(True, axis='y', linestyle=":", alpha=0.4)
ax.legend(title="panel type", loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=True)

plt.tight_layout()
plt.savefig("visualizations/panel_types_price_stacked.png", dpi=300)
plt.close()