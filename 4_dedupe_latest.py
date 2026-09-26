import pandas as pd

excluded_col = {"record_id", "snapshot_datetime", "price", "rating", "reviews_count"}

def load_and_prepare(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';')
    df["snapshot_datetime"] = pd.to_datetime(df["snapshot_datetime"])
    return df

def drop_outdated_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    compare_cols = [c for c in df.columns if c not in excluded_col]
    kept_rows = []
    for _, group in df.groupby(["brand", "model"], sort=False): # grouping by brand and model to narrow down the search
        spec_key = group[compare_cols].fillna("__NA__").astype(str).agg("|".join, axis=1) # creating unique text fingerprint for each row
        for _, spec_group in group.groupby(spec_key, sort=False): # grouping identical listings using the fingerprint
            latest_row = spec_group.loc[spec_group["snapshot_datetime"].idxmax()] # keeping only the row from most recent snapshot
            kept_rows.append(latest_row)
    return pd.DataFrame(kept_rows)

def finalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["record_id"])
    df = df.sort_values(
        by=["snapshot_datetime", "brand", "model"],
        ascending=[False, True, True]
    )
    return df

def main() -> None:
    df = load_and_prepare("data/v_monitors_flat_export.csv")
    print(f"Loaded {len(df)} rows")
    deduped = drop_outdated_duplicates(df)  # collapse same-listing rows across snapshots to just the latest
    print(f"Kept {len(deduped)} rows after removing outdated duplicates "
          f"({len(df) - len(deduped)} removed)")
    result = finalize(deduped)  # drop record_id and apply the final sort order
    result.to_csv("data/latest_records.csv", sep=';', index=False)
    print(f"Exported {len(result)} rows")

if __name__ == "__main__":
    main()