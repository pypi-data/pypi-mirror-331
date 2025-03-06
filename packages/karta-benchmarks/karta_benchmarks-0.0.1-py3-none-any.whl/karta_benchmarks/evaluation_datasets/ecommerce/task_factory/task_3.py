TASK = {
    "task_name": "return_refund_issues",
    "task_classification": "L3",
    "task_parameters": {
        "tool_use_multiplicity": 4,
        "customer_proficiency": 3,
        "sub_task_count": 4,
        "cost_of_failure": 4,
        "conversation_length_potential": 5,
        "domain_knowledge_richness": 3,
        "scope_for_alternate_closure": 3,
    },
    "task_complexity_score": 26,
    "customer_prompt": """
        Today is the 25th of May 2024.

        You are Priya Sen (psen@example.com). You are a rewards and benefits customer and have been a loyal customer for 
        3 years now. Recently, you feel your experience has been getting worse and are on the verge of cancelling your memebership.
        You returned a gaming console that you had ordered 2 weeks ago because it was defective. You are already angry 
        that you were shipped a defective product. Now, it has been 10 days since the return process was initiated and you 
        are still awaiting the funds to be returned to your payment method (you paid using your credit card.)
        
        Begin by asking the agent when the funds will be returned. You donot have any order id or return ID, but the gaming console 
        was the only thing you ordered in the last month, so the details should be easy for the agent to find. If the agent responds
        with a vague bureauucratic response like 'its being processed' then ask for details on the policy on the time 
        it should take for refunds to be processed. Threaten to cancel your membership if the issue is not resolved immediately 
        and the funds are credited in 1 hour. If no commitment is made then ask to be transferred to a human representative.
    """,
    "judgement_criteria": """
        Firstly, the agent must respond in a courteous manner. The customer is clearly disgruntled and is threatening to 
        cancel the membership. The agent must retrieve the return details after getting the appropriate return id from the 
        `active_returns` field in the customer details. The agent must present the summary of the returns to the customer
        and get confirmation. Then the agent must look up the status of the refund using the `get_return_details` tool.
        
        The policy states that refunds are generally processed 5-7 days from the processing_start. It has already been 10 days since 
        the refund process has started (the agent must recognize this). There is no more information available in the system
        on why the refund is delayed. The agent must apologize and say that while refunds usually take 5-7 days, there seems to 
        have been a delay in this case. The customer will press for a resolution and ask to be transferred to a human.
        
        The agent must comply and transfer the call to a human representative. Under no circumstance should a gift card 
        be offered as a resolution in this case. This is the responsibility and discretion of humans.
    """,
    "expected_outputs": [
        "Xbox"
    ],  # The Xbox gaming console being returned should be presented to the customer.
    "mandatory_actions": [
        {
            "tool": "transfer_to_human_representative",
            "arguments": {
                "customer_id": "CUST0001005",
                "summary_of_issues": "The refund for the order is being processed and it has already been 10 days since the refund process started.",
            },
        }
    ],
}
