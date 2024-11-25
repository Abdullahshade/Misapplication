import sqlite3
import os
import tempfile
from PIL import Image
import streamlit as st

# Database setup and connection creation
def create_connection():
    # Use tempfile to create a temporary directory for database storage
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'pneumonia_grading.db')
    
    # Check if the database file exists; if not, create it and initialize the table
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Create grades table if it doesn't already exist
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
    else:
        conn = sqlite3.connect(db_path)
    
    return conn

# Fetch data from the database
def get_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM grades')
    data = c.fetchall()
    conn.close()
    return data

# Insert sample data for testing (only if necessary)
def insert_sample_data():
    conn = create_connection()
    c = conn.cursor()
    sample_data = [
        ('image_001', 'Mild', '70%', 1),
        ('image_002', 'Moderate', '50%', 0),
    ]
    c.executemany('INSERT INTO grades (image_id, pneumonia_grading, percentage_grade, ground_truth) VALUES (?, ?, ?, ?)', sample_data)
    conn.commit()
    conn.close()

# Uncomment to insert sample data for testing
# insert_sample_data()

# Streamlit app UI and logic
st.title("Pneumonia Grading and Image Viewer")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Load data from the database
data = get_data()

# Check if there is data in the database
if len(data) > 0:
    current_index = st.session_state.current_index
    if current_index < len(data):
        row = data[current_index]
        image_id = row[1]
        grading = row[2]
        percentage_grade = row[3]
        ground_truth = row[4]

        # Display the image
        image_path = f"Images/{image_id}.jpeg"
        try:
            st.image(Image.open(image_path), caption=f"Image ID: {image_id}", use_column_width=True)
        except FileNotFoundError:
            st.error(f"Image {image_id}.jpeg not found.")

        # Update grading fields
        grading = st.selectbox("Pneumonia Grading", ["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"], index=0)
        percentage_grade = st.slider("Percentage of Grade", 0, 100, 70)

        # Save changes button
        if st.button("Save Changes"):
            # Update the database with the new values
            conn = create_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE grades SET pneumonia_grading = ?, percentage_grade = ?
                WHERE image_id = ?
            ''', (grading, f"{percentage_grade}%", image_id))
            conn.commit()
            conn.close()
            st.success("Changes saved!")
else:
    st.write("No data available.")
