import base64
import random
import requests
from PIL import Image

prompt_file = open('./prompt.txt', 'r')
GPT4_PROMPT = prompt_file.read()
prompt_file.close()


openai_secret_key = "PUT_SECRET_KEY_HERE"

def generate_prompt(encoded_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_secret_key}"
    }
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": GPT4_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    return headers, payload


def get_response(input_directory, district, image_path):
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    img = Image.open(input_directory + '/' + district + '/' + image_path)
    # crop top right corner
    img = img.crop((img.width - 500, 0, img.width, 500))
    image_path = input_directory + "/" + f'current_{str(random.randint(0, 1000000))}.png'
    img.save(image_path)
    base64_image = encode_image(image_path)
    os.remove(image_path)
    headers, payload = generate_prompt(base64_image)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response = response.json()['choices'][0]['message']['content']
    return response.split(',')