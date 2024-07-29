import os
import base64
import requests
import json
from tqdm import tqdm  # Optional: for progress bar

class OpenAIImageQuestioner:
    def __init__(self, api_key, base_directory):
        self.api_key = api_key
        self.base_directory = base_directory



    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def ask_question_about_image(self, image_path, question):
        base64_image = self.encode_image(image_path)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
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
            "max_tokens": 300
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

    def process_images(self, question):
        if not os.path.exists(self.base_directory):
            print(f"Directory does not exist: {self.base_directory}. Skipping...")
            return

        image_files = [os.path.join(self.base_directory, file) for file in os.listdir(self.base_directory) if file.endswith('.png')]
        results = []
        count = 1
        for image_path in tqdm(image_files, desc="Processing images"):
            response = self.ask_question_about_image(image_path, question)
            if response and 'choices' in response:
                result = {
                    "question_num": count,
                    "question": response['choices'][0]['message']['content']
                }
                results.append(result)
                count += 1
            else:
                print(f"Failed to get valid response for image: {image_path}")

        return results