# MultiLanguage Invoice Extractor - Code Walkthrough

This document outlines the inner workings of your Streamlit application (`app.py`), the reasoning behind each component, and the steps taken to tie it all together into a functioning AI frontend.

## 1. Setup and Environment Configuration
```python
from dotenv import load_dotenv
load_dotenv()
```
* **Why**: To keep sensitive configuration like your `GOOGLE_API_KEY` safe, it is stored in a `.env` file instead of directly in the code.
* **How**: The `python-dotenv` package reads the `.env` file and loads your secret keys into environment variables, which can then be safely accessed by `os.getenv()`.

## 2. Initializing the Google GenAI Client
```python
import streamlit as st
from google import genai
from google.genai import types
import os
from PIL import Image

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
```
* **Why**: To gain programmatic access to Google's powerful Gemini models.
* **How**: We import the new, up-to-date `google.genai` SDK. This replaces the deprecated `google-generativeai`. By initializing `genai.Client`, we authenticate using the previously loaded API key to send and receive requests.

## 3. Formatting the Image for Gemini
```python
def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = {
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
```
* **Why**: The Google GenAI library requires image data to be provided in a specific structure: a dictionary specifying the mime type (e.g. `image/jpeg` or `application/pdf`) and raw bytes.
* **How**: Streamlit's `uploaded_file` object provides a method `.getvalue()` which extracts the required raw byte data. This is formatted neatly and returned.

## 4. Querying the Gemini Model
```python
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
```
* **Why**: This is the "brain" function of your app, responsible for asking the AI to interpret your invoice.
* **How**: We use the `generate_content` method on the cutting-edge `gemini-2.5-flash` model. We pass it a consolidated list of inputs (`contents`):
  - The specific question the user asks (`input_text`).
  - The parsed image payload, converted using `types.Part.from_bytes()`.
  - Your system behavior prompt (`prompt`), which instructs the model to act as an expert invoice reader.

## 5. Building the Web Frontend Interface
```python
st.set_page_config(page_title="MultiLanguage Invoice Extractor")
st.header("MultiLanguage Invoice Extractor")
st.text_input("Input Prompt: ", key="input")
upload_file = st.file_uploader("Choose an image of the invoice...", type=["jpg", "pdf", "jpeg", "png"])
```
* **Why**: A user-friendly web interface is needed so non-technical users can interact with the AI without utilizing the terminal.
* **How**: We leverage **Streamlit**, which converts Python scripts directly into interactive web applications. 
  - `st.text_input` captures the user's question.
  - `st.file_uploader` provides a button to drag-and-drop or select the invoice file.

## 6. Displaying the Uploaded Invoice
```python
image = ""
if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
submit = st.button("Submit")
```
* **Why**: Providing visual feedback verifies for the user that their intended file was correctly uploaded.
* **How**: The Python Imaging Library (`PIL.Image`) opens the file bits into an image view. Streamlit's `st.image` renders it seamlessly into the browser. *(Note: I went ahead and changed the deprecated `use_column_width` setting to the new `use_container_width` setting so you don't receive terminal warnings!)*

## 7. Connecting the UI to the AI (Execution Context)
```python
input_prompt = """
You are an expert in understanding invoices. We will upload an image as an invoice and you
will have to answer any questions based on the uploaded invoice image.
"""

if submit:
    image_data = input_image_details(upload_file)
    response = get_gemini_response(input_prompt, image_data, st.session_state.input)
    st.subheader("The Response is")
    st.write(response)
```
* **Why**: The app must wait until all details are filled out before executing the API call to save on cost/latency and to ensure no missing parameters trigger errors.
* **How**: Streamlit pauses the generation logic until the `submit` button yields `True`. Inside this conditional block:
  1. The image is parsed into bytes.
  2. The custom system prompt is bundled with the image data and the user's specific prompt (`st.session_state.input`).
  3. The response is fetched and drawn onto the screen beautifully with `st.write`.
