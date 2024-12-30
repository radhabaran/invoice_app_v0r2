# modules/kyc_manager.py

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid
from typing import Dict, Any, Optional, Tuple
from config.customer_config import CustomerConfig
from config.kyc_application_pdf_config import KYCApplicationPDFConfig
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import csv

class KYCManager:
    def __init__(self):
        self.config = CustomerConfig()
        self.pdf_config = KYCApplicationPDFConfig()
        self.setup_data_store()
        self.setup_pdf_directories()
        self.initialize_session_state()


    def setup_data_store(self):
        """Initialize data storage and create files if they don't exist"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(self.config.DATA_DIR, exist_ok=True)
        
            # Create KYC file with headers if it doesn't exist
            if not os.path.exists(self.config.KYC_DATA_FILE):
                # Create empty DataFrame with all required columns
                df = pd.DataFrame(columns=self.config.KYC_CSV_HEADERS)
            
                # Create directory if it doesn't exist (in case KYC_DATA_FILE includes subdirectories)
                os.makedirs(os.path.dirname(self.config.KYC_DATA_FILE), exist_ok=True)
            
                # Save empty DataFrame with headers
                df.to_csv(self.config.KYC_DATA_FILE, index=False)
                print(f"Created new KYC data file: {self.config.KYC_DATA_FILE}")
       
        except Exception as e:
            st.error(f"Error setting up data store: {str(e)}")
            raise


    def setup_pdf_directories(self):
        """Create necessary directory for PDF storage"""
        os.makedirs(self.pdf_config.KYC_APPLICATION_PDF_DIR, exist_ok=True)


    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'kyc_search_results' not in st.session_state:
            st.session_state.kyc_search_results = None


    def save_kyc_record(self, kyc_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Save KYC record to CSV"""
        try:
            # Check for duplicates if this is a new record
            if 'customer_id' not in kyc_data:
                is_duplicate, existing_record = self.check_duplicate(
                    kyc_data['full_name'],
                    kyc_data['date_of_birth'],
                    kyc_data['passport_number']
                )
            
                if is_duplicate:
                    return False, f"Duplicate record found with Customer ID: {existing_record['customer_id']}"
            
                # Generate new customer ID
                kyc_data['customer_id'] = self.generate_customer_id()
                kyc_data['submission_date'] = datetime.now().strftime('%Y-%m-%d')
                kyc_data['kyc_status'] = 'Pending'

            df = pd.read_csv(self.config.KYC_DATA_FILE)
            
            if kyc_data.get('customer_id') in df['customer_id'].values:
                # Update existing record
                df.loc[df['customer_id'] == kyc_data['customer_id']] = kyc_data
            else:
                # Add new record
                df = pd.concat([df, pd.DataFrame([kyc_data])], ignore_index=True)
        
            df.to_csv(self.config.KYC_DATA_FILE, index=False)
            return True, f"KYC record saved successfully with Customer ID: {kyc_data['customer_id']}"
        except Exception as e:
            return False, f"Error saving KYC record: {str(e)}"


    def search_records(self, search_term: str) -> pd.DataFrame:
        """Search KYC records"""
        try:
            df = pd.read_csv(self.config.KYC_DATA_FILE)
            if search_term:
                mask = df.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
                return df[mask]
            return df
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return pd.DataFrame()


    def render_kyc_form(self, customer_id: Optional[str] = None, existing_data: Optional[Dict] = None):
        """Render KYC form"""
        with st.form("kyc_form"):
            if customer_id:
                st.text_input("Customer ID", value=customer_id, disabled=True)

                # Add KYC Status selector for existing records
                kyc_status = st.selectbox(
                    "KYC Status",
                    self.config.KYC_STATUS_OPTIONS,
                    index=self.config.KYC_STATUS_OPTIONS.index(existing_data.get('kyc_status', 'Pending'))
                    
                    if existing_data and existing_data.get('kyc_status') in self.config.KYC_STATUS_OPTIONS
                    else 0
                )
            # Customer Section
            st.subheader(self.config.KYC_FIELDS['customer']['title'])
            col1, col2 = st.columns(2)
            with col1:
                residential_status = st.selectbox(
                    "Residential Status*",
                    self.config.RESIDENTIAL_STATUS_OPTIONS,
                    index=self.config.RESIDENTIAL_STATUS_OPTIONS.index(existing_data.get('residential_status', ''))
                    if existing_data and existing_data.get('residential_status') in self.config.RESIDENTIAL_STATUS_OPTIONS
                    else 0
                )
                full_name = st.text_input("Full Name*", value=existing_data.get('full_name', '') if existing_data else '')
                residential_address_line1 = st.text_input(
                    "Residential Address Line 1*",
                    value=existing_data.get('residential_address_line1', '') if existing_data else ''
                )
                residential_address_line2 = st.text_input(
                    "Residential Address Line 2",
                    value=existing_data.get('residential_address_line2', '') if existing_data else ''
                )
            with col2:
                home_address_line1 = st.text_input(
                    "Home Address Line 1*",
                    value=existing_data.get('home_address_line1', '') if existing_data else ''
                )
                home_address_line2 = st.text_input(
                    "Home Address Line 2",
                    value=existing_data.get('home_address_line2', '') if existing_data else ''
                )
                contact_landline = st.text_input(
                    "Contact (Landline)",
                    value=existing_data.get('contact_landline', '') if existing_data else ''
                )
                contact_office = st.text_input(
                    "Contact (Office)",
                    value=existing_data.get('contact_office', '') if existing_data else ''
                )
                contact_mobile = st.text_input(
                    "Contact (Mobile)*",
                    value=existing_data.get('contact_mobile', '') if existing_data else ''
                )

            # Customer Information Section
            st.subheader(self.config.KYC_FIELDS['customer_information']['title'])
            col1, col2 = st.columns(2)
            with col1:
                gender = st.selectbox(
                    "Gender*",
                    self.config.GENDER_OPTIONS,
                    index=self.config.GENDER_OPTIONS.index(existing_data.get('gender', ''))
                    if existing_data and existing_data.get('gender') in self.config.GENDER_OPTIONS
                    else 0
                )
                nationality = st.selectbox(
                    "Nationality*",
                    self.config.NATIONALITY_OPTIONS,
                    index=self.config.NATIONALITY_OPTIONS.index(existing_data.get('nationality', ''))
                    if existing_data and existing_data.get('nationality') in self.config.NATIONALITY_OPTIONS
                    else 0
                )
                date_of_birth = st.date_input(
                    "Date of Birth*",
                    value=datetime.strptime(existing_data.get('date_of_birth'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('date_of_birth') else None
                )
                place_of_birth = st.text_input(
                    "Place of Birth*",
                    value=existing_data.get('place_of_birth', '') if existing_data else ''
                )
            with col2:
                passport_number = st.text_input(
                    "Passport Number*",
                    value=existing_data.get('passport_number', '') if existing_data else ''
                )
                passport_issue_place = st.text_input(
                    "Passport Issue Place*",
                    value=existing_data.get('passport_issue_place', '') if existing_data else ''
                )
                passport_issue_date = st.date_input(
                    "Passport Issue Date*",
                    value=datetime.strptime(existing_data.get('passport_issue_date'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('passport_issue_date') else None
                )
                passport_expiry_date = st.date_input(
                    "Passport Expiry Date*",
                    value=datetime.strptime(existing_data.get('passport_expiry_date'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('passport_expiry_date') else None
                )

            # Additional Passport Information
            st.subheader("Additional Passport Information (if applicable)")
            col1, col2 = st.columns(2)
            with col1:
                dual_nationality = st.text_input(
                    "Dual Nationality",
                    value=existing_data.get('dual_nationality', '') if existing_data else ''
                )
                dual_passport_number = st.text_input(
                    "Dual Passport Number",
                    value=existing_data.get('dual_passport_number', '') if existing_data else ''
                )
            with col2:
                dual_passport_issue_date = st.date_input(
                    "Dual Passport Issue Date",
                    value=datetime.strptime(existing_data.get('dual_passport_issue_date'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('dual_passport_issue_date') else None
                )
                dual_passport_expiry_date = st.date_input(
                    "Dual Passport Expiry Date",
                    value=datetime.strptime(existing_data.get('dual_passport_expiry_date'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('dual_passport_expiry_date') else None
                )

            # UAE Specific Information
            st.subheader("UAE Specific Information")
            col1, col2 = st.columns(2)
            with col1:
                emirates_id = st.text_input(
                    "Emirates ID Number*",
                    value=existing_data.get('emirates_id', '') if existing_data else ''
                )
                emirates_id_expiry = st.date_input(
                    "Emirates ID Expiry Date*",
                    value=datetime.strptime(existing_data.get('emirates_id_expiry'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('emirates_id_expiry') else None
                )
            with col2:
                visa_uid = st.text_input(
                    "Visa UID Number*",
                    value=existing_data.get('visa_uid', '') if existing_data else ''
                )
                visa_expiry = st.date_input(
                    "Visa Expiry Date*",
                    value=datetime.strptime(existing_data.get('visa_expiry'), '%Y-%m-%d').date()
                    if existing_data and existing_data.get('visa_expiry') else None
                )

            # Customer Occupation Section
            st.subheader(self.config.KYC_FIELDS['customer_occupation']['title'])
            col1, col2 = st.columns(2)
            with col1:
                occupation = st.text_input(
                    "Occupation*",
                    value=existing_data.get('occupation', '') if existing_data else ''
                )
                sponsor_business_name = st.text_input(
                    "Name of Sponsor/Business*",
                    value=existing_data.get('sponsor_business_name', '') if existing_data else ''
                )
            with col2:
                sponsor_business_address = st.text_area(
                    "Sponsor/Business Address*",
                    value=existing_data.get('sponsor_business_address', '') if existing_data else ''
                )
                sponsor_business_landline = st.text_input(
                    "Sponsor/Business Landline*",
                    value=existing_data.get('sponsor_business_landline', '') if existing_data else ''
                )
                sponsor_business_mobile = st.text_input(
                    "Sponsor/Business Mobile*",
                    value=existing_data.get('sponsor_business_mobile', '') if existing_data else ''
                )

            # Customer Profile and Payment Section
            st.subheader(self.config.KYC_FIELDS['customer_profile_payment']['title'])
            col1, col2 = st.columns(2)
            with col1:
                annual_income = st.number_input(
                    "Annual Salary/Business Income*",
                    min_value=0,
                    value=int(existing_data.get('annual_income', 0)) if existing_data else 0
                )
                investment_purpose = st.selectbox(
                    "Purpose of Investment*",
                    self.config.INVESTMENT_PURPOSE_OPTIONS,
                    index=self.config.INVESTMENT_PURPOSE_OPTIONS.index(existing_data.get('investment_purpose', ''))
                    if existing_data and existing_data.get('investment_purpose') in self.config.INVESTMENT_PURPOSE_OPTIONS
                    else 0
                )
            with col2:
                source_of_funds = st.selectbox(
                    "Source of Fund*",
                    self.config.SOURCE_OF_FUNDS_OPTIONS,
                    index=self.config.SOURCE_OF_FUNDS_OPTIONS.index(existing_data.get('source_of_funds', ''))
                    if existing_data and existing_data.get('source_of_funds') in self.config.SOURCE_OF_FUNDS_OPTIONS
                    else 0
                )
                payment_method = st.selectbox(
                    "Payment Method*",
                    self.config.PAYMENT_METHOD_OPTIONS,
                    index=self.config.PAYMENT_METHOD_OPTIONS.index(existing_data.get('payment_method', ''))
                    if existing_data and existing_data.get('payment_method') in self.config.PAYMENT_METHOD_OPTIONS
                    else 0
                )

            # Declaration
            st.markdown("### Declaration")
            st.markdown(self.config.DECLARATION_TEXT)
            declaration_accepted = st.checkbox("I accept the above declaration")

            submitted = st.form_submit_button("Submit KYC Application")
            
            if submitted:
                if not declaration_accepted:
                    st.error("Please accept the declaration to proceed")
                    return

                kyc_data = {
                    'customer_id': customer_id,
                    'kyc_status': kyc_status if customer_id else 'Pending',
                    # Customer
                    'residential_status': residential_status,
                    'full_name': full_name,
                    'residential_address_line1': residential_address_line1,
                    'residential_address_line2': residential_address_line2,
                    'home_address_line1': home_address_line1,
                    'home_address_line2': home_address_line2,
                    'contact_landline': contact_landline,
                    'contact_office': contact_office,
                    'contact_mobile': contact_mobile,
                    # Customer Information
                    'gender': gender,
                    'nationality': nationality,
                    'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                    'place_of_birth': place_of_birth,
                    'passport_number': passport_number,
                    'passport_issue_place': passport_issue_place,
                    'passport_issue_date': passport_issue_date.strftime('%Y-%m-%d'),
                    'passport_expiry_date': passport_expiry_date.strftime('%Y-%m-%d'),
                    'dual_nationality': dual_nationality,
                    'dual_passport_number': dual_passport_number,
                    'dual_passport_issue_date': dual_passport_issue_date.strftime('%Y-%m-%d') if dual_passport_issue_date else None,
                    'dual_passport_expiry_date': dual_passport_expiry_date.strftime('%Y-%m-%d') if dual_passport_expiry_date else None,
                    'emirates_id': emirates_id,
                    'emirates_id_expiry': emirates_id_expiry.strftime('%Y-%m-%d'),
                    'visa_uid': visa_uid,
                    'visa_expiry': visa_expiry.strftime('%Y-%m-%d'),
                    # Customer Occupation
                    'occupation': occupation,
                    'sponsor_business_name': sponsor_business_name,
                    'sponsor_business_address': sponsor_business_address,
                    'sponsor_business_landline': sponsor_business_landline,
                    'sponsor_business_mobile': sponsor_business_mobile,
                    # Customer Profile and Payment
                    'annual_income': annual_income,
                    'investment_purpose': investment_purpose,
                    'source_of_funds': source_of_funds,
                    'payment_method': payment_method
                }
                
                if existing_data:
                    kyc_data['status'] = existing_data['status']
                
                success, message = self.save_kyc_record(kyc_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)


    def render_kyc_tab(self, customer_id: Optional[str] = None):
        """Render KYC tab content"""
        st.subheader("KYC Management")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.button("Add")
        with col2:
            st.button("Update")
        with col3:
            if st.button("Generate KYC Application"):
                if customer_id:
                    df = pd.read_csv(self.config.KYC_DATA_FILE)
                    customer_data = df[df['customer_id'] == customer_id].to_dict('records')[0]
                    success, message = self.generate_kyc_application(customer_data)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please select a customer first")
        with col4:
            st.button("Refresh")

        # Search section
        search_term = st.text_input("Search KYC Records", placeholder="Enter customer ID, name, or passport number")
    
        # Show search results if search term is entered
        if search_term:
            results = self.search_records(search_term)
            if not results.empty:
                st.dataframe(results)
    
        # Always render the KYC form, with customer_id if provided
        self.render_kyc_form(customer_id)


    def generate_kyc_application(self, customer_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Generate KYC application PDF"""
        try:
            if customer_data.get('status').lower() != 'completed':
                return False, "PDF generation is only allowed for completed KYC applications"

            filename = f"kyc_application_{customer_data['customer_id']}.pdf"
            filepath = os.path.join(self.pdf_config.KYC_APPLICATION_PDF_DIR, filename)
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4

            # Header
            c.setFont(self.pdf_config.HEADER_FONT, self.pdf_config.HEADER_SIZE)
            c.drawString(self.pdf_config.PAGE_MARGIN, height - 50, self.pdf_config.PDF_TITLE)
            
            c.setFont(self.pdf_config.FIELD_FONT, self.pdf_config.FIELD_SIZE)
            c.drawString(self.pdf_config.PAGE_MARGIN, height - 70, self.pdf_config.PDF_SUBTITLE)

            y = height - 100

            # Generate each section
            for section in self.pdf_config.PDF_SECTIONS:
                y = self._add_section(c, section, customer_data, y)
                y -= self.pdf_config.SECTION_SPACING

            c.save()
            return True, f"PDF generated successfully: {filepath}"
        
        except Exception as e:
            return False, f"Error generating PDF: {str(e)}"


    def _add_section(self, canvas, section: str, data: Dict[str, Any], y: int) -> int:
        """Add a section to the PDF and return new y position"""
        # Section header
        canvas.setFont(self.pdf_config.SECTION_FONT, self.pdf_config.SECTION_SIZE)
        canvas.drawString(self.pdf_config.PAGE_MARGIN, y, section)
        y -= 20

        # Add fields for this section
        canvas.setFont(self.pdf_config.FIELD_FONT, self.pdf_config.FIELD_SIZE)
        if section in self.pdf_config.PDF_FIELDS:
            for label, key in self.pdf_config.PDF_FIELDS[section]:
                y -= self.pdf_config.FIELD_SPACING
                value = data.get(key, '')
                
                # Format dates properly
                if isinstance(value, str) and key.endswith(('_date', 'Date')):
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').strftime('%d-%m-%Y')
                    except:
                        pass
                        
                canvas.drawString(self.pdf_config.PAGE_MARGIN, y, f"{label}: {value}")

        # Add declaration text if it's the declaration section
        if section == 'Declaration':
            y -= 30
            canvas.setFont(self.pdf_config.FIELD_FONT, self.pdf_config.FIELD_SIZE)
            canvas.drawString(self.pdf_config.PAGE_MARGIN, y, self.pdf_config.DECLARATION_TEXT)
            
            # Add signature fields
            y -= 50
            canvas.drawString(self.pdf_config.PAGE_MARGIN, y, f"Full Name of the Customer: {data['full_name']}")
            canvas.drawString(self.pdf_config.PAGE_MARGIN, y-20, f"Signed as on Date: {datetime.now().strftime('%d-%m-%Y')}")
            canvas.drawString(self.pdf_config.PAGE_MARGIN, y-40, "Signature: _____________________")
            y -= 60

        return y

