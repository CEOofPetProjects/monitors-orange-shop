import sqlite3
import pandas as pd

def export_flat():
    with sqlite3.connect("data/monitors.db") as conn:
        df = pd.read_sql_query("SELECT * FROM v_monitors_flat", conn)

    # columns that should keep integer formatting
    int_columns = [
        'refresh_rate', 'brightness', 'contrast',
        'h_view_angle', 'v_view_angle', 'curvature_radius',
        'hdmi_count', 'dp_count', 'usb_count',
        'h_resolution', 'v_resolution', 'price', 'reviews_count'
    ]

    # cast integer columns to pandas' Int64 to prevent float conversion
    for col in int_columns:
        if col in df.columns:
            df[col] = df[col].astype('Int64')

    df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
    df = df.sort_values(
        by=["snapshot_datetime", "brand", "model"],
        ascending=[False, True, True]
    )

    df.to_csv("data/v_monitors_flat_export.csv", sep=";", index=False, encoding="utf-8-sig")
    print(f"Successfully exported {len(df)} lines")

if __name__ == "__main__":
    export_flat()