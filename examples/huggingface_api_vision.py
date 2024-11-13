from rich.console import Console
from huggingface_hub import InferenceClient

console = Console()

client = InferenceClient(api_key="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")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image in one sentence."},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                },
            },
        ],
    }
]

response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct",
    messages=messages,
    max_tokens=500,
    stream=False,
)

console.print(response)
