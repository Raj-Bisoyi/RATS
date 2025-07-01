from serpapi import search 
import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# exract information from the resume
def extract_text_from_resume(uploaded_resume):
    resume_text = ""
    if uploaded_resume is not None:
        pdf_reader = PdfReader(uploaded_resume)
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
    return resume_text

#get response from the gemini model
def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(input_prompt)
    return response.text

#display job results
def get_job_suggestions(skill_name):
    params = {
      "engine": "google_jobs",
      "q": skill_name ,
      "ltype": "1",
      "hl": "en",
      "api_key": os.getenv('JOB_API_KEY')  
    }
    res = search(params)
    jobs_results = res["jobs_results"]    
    return jobs_results





# Display the image with fixed width and height
st.image("animation.gif", width=400)


st.title('Resume Application Tracking System')

st.write("Welcome to the Resume ATS! Please upload a job description and a resume in PDF format to get started.")

uploaded_job_description = st.text_area("Enter Job Description", help='Enter the job description text')
uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=['pdf'], help='Upload a PDF file containing the resume')

col1, col2 = st.columns(2)

with col1:
    summerize_resume_btn = st.button("Extract the Information from Resume")
    job_match_btn = st.button("Find Job Match Percentage")

with col2:
    evaluate_resume_btn = st.button("Evaluate Resume")
    suggest_job_skill_btn = st.button("Suggest Job Titles and Skill Sets")



def display_job_results(job_results):
    for job in job_results:
        st.write("Title:", job['title'])
        st.write("Company:", job['company_name'])
        st.write("Location:", job['location'])
        st.write("Via:", job['via'])
        link = job.get('related_links', [{}])[0].get('link', '')
        if link:
            st.write("Related Link:")
            st.markdown(f"[Click here to open the link]({link})", unsafe_allow_html=True)
        st.write("---")

skill_name = st.text_input("Enter skill name:")
if skill_name:
    st.write(f"Showing job suggestions for '{skill_name}':")
    job_results = get_job_suggestions(skill_name)
    display_job_results(job_results)


if summerize_resume_btn:
    if uploaded_resume is not None:
        resume_text = extract_text_from_resume(uploaded_resume)
        
        summerize_resume = """
        Act as a expert and experienced Software Engineer and summerize the resume.
        extract the information from the resume convert it into a structured format 
        personal details
        education
        experience 
        projects(if any)
        and other things..
      
        Resume: {resume_text}
        
        """

        response = get_gemini_response(summerize_resume.format(resume_text=resume_text))
        st.write(response)
    else:
        st.error("Please upload the resume to generate the response.")

if job_match_btn:
    if uploaded_job_description is not None and uploaded_resume is not None:
        job_description_text = uploaded_job_description
        
        resume_text = extract_text_from_resume(uploaded_resume)
        
        input_prompt = f"""
        You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of Technology field  and ATS functionality. 
        Your task is to evaluate the resume against the provided job description and provide the percentage match. and score each section of the resume based on the job description.
        suggest missing keywords in the resume.

        Job Description: {job_description_text}
        Resume: {resume_text}
        
        """
        
        # Call the generative AI model to find the job match percentage
        response = get_gemini_response(input_prompt)
        
        st.subheader("Job Match Percentage:")
        st.write(response)
    else:
        st.error("Please upload both job description and resume to find the job match percentage.")

if evaluate_resume_btn:
    if uploaded_job_description is not None and uploaded_resume is not None:
        job_description_text = uploaded_job_description
        resume_text = extract_text_from_resume(uploaded_resume)
        input_prompt = f"""
        As an HR professional tasked with evaluating resumes, your objective is to review the provided resume against the job description 
        and assess the candidate's profile for alignment with the role.

        Resume: {resume_text}
        Job Description: {job_description_text}
        """
        
        response = get_gemini_response(input_prompt.format(job_description_text=job_description_text, resume_text=resume_text))
        
        st.subheader("Evaluation Result:")
        st.write(response)
    else:
        st.error("Please upload both job description and resume to evaluate the resume.")        

if suggest_job_skill_btn:
    if uploaded_resume is not None:
        resume_text = extract_text_from_resume(uploaded_resume)
        
        input_prompt = f"""
        You are a skilled AI model trained to analyze resumes and suggest relevant job titles and skill sets based on the provided resume.
        suggest 10 and output format in two cloumns job titles and skill sets.
        Resume: {resume_text}
        """
        
        response = get_gemini_response(input_prompt)
        
        st.subheader("Suggested Job Titles and Skill Sets:")
        st.write(response)
    else:
        st.error("Please upload the resume to suggest job titles and skill sets.")

