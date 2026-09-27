import pandas as pd

df = pd.read_csv("data/v_monitors_flat_export.csv", sep=';')
df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
df['snapshot_date'] = df['snapshot_datetime'].dt.date

snapshot_dates = sorted(df['snapshot_date'].unique())
latest_date = snapshot_dates[-1] if len(snapshot_dates) > 0 else None
previous_date = snapshot_dates[-2] if len(snapshot_dates) > 1 else None
latest_df = df[df['snapshot_date'] == latest_date].copy()
prev_df = df[df['snapshot_date'] == previous_date].copy() if previous_date else None

if prev_df is not None:
    print("=" * 67)
    print(f"SNAPSHOT COMPARISON: {latest_date} vs {previous_date}")
    print("=" * 67)
    latest_items = set(zip(latest_df['brand'].fillna(''), latest_df['model'].fillna('')))
    prev_items = set(zip(prev_df['brand'].fillna(''), prev_df['model'].fillna('')))
    new_entries = latest_items - prev_items
    removed_entries = prev_items - latest_items
    retained_entries = latest_items.intersection(prev_items)
    print(f"Total entries in previous snapshot: {len(prev_df)}")
    print(f"Total entries in latest snapshot:   {len(latest_df)}")
    print(f"Net change in total entries:        {len(latest_df) - len(prev_df)}")
    print(f"New models introduced:              {len(new_entries)}")
    print(f"Models removed:                     {len(removed_entries)}")
    print(f"Models retained across both dates:  {len(retained_entries)}\n")

print("=" * 67)
print("CHRONOLOGICAL MARKET TRENDS")
print("=" * 67)

print("> MEDIAN MARKET PRICE OVER TIME <")
price_trend = df.groupby('snapshot_date')['price'].median()
print(price_trend, "\n")

print("> AMD SYNC VS NVIDIA SYNC <")
sync_trend = df.groupby('snapshot_date').agg(
    amd_sync_share_pct=('has_amd_sync', lambda x: x.mean() * 100),
    nvidia_sync_share_pct=('has_nvidia_sync', lambda x: x.mean() * 100)
)
print(sync_trend.round(1), "\n")

print("> PANEL TYPE SHARE DISTRIBUTION OVER TIME <")
panel_trend = pd.crosstab(df['snapshot_date'], df['panel_type'])
panel_share_trend = panel_trend.div(panel_trend.sum(axis=1), axis=0) * 100
sorted_panels = panel_share_trend.mean().sort_values(ascending=False).index
print(panel_share_trend[sorted_panels].round(1), "\n")

print("=" * 67)
print(f"CURRENT MARKET ANALYSIS FOR {latest_date} SNAPSHOT")
print("=" * 67)

print("> PRICE SEGMENTATION <")
labels = ['Budget (Bottom 25%)', 'Mid-Range (25-50%)', 'Premium (50-75%)', 'Enthusiast (Top 25%)']
latest_df['price_tier'] = pd.qcut(latest_df['price'].dropna(), q=4, labels=labels)
tier_summary = latest_df.groupby('price_tier', observed=True)['price'].agg(['min', 'max', 'median', 'count'])
print(tier_summary, "\n")

print("> TOP 10 BRANDS BY MARKET PRESENCE <")
brand_stats = latest_df.groupby('brand').agg(
    listings_count=('model', 'count'),
    median_price=('price', 'median'),
    total_reviews=('reviews_count', 'sum')
)
top_brands = brand_stats.sort_values(by='listings_count', ascending=False).head(10)
print(top_brands, "\n")

print("> HARDWARE FEATURE PENETRATION <")
total_monitors = len(latest_df)
gaming_refresh_rate = (latest_df['refresh_rate'] >= 144).sum() / total_monitors * 100
has_usb_c = (latest_df['has_usbc'] == 1).sum() / total_monitors * 100
is_curved_screen = (latest_df['is_curved'] == 1).sum() / total_monitors * 100
is_4k = (latest_df['resolution_str'] == '3840x2160').sum() / total_monitors * 100
print(f"High refresh rate (144Hz+):  {gaming_refresh_rate:.2f}% of market")
print(f"USB-C connectivity:          {has_usb_c:.2f}% of market")
print(f"Curved screens:              {is_curved_screen:.2f}% of market")
print(f"4K resolution:               {is_4k:.2f}% of market\n")

print("> PRICE BY RESOLUTION <")
res_prices = latest_df.groupby('resolution_str')['price'].agg(['median', 'count']).sort_values('count', ascending=False).head(5)
print(res_prices, "\n")

print("> PRICE BY SCREEN SIZE <")
latest_df['size_tier'] = pd.cut(
    latest_df['diagonal'],
    bins=[0, 23.9, 27.1, 100],
    labels=['Compact (<24")', 'Mainstream (24"-27")', 'Large (>27")']
)
size_prices = latest_df.groupby('size_tier', observed=True)['price'].agg(['median', 'count'])
print(size_prices, "\n")

print("> PRICE BY PANEL TYPE <")
panel_prices = latest_df.groupby('panel_type')['price'].agg(['median', 'count']).sort_values('median', ascending=True)
print(panel_prices, "\n")

print("> SPECIFIC FEATURE PREMIUMS <")
median_flat = latest_df[latest_df['is_curved'] == 0]['price'].median()
median_curved = latest_df[latest_df['is_curved'] == 1]['price'].median()
median_standard_hz = latest_df[latest_df['refresh_rate'] < 144]['price'].median()
median_gaming_hz = latest_df[latest_df['refresh_rate'] >= 144]['price'].median()
print(f"Curved screen markup:   {median_curved:,.0f}₽ (Curved) vs {median_flat:,.0f}₽ (Flat)")
print(f"Gaming (144Hz+) markup: {median_gaming_hz:,.0f}₽ (Gaming) vs {median_standard_hz:,.0f}₽ (Standard)\n")