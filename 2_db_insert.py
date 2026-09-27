import os
import re
import sqlite3
from pathlib import Path
import pandas as pd

def extract_datetime_from_filename(filename: str) -> str:
    basename = Path(filename).stem # extracts file name without directory path or extension
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})', basename) # searches for pattern YYYY_MM_DD_HH_MM
    if match:
        year, month, day, hour, minute = match.groups()
        return f"{year}-{month}-{day} {hour}:{minute}" # standard SQLite ISO DATETIME string format (YYYY-MM-DD HH:MM)
    else:
        raise ValueError(
            f"Couldn't get date and time from file name '{basename}'. "
            "Expected format with timestamp like 'monitors_dns_2026_09_20_12_00.csv'"
        )

def to_flag(value) -> int: # converts cell value or NaN/None into a 0 or 1 flag for NOT NULL columns
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    return 1 if bool(value) else 0

def clean_text(value):
    if value is None or (isinstance(value, float) and pd.isna(value)): # returns None for missing or NaN values
        return None
    text = str(value).strip()
    return text if text else None # returns the cleaned string, or None if it resulted in an empty string

def load_csv_to_sqlite(csv_path: str, db_path: str = "data/monitors.db") -> None:
    if not os.path.exists(csv_path):
        print(f"Error: file '{csv_path}' not found")
        return

    snapshot_datetime = extract_datetime_from_filename(csv_path)
    print(f"\nLoading file: {csv_path} ")
    print(f"Snapshot time mark: {snapshot_datetime}")

    df = pd.read_csv(csv_path, sep=';')
    df = df.where(pd.notnull(df), None) # replaces pandas NaN values with Python None for uniform NULL handling

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            inserted_count = 0
            skipped_count = 0

            for row_num, row in df.iterrows():
                # validating brand name (required NOT NULL column), skip row if missing
                brand_name = clean_text(row['brand'])
                if not brand_name:
                    print(f"  Skipping row {row_num}: missing brand name ('model'={row.get('model')!r})")
                    skipped_count += 1
                    continue

                # inserting brand if new, then retrieving its primary key ID
                cursor.execute("INSERT OR IGNORE INTO brands (name) VALUES (?)", (brand_name,))
                cursor.execute("SELECT id FROM brands WHERE name = ?", (brand_name,))
                brand_row = cursor.fetchone()
                if brand_row is None:
                    raise RuntimeError(f"Could not find/create brand '{brand_name}' (row {row_num})")
                brand_id = brand_row[0]

                # extracting horizontal and vertical resolutions safely as integers
                h_res = row.get('h_resolution')
                v_res = row.get('v_resolution')
                h_res = int(h_res) if h_res is not None and pd.notna(h_res) else None
                v_res = int(v_res) if v_res is not None and pd.notna(v_res) else None

                # inserting panel type if present, then retrieving its primary key ID
                panel_name = clean_text(row.get('panel_type'))
                panel_type_id = None
                if panel_name:
                    cursor.execute("INSERT OR IGNORE INTO panel_types (name) VALUES (?)", (panel_name,))
                    cursor.execute("SELECT id FROM panel_types WHERE name = ?", (panel_name,))
                    panel_row = cursor.fetchone()
                    if panel_row is None:
                        raise RuntimeError(f"Could not find/create panel type '{panel_name}' (row {row_num})")
                    panel_type_id = panel_row[0]

                cursor.execute("""
                    INSERT INTO monitor_list (
                        snapshot_datetime, brand_id, model, price, rating, reviews_count,
                        diagonal, h_res, v_res, refresh_rate, panel_type_id, brightness,
                        contrast, h_view_angle, v_view_angle, curvature_radius,
                        hdmi_count, hdmi_version, dp_count, dp_version,
                        has_vga, has_dvi, has_usbc, usb_count,
                        has_amd_sync, has_nvidia_sync, has_adaptive_sync, is_smart
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot_datetime,
                    brand_id,
                    row['model'],
                    row.get('price'),
                    row.get('rating'),
                    row.get('reviews_count'),
                    row.get('diagonal'),
                    h_res,
                    v_res,
                    row.get('refresh_rate'),
                    panel_type_id,
                    row.get('brightness'),
                    row.get('contrast'),
                    row.get('h_view_angle'),
                    row.get('v_view_angle'),
                    row.get('curvature_radius'),
                    row.get('hdmi_count'),
                    row.get('hdmi_version'),
                    row.get('dp_count'),
                    row.get('dp_version'),
                    # booleans go through to_flag() so missing values become 0 instead of None/NULL
                    to_flag(row.get('has_vga')),
                    to_flag(row.get('has_dvi')),
                    to_flag(row.get('has_usbc')),
                    row.get('usb_count'),
                    to_flag(row.get('has_amd_sync')),
                    to_flag(row.get('has_nvidia_sync')),
                    to_flag(row.get('has_adaptive_sync')),
                    to_flag(row.get('is_smart'))
                ))
                inserted_count += 1

            print(f"Successfully processed and saved {inserted_count} lines"
                  + (f" ({skipped_count} skipped)" if skipped_count else ""))
    except sqlite3.Error as e:
        print(f"Database error while loading '{csv_path}': {e}")
        raise

def load_all_csvs_from_folder(folder_path: str = "data") -> None:
    for file in os.listdir(folder_path):
        if file.startswith("monitors_dns_") and file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            try:
                load_csv_to_sqlite(file_path)
            except Exception as e:
                print(f"Error with processing {file}: {e}")

if __name__ == "__main__":
    # load_csv_to_sqlite("data/snapshots/monitors_dns_2026_09_20_12_00.csv")
    load_all_csvs_from_folder("data/snapshots")