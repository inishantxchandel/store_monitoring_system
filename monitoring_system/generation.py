from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from .models import StoreActivity, StoreBusinessHours, StoreTimezone, UserReport
import pytz
from sqlalchemy import func


def convert_local_to_utc(local_time, timezone_str):
    try:
        if timezone_str is None:
            # If timezone_str is None, assume UTC as the default time zone
            return local_time.astimezone(pytz.UTC)

        # Create a time zone object for the given timezone_str
        local_timezone = pytz.timezone(timezone_str)

        # Localize the input local_time to the specified time zone
        localized_time = local_timezone.localize(local_time, is_dst=None)

        # Convert the localized time to UTC
        utc_time = localized_time.astimezone(pytz.UTC)

        return utc_time
    except (pytz.UnknownTimeZoneError, AttributeError):
        # Handle the case where an invalid time zone is provided or local_time is None
        raise ValueError(f"Invalid time zone: {timezone_str}")


def calculate_uptime(activity_data, business_hours_start, business_hours_end):
    # Calculate uptime in minutes within the specified business hours
    uptime_minutes = 0
    last_activity_time = None

    for activity in activity_data:
        if activity.timestamp_utc < business_hours_start:
            continue
        elif activity.timestamp_utc > business_hours_end:
            break

        if activity.status == "active":
            if last_activity_time is None:
                last_activity_time = activity.timestamp_utc
        else:
            if last_activity_time is not None:
                uptime_minutes += (
                    activity.timestamp_utc - last_activity_time
                ).total_seconds() / 60
                last_activity_time = None

    # Handle the case where the last activity was active
    if last_activity_time is not None:
        current_utc_time = datetime.utcnow()
        if current_utc_time <= business_hours_end:
            uptime_minutes += (
                current_utc_time - last_activity_time
            ).total_seconds() / 60

    return uptime_minutes


def generate_reports(db: Session, report_id: str):
    try:
        # Create a new UserReport record with the "Running" status
        new_report = UserReport(id=report_id, status="Running", created_at=datetime.utcnow())
        db.add(new_report)
        db.commit()

        # Get all unique store IDs
        store_ids = db.query(StoreActivity.store_id).distinct().all()
        unique_store_ids = set()  # To store unique store IDs
        response_data_list = []

        for store_id in store_ids:
            store_id = store_id[0]  # Extract the store_id from the row

            # Get store's timezone
            store_timezone = (
                db.query(StoreTimezone.timezone_str)
                .filter(StoreTimezone.store_id == store_id)
                .scalar()
            )
            print(store_timezone)
            if store_timezone is None:
                # Handle the case where store_timezone is None (you can skip the store or set a default timezone behavior as needed)
                continue

            # Calculate business hours in UTC
            business_hours = (
                db.query(StoreBusinessHours)
                .filter(StoreBusinessHours.store_id == store_id)
                .all()
            )
            for business_hour in business_hours:
                start_time_local = business_hour.start_time_local
                end_time_local = business_hour.end_time_local

                # Convert local time to UTC based on the store's timezone
                start_datetime_local = datetime.combine(
                    datetime.today(), start_time_local
                )
                end_datetime_local = datetime.combine(datetime.today(), end_time_local)

                start_time_utc = convert_local_to_utc(
                    start_datetime_local, store_timezone
                )
                end_time_utc = convert_local_to_utc(end_datetime_local, store_timezone)

                # Query activity data within business hours
                activity_data = (
                    db.query(StoreActivity)
                    .filter(
                        StoreActivity.store_id == store_id,
                        StoreActivity.timestamp_utc >= start_time_utc,
                        StoreActivity.timestamp_utc <= end_time_utc,
                    )
                    .order_by(StoreActivity.timestamp_utc)
                    .all()
                )

                # Calculate uptime and downtime based on activity_data
                uptime_last_hour = calculate_uptime(
                    activity_data, end_time_utc - timedelta(hours=1), end_time_utc
                )
                uptime_last_day = calculate_uptime(
                    activity_data, end_time_utc - timedelta(days=1), end_time_utc
                )
                uptime_last_week = calculate_uptime(
                    activity_data, end_time_utc - timedelta(weeks=1), end_time_utc
                )

                downtime_last_hour = (
                    end_time_utc - start_time_utc
                ).total_seconds() / 60 - uptime_last_hour
                downtime_last_day = (
                    end_time_utc - start_time_utc
                ).total_seconds() / 60 - uptime_last_day
                downtime_last_week = (
                    end_time_utc - start_time_utc
                ).total_seconds() / 60 - uptime_last_week

                # Create a new UserReport instance and populate its fields
                if store_id not in unique_store_ids:
                    unique_store_ids.add(store_id)
                    report_data: dict = {
                        "store_id": store_id,
                        "uptime_last_hour": uptime_last_hour,
                        "uptime_last_day": uptime_last_day,
                        "uptime_last_week": uptime_last_week,
                        "downtime_last_hour": downtime_last_hour,
                        "downtime_last_day": downtime_last_day,
                        "downtime_last_week": downtime_last_week,
                    }
                    print(report_data)

                    response_data_list.append(report_data)

                # Add the report to the database session for persistence

        # Update the report status to "Complete" once the report generation is finished
        existing_report = (
            db.query(UserReport).filter(UserReport.id == report_id).first()
        )

        if existing_report:
            #update existing report status with complete and also add data
            existing_report.status = "Complete"
            existing_report.data = response_data_list
            existing_report.completed_at = datetime.utcnow()
            db.commit()
        return
    except Exception as e:
        # Handle exceptions and update the report status accordingly
        existing_report = (
            db.query(UserReport).filter(UserReport.id == report_id).first()
        )
        if existing_report:
            existing_report.status = "Failed"
            db.commit()
        return
