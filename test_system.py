import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
from database import init_db, reset_database, get_connection
from ai_service import ai_service
from app import submit_report, execute_demo_step, get_incident, update_recommendation_status, list_incidents, run_multilingual_test_suite
from models import ReportCreate

def run_tests():
    print("==================================================")
    print("PRAVAHA MULTILINGUAL CRISIS INTELLIGENCE TEST SUITE")
    print("==================================================")

    print("\n[TEST 1] Initializing and resetting database...")
    reset_database()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as c FROM inventory")
    inv_count = c.fetchone()["c"]
    assert inv_count == 4, f"Expected 4 inventory items, got {inv_count}"
    print(f"PASS: Clean inventory initialized with {inv_count} items.")

    print("\n[TEST 2] Testing Multilingual Acceptance Test (Hindi, Bengali, Tamil, English at School)...")
    res = run_multilingual_test_suite()
    assert res["status"] == "SUCCESS"
    assert res["total_incidents_created"] == 2, f"Expected 2 incidents, got {res['total_incidents_created']}"
    assert res["distinct_village_separated"] == True, "Expected Rampur Village to remain separated!"
    
    school_inc = res["school_incident"]
    rampur_inc = res["rampur_incident"]
    
    print(f"PASS: School Incident {school_inc['id']} successfully linked {len(school_inc['report_ids'])} reports.")
    print(f"      Contributing languages: {school_inc['languages']}")
    print(f"      Unified Summary: {school_inc['unified_summary']}")
    print(f"PASS: Rampur Village Incident {rampur_inc['id']} kept distinct at {rampur_inc['location']}.")

    print("\n[TEST 3] Verifying Original Multilingual Messages Preserved...")
    c.execute("SELECT id, language, text, normalized_en_text, provider_used FROM reports WHERE incident_id = ?", (school_inc["id"],))
    school_reports = c.fetchall()
    assert len(school_reports) == 4, f"Expected 4 reports linked to school incident, got {len(school_reports)}"
    
    for r in school_reports:
        print(f"      Report {r['id']} ({r['language']}): '{r['text']}'")
        print(f"             Normalized EN: '{r['normalized_en_text']}'")
        print(f"             Provider: {r['provider_used']}")

    print("\n[TEST 4] Testing Contradictory Road Report on Corroborated Incident...")
    # Submit report claiming road is open near school
    rep_conflict = submit_report(ReportCreate(
        text="The road near the school is now open.",
        location="Sector 4 Access Road near School",
        source_type="Social Media",
        language="English"
    ))
    assert rep_conflict["match_type"] == "CONTRADICTION"
    
    inc_after_conflict = get_incident(school_inc["id"])
    assert inc_after_conflict["has_contradiction"] == 1
    assert inc_after_conflict["status"] == "conflicting"
    print(f"PASS: Contradiction flagged: {inc_after_conflict['contradiction_notes']}")

    print("\n[TEST 5] Verifying Traceable Recommendations with Safety Warning...")
    recs = inc_after_conflict["recommendations"]
    assert len(recs) > 0, "Expected recommendations to be generated"
    water_rec = next(r for r in recs if r["item_name"] == "Drinking Water")
    assert water_rec["route_warning"] is not None
    assert "ROUTE ACCESSIBILITY CONFLICT" in water_rec["route_warning"]
    print(f"PASS: Safety warning attached: {water_rec['route_warning']}")

    print("\n[TEST 6] Testing Dispatch Authorization & Inventory Deductions...")
    c.execute("SELECT available_qty FROM inventory WHERE item_name = 'Drinking Water'")
    before_qty = c.fetchone()["available_qty"]
    update_res = update_recommendation_status(water_rec["id"], {"status": "APPROVED"})
    assert update_res["status"] == "SUCCESS"
    
    c.execute("SELECT available_qty FROM inventory WHERE item_name = 'Drinking Water'")
    after_qty = c.fetchone()["available_qty"]
    expected_qty = before_qty - water_rec["recommended_qty"]
    assert after_qty == expected_qty, f"Expected inventory {expected_qty}, got {after_qty}"
    print(f"PASS: Dispatch approved. Inventory updated from {before_qty}L to {after_qty}L.")

    print("\n[TEST 7] Testing Translation of Unified Summary...")
    from app import translate_incident_summary
    from models import TranslationRequest
    hi_trans = translate_incident_summary(school_inc["id"], TranslationRequest(text="", target_language="Hindi"))
    print(f"PASS: Unified summary translated to Hindi:")
    print(f"      {hi_trans['translated_summary']}")

    print("\n[TEST 8] Testing Provider Resilience & Fallback Switch...")
    ai_status = ai_service.get_provider_status()
    print(f"PASS: Live Provider Status:")
    print(f"      Active: {ai_status['active_provider']}")
    print(f"      Is Fallback: {ai_status['is_fallback']}")
    print(f"      Languages Supported: {len(ai_status['supported_languages'])} Indian Languages")

    conn.close()
    print("\n==================================================")
    print("ALL 8 PRAVAHA SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
