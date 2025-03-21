from keras.models import load_model   
from PIL import Image, ImageOps   
import numpy as np

import requests
from io import BytesIO

np.set_printoptions(suppress=True)

model = load_model("shelf_classification/keras_model.h5", compile=False)
class_names = open("shelf_classification/labels.txt", "r").readlines()

def is_shelf_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()   
        image = Image.open(BytesIO(response.content)).convert("RGB")
        
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array
        
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]
        
        return class_name == "0 Class 1"
    
    except Exception as e:
        return f"Error: {str(e)}"
  