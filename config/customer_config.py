# config/customer_config.py

import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class CustomerConfig:
    # Base paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = field(default=os.path.join(BASE_DIR, 'data'))
    KYC_DATA_FILE: str = field(default=os.path.join(DATA_DIR, 'kyc_records.csv'))

    # KYC Form Structure
    KYC_FIELDS: Dict[str, Dict] = field(default_factory=lambda: {
        'customer': {
            'title': 'Customer',
            'fields': {
                'residential_status': {'type': 'select', 'required': True, 'label': 'Residential Status'},
                'full_name': {'type': 'text', 'required': True, 'label': 'Full Name'},
                'residential_address_line1': {'type': 'text', 'required': True, 'label': 'Residential Address Line 1'},
                'residential_address_line2': {'type': 'text', 'required': False, 'label': 'Residential Address Line 2'},
                'home_address_line1': {'type': 'text', 'required': True, 'label': 'Home Address Line 1'},
                'home_address_line2': {'type': 'text', 'required': False, 'label': 'Home Address Line 2'},
                'contact_landline': {'type': 'text', 'required': False, 'label': 'Contact Details (Landline)'},
                'contact_office': {'type': 'text', 'required': False, 'label': 'Contact Details (Office)'},
                'contact_mobile': {'type': 'text', 'required': True, 'label': 'Contact Details (Mobile)'}
            }
        },
        'customer_information': {
            'title': 'Customer Information',
            'fields': {
                'gender': {'type': 'select', 'required': True, 'label': 'Gender'},
                'nationality': {'type': 'select', 'required': True, 'label': 'Nationality'},
                'date_of_birth': {'type': 'date', 'required': True, 'label': 'Date of Birth'},
                'place_of_birth': {'type': 'text', 'required': True, 'label': 'Place of Birth'},
                'passport_number': {'type': 'text', 'required': True, 'label': 'Passport Number'},
                'passport_issue_place': {'type': 'text', 'required': True, 'label': 'Passport Issued Place'},
                'passport_issue_date': {'type': 'date', 'required': True, 'label': 'Passport Issue Date'},
                'passport_expiry_date': {'type': 'date', 'required': True, 'label': 'Passport Expiry Date'},
                'dual_nationality': {'type': 'text', 'required': False, 'label': 'Dual Nationality (if any)'},
                'dual_passport_number': {'type': 'text', 'required': False, 'label': 'Dual Passport Number'},
                'dual_passport_issue_date': {'type': 'date', 'required': False, 'label': 'Dual Passport Issue Date'},
                'dual_passport_expiry_date': {'type': 'date', 'required': False, 'label': 'Dual Passport Expiry Date'},
                'emirates_id': {'type': 'text', 'required': True, 'label': 'Emirates ID Number'},
                'emirates_id_expiry': {'type': 'date', 'required': True, 'label': 'Emirates ID Expiry Date'},
                'visa_uid': {'type': 'text', 'required': True, 'label': 'Visa UID Number'},
                'visa_expiry': {'type': 'date', 'required': True, 'label': 'Visa Expiry Date'}
            }
        },
        'customer_occupation': {
            'title': 'Customer Occupation',
            'fields': {
                'occupation': {'type': 'text', 'required': True, 'label': 'Occupation'},
                'sponsor_business_name': {'type': 'text', 'required': True, 'label': 'Name of the Sponsor or Business'},
                'sponsor_business_address': {'type': 'textarea', 'required': True, 'label': 'Sponsor or Business Address'},
                'sponsor_business_landline': {'type': 'text', 'required': True, 'label': 'Sponsor or Business Contact Details (Land Line)'},
                'sponsor_business_mobile': {'type': 'text', 'required': True, 'label': 'Sponsor or Business Contact Details (Mobile)'}
            }
        },
        'customer_profile_payment': {
            'title': 'Customer Profile and Payment',
            'fields': {
                'annual_income': {'type': 'number', 'required': True, 'label': 'Annual Salary or Business Income'},
                'investment_purpose': {'type': 'select', 'required': True, 'label': 'Purpose of Investment'},
                'source_of_funds': {'type': 'select', 'required': True, 'label': 'Source of Fund'},
                'payment_method': {'type': 'select', 'required': True, 'label': 'Payment Method'}
            }
        }
    })

    # Field Options
    GENDER_OPTIONS: List[str] = field(default_factory=lambda: [
        "Male", "Female", "Other"
    ])

    RESIDENTIAL_STATUS_OPTIONS: List[str] = field(default_factory=lambda: [
        "Resident", "Non-Resident", "Temporary Resident"
    ])

    NATIONALITY_OPTIONS: List[str] = field(default_factory=lambda: [
        "UAE", "USA", "UK", "India", "Pakistan", "Others"
    ])

    SOURCE_OF_FUNDS_OPTIONS: List[str] = field(default_factory=lambda: [
        "Salary", "Business Income", "Investments", "Inheritance", "Savings", "Other"
    ])

    INVESTMENT_PURPOSE_OPTIONS: List[str] = field(default_factory=lambda: [
        "Investment", "Personal Use", "Rental Income", "Business", "Other"
    ])

    PAYMENT_METHOD_OPTIONS: List[str] = field(default_factory=lambda: [
        "Bank Transfer", "Cheque", "Cash", "Credit Card"
    ])

    # Declaration Text
    DECLARATION_TEXT: str = (
        "I Hereby confirm that the above information provided is true and authentic "
        "on the date of this declaration. I shall notify Vihaan Real Estate in case "
        "of any changes in the above mentioned information."
    )

    # Required CSV Headers
    KYC_CSV_HEADERS: List[str] = field(default_factory=lambda: [
        'kyc_id', 'customer_id', 'submission_date', 'status',
        # Customer
        'residential_status', 'full_name', 
        'residential_address_line1', 'residential_address_line2',
        'home_address_line1', 'home_address_line2',
        'contact_landline', 'contact_office', 'contact_mobile',
        # Customer Information
        'gender', 'nationality', 'date_of_birth', 'place_of_birth',
        'passport_number', 'passport_issue_place', 'passport_issue_date', 'passport_expiry_date',
        'dual_nationality', 'dual_passport_number', 'dual_passport_issue_date', 'dual_passport_expiry_date',
        'emirates_id', 'emirates_id_expiry', 'visa_uid', 'visa_expiry',
        # Customer Occupation
        'occupation', 'sponsor_business_name', 'sponsor_business_address',
        'sponsor_business_landline', 'sponsor_business_mobile',
        # Customer Profile and Payment
        'annual_income', 'investment_purpose', 'source_of_funds', 'payment_method'
    ])

    def __post_init__(self):
        """Validate paths after initialization"""
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)

        if not os.path.exists(self.KYC_DATA_FILE):
            raise FileNotFoundError(
                f"KYC data file not found at {self.KYC_DATA_FILE}. "
                "Please ensure the required data file exists with proper headers."
            )