"""
Yoga Teaching Journal - Database Setup Script
Run this ONCE to set up your Snowflake database.

Usage:
    python setup_yoga_database.py

You'll be prompted for credentials (they won't be stored).
"""

from snowflake.snowpark import Session
import getpass
import os

# Get credentials securely (not hardcoded!)
print("=" * 50)
print("YOGA TEACHING JOURNAL - Database Setup")
print("=" * 50)
print("\nEnter your Snowflake credentials:")

account = input("Account (e.g., abc12345.us-east-1): ").strip()
user = input("Username: ").strip()
password = getpass.getpass("Password: ")  # Hidden input

connection_params = {
    "account": account,
    "user": user,
    "password": password,
}

print("\nConnecting to Snowflake...")
try:
    session = Session.builder.configs(connection_params).create()
    print("✅ Connected!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# ============================================================================
# CREATE INFRASTRUCTURE
# ============================================================================

print("\n1. Creating warehouse YOGA_WH...")
session.sql("""
    CREATE WAREHOUSE IF NOT EXISTS YOGA_WH
        WAREHOUSE_SIZE = 'XSMALL'
        AUTO_SUSPEND = 60
        AUTO_RESUME = TRUE
""").collect()
print("✅ Warehouse created!")

print("\n2. Creating database YOGA_JOURNAL...")
session.sql("CREATE DATABASE IF NOT EXISTS YOGA_JOURNAL").collect()
print("✅ Database created!")

print("\n3. Creating schemas...")
session.sql("USE DATABASE YOGA_JOURNAL").collect()
session.sql("CREATE SCHEMA IF NOT EXISTS APP_DATA").collect()
session.sql("CREATE SCHEMA IF NOT EXISTS ANALYTICS").collect()
session.sql("USE SCHEMA APP_DATA").collect()
print("✅ Schemas created!")

# ============================================================================
# CREATE TABLES
# ============================================================================

print("\n4. Creating tables...")

# Locations table
session.sql("""
    CREATE OR REPLACE TABLE LOCATIONS (
        location_id INTEGER AUTOINCREMENT PRIMARY KEY,
        location_name STRING NOT NULL,
        neighborhood STRING,
        address STRING,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ LOCATIONS table created")

# Class types table
session.sql("""
    CREATE OR REPLACE TABLE CLASS_TYPES (
        class_type_id INTEGER AUTOINCREMENT PRIMARY KEY,
        class_name STRING NOT NULL,
        duration_minutes INTEGER NOT NULL,
        is_heated BOOLEAN DEFAULT FALSE,
        display_name STRING,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ CLASS_TYPES table created")

# Themes table
session.sql("""
    CREATE OR REPLACE TABLE THEMES (
        theme_id INTEGER AUTOINCREMENT PRIMARY KEY,
        theme_name STRING NOT NULL,
        category STRING,
        notes STRING,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ THEMES table created")

# Main classes table (with VARIANT)
session.sql("""
    CREATE OR REPLACE TABLE CLASSES_TAUGHT (
        class_id INTEGER AUTOINCREMENT PRIMARY KEY,
        class_date DATE NOT NULL,
        class_time TIME,
        day_of_week STRING,
        location_id INTEGER,
        class_type_id INTEGER,
        theme_id INTEGER,
        custom_theme STRING,
        intention STRING,
        peak_pose STRING,
        sequence_notes VARIANT,
        energy_level STRING,
        student_count INTEGER,
        vibe_rating INTEGER,
        personal_notes STRING,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ CLASSES_TAUGHT table created (with VARIANT column)")

# AI output tables
session.sql("""
    CREATE OR REPLACE TABLE AI_GENERATED_THEMES (
        id INTEGER AUTOINCREMENT PRIMARY KEY,
        theme_name STRING,
        theme_approach STRING,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ AI_GENERATED_THEMES table created")

session.sql("""
    CREATE OR REPLACE TABLE AI_GENERATED_SEQUENCES (
        id INTEGER AUTOINCREMENT PRIMARY KEY,
        peak_pose STRING,
        sequence_outline STRING,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()
print("  ✅ AI_GENERATED_SEQUENCES table created")

# ============================================================================
# INSERT REFERENCE DATA
# ============================================================================

print("\n5. Inserting reference data...")

# Locations
session.sql("""
    INSERT INTO LOCATIONS (location_name, neighborhood, address) VALUES
        ('Equinox Pine Street', 'FiDi', '301 Pine St, San Francisco, CA'),
        ('Equinox Beale Street', 'FiDi', '350 Beale St, San Francisco, CA'),
        ('Equinox Van Ness', 'Van Ness', '1550 Van Ness Ave, San Francisco, CA'),
        ('Equinox Market Street', 'Mid-Market', '747 Market St, San Francisco, CA'),
        ('Equinox Palo Alto', 'Palo Alto', '440 Portage Ave, Palo Alto, CA')
""").collect()
print("  ✅ 5 locations inserted")

# Class types
session.sql("""
    INSERT INTO CLASS_TYPES (class_name, duration_minutes, is_heated, display_name) VALUES
        ('Vinyasa', 60, TRUE, 'Vinyasa 60 (Heated)'),
        ('Vinyasa', 75, TRUE, 'Vinyasa 75 (Heated)'),
        ('Vinyasa', 60, FALSE, 'Vinyasa 60'),
        ('Vinyasa', 75, FALSE, 'Vinyasa 75'),
        ('Yin', 60, FALSE, 'Yin 60'),
        ('Yin', 75, FALSE, 'Yin 75'),
        ('Restorative', 60, FALSE, 'Restorative 60'),
        ('Power', 60, TRUE, 'Power 60 (Heated)'),
        ('Slow Flow', 60, FALSE, 'Slow Flow 60')
""").collect()
print("  ✅ 9 class types inserted")

# Themes
session.sql("""
    INSERT INTO THEMES (theme_name, category, notes) VALUES
        ('Hip Openers', 'Physical', 'Pigeon, lizard, frog, 90/90'),
        ('Heart Opening', 'Physical', 'Backbends, chest openers'),
        ('Balance', 'Physical', 'Standing balances, core stability'),
        ('Twists & Detox', 'Physical', 'Seated and standing twists'),
        ('Core Strength', 'Physical', 'Plank variations, boat pose'),
        ('Hamstrings', 'Physical', 'Forward folds, splits prep'),
        ('Letting Go', 'Emotional', 'Release what no longer serves'),
        ('Self-Compassion', 'Emotional', 'Kindness toward self'),
        ('Gratitude', 'Emotional', 'Appreciation practice'),
        ('Courage', 'Emotional', 'Facing fears, trying new things'),
        ('Joy', 'Emotional', 'Playfulness, lightness'),
        ('Presence', 'Philosophical', 'Being here now'),
        ('Impermanence', 'Philosophical', 'Everything changes'),
        ('Surrender', 'Philosophical', 'Accepting what is')
""").collect()
print("  ✅ 14 themes inserted")

# ============================================================================
# INSERT SAMPLE CLASS DATA
# ============================================================================

print("\n6. Inserting sample class data...")

sample_classes = [
    ("DATEADD(day, -45, CURRENT_DATE())", "09:00", "Monday", 1, 1, 1, "Open hips to release tension", "Pigeon", "High", 22, 5, "Great energy!"),
    ("DATEADD(day, -42, CURRENT_DATE())", "18:30", "Thursday", 2, 2, 2, "Open heart to give and receive", "Wheel", "Very High", 28, 5, "Packed class!"),
    ("DATEADD(day, -38, CURRENT_DATE())", "07:00", "Monday", 1, 1, 3, "Find steadiness in instability", "Dancer", "Medium", 15, 4, "Focused group"),
    ("DATEADD(day, -35, CURRENT_DATE())", "12:00", "Thursday", 3, 3, 7, "Release what no longer serves", "Pigeon", "Low", 18, 5, "Emotional releases"),
    ("DATEADD(day, -31, CURRENT_DATE())", "09:00", "Sunday", 2, 2, 1, "Create space in hips", "Flying Pigeon", "Very High", 35, 5, "Sunday packed!"),
    ("DATEADD(day, -28, CURRENT_DATE())", "18:30", "Wednesday", 1, 1, 12, "Be here now", "Crow", "High", 20, 4, "Good arm balance work"),
    ("DATEADD(day, -24, CURRENT_DATE())", "09:00", "Saturday", 3, 2, 2, "Expand capacity for love", "Camel", "High", 25, 5, "Beautiful backbends"),
    ("DATEADD(day, -21, CURRENT_DATE())", "07:00", "Tuesday", 1, 1, 5, "Build strength from center", "Crow", "High", 16, 4, "Core was intense"),
    ("DATEADD(day, -17, CURRENT_DATE())", "18:30", "Thursday", 2, 1, 4, "Rinse and release", "Revolved Triangle", "Medium", 19, 4, "Twist-heavy class"),
    ("DATEADD(day, -14, CURRENT_DATE())", "09:00", "Sunday", 3, 2, 11, "Find joy in practice", "Dancer", "High", 30, 5, "Lots of laughter"),
    ("DATEADD(day, -10, CURRENT_DATE())", "12:00", "Wednesday", 1, 5, 14, "Surrender to what is", "Reclined Butterfly", "Low", 12, 5, "Perfect Yin class"),
    ("DATEADD(day, -7, CURRENT_DATE())", "09:00", "Saturday", 2, 1, 1, "Free the hips", "King Pigeon", "Very High", 32, 5, "Saturday hit!"),
    ("DATEADD(day, -4, CURRENT_DATE())", "18:30", "Tuesday", 1, 1, 3, "Find your center", "Standing Splits", "High", 21, 4, "Balance challenge"),
    ("DATEADD(day, -2, CURRENT_DATE())", "09:00", "Thursday", 3, 1, 9, "Appreciate what you have", "Wheel", "High", 24, 5, "Gratitude resonated"),
]

for c in sample_classes:
    sql = f"""
        INSERT INTO CLASSES_TAUGHT 
            (class_date, class_time, day_of_week, location_id, class_type_id, theme_id,
             intention, peak_pose, energy_level, student_count, vibe_rating, personal_notes)
        SELECT {c[0]}, '{c[1]}', '{c[2]}', {c[3]}, {c[4]}, {c[5]},
               '{c[6]}', '{c[7]}', '{c[8]}', {c[9]}, {c[10]}, '{c[11]}'
    """
    session.sql(sql).collect()

print(f"  ✅ {len(sample_classes)} sample classes inserted")

# ============================================================================
# CREATE ANALYTICS VIEWS
# ============================================================================

print("\n7. Creating analytics views...")

session.sql("USE SCHEMA ANALYTICS").collect()

session.sql("""
    CREATE OR REPLACE VIEW LOCATION_STATS AS
    SELECT 
        l.location_name,
        COUNT(*) AS total_classes,
        ROUND(AVG(c.vibe_rating), 1) AS avg_vibe,
        ROUND(AVG(c.student_count), 0) AS avg_students
    FROM APP_DATA.CLASSES_TAUGHT c
    JOIN APP_DATA.LOCATIONS l ON c.location_id = l.location_id
    GROUP BY l.location_name
""").collect()
print("  ✅ LOCATION_STATS view created")

session.sql("""
    CREATE OR REPLACE VIEW CLASS_TYPE_STATS AS
    SELECT 
        ct.display_name AS class_type,
        ct.is_heated,
        COUNT(*) AS total_classes,
        ROUND(AVG(c.vibe_rating), 1) AS avg_vibe,
        ROUND(AVG(c.student_count), 0) AS avg_students
    FROM APP_DATA.CLASSES_TAUGHT c
    JOIN APP_DATA.CLASS_TYPES ct ON c.class_type_id = ct.class_type_id
    GROUP BY ct.display_name, ct.is_heated
""").collect()
print("  ✅ CLASS_TYPE_STATS view created")

session.sql("""
    CREATE OR REPLACE VIEW THEME_STATS AS
    SELECT 
        COALESCE(t.theme_name, c.custom_theme) AS theme,
        COUNT(*) AS times_taught,
        ROUND(AVG(c.vibe_rating), 1) AS avg_vibe,
        ROUND(AVG(c.student_count), 0) AS avg_students
    FROM APP_DATA.CLASSES_TAUGHT c
    LEFT JOIN APP_DATA.THEMES t ON c.theme_id = t.theme_id
    WHERE COALESCE(t.theme_name, c.custom_theme) IS NOT NULL
    GROUP BY COALESCE(t.theme_name, c.custom_theme)
""").collect()
print("  ✅ THEME_STATS view created")

# ============================================================================
# VERIFY
# ============================================================================

print("\n8. Verifying setup...")
session.sql("USE SCHEMA APP_DATA").collect()

counts = {
    "LOCATIONS": session.sql("SELECT COUNT(*) as cnt FROM LOCATIONS").collect()[0]['CNT'],
    "CLASS_TYPES": session.sql("SELECT COUNT(*) as cnt FROM CLASS_TYPES").collect()[0]['CNT'],
    "THEMES": session.sql("SELECT COUNT(*) as cnt FROM THEMES").collect()[0]['CNT'],
    "CLASSES_TAUGHT": session.sql("SELECT COUNT(*) as cnt FROM CLASSES_TAUGHT").collect()[0]['CNT'],
}

print("\n📊 Data Summary:")
for table, count in counts.items():
    print(f"   {table}: {count} rows")

print("\n" + "=" * 50)
print("🎉 SETUP COMPLETE!")
print("=" * 50)
print("\nNext steps:")
print("1. Create .streamlit/secrets.toml with your credentials")
print("2. Run: streamlit run yoga_teacher_streamlit_app.py")
print("\nYour database: YOGA_JOURNAL")
print("Your warehouse: YOGA_WH")

session.close()
