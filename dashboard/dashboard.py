import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime
import io
import streamlit.components.v1 as components

# Mongo connection
client = MongoClient("mongodb://localhost:27017/")
db = client["hrm_database"]
reports_collection = db["incident_reports"]

# Sidebar filters
st.sidebar.header("🔍 Filters")
violation_type_filter = st.sidebar.text_input("Violation Type")
country_filter = st.sidebar.text_input("Country")
start_date = st.sidebar.date_input("From Date", value=datetime(2024, 1, 1))
end_date = st.sidebar.date_input("To Date", value=datetime.today())

start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

st.title("📊 Human Rights Dashboard")

# Common date format & validation
date_format = "%Y-%m-%d %H:%M:%S"
date_validation = {"incident_details.date": {"$regex": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$"}}

# Violations by Type
st.subheader("1️⃣ Violations by Type")
pipeline_violations = [
    {"$match": date_validation},
    {"$addFields": {
        "parsed_date": {
            "$dateFromString": {
                "dateString": "$incident_details.date",
                "format": date_format
            }
        }
    }},
    {"$match": {
        "parsed_date": {"$gte": start_dt, "$lte": end_dt},
        **({"incident_details.violation_types": violation_type_filter} if violation_type_filter else {}),
        **({"incident_details.location.country": country_filter} if country_filter else {})
    }},
    {"$unwind": "$incident_details.violation_types"},
    {"$group": {"_id": "$incident_details.violation_types", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
violations = list(reports_collection.aggregate(pipeline_violations))
st.write("🔍 Violations Raw:", violations)
if violations:
    df_v = pd.DataFrame(violations)
    df_v.columns = ["Violation Type", "Count"]
    st.bar_chart(df_v.set_index("Violation Type"))
    fig_pie = px.pie(df_v, names="Violation Type", values="Count", title="Violation Distribution")
    st.plotly_chart(fig_pie)
else:
    st.info("No data for selected filters.")

# Violations by Country (D3.js Map)
st.subheader("2️⃣ Violations by Country")
pipeline_geo = [
    {"$match": date_validation},
    {"$addFields": {
        "parsed_date": {
            "$dateFromString": {
                "dateString": "$incident_details.date",
                "format": date_format
            }
        }
    }},
    {"$match": {
        "parsed_date": {"$gte": start_dt, "$lte": end_dt},
        **({"incident_details.violation_types": violation_type_filter} if violation_type_filter else {}),
        **({"incident_details.location.country": country_filter} if country_filter else {})
    }},
    {"$group": {"_id": "$incident_details.location.country", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
countries = list(reports_collection.aggregate(pipeline_geo))
st.write("🔍 Countries Raw:", countries)
if countries:
    df_c = pd.DataFrame(countries)
    df_c.columns = ["Country", "Count"]
    st.bar_chart(df_c.set_index("Country"))

    # Render D3.js map
    d3_data = df_c.to_dict(orient="records")
    d3_script = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://d3js.org/d3.v7.min.js"></script>
    </head>
    <body>
    <div id="chart"></div>
    <script>
        const data = {d3_data};

        const width = 800;
        const height = 500;

        const svg = d3.select("#chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const projection = d3.geoNaturalEarth1()
            .scale(160)
            .translate([width / 2, height / 2]);

        const path = d3.geoPath().projection(projection);

        d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").then(function(world) {{
            svg.selectAll("path")
                .data(world.features)
                .join("path")
                .attr("d", path)
                .attr("fill", d => {{
                    const countryData = data.find(c => c.Country.toLowerCase() === d.properties.name.toLowerCase());
                    return countryData ? "orangered" : "#ddd";
                }})
                .attr("stroke", "white")
                .attr("stroke-width", 0.5)
                .append("title")
                .text(d => {{
                    const countryData = data.find(c => c.Country.toLowerCase() === d.properties.name.toLowerCase());
                    return countryData ? d.properties.name + ": " + countryData.Count : d.properties.name;
                }});
        }});
    </script>
    </body>
    </html>
    """
    st.subheader("🗺️ D3.js Map of Violations by Country")
    components.html(d3_script, height=550)
else:
    st.info("No country data.")

# Reports Timeline
st.subheader("3️⃣ Reports Timeline")
pipeline_timeline = [
    {"$match": date_validation},
    {"$addFields": {
        "parsed_date": {
            "$dateFromString": {
                "dateString": "$incident_details.date",
                "format": date_format
            }
        }
    }},
    {"$match": {
        "parsed_date": {"$gte": start_dt, "$lte": end_dt},
        **({"incident_details.violation_types": violation_type_filter} if violation_type_filter else {}),
        **({"incident_details.location.country": country_filter} if country_filter else {})
    }},
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$parsed_date"}},
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
]
timeline = list(reports_collection.aggregate(pipeline_timeline))
st.write("🔍 Timeline Raw:", timeline)
if timeline:
    df_t = pd.DataFrame(timeline)
    df_t.columns = ["Date", "Count"]
    df_t["Date"] = pd.to_datetime(df_t["Date"])
    st.line_chart(df_t.set_index("Date"))
else:
    st.info("No timeline data.")

# Download section
st.subheader("📥 Download Data")

def generate_excel_download(df, filename):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='xlsxwriter')
    st.download_button(
        label=f"📥 Download {filename}.xlsx",
        data=buffer.getvalue(),
        file_name=f"{filename}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def generate_csv_download(df, filename):
    st.download_button(
        label=f"📤 Download {filename}.csv",
        data=df.to_csv(index=False),
        file_name=f"{filename}.csv"
    )

if violations:
    generate_csv_download(df_v, "violations")
    generate_excel_download(df_v, "violations")

if countries:
    generate_csv_download(df_c, "countries")
    generate_excel_download(df_c, "countries")

if timeline:
    generate_csv_download(df_t, "timeline")
    generate_excel_download(df_t, "timeline")
