# Create database locally for linnux
## Init Postgresql

1. Login postgres\
   `sudo -i -u postgres`\
   ~$ `psql`

2. Create User and Password\
   `CREATE USER user_name with PASSWORD 'password';`

3. Create Database\
   ~$ `CREATE DATABASE db_name;`

4. Grant access to user
   ~$ `GRANT ALL ON DATABASE  db_name TO user_name`;
# Store Monitoring API

## Overview

The Store Monitoring API is a sophisticated backend system designed to assist restaurant owners in monitoring the online status of their establishments. It generates comprehensive reports based on store activity data, business hours, and time zones. This README provides an extensive overview of the project, its core components, and precise instructions on how to run and utilize the APIs.

## Problem Statement

Loop, a prominent restaurant management company in the US, manages a multitude of restaurants and needs to ensure the continuous online presence of their stores during their designated business hours. Occasionally, stores might go offline for unforeseen reasons, and restaurant owners require a detailed historical report of such occurrences.

## Data Sources

This project relies on three primary data sources:

1. **Hourly Polls of Store Activity Data (CSV Format)**:
   - Access the data in CSV format [here](https://drive.google.com/file/d/1UIx1hVJ7qt_6oQoGZgb8B3P2vd1FD025/view?usp=sharing)

2. **Business Hours for All Stores (CSV Format)**:
   - Access the data in CSV format [here](https://drive.google.com/file/d/1va1X3ydSh-0Rt1hsy2QSnHRA4w57PcXg/view?usp=sharing)

3. **Timezones for the Stores (CSV Format)**:
   - Access the data in CSV format [here](https://drive.google.com/file/d/101P9quxHoMZMZCVWQ5o-shonk2lgK1-o/view?usp=sharing)

## System Requirements

To effectively deploy the Store Monitoring API, the following system requirements must be met:

- **Database Storage**: The data should be stored in a relevant database.
- **API Availability**: APIs should be available to trigger report generation and retrieve reports.
- **Report Generation**: Report generation should consider business hours and extrapolate uptime and downtime accurately.
- **Data Updates**: The system should handle ongoing data updates seamlessly.

## API Requirements

The system offers two primary APIs:

1. **`/trigger_report`**: This API endpoint triggers report generation and returns a unique report ID.
2. **`/get_report`**: This API endpoint retrieves the status of the report or the CSV report data.

### Running the Application

Follow these steps to run the Store Monitoring API:

1. Clone the repository:
   ```bash
   git clone https://github.com/inishantxchandel/store_monitoring_system.git
   ```

2. Navigate to the project directory:
   ```bash
   cd store_monitoring_system
   ```

3. Create a virtual environment (Linux):
   ```bash
   python3 -m venv venv
   ```

4. Activate the virtual environment (Linux):
   ```bash
   source venv/bin/activate
   ```

5. Install project dependencies using Poetry (ensure Poetry is installed on your system):
   ```bash
   poetry install
   ```

6. Start the application server:
   ```bash
   poetry run uvicorn monitoring_system.main:app --reload
   ```
7. Create a `data` folder within the `monitoring_system` directory. Inside this folder, store the CSV files with the following names:

   - Store Activity Data: `store_activity.csv`
   - Business Hours Data: `store_business_hours.csv`
   - Timezone Data: `store_timezone.csv`

   Your directory structure should look like this:

   ```
   store_monitoring_system/
   ├── monitoring_system/
   │   ├── data/
   │   │   ├── store_activity.csv
   │   │   ├── store_business_hours.csv
   │   │   ├── store_timezone.csv
   │   ├── ...
   ├── ...
   ```

   Make sure to place the respective CSV files in this `data` folder before proceeding with the data loading step.


8. Load CSV data into the database by running the following command:
   ```bash
   python -m monitoring_system.load_data
   ```

   Note: The time taken for this step depends on the size of your CSV file.

9. With the database ready, start the application server again:
   ```bash
   poetry run uvicorn monitoring_system.main:app --reload
   ```

10. Open your browser and go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

11. Use the `/trigger_report` endpoint to initiate report generation. It will provide you with a unique report ID.

12. To check the status of the report or download the CSV report data, use the `/get_report` endpoint and provide the report ID in the parameters.

## Author

[Nishant Chandel]
