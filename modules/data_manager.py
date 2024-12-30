# data_manager.py

import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import os

class DataManager:
    def __init__(self):
        self.csv_file = 'data/cust_file.csv'
        self.ensure_data_file()


    def ensure_data_file(self):
        """Create data file if it doesn't exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
        
        if not os.path.exists(self.csv_file):
            columns = [
                'cust_unique_id', 'cust_tax_id', 'cust_fname', 'cust_lname',
                'cust_email', 'transaction_id', 'transaction_date',
                'billed_amount', 'currency', 'payment_due_date', 'payment_status'
            ]
            pd.DataFrame(columns=columns).to_csv(self.csv_file, index=False)


    def get_customer(self, customer_id: str, workflow_state_class) -> Optional['workflow_state_class']:
        """
        Retrieve customer information by customer ID
        Returns WorkflowState if found, None if not found
        """
        try:
            df = pd.read_csv(self.csv_file)
            customer_data = df[df['cust_unique_id'] == customer_id]
        
            if customer_data.empty:
                return None
        
            # Get the most recent record for the customer
            latest_record = customer_data.iloc[-1]
        
            # Create WorkflowState with the found data
            return workflow_state_class(
                customer={
                    'cust_unique_id': latest_record['cust_unique_id'],
                    'cust_tax_id': latest_record['cust_tax_id'],
                    'cust_fname': latest_record['cust_fname'],
                    'cust_lname': latest_record['cust_lname'],
                    'cust_email': latest_record['cust_email']
                },
                invoice={
                    'transaction_id': latest_record['transaction_id'],
                    'transaction_date': latest_record['transaction_date'],
                    'billed_amount': latest_record['billed_amount'],
                    'currency': latest_record['currency'],
                    'payment_due_date': latest_record['payment_due_date'],
                    'payment_status': latest_record['payment_status']
                }
            )
        except Exception as e:
            raise Exception(f"Error retrieving customer data: {str(e)}")

    def save_record(self, workflow_state_dict):
        """Save new record to CSV"""
        df = pd.read_csv(self.csv_file)
        
        record = {
            'cust_unique_id': workflow_state_dict['customer']['cust_unique_id'],
            'cust_tax_id': workflow_state_dict['customer']['cust_tax_id'],
            'cust_fname': workflow_state_dict['customer']['cust_fname'],
            'cust_lname': workflow_state_dict['customer']['cust_lname'],
            'cust_email': workflow_state_dict['customer']['cust_email'],
            'transaction_id': workflow_state_dict['invoice']['transaction_id'],
            'transaction_date': workflow_state_dict['invoice']['transaction_date'],
            'billed_amount': workflow_state_dict['invoice']['billed_amount'],
            'currency': workflow_state_dict['invoice']['currency'],
            'payment_due_date': workflow_state_dict['invoice']['payment_due_date'],
            'payment_status': workflow_state_dict['invoice']['payment_status']
        }
        

        # Add new record using loc
        df.loc[len(df)] = record
        print("*****\n\nDebugging point : df.head() : ", df.head(5))

        df.to_csv(self.csv_file, index=False)

        # Return updated WorkflowState
        return workflow_state_class(
            customer={
                'cust_unique_id': record['cust_unique_id'],
                'cust_tax_id': record['cust_tax_id'],
                'cust_fname': record['cust_fname'],
                'cust_lname': record['cust_lname'],
                'cust_email': record['cust_email']
            },
            invoice={
                'transaction_id': record['transaction_id'],
                'transaction_date': record['transaction_date'],
                'billed_amount': record['billed_amount'],
                'currency': record['currency'],
                'payment_due_date': record['payment_due_date'],
                'payment_status': record['payment_status']
            },
            completed=True
        )
    


    def check_duplicate(self, cust_unique_id):
        """Check for duplicate customer ID"""
        df = pd.read_csv(self.csv_file)
        return cust_unique_id in df['cust_unique_id'].values


    def get_all_records(self):
        """Retrieve all records"""
        return pd.read_csv(self.csv_file)


    def update_payment_status(self, transaction_id, status):
        """Update payment status"""
        df = pd.read_csv(self.csv_file)
        df.loc[df['transaction_id'] == transaction_id, 'payment_status'] = status
        df.to_csv(self.csv_file, index=False)