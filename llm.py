from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import json

class MultimodalLLM:
    def __init__(self):
        # Initialize the image captioning model (BLIP)
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.image_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        self.text_model = self.simple_text_model

    def simple_text_model(self, prompt):
        return f"Processed text prompt: {prompt}"

    def process_image_and_prompt(self, image_path, prompt):
        image = Image.open(image_path).convert('RGB')
        
        inputs = self.processor(image, return_tensors="pt")
        out = self.image_model.generate(**inputs)
        image_caption = self.processor.decode(out[0], skip_special_tokens=True)
        
        combined_prompt = f"Image Caption: {image_caption}. User Prompt: {prompt}"
        
        response = self.text_model(combined_prompt)
        
        return response

    def process_json_and_prompt(self, json_data, prompt):
        json_str = json.dumps(json_data)
        
        combined_prompt = f"JSON Data: {json_str}. User Prompt: {prompt}"
        
        response = self.text_model(combined_prompt)
        
        return response

llm = MultimodalLLM() 