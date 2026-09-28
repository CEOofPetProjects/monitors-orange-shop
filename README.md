# E-Commerce Market Intelligence: Monitors

## Project overview
This project simulates a corporate market intelligence pipeline by analyzing e-commerce retail snapshots (specs, pricing, review volume, and consumer ratings) from a major electronics retailer. To demonstrate strict technical versatility, I designed a robust relational database schema (ERD), executed the database setup using DDL SQL queries inside a Python script, and built a custom SQL VIEW to optimize relational data into an easily exportable flat table format.

## Why monitors?
Why did I decide to choose monitors? I am somewhat of a monitor enthusiast myself – already got 2 (I know – crazy, right?). But in all seriousness, monitors are excellent for data analysis because they offer the perfect balance of analytical dimensions. You have commercial data (brand name, ratings, review volume, pricing) layered against hard technical specs (like resolution, panel types, refresh rates, viewing angles, and IO).

This allows for the categorization of data into distinct business buckets (market positioning vs tangible visual performance vs connectivity), generating a rich, multi-dimensional analysis that goes beyond simple price tracking. DNS was selected simply due to their comprehensive catalog and deep technical filtering options, which provided a robust dataset for this snapshot.

## Tech stack & Methodologies
* Database architecture: sqlite3 library, Entity-Relationship Diagram (ERD) design, relational schema optimization, custom SQL VIEWs for denormalization 
* Data analytics: Python, pandas (quantile-based price tiering, percentile ranking to handle skewness)
* Data visualization: Matplotlib and Seaborn (high-impact business charting, color-palette adherence, "chart junk" elimination)

## The Pipeline
The project is modularized into sequential scripts that mirror a professional ETL and analytics workflow:
* 1_db_creation.py to create SQLite database
* 2_db_insert.py to insert data from csv snapshot file into the database
* 3_export_flat_csv.py to export data from SQL VIEW into an analytics-ready flat csv file 
* 4_pandas_analysis.py to run core exploratory data analysis
* 5_price_reviews_panel_types_scatter.py and 5_price_reviews_resolution_scatter.py to generate scatter plots mapping market traction against price using percentile distributions
* 6_panel_types_stacked.py and 6_resolution_stacked.py to construct 100% stacked bar charts to establish baseline feature expectations across four dynamic price quartiles (Budget, Lower-mid, Upper-mid, Premium)

## ERD
![Monitors Database ERD](visualizations/ERD.png)

## Analysis

### 4_pandas_analysis.py output
```
===================================================================
SNAPSHOT COMPARISON: 2026-09-26 vs 2026-08-01
===================================================================
Total entries in previous snapshot: 799
Total entries in latest snapshot:   748
Net change in total entries:        -51
New models introduced:              172
Models removed:                     216
Models retained across both dates:  554

===================================================================
CHRONOLOGICAL MARKET TRENDS
===================================================================
> MEDIAN MARKET PRICE OVER TIME <
snapshot_date
2026-08-01    19999.0
2026-09-26    19999.0
Name: price, dtype: float64 

> AMD SYNC VS NVIDIA SYNC <
               amd_sync_share_pct  nvidia_sync_share_pct
snapshot_date                                           
2026-08-01                   54.1                   23.2
2026-09-26                   54.9                   23.9 

> PANEL TYPE SHARE DISTRIBUTION OVER TIME <
panel_type      IPS    VA  OLED   TN  QD-OLED
snapshot_date                                
2026-08-01     63.6  24.2  11.6  0.6      0.0
2026-09-26     61.7  24.9  12.4  0.8      0.1 

===================================================================
CURRENT MARKET ANALYSIS FOR 2026-09-26 SNAPSHOT
===================================================================
> PRICE SEGMENTATION <
                        min     max   median  count
price_tier                                         
Budget (Bottom 25%)    4999   11999   9799.0    189
Mid-Range (25-50%)    12199   19999  15999.0    190
Premium (50-75%)      20199   40299  27999.0    182
Enthusiast (Top 25%)  40999  549999  69999.0    187 

> TOP 10 BRANDS BY MARKET PRESENCE <
              listings_count  median_price  total_reviews
brand                                                    
Acer                     103       23999.0           3134
MSI                       99       21999.0          19266
ASUS                      83       24999.0           6673
LG                        70       23399.0           7501
Samsung                   68       36499.0           7761
AOC                       45       12999.0           3429
ARDOR GAMING              41       15799.0          36330
Dell                      40       47049.0            236
DEXP                      32        9699.0          13875
Machenike                 21       16999.0           2072 

> HARDWARE FEATURE PENETRATION <
High refresh rate (144Hz+):  63.24% of market
USB-C connectivity:          22.99% of market
Curved screens:              20.45% of market
4K resolution:               16.98% of market

> PRICE BY RESOLUTION <
                 median  count
resolution_str                
1920x1080       11999.0    329
2560x1440       24999.0    196
3840x2160       45999.0    127
3440x1440       33999.0     59
5120x1440       94499.0     14 

> PRICE BY SCREEN SIZE <
                       median  count
size_tier                           
Compact (<24")        10499.0    155
Mainstream (24"-27")  18999.0    400
Large (>27")          40299.0    193 

> PRICE BY PANEL TYPE <
             median  count
panel_type                
IPS         15999.0    461
VA          21499.0    186
QD-OLED     53999.0      1
TN          62999.0      6
OLED        83999.0     93 

> SPECIFIC FEATURE PREMIUMS <
Curved screen markup:   28,199₽ (Curved) vs 17,799₽ (Flat)
Gaming (144Hz+) markup: 22,199₽ (Gaming) vs 15,999₽ (Standard)
```

### Price and review volume distribution by resolution (percentiles)
![price vs reviews by resolutions scatter](visualizations/price_reviews_resolution_scatter.png)

### Price and review volume distribution by panel types (percentiles)
![price vs reviews by panel types scatter](visualizations/price_reviews_panel_scatter.png)

### Resolution by price tiers
![price by resolutions stacked bar](visualizations/resolutions_price_stacked.png)

### Panel types by price tiers
![price by panel types stacked bar](visualizations/panel_types_price_stacked.png)
