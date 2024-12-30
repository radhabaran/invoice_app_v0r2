# invoice_gen.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import os

class InvoiceGenerator:
    def __init__(self):
        self.invoice_dir = 'invoices'
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)

    def generate_invoice(self, workflow_state_dict):
        """Generate PDF invoice"""
        filename = f"{self.invoice_dir}/INV_{workflow_state_dict['invoice']['transaction_id']}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Company Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "COMPANY NAME")
        c.setFont("Helvetica", 10)
        c.drawString(50, 735, "123 Business Street")
        c.drawString(50, 720, "City, State 12345")

        # Invoice Header (Right aligned)
        c.setFont("Helvetica-Bold", 24)
        c.drawRightString(550, 750, "INVOICE")
        c.setFont("Helvetica", 10)
        c.drawRightString(550, 735, f"Invoice No: INV-{workflow_state_dict['invoice']['transaction_id']}")
        c.drawRightString(550, 720, f"Transaction ID: TXN-{workflow_state_dict['invoice']['transaction_id']}")
        c.drawRightString(550, 705, f"Date: {workflow_state_dict['invoice']['transaction_date']}")
        c.drawRightString(550, 690, f"Due Date: {workflow_state_dict['invoice']['payment_due_date']}")

        # Divider Line
        c.line(50, 670, 550, 670)

        # Bill To Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 650, "BILL TO")
        c.setFont("Helvetica", 10)
        c.drawString(50, 630, f"Customer ID: {workflow_state_dict['customer']['cust_unique_id']}")
        c.drawString(50, 615, f"Tax ID: {workflow_state_dict['customer']['cust_tax_id']}")
        c.drawString(50, 600, f"Name: {workflow_state_dict['customer']['cust_fname']} {workflow_state_dict['customer']['cust_lname']}")
        c.drawString(50, 585, f"Email: {workflow_state_dict['customer']['cust_email']}")

        # Payment Details Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(300, 650, "PAYMENT DETAILS")
        c.setFont("Helvetica", 10)
        c.drawString(300, 630, "Bank: Bank Name")
        c.drawString(300, 615, "Account No: Account No")
        c.drawString(300, 600, "SWIFT: INTLBANK123")

        # Table Headers
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, 520, "Description")
        c.drawString(350, 520, "Currency")
        c.drawRightString(550, 520, "Amount")

        # Table Line
        c.line(50, 515, 550, 515)

        # Table Content
        c.setFont("Helvetica", 10)
        c.drawString(50, 495, "Service Charge")
        c.drawString(350, 495, workflow_state_dict['invoice']['currency'])
        c.drawRightString(550, 495, f"{workflow_state_dict['invoice']['billed_amount']:,.2f}")

        # Total Amount
        c.line(50, 450, 550, 450)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(350, 430, "Total Amount Due")
        c.drawRightString(550, 430, f"{workflow_state_dict['invoice']['currency']} {workflow_state_dict['invoice']['billed_amount']:,.2f}")

        # Payment Status
        c.setFont("Helvetica", 10)
        c.drawString(50, 430, "Payment Status:")
        c.setFillColor(colors.orange if workflow_state_dict['invoice']['payment_status'].upper() == 'PENDING' else colors.green)
        c.drawString(120, 430, workflow_state_dict['invoice']['payment_status'].upper())

        # Footer
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        footer_text = "Thank you for your business. This is a computer-generated document. No signature is required."
        c.drawCentredString(300, 350, footer_text)
        contact_text = "If you have any questions, please contact us at: support@yourcompany.com | (555) 123-4567"
        c.drawCentredString(300, 335, contact_text)

        c.save()
        return filename