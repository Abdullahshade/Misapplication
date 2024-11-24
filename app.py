import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3
import os

# SQLite Database setup
def create_connection():
    conn = sqlite3.connect('pneumonia_grading.db')  # Connect to SQLite database (or create it)
    return conn

def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id TEXT,
            pneumonia_grading TEXT,
            percentage_grade INTEGER,
            ground_truth INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM grades')
    data = c.fetchall()
    conn.close()
    return data

def update_data(image_id, grading, percentage_grade):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE grades SET pneumonia_grading = ?, percentage_grade = ?
        WHERE image_id = ?
    ''', (grading, percentage_grade, image_id))
    conn.commit()
    conn.close()

# Create table if it doesn't exist
create_table()

# Path to the images folder
images_folder = "Images"  # Folder where images are stored

# Load the updated metadata from SQLite
data = get_data()

# App title
st.title("Pneumonia Grading and Image Viewer")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Get the current row from the database
current_index = st.session_state.current_index
if current_index < len(data):
    row = data[current_index]
    image_id = row[1]  # Assuming image_id is in the second column
    grading = row[2]  # Grading in the third column
    percentage_grade = row[3]  # Percentage grade in the fourth column
    ground_truth = row[4]  # Ground truth in the fifth column

    # Display the image (load it from the images folder)
    image_path = os.path.join(images_folder, f"{image_id}.jpeg")  # Assuming 'image_id' corresponds to the image filename (with .jpeg extension)
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"Image ID: {image_id}", use_column_width=True)
    else:
        st.error(f"Image {image_id}.jpeg not found in {images_folder}.")

    # Show Ground_Truth as pneumonia status
    if ground_truth == 1:
        st.write("### Ground Truth: Pneumonia - Yes")
    else:
        st.write("### Ground Truth: Pneumonia - No")
    
    # Editable fields for metadata (Pneumonia Grading)
    st.write("### Update Pneumonia Grading:")
    grading = st.selectbox(
        "Pneumonia Grading", 
        options=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"],  # Added "No Pneumonia" and "Critical"
        index=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"].index(grading if pd.notna(grading) else "No Pneumonia")
    )

    # Convert the percentage_grade to an integer (remove the '%' symbol if it exists)
    if isinstance(percentage_grade, str) and '%' in percentage_grade:
        percentage_grade = int(percentage_grade.replace('%', ''))
    else:
        percentage_grade = int(percentage_grade)

    # Add a slider for percentage of grade (from 0 to 100)
    percentage_grade = st.slider(
        "Percentage of Grade", 
        min_value=0, 
        max_value=100, 
        value=percentage_grade,  # Ensure the value is an integer
        step=1
    )

    # Format the percentage grade as a string with '%' sign
    formatted_percentage = f"{percentage_grade}%"

    # Save changes to database
    if st.button("Save Changes"):
        update_data(image_id, grading, formatted_percentage)
        st.success(f"Changes saved! Image ID: {image_id}, Grading: {grading}, Percentage of Grade: {formatted_percentage}")

else:
    st.write("No more images available for grading.")

# Navigation between images
col1, col2 = st.columns(2)
if col1.button("Previous") and current_index > 0:
    st.session_state.current_index -= 1
if col2.button("Next") and current_index < len(data) - 1:
    st.session_state.current_index += 1
