import re
import textwrap
from exceptions import ScriptGenerationError
def clean_chunk(text):
    try:
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u201c", "").replace("\u201d", "'")
        text = re.sub(r"[^\x00-\x7f]", "", text)

        return text
    except Exception as e:
        raise ScriptGenerationError(f"Text Cleaning Failed {e}") from e

def chunk_text(text, chunk_size = 1000):

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_index = ""
    
    previous_context = ""
    for sentence in sentences:
        if len(current_index) + len(sentence) < chunk_size:
            current_index += sentence +" "

        else:
            if previous_context:
                new_content = previous_context + current_index
                chunks.append(new_content)
                
            else:
                
                chunks.append(current_index)
            whole_previous_chunk = current_index 
            previous_context = whole_previous_chunk[-150:]
            current_index = sentence + " "

        
    if current_index.strip():
        chunks.append(previous_context+current_index)


    return chunks

def create_audio_chunks(script_text, max_char =350):

    try:
        if not script_text.strip():
            raise ValueError("Cannot create audio chunks from empty text.")
        chunks = textwrap.wrap(script_text, width=max_char, break_long_words=True)

        if not chunks:
            raise ValueError("Audio chunking produced no output.")
        return chunks
    
    except ValueError:
        raise
    
    except Exception as e :
        raise ScriptGenerationError(f"Chunk Creation Failed {e}") from e