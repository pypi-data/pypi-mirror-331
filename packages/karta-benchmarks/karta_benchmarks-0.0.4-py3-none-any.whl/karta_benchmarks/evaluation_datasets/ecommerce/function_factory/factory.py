# Copyright 2025 Karta

import os
import json
from karta_benchmarks.evaluation_datasets.ecommerce.data_factory.factory import (
    factory as data_factory,
)
from typing import Dict, Any, List
from datetime import datetime
import copy
from karta_benchmarks.general_helpers.get_frame_info import get_frame_info
from karta_benchmarks.evaluation_datasets.ecommerce.schemas.schemas import SCHEMAS
import inspect


def factory() -> Dict[str, Any]:
    """
    This is the tool factory that generates a set of tools (callables) that will operate
    on a fresh instance of the data. Each tool comes with a docstring which can be used when
    binding to the agent.

    Returns:
        Dict[str, Any]: A dictionary that contains:
            - tool_mapping: A mapping between the tool name and the tool callable
            - read_tools: All the read tools
            - update_tools: All the update tools
    """
    data = data_factory()

    def transfer_to_human_representative(
        customer_id: str, summary_of_issues: str
    ) -> str:
        """
        Transfer the call to a human representative.

        Args:
            customer_id (str): The ID of the customer
            summary_of_issues (str): A string containing the summary of the issues

        Returns:
            str: A success message if the call is transferred successfully, otherwise an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        DATA["contacts"]["CNTCT000001"] = {
            "customer_id": customer_id,
            "contact_source": "CHATBOT",
            "summary": "summary",
        }
        return f"<success> Transferred the call to a human representative </success>"

    # Creating a copy of the data
    DATA = copy.deepcopy(data)

    # An empty call history
    CALL_HISTORY = []

    def vend_schemas() -> Dict[str, Any]:
        """
        Vend the schemas of the different datasets in the domain
        """
        return SCHEMAS

    def get_db_state() -> dict:
        """
        Get the current state of the database.

        Returns:
            dict: The current state of the database.
        """
        return DATA

    def get_current_date_and_time() -> str:
        """
        Get the current date and time. IMPORTANT: This is set to "2024-05-25 10:00:00" for all runs.

        Returns:
            str: The current date and time. This is set to "2024-05-25 10:00:00" for all runs.
        """
        return "2024-05-25 10:00:00"

    def get_package_details(package_id: str) -> Dict[str, Any]:
        """
        Get the details of a package by its associated package id.

        Args:
            package_id (str): The ID of the package.

        Returns:
            Dict[str, Any]: A dictionary containing the package details.
            The package details contains the package_id, destination_address,
            shipper_name, estimated_delivery_date, shipment_cost, origin_code, current_status, tracking_details.
            If the package_id is not found, an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        if package_id not in DATA["packages"]:
            return f"<error> Package with ID {package_id} not found </error>"
        return DATA["packages"][package_id]

    def get_call_history() -> List:
        """
        Get the call history after the latest reset.

        Returns:
            List: The call history.
        """
        return CALL_HISTORY

    def reset_call_history() -> None:
        """
        Reset the call history.
        """
        CALL_HISTORY.clear()

    def calculate_date_difference(date1: str, date2: str) -> int:
        """
        Calculate the difference in days between two dates which are specified as strings in the format YYYY-MM-DD.

        Args:
            date1 (str): The first date in YYYY-MM-DD format.
            date2 (str): The second date in YYYY-MM-DD format.

        Returns:
            int: The difference in days between the two dates in days.
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")
        return (date2 - date1).days

    def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
        """
        Gets Basic Customer Information by the ID of the customer

        Args:
            customer_id (str): The ID of the customer

        Returns:
            Dict[str, Any]: A dictionary containing the customer information.
            The customer information contains the customer_id, first_name, date of birth,
            gender, account_creation_date, last_order_date, is_active, is_email_verified,
            is_phone_verified, is_fraud_flag, is_rewards_and_benfits_member, active_orders,
            active_returns.
            If the customer_id is not found, an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        if customer_id not in DATA["customers"]:
            raise f"<error> Customer with ID {customer_id} not found </error>"
        return DATA["customers"][customer_id]

    def get_customer_by_email(email: str) -> Dict[str, Any]:
        """
        Gets Basic Customer Information by the email of the customer

        Args:
            email (str): The email of the customer

        Returns:
            Dict[str, Any]: A dictionary containing the customer information.
            The customer information contains the customer_id, first_name, date of birth,
            gender, account_creation_date, last_order_date, is_active, is_email_verified,
            is_phone_verified, is_fraud_flag, is_rewards_and_benfits_member, active_orders,
            active_returns.
            If the customer with the given email is not found, an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        for customer_id, customer_info in DATA["customers"].items():
            if customer_info["email"] == email:
                return customer_info
        return f"<error> Customer with email {email} not found </error>"

    def issue_gift_card(customer_id: str, amount: float) -> str:
        """
        Issue a gift card to a customer.

        Args:
            customer_id (str): The ID of the customer
            amount (float): The amount of the gift card

        Returns:
            str: A success message if the gift card is issued successfully,
            otherwise an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        # Check if the customer exists
        if customer_id not in DATA["customers"]:
            return f"<error> Customer with ID {customer_id} not found </error>"

        # Check if the amount is positive
        if amount <= 0:
            return f"<error> Amount must be positive </error>"

        # We use a constant gift card id always
        id = "GFT000001"

        # Create a new gift card entry in the payment_methods table
        DATA["payment_methods"][id] = {
            "issued_at": get_current_date_and_time(),
            "customer_id": customer_id,
            "payment_method_type": "GIFT_CARD",
            "amount_remaining": amount,
        }

        return f"<success> Gift card {id} issued to customer with ID {customer_id} with amount {amount} </success>"

    def get_item_details(item_id: str) -> Dict[str, Any]:
        """
        Get the details of an item by its associated item id.

        Args:
            item_id (str): The ID of the item

        Returns:
            Dict[str, Any]: A dictionary containing the item details.
            The item details contains the item_id, item_name, item_description,
            item_weight, item_cost, item_category. The return eligibility of
            each item is also provided.
            If the item_id is not found, an error message is returned
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        if item_id not in DATA["items"]:
            return f"<error> Item with ID {item_id} not found </error>"
        return DATA["items"][item_id]

    def get_order_details(order_id: str) -> Dict[str, Any]:
        """
        Get the details of an order by its associated order id.

        Args:
            order_id (str): The ID of the order

        Returns:
            Dict[str, Any]: A dictionary containing the order details.
            If the order_id is not found, an error message is returned.
            The order details contains the order_date, customer_id, payment_status, shipping_address,
            items_ordered, payment_method.
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        if order_id not in DATA["orders"]:
            return f"<error> Order with ID {order_id} not found </error>"
        return DATA["orders"][order_id]

    def summarize_returns(return_ids: List[str]) -> Dict[str, Any]:
        """
        Summarizes the details of multiple returns.

        Args:
            return_ids (List[str]): The IDs of the returns to summarize

        Returns:
            Dict[str, Any]: A dictionary containing the summarized return details.
            The summarized return details contains the return_id as the key and for each return_id, the return_date,
            return_reason, return_status, and a list of items returned.
            If a return_id is not found, the value of the return_id key is the error message.
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        summarized_returns = {}
        for return_id in return_ids:
            return_details = get_return_details(return_id)
            if "<error>" in return_details:
                summarized_returns[return_id] = return_details
                continue
            append_dict = {}
            append_dict["order_id"] = return_details["order_id"]
            append_dict["return_reason"] = return_details["return_reason"]
            append_dict["items_returned"] = []
            for item in return_details["items_returned"]:
                item_id = item["item_number"]
                description = get_item_details(item_id)["item_description"]
                quantity = item["qty"]
                refundable_amount = item["refundable_amount"]
                append_dict["items_returned"].append(
                    {
                        "item_id": item_id,
                        "description": description,
                        "quantity": quantity,
                        "refundable_amount": refundable_amount,
                    }
                )
            summarized_returns[return_id] = append_dict
        return summarized_returns

    def summarize_orders(order_ids: List[str]) -> Dict[str, Any]:
        """
        Summarize the details of multiple orders.

        Args:
            order_ids (List[str]): The IDs of the orders to summarize

        Returns:
            Dict[str, Any]: A dictionary containing the summarized order details.
            The summarized order details contains the order_id as the key and for each order_id, the order_date,
            and items_ordered (containing the item_id, description, quantity and current shipment status of each item).
            If an order_id is not found, the value of the order_id key is the error message.
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        summarized_orders = {}
        for order_id in order_ids:
            order_details = get_order_details(order_id)
            if "<error>" in order_details:
                summarized_orders[order_id] = order_details
                continue
            # Get all the items in the order
            append_dict = {}
            append_dict["order_date"] = order_details["order_date"]
            append_dict["items_ordered"] = []
            for item in order_details["items_ordered"]:
                item_id = item["item_number"]
                description = get_item_details(item_id)["item_description"]
                quantity = item["qty"]
                package_id = item["package_id"]
                if package_id != "":
                    package_details = get_package_details(package_id)
                    package_status = package_details["current_status"]
                else:
                    package_status = "NOT_YET_SHIPPED"
                append_dict["items_ordered"].append(
                    {
                        "item_id": item_id,
                        "description": description,
                        "quantity": quantity,
                        "current_shipment_status": package_status,
                    }
                )
            summarized_orders[order_id] = append_dict
        return summarized_orders

    def get_return_details(return_id: str) -> Dict[str, Any]:
        """
        Get the details of a return by its associated return id.

        Args:
            return_id (str): The ID of the return

        Returns:
            Dict[str, Any]: A dictionary containing the return details.
            The return details contains the return_id, order_id, customer_id, return_reason, return_status,
            items_returned, event_history and refund_details which further contain more details regarding the
            refund.
            If the return_id is not found, an error message is returned.
        """
        CALL_HISTORY.append(get_frame_info(inspect.currentframe()))
        if return_id not in DATA["returns"]:
            return f"<error> Return with ID {return_id} not found </error>"
        return DATA["returns"][return_id]

    return {
        "tool_mapping": {
            "get_db_state": get_db_state,
            "get_call_history": get_call_history,
            "reset_call_history": reset_call_history,
            "calculate_date_difference": calculate_date_difference,
            "get_customer_by_id": get_customer_by_id,
            "get_customer_by_email": get_customer_by_email,
            "vend_schemas": vend_schemas,
            "get_current_date_and_time": get_current_date_and_time,
            "get_package_details": get_package_details,
            "issue_gift_card": issue_gift_card,
            "get_item_details": get_item_details,
            "get_order_details": get_order_details,
            "summarize_orders": summarize_orders,
            "transfer_to_human_representative": transfer_to_human_representative,
            "summarize_returns": summarize_returns,
            "get_return_details": get_return_details,
        },
        "read_tools": [
            calculate_date_difference,
            get_customer_by_id,
            get_customer_by_email,
            get_current_date_and_time,
            get_package_details,
            get_item_details,
            get_order_details,
            summarize_orders,
            transfer_to_human_representative,
            get_return_details,
            summarize_returns,
        ],
        "update_tools": [issue_gift_card, transfer_to_human_representative],
    }
