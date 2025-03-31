import json
import os
import boto3
import requests
import time
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from botocore.exceptions import ClientError
import asyncio
from pyppeteer import launch
from constants import get_wa_alert_pdf_template
from dotenv import load_dotenv
from xhtml2pdf import pisa

load_dotenv()

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET_REGION = os.getenv("S3_BUCKET_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME_WA_PDF")

class PDFGenerator:
    def __init__(self, output_dir: str = "pdf"):
        self.json_path = "alerts.json"
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template = self._load_template()
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
            region_name=S3_BUCKET_REGION
        )

        # Configuration constants
        self.MAX_RETRIES = 5
        self.TIMEOUT_MS = 30000  # 30 seconds
        self.RETRY_DELAY_MS = 3000  # 3 seconds

        # Environment variables
        self.WA_MICROSERVICE_URL = os.getenv('WA_MICROSERVICE_URL')

    def _load_json_data(self):
        with open(self.json_path, 'r') as f:
            self.json_data = json.load(f)

    def _load_template(self):
        return self.env.from_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Inventory and Sales Report - {{person_name}}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                .container { max-width: 1000px; margin: 0 auto; }
                .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
                .recipient-section { border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
                .recipient-header { background-color: #f5f5f5; padding: 10px; border-radius: 3px; margin-bottom: 15px; }
                .recipient-header h2 { margin: 0; color: #333; font-size: 18px; }
                .recipient-info { font-size: 14px; color: #666; margin: 5px 0; }
                .messages-list { margin-left: 20px; }
                .message-item { margin-bottom: 10px; font-size: 14px; }
                .products-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
                .products-table th, .products-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .products-table th { background-color: #f0f0f0; font-weight: bold; }
                .alert { color: #d32f2f; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Inventory and Sales Report</h1>
                    <p>Date: March 28, 2025</p>
                </div>
                <div class="recipient-section">
                    <div class="recipient-header">
                        <h2>Recipient: {{recipient_phone}}</h2>
                        <div class="recipient-info">Name: {{person_name}}</div>
                        <div class="recipient-info">Role: {{role}}</div>
                    </div>
                    <div class="messages-list">
                        {{messages_html | safe}}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)
    
    def _generate_pdf(self, html_content, output_path):
        """Generate a PDF from HTML using xhtml2pdf."""
        try:
            with open(output_path, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
            
            if pisa_status.err:
                print("Error generating PDF")
                return None

            with open(output_path, "rb") as pdf_file:
                pdf_binary = pdf_file.read()

            print("Done with PDF")
            return pdf_binary
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return None
    

    def _generate_messages_html(self, messages):
        messages_html = ""
        for message in messages:
            if "Product:" in message and "Last Sale:" in message:
                products = [line.split(', Last Sale:') for line in message.split('\n')]
                products_data = [{'product_name': p[0].replace('Product:', '').strip(), 
                                'last_sale_date': p[1].strip()} for p in products if len(p) == 2]
                messages_html += self.env.from_string("""
                    <table class="products-table">
                        <thead><tr><th>Product Name</th><th>Last Sale Date</th></tr></thead>
                        <tbody>
                            {% for product in products %}
                            <tr><td>{{product.product_name}}</td><td>{{product.last_sale_date}}</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                """).render(products=products_data)
            else:
                messages_html += f'<div class="message-item {"alert" if "Alert:" in message else ""}">{message}</div>'
        return messages_html 

    def _upload_to_s3(self, pdf_content, key):
        """Upload PDF content to S3 and return the signed URL"""
        try:
            
            print(S3_BUCKET_REGION , S3_BUCKET_NAME , key)
            return
            
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=key,
                Body=pdf_content,
                ContentType='application/pdf'
            )

            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
                ExpiresIn=3600  
            )

            return signed_url
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise

    def _send_to_whatsapp_service(self, whatsapp_data, attempt=1):
        """Send PDF URL to WhatsApp service with retry logic"""
        try:
            WA_MICROSERVICE_URL = "https://whatsapp.baylink.in/send-message"
            template = get_wa_alert_pdf_template(whatsapp_data['recipient'], whatsapp_data['pdfUrl'])

            print(f"Attempting to send to WhatsApp service (attempt {attempt}/{self.MAX_RETRIES})")
            response = requests.post(
                WA_MICROSERVICE_URL,
                json=template,
                timeout=10
            )
            response.raise_for_status()
            print(f"WhatsApp service response: {response.json()}")
            return response.json()
        except (requests.RequestException, requests.Timeout) as error:
            print(f"Error in attempt {attempt}/{self.MAX_RETRIES}: {error}")
            if attempt < self.MAX_RETRIES:
                print(f"Retrying in {self.RETRY_DELAY_MS/1000} seconds...")
                time.sleep(self.RETRY_DELAY_MS / 1000)
                return self._send_to_whatsapp_service(whatsapp_data, attempt + 1)
            raise error

    def generate_and_send_pdfs(self):
        self._load_json_data()
 
        try:
            loop = asyncio.get_running_loop()   
        except RuntimeError:
            loop = asyncio.new_event_loop()   
            asyncio.set_event_loop(loop)

        for recipient in self.json_data:
            messages_html = self._generate_messages_html(recipient['messages'])
            html_content = self.template.render(
                recipient_phone=recipient['recipient'],
                person_name=recipient['person_name'],
                role=recipient['role'],
                messages_html=messages_html
            )

            timestamp = int(time.time())
            formatted_date = datetime.now().strftime('%Y-%m-%d')
            output_path = f"{self.output_dir}/report_{recipient['recipient']}_{formatted_date}_{timestamp}.pdf"

            pdf_content = self._generate_pdf(html_content, output_path)

            key = f"reports/report_{recipient['recipient']}_{formatted_date}_{timestamp}.pdf"

            pdf_url = self._upload_to_s3(pdf_content, key)
            print(f"Uploaded PDF to S3")

            whatsapp_data = {
                "pdfUrl": pdf_url,
                "recipient": "7007555103",  # recipient['recipient'],
            }

            try:
                whatsapp_response = self._send_to_whatsapp_service(whatsapp_data)
                print(f"Successfully sent to WhatsApp for {recipient['recipient']}: {whatsapp_response}")
            except Exception as e:
                print(f"Failed to send WhatsApp message for {recipient['recipient']}: {e}")

        print("PDF generation and WhatsApp sending process completed!")