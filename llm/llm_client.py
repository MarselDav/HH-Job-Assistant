import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from google.genai.types import FinishReason
from pydantic import BaseModel
import time

from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self, model : str = "gemini-3.6-flash") -> None:
        load_dotenv()
        self._client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        self._model = model

        # настройки повторных попыток получения ответа и обязательной паузы
        self._max_retries = 5
        self._min_delay = 2.0
        self._current_delay = 0.0
        self._last_request_time = 0.0

    def generate(self, prompt : str, response_schema : type[T]) -> T:
        response = None
        for attempt in range(self._max_retries):
            self._wait_if_needed()
            self._last_request_time = time.time()

            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_schema=response_schema,
                        response_mime_type="application/json"
                    )
                )

                # сбрасываем при успешности запроса
                self._current_delay = 0

                break

            except APIError as e:
                if e.code == 503:
                    if attempt == self._max_retries - 1:
                        print("[LLMClient] Число попыток исчерпано")

                    self._current_delay = self._min_delay * (2 ** attempt)
                    print(f"[LLMClient] Ошибка 503 (Модель перегружена). "
                          f"Попытка {attempt + 1}/{self._max_retries}. Ждем {self._current_delay} сек...")

        if response is None:
            raise RuntimeError(f"[LLMClient] Не удалось получить ответ от LLM даже после "
                               f"{self._max_retries} запросов")

        print("[LLMClient] Model:", response.model_version)
        print("[LLMClient] Response ID:", response.response_id)
        print("[LLMClient] Finish reason:", response.candidates[0].finish_reason)
        print("[LLMClient] Finish reason type:", type(response.candidates[0].finish_reason))

        print("[LLMClient] Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("[LLMClient] Output tokens:", response.usage_metadata.candidates_token_count)
        print("[LLMClient] Thoughts tokens:", response.usage_metadata.thoughts_token_count)
        print("[LLMClient] Total tokens:", response.usage_metadata.total_token_count)

        if response.candidates[0].finish_reason == FinishReason.STOP:
            print(f"[LLMClient] Запрос (id: {response.response_id}) успешно выполнен")

        if response.candidates[0].finish_reason == FinishReason.FINISH_REASON_UNSPECIFIED:
            raise RuntimeError("[LLMClient] Остановка выполнения запроса по неизвестным причинам")

        if response.candidates[0].finish_reason == FinishReason.MAX_TOKENS:
            raise RuntimeError("[LLMClient] Не хватило токенов")

        if response.parsed is None:
            raise RuntimeError("[LLMClient] LLM returned no parsed response")

        return response.parsed


    def _wait_if_needed(self):
        now = time.time()
        time_passed = now - self._last_request_time

        required_delay = max(self._min_delay, self._current_delay)

        if time_passed < required_delay:
            sleep_time = required_delay - time_passed
            print(f"[LLMClient] Выдерживаем авто-паузу перед запросом: {sleep_time:.2f} сек.")

            time.sleep(sleep_time)