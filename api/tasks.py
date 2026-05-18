from celery import Celery
from controllers import podcast_controller  as pc
import base64 
celery_app = Celery(
    "podcast",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def generate_podcast_task(text, model):
    
    output = pc.generate_pdf_to_podcast(text, model)
    encoded = base64.b64encode(output).decode("utf-8")
    return encoded

@celery_app.task
def generate_text_to_speech_task(text, model):
    
    output = pc.generate_text_to_speech(text, model)
    encoded = base64.b64encode(output).decode("utf-8")
    return encoded
