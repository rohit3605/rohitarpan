import streamlit as st
import mysql.connector
import serial
import time as tt
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2
import tempfile
from tensorflow.keras.preprocessing import image
import pyttsx3
from twilio.rest import Client
import sqlite3



################################################################### Twilo account set #######################################################
account_sid = 'ACe115119f2129f817eb767997e304ffc0'
auth_token = '1cf92e18c8b977d2f71581691e542181'
twilio_number = '+13022484056'
################################################################### Twilo account set #######################################################

##################################################################### SMS source setup #######################################################
def SMSSource() :
    client = Client(account_sid, auth_token)
    return client
##################################################################### SMS source setup #######################################################

#################################################################### For set sms send number's #####################################################
recipient_number1 = '+917363064067'

recipient_number2 = '+917811050018'

recipient_number3 = '+918670516762'

recipient_number4 = '+917047283086'

client = Client(account_sid, auth_token)
#################################################################### For set sms send number's #####################################################

################################################################### SMS alet message set ######################################################
def SMSAlet(message, client, recipient_number1, recipient_number2, recipient_number3, recipient_number4)  :  
    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number1
    )

    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number2
    )

    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number3
    )

    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number4
    )
    print(message.sid)
################################################################### SMS alet message set ######################################################

############################################################# For title ######################################
st.title("🔥 FIRE DETECTION SYSTEM 🔥")
st.sidebar.header("Options")

############################################################## For title #####################################



############################################################## Database connection ########################################################
conn = sqlite3.connect("temp_db_converted.sqlite")
cursor = conn.cursor()
print("SQLite Database Connected Successfully!")
############################################################## Database connection ########################################################

############################ Database name set ###############################
DB_NAME = "temp_db_converted.sqlite"
def connect_db():
    return sqlite3.connect(DB_NAME)
############################## Database name set #############################

######################### For table create2 ##################################
def create_table2():
    """Create table if it doesn't exist"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            smoke REAL NOT NULL,
            temperature REAL NOT NULL,
            fire REAL NOT NULL  -- Added 'fire' column
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table 'sensor_data' created successfully!")

    except Exception as e:
        print(f"❌ Error creating table: {e}")



######################### For table create2 ##################################

######################### For table create1 ##################################
def create_table1():
    """Create the smoke_data table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS smoke_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smoke INTEGER,
                temperature REAL
            )
            """)
            conn.commit()
            print("Table 'smoke_data' verified!")
    except Exception as e:
        print(f"Error creating table: {e}")
########################## For table create1 ######################################

################################################ For text to speach  ##############################################
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # Speed of speech
    engine.setProperty("volume", 1.0)  # Volume level (0.0 to 1.0)
    
    # Speak the text
    engine.say(text)
    engine.runAndWait()
################################################ For text to speach  ##############################################

########################################################### Insert data to the database ################################################## 
def insert_sensor_dataTemp(smoke, temperature):
    """Insert smoke and temperature values into smoke_data."""
    create_table1()  # Ensure table exists before inserting
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO smoke_data (smoke, temperature) 
            VALUES (?, ?);
            """, (smoke, temperature))
            conn.commit()
            print(f"Data inserted into smoke_data: Smoke={smoke}, Temperature={temperature}")
    except Exception as e:
        print(f"Error inserting data into smoke_data: {e}")
########################################################### Insert data to the database ################################################## 

############################################################## delete_oldest_record ###################################################  
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
############################################################## delete_oldest_record ###################################################


############# Insert sensor data   #######################################################

def insert_sensor_data2(smoke, temperature, fire):
    create_table2()  # Ensure table exists before inserting data
    try:
        conn = connect_db()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO sensor_data (smoke, temperature, fire) 
        VALUES (?, ?, ?);
        """
        values = (smoke, temperature, fire)
        
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Data inserted: Smoke={smoke}, Temperature={temperature}, Fire={fire}")

    except Exception as e:
        print(f"❌ Error inserting data: {e}")


   

############# Insert sensor data   #####################################################





########################################################### Connect to Arduino via Serial ################################################
def connectSerial():
    try:
        ser = serial.Serial('COM5', 9600, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f'Connection error: {e}')
        return None
########################################################### Connect to Arduino via Serial ################################################

########################################################### Load Fire Detection Model  ############################################### 
@st.cache_resource
def load_model():
    try:
        return tf.keras.models.load_model("model.h5")  
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None
############################################################### Load Fire Detection Model ################################################

################################################################# Fire Prediction using camera ######################################################
def predict_image(img_path):
    try:
        if model is None:
            return None
        target_size = model.input_shape[1:]
        img = image.load_img(img_path, target_size=target_size)
        x = image.img_to_array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        val = model.predict(x)
        return float(val[0][0])
    except Exception as e:
        st.error(f"⚠️ Prediction error: {e}")
        return None
################################################################# Fire Prediction using camera ######################################################

############################ Get sensor data #################################### 
def get_sensor_data1():
    """Fetch sensor data from SQLite database."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM smoke_data ORDER BY id DESC")  # Fetching from the correct table
            data = cursor.fetchall()
            print("Fetched data:", data)
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return [] 
############################ Get sensor data ####################################


############################ Get sensor data #################################### 
def get_sensor_data2():
    """Fetch sensor data from SQLite database"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return []
############################ Get sensor data ####################################

################################# For display data1 ############################### 
def display_data1():
    """Display sensor data in Streamlit."""
    data = get_sensor_data1()

    if data:
        num_columns = len(data[0]) if data else 0  
        columns = ["ID", "Smoke", "Temperature"][:num_columns]  # Adjusted column names

        df = pd.DataFrame(data, columns=columns)  
        st.dataframe(df)  
    else:
        st.warning("No data available.")
################################# For display data1 ###############################

################################# For display data2 ############################### 
def display_data2():
    """Display sensor data in Streamlit"""
    data = get_sensor_data2()

    if data:
        num_columns = len(data[0]) 
        columns = ["ID", "Time", "Smoke", "Temperature", "Fire"][:num_columns]  

        df = pd.DataFrame(data, columns=columns)  
        st.dataframe(df)  
    else:
        st.warning("No data available.")
################################# For display data2 ############################### 


######################################################### Detection camera, smoke && temp ################################################
def start_camera():
    ser = connectSerial()
    if not ser:
        st.error("❌ Failed to connect to Arduino.")
        return
    
    #insert_sensor_data2(500, 500 , 1.0)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Camera not accessible.")
        return

    frame_placeholder = st.empty()
    prediction_placeholder = st.empty()


    temperatureC = 0.0
    analogTemp = 0.0
    count = 0
    while cap.isOpened():
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                temperatureC, analogTemp = map(float, line.split(','))
                print(f"🌡 Temperature: {temperatureC}°C, 💨 Smoke: {analogTemp}ppm")
            except ValueError:
                print("⚠️ Invalid sensor data received.")
        
      
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Failed to capture frame from camera.")
            break

        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")

        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            img_path = temp_file.name
            cv2.imwrite(img_path, frame_rgb)

        
        CameraValue = predict_image(img_path)
        #CameraValue = 0.4
        #analogTemp = 300
        #temperatureC = 15
        if CameraValue is not None:
            if CameraValue > 0.3 and analogTemp >= 250 and temperatureC >= 13:  
                count += 1
                print(f'Fire detected   Count: {count} under the 3 count')
                prediction_placeholder.subheader(f"🔥 Fire Detected! ")   #{str(CameraValue)} 
                if count >= 3:
                    insert_sensor_data2(analogTemp, temperatureC , 1.0)
                    for i in range(6) :
                        text_to_speech('Fire')
                        text_to_speech('Fire detected on the 1st floor! Please evacuate immediately using the nearest exit. 🚪⚠️')
                        if(i == 6) :
                            #message = '🔥 Fire detected on the 1st floor! Please evacuate immediately using the nearest exit. 🚪⚠️'
                            SMSAlet(message, SMSSource(), recipient_number1, recipient_number2,  recipient_number3, recipient_number4) 
                        else :
                            print(i) 
                    return  
            else:
                prediction_placeholder.subheader(f"✅ No Fire Detected ")   #{str(CameraValue)}
                insert_sensor_dataTemp(analogTemp, temperatureC)
                delete_oldest_record()
                
                

        tt.sleep(1)  

    cap.release()
    cv2.destroyAllWindows()
    
######################################################### Detection camera, smoke && temp ################################################

if __name__ == "__main__":
    model = load_model()
    if st.sidebar.button("Start Live Camera"):
        start_camera()
        
if st.sidebar.button("Show Sensor Data"):
    st.markdown("# Sensor display data 🌡💨")
    display_data1()
    
if st.sidebar.button("Show Fire data"):
    st.markdown("# FirePredict display data 🌡💨 🔥")
    display_data2()
