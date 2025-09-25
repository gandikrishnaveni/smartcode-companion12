from ibm_watsonx_ai.foundation_models import Model
import os

model = Model(
    model_id="ibm/granite-13b-chat-v2",
    params={"decoding_method": "greedy", "max_new_tokens": 100},
    credentials={
        "apikey": os.getenv("WATSONX_APIKEY"),
        "url": os.getenv("WATSONX_URL")
    },
    project_id=os.getenv("WATSONX_PROJECT_ID")
)

try:
    result = model.generate_text("print hello world in Java with comments")
    print(result)
except Exception as e:
    print("Error:", e)
