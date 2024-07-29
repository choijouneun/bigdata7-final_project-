import base64
import requests
import json

class OpenAIImageQuestioner:
    def __init__(self, api_key):
        self.api_key = api_key

    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"File not found: {image_path}")
            return None

    def ask_question_about_image(self, image_path, question):
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return None
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 600
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        try:
            response_json = response.json()
            if 'choices' in response_json:
                return response_json
            else:
                print(f"Unexpected response format: {response_json}")
                return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {response.text}")
            return None

    def process_image(self, image_path, question):
        response = self.ask_question_about_image(image_path, question)
        if response and 'choices' in response:
            result = {
                "question_num": 1,
                "question": response['choices'][0]['message']['content'],
            }
            return result
        else:
            print(f"Failed to get valid response for image: {image_path}")
            return None
