# AIMon - LlamaIndex: Response Utilities

import logging
from llama_index.core.query_engine import RetrieverQueryEngine

# Function to build a query engine and get LLM response
def get_response(user_query, retriever, llm):
    query_engine = RetrieverQueryEngine.from_args(retriever, llm)
    response = query_engine.query(user_query)
    return response

# Function to extract source docs from LlamaIndex response
def get_source_docs(chat_response):
    contexts = []
    relevance_scores = []
    if hasattr(chat_response, 'source_nodes'):
        for node in chat_response.source_nodes:
            if hasattr(node, 'node') and hasattr(node.node, 'text') and hasattr(node, 'score') and node.score is not None:
                contexts.append(node.node.text)
                relevance_scores.append(node.score)
            elif hasattr(node, 'text') and hasattr(node, 'score') and node.score is not None:
                contexts.append(node.text)
                relevance_scores.append(node.score)
            else:
                logging.info("Node does not have required attributes.")
    else:
        logging.info("No source_nodes attribute found in the chat response.")
    return contexts, relevance_scores

# Function to extract metadata from the response
def extract_response_metadata(user_query, user_instructions, response):
    context, relevance_scores = get_source_docs(response)
    return context, user_query, user_instructions, response.response

## Function to only extract the context from the response metadata
def extract_context(user_query, user_instructions, response):
    context, relevance_scores = get_source_docs(response)
    return context
