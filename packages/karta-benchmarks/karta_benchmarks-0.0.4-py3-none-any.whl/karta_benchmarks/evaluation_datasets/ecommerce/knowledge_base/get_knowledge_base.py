def knowledge_base() -> str:
    """
    Get the knowledge base for the ecommerce domain.
    
    Returns:
        str: The knowledge base for the ecommerce domain. The knowledge base is a markdown file, this
        functions returns it as a dumb string.
    """
    # Look for the domain_knowledge.md file in the knowledge_base directory
    # Return the file as a string
    with open("karta_benchmarks/evaluation_datasets/ecommerce/knowledge_base/domain_knowledge.md", "r") as file:
        return file.read()
