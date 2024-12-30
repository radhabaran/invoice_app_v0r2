# app.py

import streamlit as st
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
from modules.data_manager import DataManager
from modules.invoice_gen import InvoiceGenerator
from modules.email_handler import EmailHandler
from modules.workflow import WorkflowManager
from modules.validator import DataValidator

class WorkflowState(BaseModel):
    customer: Dict[str, Any]
    invoice: Dict[str, Any]
    validation_status: Optional[Dict[str, Any]] = None
    invoice_creation_status: Optional[Dict[str, Any]] = None
    email_notification_status: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed: bool = False


class InvoiceApp:
    def __init__(self):
        if not hasattr(st.session_state, 'workflow_manager'):
            st.session_state.workflow_manager = self.init_systems()
        
        if not hasattr(st.session_state, 'state'):
            st.session_state.state = WorkflowState(
                customer={
                    'cust_unique_id': '',
                    'cust_tax_id': '',
                    'cust_fname': '',
                    'cust_lname': '',
                    'cust_email': ''
                },
                invoice={
                    'transaction_id': '',
                    'transaction_date': '',
                    'billed_amount': 0.0,
                    'currency': 'USD',
                    'payment_due_date': '',
                    'payment_status': 'pending'
                }
            )
        
        self.workflow_manager = st.session_state.workflow_manager
        self.validator = DataValidator()
        self.state = st.session_state.state


    @staticmethod
    def init_systems():
        try:
            data_manager = DataManager()
            invoice_generator = InvoiceGenerator()
            email_handler = EmailHandler()
            return WorkflowManager(data_manager, invoice_generator, email_handler, WorkflowState)
        except Exception as e:
            st.error(f"System initialization failed: {str(e)}")
            return None


    def update_state(self, customer_id: str, tax_id: str, first_name: str, 
                    last_name: str, email: str, amount: float, currency: str, payment_status: str):
        """Update state with new data"""
        now = datetime.now()
        transaction_id = str(uuid.uuid4())
        
        self.state.customer.update({
            'cust_unique_id': customer_id,
            'cust_tax_id': tax_id,
            'cust_fname': first_name,
            'cust_lname': last_name,
            'cust_email': email
        })
        
        self.state.invoice.update({
            'transaction_id': transaction_id,
            'transaction_date': now.strftime('%Y-%m-%d'),
            'billed_amount': amount,
            'currency': currency,
            'payment_due_date': (now + timedelta(days=30)).strftime('%Y-%m-%d'),
            'payment_status': payment_status.lower()
        })


    def search_customer(self, customer_id: str):
        """Search customer and update state"""
        try:
            result = self.workflow_manager.data_manager.get_customer(customer_id, WorkflowState)
            
            if result:
                self.state.customer.update(result.customer)
                self.state.invoice.update(result.invoice)
            
                return True
            
            st.warning("Customer not found")
            return False
        
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return False


    def handle_submit(self, customer_id: str, tax_id: str, first_name: str, 
                     last_name: str, email: str, amount: float, currency: str, payment_status: str):
        """Handle form submission"""
        try:
            self.update_state(
                customer_id, tax_id, first_name, last_name, email, amount, currency, payment_status
            )
            
            validation_result = self.validator.validate_workflow_state(self.state.dict())
            if validation_result is not None:  # If there are validation errors
                st.error(f"Validation failed: {validation_result}")
                return

            # Save to CSV immediately after validation
            updated_state = self.workflow_manager.data_manager.save_record(self.state.dict())

            if updated_state:
                self.state.customer.update(updated_state.customer)
                self.state.invoice.update(updated_state.invoice)
                self.state.completed = updated_state.completed
                st.success("Record saved successfully")
                print("*****\n\n Debugging point in handle_submit: cust_unique_id : ", self.state.customer['cust_unique_id'])
            else:
                st.error("Failed to save record")
                return

        except Exception as e:
            st.error(f"Submission failed: {str(e)}")


    def handle_generate_invoice(self):
        """Handle invoice generation"""
        print("\n\nDebug - Customer ID at start of generate:", self.state.customer['cust_unique_id'])

        if self.state.customer['cust_unique_id'] == '':
            st.error("Please submit record first")
            return

        result = self.workflow_manager.run_workflow(self.state)
        print("\n\nDebug - Workflow result:", result.dict() if result else "No result")
        if result.error:
            st.error(result.error)
        else:
            self.state = result
            st.success(f"Invoice generated and sent to {result.customer['cust_email']}")


    def reset_state(self):
        """Reset the state"""
        new_state = WorkflowState(
            customer={
                'cust_unique_id': '',
                'cust_tax_id': '',
                'cust_fname': '',
                'cust_lname': '',
                'cust_email': ''
            },
            invoice={
                'transaction_id': '',
                'transaction_date': '',
                'billed_amount': 0.0,
                'currency': 'USD',
                'payment_due_date': '',
                'payment_status': 'pending'
            }
        )

        # Reset both instance state and session state
        self.state = new_state
        st.session_state.state = new_state

        # Clear the customer_id input value from session state
        if 'customer_id' in st.session_state:
            del st.session_state['customer_id']

        st.rerun()


    def render_main_page(self):
        """Render the main UI"""
        st.title("Invoice Management System")

        # Main container with custom width
        with st.container():
            # Customer ID row
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                customer_id = st.text_input("Customer ID*", 
                    value=self.state.customer['cust_unique_id'],
                    placeholder="Enter unique ID",
                    key='customer_id'
                )

            # Search button in its own row
            with col2:
                # Add some vertical spacing to align with the input field
                st.write("")  # This creates a small vertical gap
                if st.button("Search", type="primary", key="search_button",
                            help="Search for customer records",
                            use_container_width=True):
                    if customer_id:
                        self.search_customer(customer_id)

            # Tax ID and Email row with increased width
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                tax_id = st.text_input("Tax ID*", 
                    value=self.state.customer['cust_tax_id'],
                    placeholder="Enter tax ID")
            with col2:
                email = st.text_input("Email*", 
                    value=self.state.customer['cust_email'],
                    placeholder="Email address")

            # First name and Last name row
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                first_name = st.text_input("First Name", 
                    value=self.state.customer['cust_fname'],
                    placeholder="First name")
            with col2:
                last_name = st.text_input("Last Name", 
                    value=self.state.customer['cust_lname'],
                    placeholder="Last name")

            # Amount, Currency, Payment Due Date row
            col1, col2, col3, col4 = st.columns([0.3, 0.2, 0.25, 0.25])
            with col1:
                amount = st.text_input("Amount*", 
                    value=self.state.invoice['billed_amount'] if self.state.invoice['billed_amount'] > 0 else '',
                    placeholder="Enter amount")
            with col2:
                currency = st.selectbox("Currency", 
                    ["USD", "EUR", "GBP", "JPY"],
                    index=["USD", "EUR", "GBP", "JPY"].index(self.state.invoice['currency']))
            with col3:
                due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                st.text_input("Payment Due Date", value=due_date, disabled=True)
            with col4:
                payment_status = st.selectbox("Payment Status",
                    ["Pending", "Paid", "Overdue", "Cancelled"],
                    index=["pending", "paid", "overdue", "cancelled"].index(
                        self.state.invoice['payment_status'].lower()))

            # Action buttons with right alignment and blue background
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
            with col1:
                if st.button("Submit New Record", 
                        type="primary",
                        use_container_width=True,
                        key="submit_button"):
                    try:
                        self.handle_submit(customer_id, tax_id, first_name, last_name, 
                                     email, float(amount), currency, payment_status)
                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")
        
            with col2:
                if st.button("Generate & Send Invoice",
                        type="primary",
                        use_container_width=True,
                        key="generate_button"):
                    
                    print("\n\nDebug in Generate & Send Invoice - State before generate invoice:", self.state.dict())
                    self.handle_generate_invoice()
            
            with col3:
                if st.button("🔄 Reset",
                        type="primary",
                        use_container_width=True,
                        key="reset_button"):
                        self.reset_state()

            # Current Record Display
            if self.state.customer['cust_unique_id']:
                st.markdown("---")
                st.subheader("Current Record")
                with st.container(border=True):
                    st.write(f"ID: {self.state.customer['cust_unique_id']}")
                    st.write(f"Name: {self.state.customer['cust_fname']} {self.state.customer['cust_lname']}")
                    st.write(f"Amount: ${self.state.invoice['billed_amount']} {self.state.invoice['currency']}")
                    status_color = "red" if payment_status.lower() == "pending" else "green"
                    st.markdown(f"Payment Status: <span style='color: {status_color}'>{payment_status}</span>", unsafe_allow_html=True)

                if self.state.completed:
                    with st.container():
                        st.write("✓ Record saved")
                        if self.state.email_notification_status:
                            st.write(f"✓ Invoice sent to {self.state.customer['cust_email']}")
    def main(self):
        self.render_main_page()


def main():
    
    app = InvoiceApp()
    app.main()

if __name__ == "__main__":
    main()