# modules/kyc_manager.py

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid
from typing import Dict, Any, Optional, Tuple
from config.customer_config import CustomerConfig

class KYCManager:
    def __init__(self):
        self.config = CustomerConfig()
        self.setup_data_store()
        self.initialize_session_state()


    def setup_data_store(self):
        """Initialize data storage"""
        if not os.path.exists(self.config.DATA_DIR):
            os.makedirs(self.config.DATA_DIR)
            
        if not os.path.exists(self.config.KYC_DATA_FILE):
            raise FileNotFoundError(
                f"KYC data file not found at {self.config.KYC_DATA_FILE}. "
                "Please ensure the required data file exists with proper headers."
            )


    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'kyc_search_results' not in st.session_state:
            st.session_state.kyc_search_results = None


    def save_kyc_record(self, kyc_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Save KYC record to CSV"""
        try:
            df = pd.read_csv(self.config.KYC_DATA_FILE)
            
            if 'kyc_id' not in kyc_data:
                kyc_data['kyc_id'] = str(uuid.uuid4())
                kyc_data['submission_date'] = datetime.now().strftime('%Y-%m-%d')
                kyc_data['status'] = 'Pending'
                df = pd.concat([df, pd.DataFrame([kyc_data])], ignore_index=True)
            else:
                df.loc[df['kyc_id'] == kyc_data['kyc_id']] = kyc_data
            
            df.to_csv(self.config.KYC_DATA_FILE, index=False)
            return True, "KYC record saved successfully"
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
                    kyc_data['kyc_id'] = existing_data['kyc_id']
                    kyc_data['submission_date'] = existing_data['submission_date']
                    kyc_data['status'] = existing_data['status']
                
                success, message = self.save_kyc_record(kyc_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)


    def render_kyc_tab(self, customer_id: Optional[str] = None):
        """Render KYC tab content"""
        if customer_id:
            st.subheader(f"KYC Application for Customer: {customer_id}")
            self.render_kyc_form(customer_id)
        else:
            st.info("Please select a customer first")