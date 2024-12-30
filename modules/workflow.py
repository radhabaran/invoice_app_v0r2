# workflow.py

from langgraph.graph import StateGraph
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any

class WorkflowManager:
    def __init__(self, data_manager, invoice_generator, email_handler, workflow_state_class):
        self.data_manager = data_manager
        self.invoice_generator = invoice_generator
        self.email_handler = email_handler
        self.graph = self.setup_workflow(workflow_state_class)

    def setup_workflow(self, workflow_state_class):
        """Setup LangGraph workflow"""
        workflow = StateGraph(state_schema=workflow_state_class)
        
        workflow.add_node("validate", self.validate_step)
        workflow.add_node("generate_invoice", self.generate_invoice_step)
        workflow.add_node("send_notification", self.send_notification_step)
        
        return workflow

    def validate_step(self, workflow_state):
        """Validation step"""

        if not workflow_state.customer['cust_unique_id']:
            workflow_state.error = "Customer ID is required"
            return workflow_state

        if self.data_manager.check_duplicate(workflow_state.customer['cust_unique_id']):
            workflow_state.error = "Duplicate customer ID"
            return workflow_state

        workflow_state.validation_status = {
            "is_valid": True,
            "validated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return workflow_state

    def generate_invoice_step(self, workflow_state):
        """Invoice generation step"""
        try:
            invoice_path = self.invoice_generator.generate_invoice(workflow_state.dict())
            
            workflow_state.invoice_creation_status = {
                "is_generated": True,
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "file_path": invoice_path
            }
            workflow_state.error = None
        except Exception as e:
            workflow_state.error = f"Invoice generation failed: {str(e)}"
            
        return workflow_state

    def send_notification_step(self, workflow_state):
        """Email notification step"""
        try:
            email_sent = self.email_handler.send_invoice(
                workflow_state.customer['cust_email'],
                workflow_state.dict(),
                workflow_state.invoice_creation_status['file_path']
            )
            
            workflow_state.email_notification_status = {
                "is_sent": email_sent,
                "sent_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "recipient": workflow_state.customer['cust_email']
            }
            print("*********\n\nDebugging : email_notification_status : ", workflow_state.email_notification_status)
        except Exception as e:
            workflow_state.error = f"Email notification failed: {str(e)}"
            
        return workflow_state

    def run_workflow(self, workflow_state):
        """Execute complete workflow"""
        try:
            # Run validation
            workflow_state = self.validate_step(workflow_state)
            if workflow_state.error and workflow_state.error != "Duplicate customer ID":
                return workflow_state

            # Generate invoice
            workflow_state = self.generate_invoice_step(workflow_state)
            if workflow_state.error:
                return workflow_state

            # Send notification
            workflow_state = self.send_notification_step(workflow_state)
            if workflow_state.error:
                return workflow_state

            # Save to database only if it's not a duplicate record
            # if not workflow_state.error:
            #     self.data_manager.save_record(workflow_state.dict())
            
            workflow_state.completed = True
            return workflow_state

        except Exception as e:
            workflow_state.error = f"Workflow execution failed: {str(e)}"
            return workflow_state