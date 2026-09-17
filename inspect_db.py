import sys
sys.path.insert(0, "C:/Users/ycode/Documents/atlas-weather-risk-pipeline/load")

from postgres import engine
from sqlalchemy import text

print("=== DB CONNECTION INFO ===")
with engine.connect() as conn:
    print("Database:", conn.execute(text("SELECT current_database()")).scalar())
    print("Schema:", conn.execute(text("SELECT current_schema()")).scalar())
    print("Tables in public:", conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
    )).fetchall())

print()
print("=== weather_risk CHECK ===")
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE tablename = 'weather_risk'"
    ))
    rows = result.fetchall()
    print("Found:", rows)
    if rows:
        print()
        print("=== weather_risk COLUMNS ===")
        cols = conn.execute(text(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'weather_risk' ORDER BY ordinal_position"
        )).fetchall()
        for c in cols:
            print(f"  {c[0]}  {c[1]}  nullable={c[2]}")

print()
print("=== FOREIGN KEYS ON weather_risk ===")
with engine.connect() as conn:
    fks = conn.execute(text(
        "SELECT tc.constraint_name, tc.table_name, kcu.column_name, ccu.table_name AS foreign_table, ccu.column_name AS foreign_column FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'weather_risk'"
    )).fetchall()
    print("FKs:", fks if fks else "none")

print()
print("=== ALL TABLES (all schemas) ===")
with engine.connect() as conn:
    all_tables = conn.execute(text(
        "SELECT schemaname, tablename FROM pg_tables ORDER BY schemaname, tablename"
    )).fetchall()
    for s, t in all_tables:
        print(f"  {s}.{t}")
