import os
import sqlite3

db_path = "data/monitors.db"
def create_database() -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS matrix_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS monitor_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_datetime DATETIME NOT NULL,
                brand_id INTEGER NOT NULL,
                model TEXT NOT NULL,
                price INTEGER,
                rating REAL,
                reviews_count INTEGER,
                diagonal REAL,
                h_res INTEGER,
                v_res INTEGER,
                refresh_rate INTEGER,
                matrix_type_id INTEGER,
                brightness INTEGER,
                contrast INTEGER,
                h_view_angle INTEGER,
                v_view_angle INTEGER,
                curvature_radius INTEGER,
                hdmi_count INTEGER,
                hdmi_version TEXT,
                dp_count INTEGER,
                dp_version TEXT,
                has_vga INTEGER NOT NULL DEFAULT 0 CHECK (has_vga IN (0, 1)),
                has_dvi INTEGER NOT NULL DEFAULT 0 CHECK (has_dvi IN (0, 1)),
                has_usbc INTEGER NOT NULL DEFAULT 0 CHECK (has_usbc IN (0, 1)),
                usb_count INTEGER,
                has_amd_sync INTEGER NOT NULL DEFAULT 0 CHECK (has_amd_sync IN (0, 1)),
                has_nvidia_sync INTEGER NOT NULL DEFAULT 0 CHECK (has_nvidia_sync IN (0, 1)),
                has_adaptive_sync INTEGER NOT NULL DEFAULT 0 CHECK (has_adaptive_sync IN (0, 1)),
                is_smart INTEGER NOT NULL DEFAULT 0 CHECK (is_smart IN (0, 1)),
                FOREIGN KEY (brand_id) REFERENCES brands(id),
                FOREIGN KEY (matrix_type_id) REFERENCES matrix_types(id)
            );

            CREATE INDEX IF NOT EXISTS idx_monitor_list_brand_id
                ON monitor_list(brand_id);

            CREATE INDEX IF NOT EXISTS idx_monitor_list_matrix_type_id
                ON monitor_list(matrix_type_id);

            CREATE INDEX IF NOT EXISTS idx_monitor_list_snapshot_datetime
                ON monitor_list(snapshot_datetime);

            CREATE VIEW IF NOT EXISTS v_monitors_flat AS
            SELECT
                s.id AS record_id,
                s.snapshot_datetime,
                b.name AS brand,
                s.model,
                s.price,
                s.rating,
                s.reviews_count,
                s.diagonal,
                s.h_res || 'x' || s.v_res AS resolution_str,
                s.h_res AS h_resolution,
                s.v_res AS v_resolution,
                m.name AS matrix_type,
                s.refresh_rate,
                s.brightness,
                s.contrast,
                s.h_view_angle,
                s.v_view_angle,
                s.curvature_radius,
                CASE WHEN s.curvature_radius IS NOT NULL THEN 1 ELSE 0 END AS is_curved,
                s.hdmi_count,
                s.hdmi_version,
                s.dp_count,
                s.dp_version,
                s.has_vga,
                s.has_dvi,
                s.has_usbc,
                s.usb_count,
                s.has_amd_sync,
                s.has_nvidia_sync,
                s.has_adaptive_sync,
                s.is_smart
            FROM monitor_list s
            LEFT JOIN brands b ON s.brand_id = b.id
            LEFT JOIN matrix_types m ON s.matrix_type_id = m.id;
            """)
        print("Successfully created database")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise

if __name__ == "__main__":
    create_database()