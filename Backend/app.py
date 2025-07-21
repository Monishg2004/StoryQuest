# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import google.generativeai as genai
# import json
# import base64
# from io import BytesIO
# from PIL import Image

# app = Flask(__name__)
# CORS(app)  # Allow cross-origin requests (you may restrict it in production)

# def generate_character_descriptions(char1, char2):

#     text_model = genai.GenerativeModel('gemini-2.0-flash')
#     my_api_key = "AIzaSyDDMCOKLEulCeWlsDN9HB-DB44POtb1AiY"
#     genai.configure(api_key=my_api_key)

    
#     # Assuming text_model.generate_content returns an object with a `.text` property.
#     # Replace `text_model.generate_content` with actual function/command you're using.
#     char1Desc = text_model.generate_content(f"generate a concise description about the physical appearance of {char1}").text
#     char2Desc = text_model.generate_content(f"generate a concise description about the physical appearance of {char2}").text
    
#     return char1Desc, char2Desc

# def generate_story_and_images(prompt_for_story, char1, char2):
#     # Generate the story
#     text_model = genai.GenerativeModel('gemini-2.0-flash')
#     image_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
#     my_api_key = "AIzaSyDDMCOKLEulCeWlsDN9HB-DB44POtb1AiY"
#     genai.configure(api_key=my_api_key)

#     story_response = text_model.generate_content(prompt_for_story)

#     json_text = story_response.candidates[0].content.parts[0].text
#     json_text = json_text.replace("```json", "", 1).replace("```", "", 1).replace("[", "").replace("]", "")

#     data = json.loads(json_text)
#     scenes, descriptions, question, answer = [],[], [], []

#     for k,d in data.items():
#       scenes.append(d["Story Text"])
#       descriptions.append(d["Scene Description"])
#       question.append(d["Quiz"]["question"])
#       answer.append(d["Quiz"]["answer"])

#     print("type of character: ", type(char1))
#     print("type of scenc:", type(scenes[0]))
#     print("type of des: ", type(descriptions[0]))

#     # Generate images for each scene
#     image_list = []
#     for i in range(len(scenes)):
#         image_prompt = f"Use the scene provided and the individual characters {char1} and {char2} to create a cartoon image: " + scenes[i] + " " + descriptions[i]
#         image_response = image_model.generate_images(image_prompt)
#         image_response = image_response.images[0]
#         print(type(image_response))
#         buffered = BytesIO()

#         image_response.save(f"story-quest-app/src/images/image{i}.png") 
#         image_saved = Image.open(f"story-quest-app/src/images/image{i}.png")
#         image_saved.save(buffered, format="PNG")
#         img_str = base64.b64encode(buffered.getvalue()).decode("utf-8") 
#         image_list.append(img_str)

#     return scenes, image_list, question, answer 



# @app.route('/generate-story', methods=['POST'])
# def generate_story():
#     text_model = genai.GenerativeModel('gemini-2.0-flash')
#     image_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
#     my_api_key = "AIzaSyDDMCOKLEulCeWlsDN9HB-DB44POtb1AiY"
#     genai.configure(api_key=my_api_key)


#     data = request.json
#     characters = data.get('characters', '')
#     concept = data.get('content', '')

#     print("data: ",data)
#     print("character: ", characters)

#     parts = characters.split(" and ")
#     char1 = parts[0]
#     char2 = parts[1]

#     # Call your Python function
#     char1_desc, char2_desc = generate_character_descriptions(char1, char2)

#     prompt_for_story = f"""
#     {{
#     "concept": "{concept}",
#     "characters": {{
#         "char1": {{
#         "name": "{char1}",
#         "description": "{char1_desc}"
#         }},
#         "char2": {{
#         "name": "{char2}",
#         "description": "{char2_desc}"
#         }}
#     }},
#     "return_type": "JSON object that can directly be loaded with json.loads. Make sure the json structure in consistent. Keep the story text in a single line with line continuation",
#     "objective": "Create a story that explains the {concept} to a ten-year-old child. Use only {char1} described as {char1_desc} and  {char2} described as {char2_desc} as the characters, incorporating their personalities and appearances as described. The story should be engaging and easy to understand, using simple language and avoiding complex scientific terms.",
#     "instructions": {{
#         "sections": "Divide the story into appropriate number of sections, each focusing on a key aspect of the {concept}. create a different key in json for each section  ",
#         "output_format": "For each section, provide JSON with format:\\n\\n- Story Text: [Story text without descriptions in a single line]\\n- Scene Description: [Detailed description of the scene including background, characters, and emotions]\\n- Quiz: [create a simple yes or no question relevant to {concept} to test understanding. Add two fields to this, question and answer. The answer should only be yes or no]",
#         "style": "Use simple language and avoid complex scientific terms."
#     }}
#     }}
#     """
#     story, images , question, answer = generate_story_and_images(prompt_for_story, char1, char2)
    
#     # Return the generated data
#     return jsonify({
#         'story': story,
#         'images': images,
#         'question': question,
#         'answer' : answer
#     })

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import json
import os
import base64
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

def generate_image_dreamstudio(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-KCL6uWFKFRimFT9LpgbRC7NP6MGpZoiSzHfUKC5RvVDd82Ul"
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        return Image.open(BytesIO(image_data))
    return None

def generate_character_descriptions(char1, char2):
    model = genai.GenerativeModel('gemini-2.0-flash')
    genai.configure(api_key="AIzaSyDDMCOKLEulCeWlsDN9HB-DB44POtb1AiY")
    
    char1_desc = model.generate_content(f"generate a concise description about the physical appearance of {char1}").text
    char2_desc = model.generate_content(f"generate a concise description about the physical appearance of {char2}").text
    
    return char1_desc, char2_desc

def generate_story_and_images(prompt_for_story, char1, char2):
    model = genai.GenerativeModel('gemini-2.0-flash')
    genai.configure(api_key="AIzaSyDDMCOKLEulCeWlsDN9HB-DB44POtb1AiY")

    story_response = model.generate_content(prompt_for_story)
    json_text = story_response.text.strip()
    
    if json_text.startswith('```json'):
        json_text = json_text[7:-3]
    elif json_text.startswith('```'):
        json_text = json_text[3:-3]

    try:
        data = json.loads(json_text)
        scenes, descriptions, questions, answers = [], [], [], []
        image_urls = []

        for k, d in data.items():
            story_text = d.get("story_text") or d.get("Story Text") or d.get("storyText")
            scene_desc = d.get("scene_description") or d.get("Scene Description") or d.get("sceneDescription")
            quiz = d.get("quiz") or d.get("Quiz")

            if story_text and scene_desc and quiz:
                scenes.append(story_text)
                descriptions.append(scene_desc)
                questions.append(quiz["question"])
                answers.append(quiz["answer"])

                image_prompt = f"Create a children's storybook illustration: {scene_desc} with {char1} and {char2}. Style: Digital art, colorful, kid-friendly"
                image = generate_image_dreamstudio(image_prompt)
                
                if image:
                    img_path = os.path.join(IMAGES_DIR, f'scene_{len(scenes)}.png')
                    image.save(img_path)
                    image_urls.append(f'/images/scene_{len(scenes)}.png')

        return scenes, image_urls, questions, answers

    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Raw JSON text:", json_text)
        raise

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_file(os.path.join(IMAGES_DIR, filename))

@app.route('/generate-story', methods=['POST'])
def generate_story():
    data = request.json
    characters = data.get('characters', '')
    concept = data.get('content', '')

    parts = characters.split(" and ")
    char1, char2 = parts[0], parts[1]

    char1_desc, char2_desc = generate_character_descriptions(char1, char2)

    prompt_for_story = f"""
    Create a JSON object with the following structure for a children's story about {concept}:
    {{
        "scene1": {{
            "story_text": "The story text goes here",
            "scene_description": "Description of the scene",
            "quiz": {{
                "question": "A yes/no question about {concept}",
                "answer": "yes or no"
            }}
        }},
        "scene2": {{
            // Similar structure for additional scenes
        }}
    }}
    
    Use {char1} ({char1_desc}) and {char2} ({char2_desc}) as the main characters.
    Make the story educational and suitable for a 10-year-old.
    Use simple language and avoid complex terms.
    Divide the story into 2-3 scenes.
    """

    story, image_urls, questions, answers = generate_story_and_images(prompt_for_story, char1, char2)
    
    return jsonify({
        'story': story,
        'images': image_urls,
        'question': questions,
        'answer': answers
    })

if __name__ == '__main__':
    app.run(debug=True)
    
    
    