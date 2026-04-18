from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from google import genai
from google.genai import types
import os
from PIL import Image

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, image_parts, prompt):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            input_text,
            types.Part.from_bytes(data=image_parts["data"], mime_type=image_parts["mime_type"]),
            prompt
        ]
    )
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = {
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    

# Initialize our Streamlit app
st.set_page_config(page_title="MultiLanguage Invoice Extractor")
st.header("MultiLanguage Invoice Extractor")
st.text_input("Input Prompt: ", key="input")
upload_file = st.file_uploader("Choose an image of the invoice...", type=["jpg", "pdf", "jpeg", "png"])

image = ""
if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
submit = st.button("Submit")

input_prompt = """
You are an expert in understanding invoices. We will upload an image as an invoice and you
will have to answer any questions based on the uploaded invoice image.
"""

# If submit button is clicked
if submit:
    image_data = input_image_details(upload_file)
    response = get_gemini_response(input_prompt, image_data, st.session_state.input)
    st.subheader("The Response is")
    st.write(response)
