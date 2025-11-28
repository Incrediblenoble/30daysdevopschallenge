
"""
This script implements a 5-step prompt chain for an intelligent customer support system for a bank.
The chain processes a customer's free-text query to understand their intent, categorize the query,
extract relevant details, and generate an appropriate response.
"""
import re

def run_prompt_chain(query: str) -> list:
    """
    Processes a customer's query through a 5-step prompt chain.

    Each step simulates the output of a language model prompt, building a logical reasoning chain
    from understanding to classification to response.

    Args:
        query: The customer's free-text query.

    Returns:
        A list of five intermediate outputs, one from each stage of the chain.
    """
    outputs = []
    available_categories = [
        "Account Opening", "Billing Issue", "Account Access", "Transaction Inquiry",
        "Card Services", "Account Statement", "Loan Inquiry", "General Information"
    ]

    # --- Step 1: Interpret the customer’s intent ---
    # This prompt is designed to understand the fundamental goal of the customer's query.
    # It helps translate the unstructured text into a clear statement of intent.
    intent_prompt = f"Interpret the customer's intent based on the following query: '{query}'"
    # Simulated LLM response for intent
    intent = f"The customer is asking about: {query}"
    outputs.append(intent)

    # --- Step 2: Map the query to possible categories ---
    # This prompt suggests potential categories based on the interpreted intent.
    # It narrows down the possibilities from a broad list of available services.
    category_mapping_prompt = f"Based on the intent '{intent}', map the query to one or more of the following categories: {', '.join(available_categories)}"
    # Simulated LLM response for mapping using keyword matching
    possible_categories = []
    if any(keyword in query.lower() for keyword in ["open account", "new savings"]):
        possible_categories.append("Account Opening")
    if any(keyword in query.lower() for keyword in ["bill", "charge", "fee"]):
        possible_categories.append("Billing Issue")
    if any(keyword in query.lower() for keyword in ["login", "password", "access"]):
        possible_categories.append("Account Access")
    if any(keyword in query.lower() for keyword in ["transaction", "purchase"]):
        possible_categories.append("Transaction Inquiry")
    if any(keyword in query.lower() for keyword in ["card", "debit", "credit"]):
        possible_categories.append("Card Services")
    if "statement" in query.lower():
        possible_categories.append("Account Statement")
    if "loan" in query.lower():
        possible_categories.append("Loan Inquiry")
    if not possible_categories or "information" in query.lower():
        possible_categories.append("General Information")
    outputs.append(possible_categories)

    # --- Step 3: Choose the most appropriate category ---
    # This prompt makes a final decision on the best category for the query.
    # It ensures the query is routed to the correct workflow.
    category_choice_prompt = f"From the possible categories {possible_categories}, choose the single most appropriate one for the query: '{query}'"
    # Simulated LLM response for choice (simplified to picking the first match)
    chosen_category = possible_categories[0]
    outputs.append(chosen_category)

    # --- Step 4: Extract additional details ---
    # This prompt identifies specific pieces of information needed to resolve the query.
    # Details like dates, amounts, or specific product names are extracted.
    details_extraction_prompt = f"For a query in the '{chosen_category}' category, extract additional details like transaction dates, amounts, or card types from: '{query}'"
    # Simulated LLM response for extraction using regex
    additional_details = {}
    amounts = re.findall(r'\$\d+\.?\d*', query)
    if amounts:
        additional_details["amount"] = amounts[0]
    dates = re.findall(r'\d{2}/\d{2}/\d{4}|\w+ \d{1,2}, \d{4}|yesterday|today', query)
    if dates:
        additional_details["date"] = dates[0]
    card_types = re.findall(r'credit|debit', query)
    if card_types:
        additional_details["card_type"] = card_types[0]
    if not additional_details:
        additional_details["status"] = "No specific details found. More information may be required."
    outputs.append(additional_details)

    # --- Step 5: Generate a short response ---
    # This final prompt creates a customer-facing response based on the chosen category and extracted details.
    # The goal is to provide a helpful and context-aware reply.
    response_generation_prompt = f"Generate a short, helpful response for a customer with a query in the '{chosen_category}' category, considering these details: {additional_details}"
    # Simulated LLM response for generation using a predefined map
    response_map = {
        "Account Opening": "I can certainly help you with opening a new account. Are you an existing customer?",
        "Billing Issue": "I see you have a question about a bill. To clarify, could you please provide the date of the charge?",
        "Account Access": "I understand you're having trouble accessing your account. I'll need to verify your identity to proceed.",
        "Transaction Inquiry": "I can look into that transaction for you. Could you please provide the date and amount?",
        "Card Services": "For card-related services, I'll need your card number to proceed.",
        "Account Statement": "I can help you with your account statement. Which month's statement are you looking for?",
        "Loan Inquiry": "I can provide information on loans. Are you interested in a personal, auto, or home loan?",
        "General Information": "I can help with that. What specific information are you looking for?"
    }
    response = response_map.get(chosen_category, "How can I assist you further today?")
    outputs.append(response)

    return outputs

if __name__ == '__main__':
    # Example 1: A query with specific details
    customer_query = "I have a question about a transaction for $50 on my credit card yesterday."
    results = run_prompt_chain(customer_query)
    print("--- Query 1 ---")
    for i, result in enumerate(results):
        print(f"Step {i+1}: {result}")

    print("\n" + "="*20 + "\n")

    # Example 2: A simpler query
    customer_query_2 = "I want to open a new savings account."
    results_2 = run_prompt_chain(customer_query_2)
    print("--- Query 2 ---")
    for i, result in enumerate(results_2):
        print(f"Step {i+1}: {result}")
