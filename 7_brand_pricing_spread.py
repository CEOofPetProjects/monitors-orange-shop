import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=";")
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
df['snapshot_date'] = df['snapshot_datetime'].dt.date
latest_date = df['snapshot_date'].max()
df = df[df['snapshot_date'] == latest_date].copy()
df['brand_clean'] = df['brand'].str.upper().str.strip() # capitalizing brand names

top_brands = df['brand_clean'].value_counts().head(10).index # top 10 brands by sku count
df_top = df[df['brand_clean'].isin(top_brands)]
brand_order = df_top.groupby('brand_clean')['price'].median().sort_values(ascending=False).index # desc sort brands by median price
custom_palette = sns.blend_palette(["#1982c4", "#8ac926", "#ffca3a", "#ff595e"], n_colors=10) # gradient palette

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

sns.boxplot( 
    data=df_top, 
    x="price", 
    y="brand_clean", 
    order=brand_order, 
    palette=custom_palette, 
    showfliers=True, 
    flierprops=dict(marker='o', markersize=4, alpha=0.5), 
    ax=ax 
) 

ax.set_xscale("log") # logarithmic scale fox x axis
custom_ticks = [10000, 25000, 50000, 100000, 250000, 500000] 
ax.set_xticks(custom_ticks)
ax.set_xticklabels([f"{tick:,.0f}" for tick in custom_ticks])
ax.set_xlim(left=5000)
ax.set_xlabel("retail price (₽) in logarithmic scale", fontsize=11, labelpad=8)
ax.set_ylabel("competitor brand", fontsize=11, labelpad=8)
ax.set_title("BRAND PRICING SPREAD", fontsize=14, fontweight="bold", pad=15)
ax.grid(True, axis='x', linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("visualizations/brand_pricing_spread.png", dpi=300)
plt.close()