
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from .models import StoreActivity, StoreBusinessHours, StoreTimezone, UserReport
import pytz
from sqlalchemy import func

def convert_local_to_utc(local_time, timezone_str):
    """
    Convert a local time to UTC time based on the provided timezone string.

    Args:
        local_time (datetime): The local time to convert.
        timezone_str (str): The timezone string (e.g., 'America/New_York').

    Returns:
        datetime: The corresponding UTC time.
    Raises:
        ValueError: If an invalid timezone string is provided.
    """
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

def calculate_uptime_downtime(activity_data, business_hours_start, business_hours_end):
    """
    Calculate uptime and downtime based on activity data and business hours.

    Args:
        activity_data (list): List of StoreActivity records.
        business_hours_start (datetime): Start of business hours in UTC.
        business_hours_end (datetime): End of business hours in UTC.

    Returns:
        tuple: A tuple containing uptime (in minutes) and downtime (in minutes).
    """
    # Initialize uptime and downtime to zero
    uptime_minutes = 0
    downtime_minutes = 0

    # Iterate through time intervals within business hours
    current_time = business_hours_start
    while current_time < business_hours_end:
        next_time = current_time + timedelta(minutes=15)  # 15-minute intervals

        # Check if there is activity data within the current time interval
        has_activity = any(
            activity.timestamp_utc >= current_time and
            activity.timestamp_utc < next_time and
            activity.status == "active"
            for activity in activity_data
        )

        if has_activity:
            uptime_minutes += 15  # 15 minutes of uptime
        else:
            downtime_minutes += 15  # 15 minutes of downtime

        current_time = next_time

    return uptime_minutes, downtime_minutes

def generate_reports(db, report_id):
    """
    Generate reports for store uptime and downtime.

    Args:
        db (Session): SQLAlchemy session.
        report_id (int): Unique ID for the report.
    """
    try:
        # Create a new UserReport record with the "Running" status
        new_report = UserReport(id=report_id, status="Running", created_at=datetime.utcnow())
        db.add(new_report)
        db.commit()

        # Get all unique store IDs
        store_ids = db.query(StoreActivity.store_id).distinct().all()
        unique_store_ids = set()
        response_data_list = []

        for store_id in store_ids:
            store_id = store_id[0]  # Extract the store_id from the row

            # Get store's timezone
            store_timezone_record = (
                db.query(StoreTimezone.timezone_str)
                .filter(StoreTimezone.store_id == store_id)
                .first()
            )
            
            if store_timezone_record:
                store_timezone = store_timezone_record.timezone_str
            else:
                # Handle the case where no matching record is found or store_timezone is None
                store_timezone = "America/Chicago"  # Default to America/Chicago

            # Calculate business hours in UTC
            business_hours = (
                db.query(StoreBusinessHours)
                .filter(StoreBusinessHours.store_id == store_id)
                .all()
            )
            for business_hour in business_hours:
                start_time_local = business_hour.start_time_local
                end_time_local = business_hour.end_time_local

                # Handle business hours that span across two days
                if start_time_local > end_time_local:
                    end_time_local += timedelta(days=1)

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
                uptime_minutes, downtime_minutes = calculate_uptime_downtime(
                    activity_data, start_time_utc, end_time_utc
                )

                # Create a new UserReport instance and populate its fields
                if store_id not in unique_store_ids:
                    unique_store_ids.add(store_id)
                    report_data = {
                        "store_id": store_id,
                        "uptime_last_hour": uptime_minutes,
                        "uptime_last_day": uptime_minutes / 60,
                        "uptime_last_week": uptime_minutes / 60 / 24 * 7,
                        "downtime_last_hour": downtime_minutes,
                        "downtime_last_day": downtime_minutes / 60,
                        "downtime_last_week": downtime_minutes / 60 / 24 * 7,
                    }
                    print(report_data)
                    response_data_list.append(report_data)

        # Update the report status to "Complete" once the report generation is finished
        existing_report = (
            db.query(UserReport).filter(UserReport.id == report_id).first()
        )

        if existing_report:
            # Update existing report status with complete and also add data
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


