import sqlite3
import json
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "pravaha.db")
db_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    cursor = conn.cursor()

    # Reports table with immutable original text and translated/normalized text
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL,
        language TEXT NOT NULL,
        language_code TEXT NOT NULL,
        normalized_en_text TEXT,
        timestamp TEXT NOT NULL,
        location TEXT,
        normalized_location_id TEXT,
        source_type TEXT,
        category TEXT,
        needs_json TEXT,
        severity TEXT,
        extracted_claims_json TEXT,
        processing_status TEXT,
        provider_used TEXT,
        incident_id TEXT
    )
    """)

    # Incidents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        location TEXT NOT NULL,
        normalized_location_id TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        report_ids_json TEXT NOT NULL,
        languages_json TEXT NOT NULL,
        unified_summary TEXT,
        has_contradiction INTEGER NOT NULL DEFAULT 0,
        contradiction_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        operator_notes TEXT
    )
    """)

    # Evidence claims table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence_claims (
        id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        report_id TEXT NOT NULL,
        claim_type TEXT NOT NULL,
        claim_text TEXT NOT NULL,
        is_conflicting INTEGER DEFAULT 0,
        conflict_with_claim_id TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Simulated inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id TEXT PRIMARY KEY,
        item_name TEXT NOT NULL,
        total_qty INTEGER NOT NULL,
        available_qty INTEGER NOT NULL,
        unit TEXT NOT NULL,
        depot_name TEXT NOT NULL
    )
    """)

    # Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        incident_title TEXT NOT NULL,
        item_name TEXT NOT NULL,
        recommended_qty INTEGER NOT NULL,
        unit TEXT NOT NULL,
        depot_name TEXT NOT NULL,
        rationale TEXT NOT NULL,
        route_warning TEXT,
        status TEXT NOT NULL DEFAULT 'PROPOSED'
    )
    """)

    # Activity logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT DEFAULT 'INFO'
    )
    """)

    conn.commit()

    # Seed initial inventory if empty
    cursor.execute("SELECT COUNT(*) as count FROM inventory")
    if cursor.fetchone()["count"] == 0:
        seed_inventory(cursor)
        conn.commit()

    conn.close()

def seed_inventory(cursor):
    inventory_data = [
        ("INV-001", "Drinking Water", 500, 500, "Liters", "Depot A - Central Logistics"),
        ("INV-002", "Emergency Food Packets", 350, 350, "Kits", "Depot A - Central Logistics"),
        ("INV-003", "Trauma & First Aid Kits", 45, 45, "Units", "District Base Hospital"),
        ("INV-004", "Inflatable Rescue Boats", 4, 4, "Boats", "NDRF Base Sector 9")
    ]
    cursor.executemany("""
    INSERT INTO inventory (id, item_name, total_qty, available_qty, unit, depot_name)
    VALUES (?, ?, ?, ?, ?, ?)
    """, inventory_data)

def log_activity(event_type: str, title: str, description: str, severity: str = "INFO", conn=None):
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True
    
    cursor = conn.cursor()
    log_id = f"LOG-{int(datetime.now().timestamp()*1000)}"
    cursor.execute("""
    INSERT INTO activity_logs (id, timestamp, event_type, title, description, severity)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (log_id, datetime.now().isoformat(), event_type, title, description, severity))
    conn.commit()
    
    if close_at_end:
        conn.close()

def reset_database():
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports")
        cursor.execute("DELETE FROM incidents")
        cursor.execute("DELETE FROM evidence_claims")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM recommendations")
        cursor.execute("DELETE FROM activity_logs")
        seed_inventory(cursor)
        conn.commit()
        conn.close()
        log_activity("SYSTEM_RESET", "Database Reset", "System reset to initial demonstration state with clean inventory.", "WARNING")
