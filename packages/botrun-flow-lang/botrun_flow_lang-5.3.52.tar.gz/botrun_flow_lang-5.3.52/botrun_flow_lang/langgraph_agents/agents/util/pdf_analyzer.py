import anthropic
import base64
import httpx
from vertexai.generative_models import GenerativeModel, Part
import vertexai
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import aiplatform

load_dotenv()


def analyze_pdf(pdf_url: str, user_input: str):
    """
    Analyze a PDF file using Claude API

    Args:
        pdf_url: URL to the PDF file
        user_input: User's query about the PDF content

    Returns:
        str: Claude's analysis of the PDF content based on the query
    """
    try:
        # Download and encode the PDF file from URL
        pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

        # Initialize Anthropic client
        client = anthropic.Anthropic()

        # Send to Claude
        message = client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=4096,  # Increased token limit for detailed analysis
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data,
                            },
                        },
                        {"type": "text", "text": user_input},
                    ],
                }
            ],
        )

        return message.content[0].text

    except Exception as e:
        print(f"Error analyzing PDF with anthropic: {str(e)}")
        # return f"Error analyzing PDF: {str(e)}"

    try:

        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI"),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        vertexai.init(
            project="scoop-386004",
            location="us-central1",  # 目前 gemini 2.0 只支援 us-central1
            credentials=credentials,
        )
        model = GenerativeModel("gemini-2.0-flash")

        # pdf_file = Part.from_uri(
        #     uri=pdf_url,
        #     mime_type="application/pdf",
        # )
        pdf_file = Part.from_data(
            data=pdf_data,
            mime_type="application/pdf",
        )
        contents = [pdf_file, user_input]

        response = model.generate_content(contents)
        # print(response.text)
        return response.text
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error analyzing PDF with gemini: {str(e)}")
    return "Error analyzing PDF"
