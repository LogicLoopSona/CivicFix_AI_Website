import os, json, uuid, re
from datetime import datetime
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "complaints.json")

app = Flask(__name__)
app.secret_key = "civicfix-ai-demo-secret-change-this"
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

def load_complaints():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_complaints(items):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

def classify_issue(description, filename=""):
    """Transparent demo classifier: keyword rules, not a trained computer-vision model."""
    text = (description + " " + filename).lower()
    rules = [
        ("Pothole / Road Damage", ["pothole", "road", "crack", "damage", " सड़क", "गड्ढा"], "Public Works Department"),
        ("Garbage / Waste", ["garbage", "waste", "trash", "dump", "kachra", "कचरा"], "Sanitation Department"),
        ("Broken Streetlight", ["streetlight", "street light", "lamp", "dark", "light pole"], "Electrical Department"),
        ("Water Leakage", ["water", "leak", "pipe", "drain", "जल", "पानी"], "Water Supply Department"),
    ]
    for category, words, dept in rules:
        if any(w in text for w in words):
            return category, dept, "Keyword-based demo match"
    return "Other Civic Issue", "Municipal Helpdesk", "No strong keyword match; manual review recommended"

def assess_severity(description):
    t = description.lower()
    if any(w in t for w in ["accident", "danger", "open manhole", "major", "severe", "school", "hospital", "flood"]):
        return "Critical"
    if any(w in t for w in ["large", "heavy", "blocked", "overflow", "broken", "deep", "urgent"]):
        return "High"
    if any(w in t for w in ["small", "minor", "slight"]):
        return "Low"
    return "Medium"

def priority_score(severity, reports=1):
    base = {"Low": 20, "Medium": 45, "High": 70, "Critical": 90}.get(severity, 45)
    return min(100, base + min(max(reports - 1, 0) * 3, 10))

@app.route("/")
def home():
    complaints = load_complaints()
    stats = {
        "total": len(complaints),
        "pending": sum(c["status"] in ["Reported", "AI Verified", "Assigned"] for c in complaints),
        "progress": sum(c["status"] == "In Progress" for c in complaints),
        "resolved": sum(c["status"] == "Resolved" for c in complaints),
    }
    return render_template("index.html", stats=stats, recent=sorted(complaints, key=lambda x: x["created_at"], reverse=True)[:4])

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact = request.form.get("contact", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        lat = request.form.get("latitude", "").strip()
        lng = request.form.get("longitude", "").strip()
        photo = request.files.get("photo")
        if not name or not description or not location:
            flash("Please complete your name, description and location.", "error")
            return redirect(url_for("report"))
        image_name = ""
        if photo and photo.filename:
            ext = os.path.splitext(photo.filename)[1].lower()
            if ext not in ALLOWED:
                flash("Please upload a JPG, PNG or WEBP image.", "error")
                return redirect(url_for("report"))
            image_name = uuid.uuid4().hex + ext
            photo.save(os.path.join(UPLOAD_DIR, image_name))
        category, department, ai_note = classify_issue(description, image_name)
        severity = assess_severity(description)
        complaints = load_complaints()
        # Simple duplicate hint: same category and normalized location.
        normalized = re.sub(r"\W+", "", location.lower())
        duplicate = next((c for c in complaints if c["category"] == category and re.sub(r"\W+", "", c["location"].lower()) == normalized and c["status"] != "Resolved"), None)
        reports = 2 if duplicate else 1
        complaint = {
            "id": "CFAI-" + uuid.uuid4().hex[:7].upper(),
            "name": name, "contact": contact, "description": description,
            "location": location, "latitude": lat, "longitude": lng,
            "photo": image_name, "category": category, "department": department,
            "severity": severity, "priority": priority_score(severity, reports),
            "duplicate_of": duplicate["id"] if duplicate else "",
            "status": "AI Verified", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "resolution_photo": "", "updates": ["Complaint received", "Demo AI screening completed"]
        }
        complaints.append(complaint)
        save_complaints(complaints)
        return render_template("submitted.html", complaint=complaint)
    return render_template("report.html")

@app.route("/track", methods=["GET", "POST"])
def track():
    result = None
    if request.method == "POST":
        cid = request.form.get("complaint_id", "").strip().upper()
        result = next((c for c in load_complaints() if c["id"] == cid), None)
        if not result:
            flash("No complaint found. Please check the ID.", "error")
    return render_template("track.html", complaint=result)

@app.route("/dashboard")
def dashboard():
    complaints = sorted(load_complaints(), key=lambda x: (x["priority"], x["created_at"]), reverse=True)
    stats = {
        "total": len(complaints),
        "pending": sum(c["status"] in ["Reported", "AI Verified", "Assigned"] for c in complaints),
        "progress": sum(c["status"] == "In Progress" for c in complaints),
        "resolved": sum(c["status"] == "Resolved" for c in complaints),
        "critical": sum(c["severity"] == "Critical" and c["status"] != "Resolved" for c in complaints),
    }
    return render_template("dashboard.html", complaints=complaints, stats=stats)

@app.route("/admin/update/<cid>", methods=["POST"])
def update_complaint(cid):
    complaints = load_complaints()
    item = next((c for c in complaints if c["id"] == cid), None)
    if not item:
        flash("Complaint not found.", "error")
        return redirect(url_for("dashboard"))
    status = request.form.get("status", item["status"])
    allowed_status = ["Reported", "AI Verified", "Assigned", "In Progress", "Resolved"]
    if status in allowed_status:
        item["status"] = status
        item["updates"].append(f"Status updated to {status}")
    dept = request.form.get("department", "").strip()
    if dept:
        item["department"] = dept
    proof = request.files.get("resolution_photo")
    if proof and proof.filename:
        ext = os.path.splitext(proof.filename)[1].lower()
        if ext in ALLOWED:
            name = "proof_" + uuid.uuid4().hex + ext
            proof.save(os.path.join(UPLOAD_DIR, name))
            item["resolution_photo"] = name
            item["updates"].append("After-repair evidence uploaded")
    save_complaints(complaints)
    flash("Complaint updated successfully.", "success")
    return redirect(url_for("dashboard"))

@app.route("/api/complaints")
def api_complaints():
    return jsonify(load_complaints())

@app.errorhandler(413)
def too_large(_):
    flash("File is too large. Maximum upload size is 8 MB.", "error")
    return redirect(url_for("report"))

if __name__ == "__main__":
    app.run(debug=True)
