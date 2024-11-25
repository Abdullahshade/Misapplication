import os
import sqlite3
import streamlit as st
from PIL import Image
from pathlib import Path

# Ensure the correct path for the database and images folder
current_dir = Path(__file__).parent

# For the database path, ensure it points to the file in the current directory
db_path = os.path.join(current_dir, 'pneumonia_grading.db')
images_folder = os.path.join(current_dir, 'Images')

# Check if the database exists
if not os.path.exists(db_path):
    st.error("Database file is missing. Please upload it.")
else:
    st.success("Database file found!")

# Function to load the images from the Images folder
def load_images(image_dir):
    # Check if the Images folder exists
    if os.path.exists(image_dir):
        images = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith(('jpg', 'jpeg', 'png'))]
        return images
    else:
        st.warning("Images folder is missing.")
        return []

# Display images
def display_images(images):
    if images:
        for img_path in images:
            image = Image.open(img_path)
            st.image(image, caption=os.path.basename(img_path), use_column_width=True)
    else:
        st.warning("No images to display.")

# Streamlit UI
st.title("Pneumonia Grading and Image Viewer")

# Upload Database File (optional if you want manual upload)
db_file = st.file_uploader("Upload Database File (if missing)", type=["db", "sqlite"])
if db_file is not None:
    with open(db_path, "wb") as f:
        f.write(db_file.read())
    st.success(f"Database file {db_file.name} uploaded successfully.")

# Upload Images (optional if you want manual upload)
uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        image_path = os.path.join(images_folder, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded {len(uploaded_files)} images.")

# Load and Display Images
images = load_images(images_folder)
display_images(images)

# Database Connection and Grading Logic
def connect_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None

conn = connect_db(db_path)
if conn:
    cursor = conn.cursor()

    # Example query: Grading and displaying data from database (Modify this with your actual query logic)
    cursor.execute("SELECT * FROM pneumonia_grading")
    rows = cursor.fetchall()

    if rows:
        st.write("Grading Data:")
        for row in rows:
            st.write(row)
    else:
        st.warning("No grading data available in the database.")
    conn.close()
else:
    st.error("Unable to connect to the database.")
