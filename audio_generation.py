from chunking import (
    clean_chunk,
    create_audio_chunks
)
import os
from pydub import AudioSegment
from exceptions import AudioGenerationError
def generate_studio_audio(tem_dir,audio_chunk, select_model, tts_service,index):
    try:
        if audio_chunk.strip():
                
            response = user_selected_model(audio_chunk, tts_service, select_model)

            raw_audio = AudioSegment(
            data=response.audio,
            sample_width=2,
            frame_rate = 44100,
            channels = 1
            )

            return raw_audio.export(os.path.join(tem_dir, f"podcast_part_{index}.wav"), format="wav")
            
    except Exception as e :
        raise AudioGenerationError(f"Audio generation Failed. {e}") from e 

def export_the_audio(tem_dir, audio_chunks):

    try:
        combined_audio = AudioSegment.empty()

        for index, audio_chunk in enumerate(audio_chunks):
            file_path = os.path.join(tem_dir, f"podcast_part_{index}.wav")
            if os.path.exists(file_path):
                audio_part = AudioSegment.from_wav(file_path)

                combined_audio += audio_part
            else:
                raise RuntimeError(f"Audio file dosen't exists for {index + 1}")

        combined_audio.export(
            os.path.join(tem_dir, f"Final_Podcast.mp3"),
            format="mp3"
        )

        with open(os.path.join(tem_dir, "Final_Podcast.mp3"), "rb") as f:
        
            final_audio_bytes = f.read()

        return final_audio_bytes
    
    except RuntimeError:
        raise
    except Exception as e :
        raise AudioGenerationError(f"Unexpected audio pipeline error: {e}") from e

def user_selected_model(audio_chunk, tts_service, model = "Jason"):
    try:
        response = tts_service.synthesize(
            text= audio_chunk,
            language_code ="en-US",
            voice_name="Magpie-Multilingual.EN-US."+model,
            sample_rate_hz=44100
        )

        return response
    except Exception as e:
        raise AudioGenerationError(f"Model Selection Failed {e}") from e