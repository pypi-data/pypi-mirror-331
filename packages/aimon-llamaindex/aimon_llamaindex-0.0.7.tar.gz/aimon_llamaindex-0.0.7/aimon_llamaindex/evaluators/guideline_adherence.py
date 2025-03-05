from typing import Any              
from aimon import Client
from .aimon_evaluator import AIMonEvaluator, generate_random_string

class GuidelineEvaluator(AIMonEvaluator):
    
    def __init__(self, 
                 aimon_client:Client, 
                 publish: bool = False, 
                 application_name:str = "ApplicationName"+generate_random_string(5), 
                 model_name:str = "ModelName"+generate_random_string(5)) -> None:                  
        
        super().__init__(aimon_client, publish, application_name, model_name)

    def create_payload(self, context, user_query, user_instructions, generated_text) -> dict:
        
        aimon_payload = super().create_payload(context, user_query, user_instructions, generated_text, config={'instruction_adherence': {'detector_name': 'default'}})
        
        return aimon_payload

    def evaluate(self, user_query, user_instructions, llamaindex_llm_response, **kwargs: Any):

        context, response = self.extract_response_metadata(llamaindex_llm_response)

        aimon_payload = self.create_payload(context, user_query, user_instructions, response)
    
        detect_response = self.detect_aimon_response(aimon_payload)

        return detect_response.instruction_adherence