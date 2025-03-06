TASK = {
    "task_name": "delayed_headphones_delivery",
    "task_classification": "L2",
    "task_parameters": {
        "tool_use_multiplicity": 3,
        "customer_proficiency": 2,
        "sub_task_count": 4,
        "cost_of_failure": 2,
        "conversation_length_potential": 4,
        "domain_knowledge_richness": 3,
        "scope_for_alternate_closure": 3,
    },
    "judgement_criteria": """The agent must first retrieve the customer details using the customer email.
                    Then, it must retrieve the item details using the item id.
                    Then, it must retrieve the package details using the package id.
                    Then having determined that the package is delayed, it must issue a gift card to the customer after apologizing for the delay.
                    """,
    "task_complexity_score": 21,
    "customer_prompt": """Today is the 25th of May 2024. 
                    You are Rahul Gupta (rahul_gupta@example.com). 
                    You placed an order for a pair of wireless headphones five days ago. 
                    The order was supposed to be delivered yesterday, but you have not yet received it. The tracking status still shows ‘In Transit.’ 
                    You donot have an order id.
                    Initially, you are slightly concerned but remain polite. 
                    You start by simply asking when your order will be delivered. 
                    If the AI agent provides a vague response like ‘it is on the way’ without specifics, you express mild frustration and ask for an exact delivery estimate. 
                    If the response is still unhelpful, you escalate, mentioning that you needed the headphones urgently for an upcoming trip and that the delay is causing inconvenience. 
                    Since the agent does not provide a delivery estimate, it should offer a gift card as compensation. 
                    If you accept the offer, the issue is resolved. Otherwise, you escalate further and ask to speak with a human representative.
                    """,
    "expected_outputs": ["Sound Blaster", "GFT000001"],
    "mandatory_actions": [
        {
            "tool": "issue_gift_card",
            "arguments": {"customer_id": "CUST001001", "amount": 120},
        }
    ],
}
