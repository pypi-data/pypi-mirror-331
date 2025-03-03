from .pipeline import Pipeline
import threading
from ..utillake import Utillake
import PyPDF2
from markdownify import markdownify as md
import unicodedata
from io import BytesIO
import requests
from docx import Document
import os


class Datalake:
    def __init__(self):
        self.pipelines = {}
        self.utillake=Utillake()
        self.datalake_id = None
        self.params = {}

    def create_pipeline(self, name):
        if name in self.pipelines:
            raise ValueError(f"Pipeline with name '{name}' already exists.")
        pipeline = Pipeline(name)
        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline_by_name(self, name):
        return self.pipelines.get(name)

    def execute_all(self):
        threads = []
        for pipeline in self.pipelines.values():
            thread = threading.Thread(target=pipeline.execute)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


    def create(self, payload=None):
        api_endpoint = '/datalake/create'
        if not payload:
            payload = {}

        response = self.utillake.call_api(api_endpoint, payload, self)
        if response and 'datalake_id' in response:
            self.datalake_id = response['datalake_id']

        return response

    def document_fetch(self, payload):
        api_endpoint = '/datalake/document/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def document_push(self, payload):
        api_endpoint = '/datalake/document/push'
        return self.utillake.call_api(api_endpoint, payload, self)

    def generate_markdown(self, payload):
        """
        Transforms a document (PDF from URL, PDF from local file, or DOCX) into markdown content.

        Args:
            payload (dict): Contains document data, source, and type.

        Returns:
            str: Markdown content extracted from the document.
        """
        file = payload["document_data"]
        document_type = payload["document_type"]
        document_source = payload["document_source"]

        # **Handle URL Documents**
        if document_source == "url":
            response = requests.get(file)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch document from URL: {file}")

            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower() or file.lower().endswith(".pdf") or self.is_pdf(response.content):
                pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
                text_content = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

                # Normalize and convert to Markdown
                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)
            else:
                raise ValueError("Unsupported file type. Only PDFs are supported.")

        # **Handle Local Files**
        elif document_source == "local_storage":
            if not os.path.exists(file):
                raise ValueError(f"Local file not found: {file}")

            if document_type == "pdf" and file.lower().endswith(".pdf"):
                with open(file, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text_content = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)

            elif document_type == "docx" and file.lower().endswith(".docx"):
                doc = Document(file)
                text_content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)


            else:
                raise ValueError("Unsupported local file type. Only PDFs and DOCX are supported.")

        else:
            raise ValueError("Unsupported document source. Use 'url' or 'local_file'.")



    def is_pdf(self, file_bytes):
        """
        Checks if the given file bytes represent a valid PDF.

        Args:
            file_bytes (bytes): The file content.

        Returns:
            bool: True if it's a valid PDF, False otherwise.
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            return True
        except PyPDF2.errors.PdfReadError:
            return False