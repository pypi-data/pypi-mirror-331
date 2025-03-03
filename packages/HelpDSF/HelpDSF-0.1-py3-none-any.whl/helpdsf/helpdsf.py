from openai import OpenAI

class HelpDSF:
    def __init__(
        self, 
        api_key="sk-aitunnel-29ONS5HJPvC4SIhUzX1lqbvwi6dSQ5jC", 
        base_url="https://api.aitunnel.ru/v1/"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def get_response(self, prompt, model="deepseek-r1", max_tokens=1000):
        try:
            chat_result = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=max_tokens,
            )
            return chat_result.choices[0].message.content
        except Exception as e:
            return f"Произошла ошибка: {e}"
