import streamlit as st
import pandas as pd
from PIL import Image

# Path to the updated metadata CSV and images folder
metadata_file = "Updated_GTruth_with_Grading.csv"  # Update the path to your CSV file
images_folder = "Images"  # Folder where images are stored

# Load the updated metadata
metadata = pd.read_csv(metadata_file)

# App title
st.title("Pneumonia Grading and Image Viewer")

# Initialize session state for the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Get the current row
current_index = st.session_state.current_index
row = metadata.iloc[current_index]

# Check if the image has been labeled in the 'Pneumonia_Grading' column
if pd.isna(row['Pneumonia_Grading']) or row['Pneumonia_Grading'] == "No":
    # Image has not been labeled, display the image
    image_path = f"{images_folder}/{row['Id']}.jpeg"  # Assuming 'Id' corresponds to the image filename (with .jpeg extension)
    try:
        st.image(Image.open(image_path), caption=f"Image ID: {row['Id']}", use_column_width=True)
    except FileNotFoundError:
        st.error(f"Image {row['Id']}.jpeg not found in {images_folder}.")
    
    # Show Ground_Truth as pneumonia status
    ground_truth = row['Ground_Truth']
    if ground_truth == 1:
        st.write("### Ground Truth: Pneumonia - Yes")
    else:
        st.write("### Ground Truth: Pneumonia - No")
    
    # Editable fields for metadata (Pneumonia Grading)
    st.write("### Update Pneumonia Grading:")
    grading = st.selectbox(
        "Pneumonia Grading", 
        options=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"],  # Added "No Pneumonia" and "Critical"
        index=["No Pneumonia", "Mild", "Moderate", "Severe", "Critical"].index(row["Pneumonia_Grading"] if pd.notna(row["Pneumonia_Grading"]) else "No Pneumonia")
    )

    # Add a slider for percentage of grade (from 0 to 100)
    percentage_grade = row.get("Percentage of Grade", 0)  # Get the value from CSV or default to 0
    if not isinstance(percentage_grade, (int, float)) or pd.isna(percentage_grade):
        percentage_grade = 0  # Default to 0 if invalid data

    # Slider for selecting percentage
    percentage_grade = st.slider(
        "Percentage of Grade", 
        min_value=0, 
        max_value=100, 
        value=int(percentage_grade),  # Ensure the value is an integer
        step=1
    )

    # Format the percentage grade as a string with '%' sign
    formatted_percentage = f"{percentage_grade}%"

    # Save changes
    if st.button("Save Changes"):
        metadata.at[current_index, "Pneumonia_Grading"] = grading
        metadata.at[current_index, "Percentage of Grade"] = formatted_percentage  # Save formatted percentage grade
        metadata.to_csv(metadata_file, index=False)
        st.success(f"Changes saved! Percentage of Grade: {formatted_percentage}")

else:
    # Image is already labeled, skip displaying anything (do not show the image or grading page)
    st.session_state.current_index += 1  # Skip to the next image if this one is labeled

# Navigation between images
col1, col2 = st.columns(2)
if col1.button("Previous") and current_index > 0:
    st.session_state.current_index -= 1
if col2.button("Next") and current_index < len(metadata) - 1:
    st.session_state.current_index += 1
