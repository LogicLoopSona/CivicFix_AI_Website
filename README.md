# CivicFix AI — Civic Issue Reporting & Resolution

A beginner-friendly, locally runnable MVP inspired by the supplied CivicFix AI presentation.

## Features
- Citizen complaint form with photo upload and GPS location capture
- Demo AI screening for potholes/road damage, garbage, broken streetlights and water leakage
- Severity estimation and transparent priority score
- Same-category + same-location duplicate hint
- Complaint tracking by ID
- Authority dashboard with status and department updates
- Upload after-repair evidence

## Important note about AI
This starter project uses a **keyword-based demo classifier**. It does not yet run a trained YOLO/OpenCV computer-vision model. The interface and data flow are ready to connect to a real image model later. Do not present demo classification as production-grade AI.

## Requirements
- Windows 10/11, macOS or Linux
- Python 3.10 or newer
- VS Code (recommended)

## Run on Windows (PowerShell)
1. Extract the ZIP.
2. Open the `CivicFix_AI_Website` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this once in the same terminal and retry:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
6. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
7. Start the website:
   ```powershell
   py app.py
   ```
8. Open this address in your browser:
   `http://127.0.0.1:5000`

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

## Try the demo
1. Click **Report an Issue**.
2. Enter a location and describe an issue. Example: "Large pothole near school, dangerous for two-wheelers".
3. Optionally upload a JPG/PNG/WEBP photo and use **Use my location**.
4. Submit and save the generated complaint ID.
5. Open **Authority Dashboard** to change status and department.
6. Use **Track Complaint** with the complaint ID.

## Project structure
```
CivicFix_AI_Website/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── complaints.json
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/
└── templates/
    ├── base.html
    ├── index.html
    ├── report.html
    ├── submitted.html
    ├── track.html
    └── dashboard.html
```

## Notes
- Data is stored locally in `data/complaints.json`; uploaded photos are stored in `static/uploads/`.
- This is a college-project MVP, not a secure production deployment. There is no real admin login yet. Add authentication, database backups, input hardening, HTTPS and a trained/validated AI model before public deployment.
- Browser GPS works on `localhost` or a secure HTTPS website and requires permission.
- Never upload sensitive personal information in a public demo.
