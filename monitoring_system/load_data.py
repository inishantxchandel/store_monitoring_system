import csv
from monitoring_system import database, models
import concurrent.futures

# Define a function to load data from a CSV file into a specified model
def load_csv_data(csv_filename, model_class):
    try:
        db = database.SessionLocal()  # Create a new session for each thread
        with open(csv_filename, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data_objects = []
            for row in csv_reader:
                # Create objects but don't add them to the session yet
                data_object = model_class(**row)
                data_objects.append(data_object)
            # Add all objects to the session in a single commit
            db.bulk_save_objects(data_objects)
            print(f"Data from {csv_filename} loaded successfully")
            db.commit()
        db.close()  # Close the session for this thread
    except Exception as e:
        # Handle any exceptions and rollback changes if necessary
        db.rollback()
        print(f"Error loading data from {csv_filename}: {str(e)}")

if __name__ == "__main__":
    try:
        # Define the CSV files and corresponding model classes
        csv_files = [
            ('monitoring_system/data/store_activity.csv', models.StoreActivity),
            ('monitoring_system/data/store_business_hours.csv', models.StoreBusinessHours),
            ('monitoring_system/data/store_timezone.csv', models.StoreTimezone)
        ]

        # Use concurrent.futures.ThreadPoolExecutor to load data concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(load_csv_data, csv_file, model_class): (csv_file, model_class) for csv_file, model_class in csv_files}
            for future in concurrent.futures.as_completed(futures):
                csv_file, model_class = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error loading data from {csv_file}: {str(e)}")

        print("All data loaded successfully")
    except Exception as e:
        # Handle any exceptions and rollback changes if necessary
        print(f"Error loading data: {str(e)}")
