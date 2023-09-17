from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from . import models
from sqlalchemy.orm import Session
from .models import UserReport as Report
from .generation import generate_reports
from .database import engine,SessionLocal
import uuid
import random
import json
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Store Monitoring API!"}


@app.post("/trigger_report", response_model=dict)
async def trigger_report(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    # Generate a unique report_id (e.g., using UUID)
    report_id = random.randint(1,1000000000)


    # Trigger the report generation in the background using background_tasks
    background_tasks.add_task(generate_reports, db, report_id)

    return {"report_id": report_id}


from fastapi import Response
import csv
from io import StringIO

@app.get("/get_report", response_model=dict)
async def get_report(report_id: str = Query(...), db: Session = Depends(get_db)):
    # Check if the report_id exists in the reports table
    report = db.query(Report).filter(Report.id == report_id).first()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check if the report generation is complete
    if report.status == "Complete":
        # Convert the JSON data to CSV format
        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        
        # Write the header row
        header_row = ["store_id", "uptime_last_hour", "uptime_last_day", "uptime_last_week",
                      "downtime_last_hour", "downtime_last_day", "downtime_last_week"]
        csv_writer.writerow(header_row)
        
        # Write data rows based on the report data
        for item in report.data:
            csv_writer.writerow([item.get("store_id", ""),
                                 item.get("uptime_last_hour", ""),
                                 item.get("uptime_last_day", ""),
                                 item.get("uptime_last_week", ""),
                                 item.get("downtime_last_hour", ""),
                                 item.get("downtime_last_day", ""),
                                 item.get("downtime_last_week", "")])

        # Prepare the response with the CSV data
        csv_data.seek(0)
        headers = {
            "Content-Disposition": f"attachment; filename=report.csv"
        }

        return Response(content=csv_data.getvalue(), media_type="text/csv", headers=headers)
    else:
        # Report generation is still running
        return {"status": "Running"}

