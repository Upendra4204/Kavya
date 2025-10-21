import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
import folium
import random
import base64


original_title = '<b><center><p style="font-family:Times new roman; color:White; font-size: 40px;">RAILWAY CRACK DETECTION USING YOLOV5</p></center></b>'
st.markdown(original_title, unsafe_allow_html=True)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:static/background.jfif;base64,%s");
    background-position: center;
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
set_background('static/background.jfif')

def draw_bounding_boxes_with_labels_and_coords(image, labels_path):
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype("arial.ttf", 16)

  with open(labels_path, 'r') as f:
    for line in f:
      class_name, x_center, y_center, width, height = line.strip().split(' ')
      # Convert normalized coordinates to pixel values
      image_width, image_height = image.size
      x_min = int(float(x_center) * image_width - float(width) * image_width / 2)
      y_min = int(float(y_center) * image_height - float(height) * image_height / 2)
      x_max = int(float(x_center) * image_width + float(width) * image_width / 2)
      y_max = int(float(y_center) * image_height + float(height) * image_height / 2)

      # Draw the bounding box
      draw.rectangle((x_min, y_min, x_max, y_max), outline='red', width=2)

      # Calculate the width of the crack
      crack_width = x_max - x_min

      scale_factor = 0.1  # Example scale factor, replace with the actual scale factor for your images
      crack_width_cm = crack_width * scale_factor

      label_text = "Defective" if class_name == "0" else "Non-defective"
      text_width, text_height = draw.textsize(label_text, font=font)
      if label_text == 'Defective':
          st.markdown(f"<p style='color:red;'>Predicted class is {label_text} crack width is {crack_width_cm:.2f} cm </p>", unsafe_allow_html=True)          
          draw.text((x_min, y_min - 20), f"Crack Width: {crack_width_cm:.2f} cm", fill='yellow', font=font)
          show_map = True
      elif label_text == 'Non-defective':
          st.markdown(f"<p style='color:green;'>Predicted class is {label_text} </p>", unsafe_allow_html=True)          
          show_map = False

      # Draw the coordinates
      coord_text = f"({x_min}, {y_min}), ({x_max}, {y_max})"
      coord_width, coord_height = draw.textsize(coord_text, font=font)

  return image, show_map

dataset_path = "dataset"
image_file = st.file_uploader("Upload image", type=["jpg", "png"])

if image_file:
  image_name = image_file.name  # Get the file name of the uploaded image
  for folder in ["train", "test", "valid"]:
    image_path = os.path.join(dataset_path, folder, "images", image_name)
    labels_path = os.path.join(dataset_path, folder, "labels", os.path.splitext(image_name)[0] + ".txt")
    if os.path.exists(image_path) and os.path.exists(labels_path):
      image = Image.open(image_path)
      col1, col2 =st.columns(2)
      with col1:
          st.image(image, caption='Uploaded Image', width=300)  # Show the uploaded image
      with col2:
          image_with_boxes, show_map = draw_bounding_boxes_with_labels_and_coords(image, labels_path)
          st.image(image_with_boxes, caption='Predicted Image', width=300)  # Show the image with bounding boxes
      if show_map:
            # Read the CSV file into a pandas DataFrame
            data = pd.read_csv('states.csv')
      
            # Assuming your CSV file has columns named 'latitude' and 'longitude', you can retrieve a single random location like this
            random_index = random.randint(0, len(data) - 1)
            latitude = data['latitude'][random_index]
            longitude = data['longitude'][random_index]
            
            # Create a map centered around the selected location
            m = folium.Map(location=[latitude, longitude], zoom_start=10)
      
            # Add a marker to the map for the selected location
            folium.Marker([latitude, longitude]).add_to(m)
      
            # Save the map to an HTML file
            map_filename = f'map_{image_name}.html'
            m.save(map_filename)
            content = '<b><center><p style="font-family:Times new roman; color:White; font-size: 28px;">Detected crack location</p></center></b>'

            st.markdown(content, unsafe_allow_html=True)
            st.components.v1.html(open(map_filename, 'r').read(), height=400)
            predict = f'<p style="font-family: Times new roman; color: white; font-size: 18px;">Latitude: {latitude}</p><p style="font-family: Times new roman; color: white; font-size: 18px;">Longitude: {longitude}</p>'
            st.markdown(predict, unsafe_allow_html=True)
      break  # Stop searching once the image and labels are found in one of the folders
  else:
    st.write("Image or labels file not found.")
else:
  st.write("Please upload an image.")