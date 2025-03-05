import os
import random
import string
import logging
from aimon import Client
from typing import Any                                              

def generate_random_string(length):
  """Generates a random string of letters and digits."""
  characters = string.ascii_letters + string.digits
  return ''.join(random.choice(characters) for i in range(length))

class AIMonEvaluator:

    ## Constructor of the Base Class
    def __init__(self, 
                 aimon_client:Client, 
                 publish: bool = False, 
                 application_name:str = "ApplicationName"+generate_random_string(5), 
                 model_name:str = "ModelName"+generate_random_string(5),
                 detector_configuration:dict[str, dict[str, str]] = {   'hallucination': {'detector_name': 'default'},
                                                                        'conciseness': {'detector_name': 'default'},
                                                                        'completeness': {'detector_name': 'default'},
                                                                        'instruction_adherence': {'detector_name': 'default'},
                                                                        'toxicity': {'detector_name': 'default'},
                                                                        'retrieval_relevance': {'detector_name': 'default'}
                                                                    }
                ) -> None:
 
        self.publish = publish
        self.client = aimon_client
        self.model_name = model_name
        self.application_name = application_name
        self.detector_configuration = detector_configuration

    ## AIMon payload creation
    def create_payload(self, context, user_query, user_instructions, generated_text, config, **kwargs) -> dict:
        
        task_definition = kwargs.get('task_definition', None)

        aimon_payload = {
            'context': context,
            'user_query': user_query,
            'generated_text': generated_text,
            'instructions': user_instructions,
            'config': config
        }

        aimon_payload['publish'] = self.publish

        if 'retrieval_relevance' in aimon_payload['config']:
            if task_definition == None:
                raise ValueError(   "When retrieval_relevance is specified in the config, "
                                    "'task_definition' must be present and should not be None.")
            else:
                aimon_payload['task_definition'] = task_definition

        if self.publish:
            aimon_payload['model_name'] = self.model_name
            aimon_payload['application_name'] = self.application_name

        return aimon_payload
    

    ## AIMon Detect
    def detect_aimon_response(self,aimon_payload):
        
        try:
            detect_response = self.client.inference.detect(body=[aimon_payload])
            # Check if the response is a list
            if isinstance(detect_response, list) and len(detect_response) > 0:
                detect_result = detect_response[0]
            elif isinstance(detect_response, dict):
                detect_result = detect_response  # Single dict response
            else:
                raise ValueError("Unexpected response format from detect API: {}".format(detect_response))
        except Exception as e:
                # Log the error and raise it
                print(f"Error during detection: {e}")
                raise
        
        return detect_result
    
    
    ## Function to extract metadata from the response

    def extract_response_metadata(self, llm_response):

        def get_source_docs(llm_response):
            contexts = []
            relevance_scores = []
            if hasattr(llm_response, 'source_nodes'):
                for node in llm_response.source_nodes:
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

        context, relevance_scores = get_source_docs(llm_response)
        return context, llm_response.response
    
    ## Function to evaluate the LLM response

    def evaluate(self, user_query, user_instructions, llamaindex_llm_response, task_definition = None, **kwargs:Any):
        
        context, response = self.extract_response_metadata(llamaindex_llm_response)

        aimon_payload = self.create_payload(context, user_query, user_instructions, response, config=self.detector_configuration, task_definition = task_definition)
    
        evaluation_result = self.detect_aimon_response(aimon_payload)

        return evaluation_result
    