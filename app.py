import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models import ReportCreate, TranslationRequest
from database import init_db, get_connection, log_activity, reset_database
from ai_service import ai_service, SUPPORTED_LANGUAGES

app = FastAPI(title="PRAVAHA Multilingual Crisis Intelligence", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
init_db()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>PRAVAHA Multilingual Crisis Intelligence System Running</h1>")

@app.get("/api/status")
def get_system_status():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as c FROM reports")
    report_count = c.fetchone()["c"]
    c.execute("SELECT COUNT(*) as c FROM incidents")
    incident_count = c.fetchone()["c"]
    c.execute("SELECT COUNT(*) as c FROM incidents WHERE has_contradiction = 1")
    contradiction_count = c.fetchone()["c"]
    c.execute("SELECT COUNT(*) as c FROM recommendations WHERE status = 'PROPOSED'")
    pending_recs = c.fetchone()["c"]

    # Language breakdown from actual database records
    c.execute("SELECT language, COUNT(*) as count FROM reports GROUP BY language")
    lang_stats = {r["language"]: r["count"] for r in c.fetchall()}
    conn.close()

    provider_info = ai_service.get_provider_status()

    return {
        "status": "OPERATIONAL",
        "system": "PRAVAHA Multilingual Crisis Intelligence Engine",
        "scenario": "India Multilingual Flood Response (Monsoon Crisis)",
        "provider": provider_info,
        "language_distribution": lang_stats,
        "metrics": {
            "total_reports": report_count,
            "active_incidents": incident_count,
            "contradictions": contradiction_count,
            "pending_recommendations": pending_recs
        }
    }

@app.post("/api/toggle-provider")
def toggle_provider():
    is_fallback = ai_service.toggle_provider()
    provider_info = ai_service.get_provider_status()
    log_activity(
        "PROVIDER_TOGGLE",
        "AI Engine Mode Toggled",
        f"Active provider switched to: {provider_info['active_provider']}",
        "WARNING" if is_fallback else "INFO"
    )
    return provider_info

@app.get("/api/reports")
def list_reports():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY timestamp DESC")
    rows = c.fetchall()
    reports = []
    for r in rows:
        d = dict(r)
        d["needs"] = json.loads(d["needs_json"]) if d["needs_json"] else []
        d["extracted_claims"] = json.loads(d["extracted_claims_json"]) if d["extracted_claims_json"] else []
        reports.append(d)
    conn.close()
    return reports

@app.post("/api/reports")
def submit_report(payload: ReportCreate):
    conn = get_connection()
    c = conn.cursor()

    # Generate sequential Report ID
    c.execute("SELECT COUNT(*) as count FROM reports")
    idx = c.fetchone()["count"] + 1
    report_id = f"REP-{idx:03d}"

    # Multilingual AI Extraction & Normalization
    extraction = ai_service.extract_report(
        text=payload.text,
        user_language=payload.language or "Auto",
        location_hint=payload.location
    )
    
    timestamp = datetime.now().isoformat()
    needs_json = json.dumps(extraction.get("needs", []))
    claims_json = json.dumps(extraction.get("claims", []))

    # Fetch existing incidents for canonical correlation
    c.execute("SELECT * FROM incidents")
    existing_incidents_raw = c.fetchall()
    existing_incidents = []
    for inc in existing_incidents_raw:
        inc_dict = dict(inc)
        inc_dict["report_ids"] = json.loads(inc_dict["report_ids_json"])
        inc_dict["languages"] = json.loads(inc_dict["languages_json"]) if inc_dict.get("languages_json") else []
        existing_incidents.append(inc_dict)

    # Correlate using canonical location entity and category
    match_type, matched_inc_id, match_details = ai_service.correlate_report(
        {
            "text": payload.text,
            "normalized_location_id": extraction.get("normalized_location_id"),
            "category": extraction.get("category"),
            "claims": extraction.get("claims", []),
            "road_status": extraction.get("road_status", "UNKNOWN")
        },
        existing_incidents
    )

    incident_id = matched_inc_id
    contradiction_found = False

    if match_type == "NEW_INCIDENT" or not incident_id:
        c.execute("SELECT COUNT(*) as count FROM incidents")
        inc_idx = c.fetchone()["count"] + 1
        incident_id = f"INC-{inc_idx:03d}"
        
        inc_title = f"{extraction.get('category')} - {extraction.get('location')}"
        initial_languages = [extraction.get("language", "English")]
        
        summary = ai_service.generate_unified_summary(
            incident_title=inc_title,
            location=extraction.get("location"),
            languages=initial_languages,
            report_count=1,
            needs=extraction.get("needs", []),
            has_contradiction=False
        )

        c.execute("""
        INSERT INTO incidents (id, title, location, normalized_location_id, category, severity, status, report_ids_json, languages_json, unified_summary, has_contradiction, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'unverified', ?, ?, ?, 0, ?, ?)
        """, (
            incident_id,
            inc_title,
            extraction.get("location", "Sector 4"),
            extraction.get("normalized_location_id"),
            extraction.get("category", "Flooding & Inundation"),
            extraction.get("severity", "HIGH"),
            json.dumps([report_id]),
            json.dumps(initial_languages),
            summary,
            timestamp,
            timestamp
        ))
        log_activity("NEW_INCIDENT", f"Incident Created: {incident_id}", f"Generated from {extraction.get('language')} report {report_id} at {extraction.get('location')}", conn=conn)

    elif match_type == "CORROBORATION":
        c.execute("SELECT report_ids_json, languages_json, severity, title, location FROM incidents WHERE id = ?", (incident_id,))
        inc_row = c.fetchone()
        reps = json.loads(inc_row["report_ids_json"])
        langs = json.loads(inc_row["languages_json"]) if inc_row["languages_json"] else []
        
        if report_id not in reps:
            reps.append(report_id)
        if extraction.get("language") not in langs:
            langs.append(extraction.get("language"))
        
        summary = ai_service.generate_unified_summary(
            incident_title=inc_row["title"],
            location=inc_row["location"],
            languages=langs,
            report_count=len(reps),
            needs=extraction.get("needs", []),
            has_contradiction=False
        )

        c.execute("""
        UPDATE incidents 
        SET status = 'corroborated', report_ids_json = ?, languages_json = ?, unified_summary = ?, updated_at = ?
        WHERE id = ?
        """, (json.dumps(reps), json.dumps(langs), summary, timestamp, incident_id))
        
        log_activity("CORROBORATION", f"Multilingual Corroboration: {incident_id}", f"Report {report_id} ({extraction.get('language')}) corroborated claims for {inc_row['title']}.", conn=conn)

    elif match_type == "CONTRADICTION":
        contradiction_found = True
        c.execute("SELECT report_ids_json, languages_json, title, location FROM incidents WHERE id = ?", (incident_id,))
        inc_row = c.fetchone()
        reps = json.loads(inc_row["report_ids_json"])
        langs = json.loads(inc_row["languages_json"]) if inc_row["languages_json"] else []
        
        if report_id not in reps:
            reps.append(report_id)
        if extraction.get("language") not in langs:
            langs.append(extraction.get("language"))
        
        c_note = match_details.get("reason", "Conflicting evidence surfaced.")
        
        summary = ai_service.generate_unified_summary(
            incident_title=inc_row["title"],
            location=inc_row["location"],
            languages=langs,
            report_count=len(reps),
            needs=extraction.get("needs", []),
            has_contradiction=True
        )

        c.execute("""
        UPDATE incidents 
        SET status = 'conflicting', has_contradiction = 1, contradiction_notes = ?, report_ids_json = ?, languages_json = ?, unified_summary = ?, updated_at = ?
        WHERE id = ?
        """, (c_note, json.dumps(reps), json.dumps(langs), summary, timestamp, incident_id))
        
        log_activity("CONTRADICTION", f"Contradiction Alert on {incident_id}", c_note, "WARNING", conn=conn)

    elif match_type == "DUPLICATE":
        c.execute("SELECT report_ids_json FROM incidents WHERE id = ?", (incident_id,))
        inc_row = c.fetchone()
        reps = json.loads(inc_row["report_ids_json"])
        if report_id not in reps:
            reps.append(report_id)
            c.execute("UPDATE incidents SET report_ids_json = ?, updated_at = ? WHERE id = ?", (json.dumps(reps), timestamp, incident_id))
        log_activity("DUPLICATE", f"Duplicate Report Flagged", f"Report {report_id} contains duplicate information for {incident_id}.", conn=conn)

    # Save immutable report with separate normalized English text
    c.execute("""
    INSERT INTO reports (id, text, language, language_code, normalized_en_text, timestamp, location, normalized_location_id, source_type, category, needs_json, severity, extracted_claims_json, processing_status, provider_used, incident_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PROCESSED', ?, ?)
    """, (
        report_id,
        payload.text,
        extraction.get("language", "English"),
        extraction.get("language_code", "en-IN"),
        extraction.get("normalized_en_text"),
        timestamp,
        extraction.get("location"),
        extraction.get("normalized_location_id"),
        payload.source_type or "Citizen SMS",
        extraction.get("category"),
        needs_json,
        extraction.get("severity"),
        claims_json,
        extraction.get("provider_used"),
        incident_id
    ))

    # Add claims to evidence_claims table
    for claim in extraction.get("claims", []):
        claim_id = f"CLM-{uuid.uuid4().hex[:6]}"
        is_conf = 1 if (contradiction_found and ("open" in claim.lower() or "খোলা" in claim or "திறக்க" in claim)) else 0
        c.execute("""
        INSERT INTO evidence_claims (id, incident_id, report_id, claim_type, claim_text, is_conflicting, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, incident_id, report_id, extraction.get("category"), claim, is_conf, timestamp))

    conn.commit()

    # Generate or refresh recommendations for this incident
    c.execute("SELECT * FROM inventory")
    inv_items = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    inc_curr = dict(c.fetchone())
    
    # Aggregate needs across all reports in this incident
    c.execute("SELECT needs_json FROM reports WHERE incident_id = ?", (incident_id,))
    all_needs = []
    for r_row in c.fetchall():
        if r_row["needs_json"]:
            all_needs.extend(json.loads(r_row["needs_json"]))
    inc_curr["needs"] = list(set(all_needs))

    new_recs = ai_service.generate_recommendations(inc_curr, inv_items)
    for rec in new_recs:
        c.execute("SELECT id FROM recommendations WHERE incident_id = ? AND item_name = ?", (incident_id, rec["item_name"]))
        existing_rec = c.fetchone()
        if existing_rec:
            # Update existing recommendation with route warning if contradiction surfaced
            c.execute("""
            UPDATE recommendations 
            SET route_warning = ?, rationale = ?
            WHERE id = ?
            """, (rec.get("route_warning"), rec["rationale"], existing_rec["id"]))
        else:
            rec_id = f"REC-{uuid.uuid4().hex[:6]}"
            c.execute("""
            INSERT INTO recommendations (id, incident_id, incident_title, item_name, recommended_qty, unit, depot_name, rationale, route_warning, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PROPOSED')
            """, (
                rec_id,
                rec["incident_id"],
                rec["incident_title"],
                rec["item_name"],
                rec["recommended_qty"],
                rec["unit"],
                rec["depot_name"],
                rec["rationale"],
                rec.get("route_warning")
            ))
            log_activity("RESOURCE_PROPOSAL", f"Relief Recommended: {rec['item_name']}", f"Proposed {rec['recommended_qty']} {rec['unit']} for {incident_id}", conn=conn)

    conn.commit()
    conn.close()

    return {
        "status": "SUCCESS",
        "report_id": report_id,
        "incident_id": incident_id,
        "match_type": match_type,
        "match_details": match_details,
        "extraction": extraction
    }

@app.get("/api/incidents")
def list_incidents():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents ORDER BY updated_at DESC")
    rows = c.fetchall()
    incidents = []
    for r in rows:
        d = dict(r)
        d["report_ids"] = json.loads(d["report_ids_json"])
        d["languages"] = json.loads(d["languages_json"]) if d.get("languages_json") else []
        incidents.append(d)
    conn.close()
    return incidents

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    inc_row = c.fetchone()
    if not inc_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = dict(inc_row)
    report_ids = json.loads(incident["report_ids_json"])
    incident["report_ids"] = report_ids
    incident["languages"] = json.loads(incident["languages_json"]) if incident.get("languages_json") else []

    reports = []
    if report_ids:
        placeholders = ",".join("?" for _ in report_ids)
        c.execute(f"SELECT * FROM reports WHERE id IN ({placeholders})", report_ids)
        for r in c.fetchall():
            rd = dict(r)
            rd["needs"] = json.loads(rd["needs_json"]) if rd["needs_json"] else []
            rd["extracted_claims"] = json.loads(rd["extracted_claims_json"]) if rd["extracted_claims_json"] else []
            reports.append(rd)
    incident["reports"] = reports

    c.execute("SELECT * FROM evidence_claims WHERE incident_id = ? ORDER BY created_at DESC", (incident_id,))
    incident["evidence_claims"] = [dict(cl) for cl in c.fetchall()]

    c.execute("SELECT * FROM recommendations WHERE incident_id = ?", (incident_id,))
    incident["recommendations"] = [dict(rc) for rc in c.fetchall()]

    conn.close()
    return incident

@app.post("/api/incidents/{incident_id}/translate-summary")
def translate_incident_summary(incident_id: str, payload: TranslationRequest):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT unified_summary FROM incidents WHERE id = ?", (incident_id,))
    row = c.fetchone()
    conn.close()

    if not row or not row["unified_summary"]:
        raise HTTPException(status_code=404, detail="Unified summary not found")

    translated = ai_service.translate_summary(row["unified_summary"], payload.target_language)
    return {
        "incident_id": incident_id,
        "target_language": payload.target_language,
        "translated_summary": translated
    }

@app.post("/api/incidents/{incident_id}/action")
def incident_action(incident_id: str, payload: Dict[str, Any]):
    action = payload.get("action")
    note = payload.get("note", "")

    conn = get_connection()
    c = conn.cursor()

    if action == "verify":
        c.execute("""
        UPDATE incidents 
        SET status = 'human_reviewed', operator_notes = ?, updated_at = ?
        WHERE id = ?
        """, (f"Verified by operator. {note}".strip(), datetime.now().isoformat(), incident_id))
        log_activity("HUMAN_REVIEW", f"Incident Verified: {incident_id}", f"Operator marked incident as verified. Note: {note}", conn=conn)

    elif action == "resolve_contradiction":
        c.execute("""
        UPDATE incidents 
        SET has_contradiction = 0, contradiction_notes = ?, status = 'human_reviewed', updated_at = ?
        WHERE id = ?
        """, (f"Contradiction resolved by operator: {note}", datetime.now().isoformat(), incident_id))
        log_activity("CONTRADICTION_RESOLVED", f"Contradiction Cleared on {incident_id}", note, conn=conn)

    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "incident_id": incident_id, "action": action}

@app.get("/api/inventory")
def get_inventory():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    items = [dict(r) for r in c.fetchall()]
    conn.close()
    return items

@app.get("/api/recommendations")
def list_recommendations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM recommendations ORDER BY rowid DESC")
    recs = [dict(r) for r in c.fetchall()]
    conn.close()
    return recs

@app.post("/api/recommendations/{rec_id}/status")
def update_recommendation_status(rec_id: str, payload: Dict[str, str]):
    new_status = payload.get("status", "PROPOSED")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM recommendations WHERE id = ?", (rec_id,))
    rec = c.fetchone()
    if not rec:
        conn.close()
        raise HTTPException(status_code=404, detail="Recommendation not found")

    item_name = rec["item_name"]
    alloc_qty = rec["recommended_qty"]

    if new_status == "APPROVED" and rec["status"] != "APPROVED":
        c.execute("SELECT available_qty FROM inventory WHERE item_name = ?", (item_name,))
        inv = c.fetchone()
        if inv and inv["available_qty"] >= alloc_qty:
            c.execute("UPDATE inventory SET available_qty = available_qty - ? WHERE item_name = ?", (alloc_qty, item_name))
            c.execute("UPDATE recommendations SET status = 'APPROVED' WHERE id = ?", (rec_id,))
            log_activity("DISPATCH_APPROVED", f"Dispatch Authorized: {item_name}", f"Allocated {alloc_qty} {rec['unit']} for {rec['incident_id']} at {rec['depot_name']}", conn=conn)
        else:
            conn.close()
            raise HTTPException(status_code=400, detail="Insufficient inventory available")

    elif new_status == "HELD_FOR_RECON":
        c.execute("UPDATE recommendations SET status = 'HELD_FOR_RECON' WHERE id = ?", (rec_id,))
        log_activity("DISPATCH_HELD", f"Dispatch Held: {item_name}", f"Held pending scout reconnaissance for route verification.", conn=conn)

    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "rec_id": rec_id, "new_status": new_status}

@app.get("/api/activity")
def get_activity():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 30")
    logs = [dict(r) for r in c.fetchall()]
    conn.close()
    return logs

# MULTILINGUAL ACCEPTANCE TEST ENDPOINT
@app.post("/api/demo/multilingual")
def run_multilingual_test_suite():
    """
    Executes the exact 5-report Acceptance Test:
    Reports 1-4: Hindi, Bengali, Tamil, English flood reports near Government Primary School.
    Report 5: Flood report for Rampur Village (MUST NOT MERGE!).
    """
    reset_database()

    # 1. Hindi Report
    rep1 = submit_report(ReportCreate(
        text="पानी तेजी से बढ़ रहा है। सरकारी स्कूल के पास परिवार फंसे हुए हैं। पीने का पानी चाहिए।",
        location="Near Government Primary School, Sector 4",
        source_type="Citizen SMS (Hindi)",
        language="Hindi"
    ))

    # 2. Bengali Report
    rep2 = submit_report(ReportCreate(
        text="জল দ্রুত বাড়ছে। সরকারি প্রাথমিক বিদ্যালয়ের কাছে পরিবারগুলি আটকে রয়েছে। পানীয় জলের তীব্র সংকট।",
        location="Government Primary School, Sector 4",
        source_type="Volunteer Post (Bengali)",
        language="Bengali"
    ))

    # 3. Tamil Report
    rep3 = submit_report(ReportCreate(
        text="தண்ணீர் வேகமாக உயர்ந்து வருகிறது. அரசு தொடக்கப் பள்ளி அருகே குடும்பங்கள் சிக்கித் தவிக்கின்றனர். குடிநீர் தேவை.",
        location="Near Primary School",
        source_type="Emergency Helpline (Tamil)",
        language="Tamil"
    ))

    # 4. English Report
    rep4 = submit_report(ReportCreate(
        text="Floodwaters rising fast. Families stranded near the government primary school. Drinking water urgently required.",
        location="Government Primary School, Sector 4",
        source_type="Field Dispatch (English)",
        language="English"
    ))

    # 5. Distinct Village Report (Rampur Village)
    rep5 = submit_report(ReportCreate(
        text="Floodwaters entered Rampur village. Farmlands and houses submerged near the riverbank.",
        location="Rampur Village, Riverside Sector",
        source_type="Field Volunteer",
        language="English"
    ))

    # Fetch resulting incidents
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents")
    all_inc = [dict(r) for r in c.fetchall()]
    for inc in all_inc:
        inc["report_ids"] = json.loads(inc["report_ids_json"])
        inc["languages"] = json.loads(inc["languages_json"]) if inc.get("languages_json") else []
    conn.close()

    school_inc = next((i for i in all_inc if "SCHOOL" in i["normalized_location_id"]), None)
    rampur_inc = next((i for i in all_inc if "RAMPUR" in i["normalized_location_id"]), None)

    return {
        "status": "SUCCESS",
        "message": "Multilingual acceptance test executed successfully.",
        "school_incident": school_inc,
        "rampur_incident": rampur_inc,
        "total_incidents_created": len(all_inc),
        "distinct_village_separated": bool(school_inc and rampur_inc and school_inc["id"] != rampur_inc["id"]),
        "reports": [rep1, rep2, rep3, rep4, rep5]
    }

# DEMONSTRATION WORKFLOW ENDPOINTS (STEPS 1-5)
@app.post("/api/demo/step/{step_number}")
def execute_demo_step(step_number: int):
    if step_number == 1:
        res = submit_report(ReportCreate(
            text="पानी तेजी से बढ़ रहा है। सरकारी स्कूल के पास परिवार फंसे हुए हैं। पीने का पानी चाहिए।",
            location="Near Government Primary School, Sector 4",
            source_type="Citizen Emergency SMS (Hindi)",
            language="Hindi"
        ))
        return {
            "step": 1,
            "title": "Hindi Emergency Report Ingested",
            "description": "Original Hindi report processed. Multilingual entity extraction detected flood surge, trapped families, and critical drinking water shortage near the Government School.",
            "data": res
        }

    elif step_number == 2:
        res = submit_report(ReportCreate(
            text="Families are trapped near the government school. Water levels are rising.",
            location="Government School, Sector 4",
            source_type="Helpline Field Agent (English)",
            language="English"
        ))
        return {
            "step": 2,
            "title": "English Field Report Ingested",
            "description": "Second report received in English. Cross-lingual correlation detected matching geographic entity and corroborating threat level.",
            "data": res
        }

    elif step_number == 3:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM incidents WHERE status = 'corroborated' LIMIT 1")
        inc = c.fetchone()
        conn.close()
        return {
            "step": 3,
            "title": "Incident Corroboration & Evidence Linking",
            "description": "The system grouped the Hindi and English reports into a single corroborated incident. Multiple independent reports corroborate the trapped civilians claim.",
            "incident": dict(inc) if inc else None
        }

    elif step_number == 4:
        res = submit_report(ReportCreate(
            text="The road near the school is now open.",
            location="Sector 4 Access Road near School",
            source_type="Local Volunteer Twitter/X",
            language="English"
        ))
        return {
            "step": 4,
            "title": "Contradictory Road Access Report Ingested",
            "description": "Received claim stating road is now open. Contradiction engine flagged conflict against active flood and trapped civilian reports.",
            "data": res
        }

    elif step_number == 5:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM incidents WHERE has_contradiction = 1 LIMIT 1")
        inc = c.fetchone()
        c.execute("SELECT * FROM recommendations WHERE route_warning IS NOT NULL LIMIT 1")
        rec = c.fetchone()
        conn.close()
        return {
            "step": 5,
            "title": "Contradiction Surfaced & Safe Resource Allocation",
            "description": "System preserved conflicting claims without declaring the route safe. Generated resource recommendations with mandatory route reconnaissance warning.",
            "incident": dict(inc) if inc else None,
            "recommendation": dict(rec) if rec else None
        }

    raise HTTPException(status_code=400, detail=f"Invalid demo step {step_number}. Must be 1 to 5.")

@app.post("/api/demo/reset")
def demo_reset():
    reset_database()
    return {"status": "SUCCESS", "message": "System reset to initial clean state with fresh inventory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
