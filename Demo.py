import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import re
from io import BytesIO
import PyPDF2
import os
from google.cloud import aiplatform
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"/Users/adam/Documents/gcphackathon/gcp_keys.json"


def init_ai_platform(project_id, region):
    aiplatform.init(project=project_id, location=region)

project_id = '11111111'
region = 'us-central1'

if st.button('Initialize AI Platform'):
    init_ai_platform(project_id, region)
    st.success(f"AI Platform initialized for project: {project_id} in region: {region}")

def extract_text_from_pdf(file_like, pagenumber):
    pdf_reader = PyPDF2.PdfReader(file_like)  
    text = ''
    page_obj = pdf_reader.pages[pagenumber - 1]   
    if page_obj.extract_text():
        text += page_obj.extract_text() 
    return text  

# Upload PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
startpage_number = st.number_input("Enter start page number", value=1, step=1)
numberofpages = st.number_input("Enter number of pages", value=1, step=1)
resulttext = " "
if uploaded_file is not None and numberofpages > 0:
    summary = []
    for i in range(numberofpages):
        current_page_number = startpage_number + i
        text_from_pdf = extract_text_from_pdf(uploaded_file, current_page_number)
        summary.append(text_from_pdf)
        uploaded_file.seek(0)
    if summary:
        resulttext = " ".join(summary)
        st.text(" ".join(summary))  # Display the collected text.
        
        
def configure_model():
    # Initialize client for Vertex AI
    vertexai.init(project="ABCXYZ", location="us-central1")
    model = GenerativeModel("gemini-1.0-pro-002")
    return model

def generate_content(model, text_to_rewrite, generation_config, safety_settings):
    # Generate rephrased content using the provided model and configurations
    responses = model.generate_content(
        [text_to_rewrite],
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    return responses

def extract_answer(response):
    # Extract text from the model's response
    if "content" in response and "parts" in response["content"] and "text" in response["content"]["parts"]:
        return response["content"]["parts"]["text"]
    else:
        return "No answer text found."

def main():
    textdata = ""
    # Text to rewrite (example prompt)
    st.subheader("Use AI to rewrite and enhance text")
    #input_text = st.text_area("Enter the prompt:", height=300)
    #text_to_rewrite = input_text + ":"+ resulttext

    # Text to rewrite (example prompt)
    #st.subheader("Use AI to rewrite and enhance text")

    # Define the prompts
    prompt_1 = "You are a content creator, You are presented existing content, you need to Rewrite academic content as a nice story, Rewrite the below syllabus - Explain for deaf people but have eye sight, include key topics, include it within 200 words as simple bulleted points, content is: "
    prompt_2 = "You are a content creator, You are presented existing content, you need to Rewrite academic content as a nice story, Rewrite the below syllabus - Explain for blind but can hear, include key topics, include it within 200 words as simple easy words bullet points, content is: "
    prompt_3 = "Generate top 10 image prompts for key topics in this document, list as bullet points: "
    # Checkboxes for user to select the prompt
    use_prompt_1 = st.checkbox("Prompt to repurpose content for Special kids - Deaf People (with eyesight)", value=False)
    use_prompt_2 = st.checkbox("Prompt to repurpose content for Blind People (who can hear)", value=False)
    use_prompt_3 = st.checkbox("List image prompts for key topics", value=False)

    if use_prompt_1:
            textdata = prompt_1 +":"+ resulttext
    elif use_prompt_2:
            textdata = prompt_2 +":"+ resulttext
    elif use_prompt_3:
            textdata = prompt_3 +":"+ resulttext

    text_to_rewrite = textdata

    if st.button('Rewrite Content'):
        # Configuration for generation
        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 1,
            "top_p": 1,
        }

        # Safety settings configuration
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Get the configured model
        model = configure_model()

        # Generate content
        responses = generate_content(model, text_to_rewrite, generation_config, safety_settings)

      
        st.write("### Generated Rewritten Content", responses.text)
        
if __name__ == '__main__':
    main()        
