TASK = {
    "task_name": "failed_payment_enquiry",
    "task_classification": "L1",
    "task_parameters": {
        "tool_use_multiplicity": 2,
        "customer_proficiency": 2,
        "sub_task_count": 2,
        "cost_of_failure": 1,
        "conversation_length_potential": 1,
        "domain_knowledge_richness": 1,
        "scope_for_alternate_closure": 1,
    },
    "task_complexity_score": 10,
    "customer_prompt": """Today is the 25th of May 2024. 

            You are Riddhima (riddhi@example.com). You have placed two orders yesterday. 
            One of the orders has an expensive Lenovo laptop. You paid for the order using your credit card, but the order has not
            been confirmed as yet. You know this because you usually receive a confirmation mail. The amount has been debited from your account.
            You are now very concerned and want to know what is happening.

            Start by sounding concerned and ask the agent to check the status of your order. Since you have multiple orders open, the agent will have to show you your
            order details and you will have to choose. Wait for him to do this. After picking the order which has the laptop, the agent will proceed to help you.

            If the agent is not able to resolve the issue immediately and asks you to wait till the payment is reversed, you should get frustrated and tell it that 
            this is the fourth time this has happened and you want to talk to a human. Donot stop conversing till you are transferred to a human. Remember you are 
            a benefits and rewards member and you should not have such a poor experience.

            If the payment is immediately reversed, you should be happy and say thank you.
            """,
    "judgement_criteria": """The agent must first retrieve the customer details using the customer email.
                    Then, it must retrieve the active orders for the customer.
                    Then, since there are multiple orders for the customer, the must summarize the order details and present them to the customer.
                    After the customer identifies the order id, the agent must retrieve the order details and get the payment status.
                    The payment status is failed. So, the agent must inform the customer that the payment has failed and ask the customer should try paying again.
                    It should also re-assure the customer that the amount that has already been debited will be refunded in 24 hrs.
                    Since the customer will be insistent still, the agent must transfer the call to a human representative.
                    """,
    "expected_outputs": ["ORD202405231"],
    "mandatory_actions": [
        {
            "tool": "transfer_to_human_representative",
            "arguments": {
                "customer_id": "CUST001004",
                "summary_of_issues": "The payment has failed. The amount that has already been debited will be refunded in 24 hrs.",
            },
        }
    ],
}
