import sqlite3
import streamlit as st
import pandas as pd

# Database name
DB_NAME = "temp_db_converted.sqlite"

# Function to connect to the database
def connect_db():
    return sqlite3.connect(DB_NAME)

# Function to create the table
def create_table():
    """Create the smoke_data table if it doesn't exist."""
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS smoke_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smoke INTEGER,
                temperature REAL
            )
            """)
            conn.commit()
            print("✅ Table 'smoke_data' verified!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

# Function to insert sensor data
def insert_sensor_data(smoke, temperature):
    """Insert new smoke and temperature data into the database."""
    create_table()  # Ensure table exists before inserting
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO smoke_data (smoke, temperature) 
            VALUES (?, ?)
            """, (smoke, temperature))
            conn.commit()
            print(f"✅ Data inserted: Smoke={smoke}, Temperature={temperature}")
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        
# Function to delete the oldest record
def delete_oldest_record():
    """Delete the oldest record from the smoke_data table to keep data manageable."""
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            delete_query = """
            DELETE FROM smoke_data 
            WHERE id = (SELECT id FROM smoke_data ORDER BY id ASC LIMIT 1)
            """
            cursor.execute(delete_query)
            conn.commit()
            print("🗑️ Oldest record deleted.")
    except Exception as e:
        print(f"❌ Error deleting data: {e}")


# Function to fetch sensor data (only ID, Smoke, and Temperature)
def get_sensor_data():
    """Fetch sensor data (ID, Smoke, Temperature) from SQLite database."""
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, smoke, temperature FROM smoke_data ORDER BY id DESC")
            data = cursor.fetchall()
        
        return data  # Returns only 3 columns: ID, Smoke, Temperature

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return []

# Streamlit UI
def main():
    st.title("🔥 Smoke & Temperature Sensor Data")

    create_table()  # Ensure table exists

    # Insert a test record (Optional: Remove this in production)
    insert_sensor_data(0, 0)
    for i in range(5) :
        insert_sensor_data(0, 0)

    # Fetch data from the database
    data = get_sensor_data()
    
    if data:
        try:
            df = pd.DataFrame(data, columns=["ID", "Smoke Level", "Temperature"])
            st.dataframe(df)
        except ValueError as e:
            st.error(f"⚠️ Data format issue: {e}")
    else:
        st.warning("⚠️ No data found in the database.")

if __name__ == "__main__":
    main()
