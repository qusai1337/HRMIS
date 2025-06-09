
#  Human Rights Monitor MIS (COMP4382)

A secure, modular Management Information System for documenting, analyzing, and visualizing human rights violations.

---

##  Project Structure

```
human-rights-monitor/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── cases.py
│   │   ├── reports.py
│   │   ├── victims.py
│   │   └── analytics.py
│   ├── models/
│   ├── database.py
│   └── requirements.txt
├── dashboard/
│   └── dashboard.py  # Streamlit dashboard
├──
│   └── hrm_postman_collection.json
└── README.md
```

---

## Tech Stack

- **Backend**: FastAPI + MongoDB
- **Frontend**: Streamlit
- **Data Viz**: D3.js, Plotly, Matplotlib
- **Others**: Pandas, XlsxWriter, PyMongo

---

## How to Run

### ▶ Backend (FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

4. Access docs:
   - Swagger UI: `http://localhost:8000/docs`
   - Redoc: `http://localhost:8000/redoc`

---

### 📊 Frontend Dashboard (Streamlit)

1. From root folder:
   ```bash
   streamlit run frontend/dashboard.py
   ```

2. The dashboard includes:
   - Filters (date, violation type, country)
   - Violation charts (bar, pie)
   - Timeline line chart
   - Choropleth map (D3.js)
   - Download Excel/CSV reports

---

##  API Collection

Postman collection is available in the `postman/` folder.

- **GET** `/analytics/violations`
- **GET** `/analytics/geodata`
- **GET** `/analytics/timeline`
- **POST/GET/PATCH/DELETE** for:
  - `/cases/`
  - `/reports/`
  - `/victims/`

---

##  Authors & Modules

by qusai iyad
---

## 📅ubmission

- GitHub Repo Link submitted on Ritaj 
- Project uploaded as `.zip` to ITC 

---

##  Disclaimer

This is an academic project developed for COMP4382 – Spring 2024/2025.  
All data used is synthetic and for demonstration only.
