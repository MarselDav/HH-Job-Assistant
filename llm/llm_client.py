import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import FinishReason
from pydantic import BaseModel

from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self, model : str = "gemini-3.6-flash") -> None:
        load_dotenv()
        self.client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        self.model = model

    def generate(self, prompt : str, response_schema : type[T]) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_schema=response_schema,
                response_mime_type="application/json"
            )
        )

        print("Model:", response.model_version)
        print("Response ID:", response.response_id)
        print("Finish reason:", response.candidates[0].finish_reason)
        print("Finish reason type:", type(response.candidates[0].finish_reason))

        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Output tokens:", response.usage_metadata.candidates_token_count)
        print("Thoughts tokens:", response.usage_metadata.thoughts_token_count)
        print("Total tokens:", response.usage_metadata.total_token_count)

        if response.candidates[0].finish_reason == FinishReason.STOP:
            print(f"Запрос (id: {response.response_id}) успешно выполнен")

        if response.candidates[0].finish_reason == FinishReason.FINISH_REASON_UNSPECIFIED:
            raise RuntimeError("Остановка выполнения запроса по неизвестным причинам")

        if response.candidates[0].finish_reason == FinishReason.MAX_TOKENS:
            raise RuntimeError("Не хватило токенов")

        if response.parsed is None:
            raise RuntimeError("LLM returned no parsed response")

        return response.parsed
        # return response_schema.model_validate_json(response.text)
