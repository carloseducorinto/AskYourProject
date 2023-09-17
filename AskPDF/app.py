import streamlit as st
from  dotenv import load_dotenv
from PyPDF2 import PdfReader


#  Extracts and concatenates text content from a list of PDF documents.
#  Args:pdf_docs (list): A list of paths to PDF documents.
#  Returns: str: Combined text extracted from all provided PDF documents.

def get_pdf_text(pdf_docs):
    text= ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text+=page.extract_text()
    return text        

    

def main():
    load_dotenv()
    st.set_page_config(page_title='Chat with Your Project', page_icon=':book:', layout='wide')
    st.header('Chat with Your Project :book:')
    st.text_input('Ask a questions about your project')
    

    with st.sidebar:
        st.subheader('Project Documents')
        pdf_docs= st.file_uploader("Upload your project documents and click on 'Process'",
                                   accept_multiple_files=True, type=['pdf']) 
        if st.button('Process'):
            with st.spinner("Processing"):
                
            # get pdf text
              raw_text = get_pdf_text(pdf_docs)  
              st.write(raw_text)
            # get text chunks

            # create vetor store



if __name__ == '__main__':
    main()