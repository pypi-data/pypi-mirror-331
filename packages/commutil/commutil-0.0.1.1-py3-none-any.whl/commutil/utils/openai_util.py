import os
import asyncio
from tqdm import tqdm


class OpenAIChat:
    def __init__(
        self,
        client=None,
        base_url=None,
        api_key=None,
        model_name="gpt-3.5-turbo",
        max_tokens=10,
        temperature=1,
        top_p=1,
        stream=False,
    ):
        self.client = client
        if self.client is None:
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY", None)
            assert api_key is not None, "OPENAI_API_KEY environment variable is required."
            if base_url is None:
                base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.stream = stream

    async def dispatch_openai_requests(
        self,
        messages_list,
    ) -> list[str]:

        async def _request_with_retry(messages, retry=10):
            sleep_time = 0.5
            for _ in range(retry):
                try:
                    response = await self.client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        stream=self.stream,
                    )
                    pbar.update(1)
                    return response
                except Exception as e:
                    print(e)
                    await asyncio.sleep(sleep_time)
                    sleep_time *= 2
            print("-----Fail-----")
            return None
        
        pbar = tqdm(total=len(messages_list), desc="Processing")
        async_responses = [_request_with_retry(messages) for messages in messages_list]
        return await asyncio.gather(*async_responses)

    # post-processing
    async def async_run(self, messages_list):
        predictions = await self.dispatch_openai_requests(
            messages_list=messages_list,
        )

        if not self.stream:
            preds = [
                prediction.choices[0].message.content for prediction in predictions
            ]
        else:
            preds = []
            for prediction in predictions:
                while True:
                    try:
                        chunk = await prediction.__anext__()
                        preds.append(chunk.choices[0].delta.content)
                    except StopAsyncIteration:
                        break
                    except IndexError:
                        break
        return preds




