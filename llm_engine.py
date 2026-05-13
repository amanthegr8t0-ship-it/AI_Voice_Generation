
import requests
import riva.client
from config import NVIDIA_API_KEY
from exceptions import ScriptGenerationError

def request_transmission(chunk):

    prompt = f"""
    Turn the following PDF content into an engaging podcast-style explanation.

    Rules:
    - Make it conversational
    - Make it beginner friendly
    - Explain concepts naturally
    - Use simple language
    - Sound like a podcast host teaching listeners
    - Add excitement and smooth transitions
    - Avoid robotic explanations
    - CRITICAL: DO NOT write stage directions, sound effects, or speaker labels.
    - CRITICAL: Do not use brackets like [soft music] or (laughs). Write ONLY the spoken words.

    PDF Content:

    {chunk}
    """

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
    }
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        chunk_answer = result["choices"][0]["message"]["content"]
        
        chunk_podcast_script = chunk_answer + "\n\n"
        return chunk_podcast_script
    
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"NVIDIA API request failed (HTTP {e.response.status_code}): {e}") from e
    except requests.exceptions.ConnectionError as e :
        raise RuntimeError(f"Could not reach NVIDIA API — check your connection: {e}") from e
    except (KeyError,IndexError) as e:
        raise RuntimeError(f"Unexpected API response structure: {e}") from e
    except Exception as e:
        raise ScriptGenerationError(f"Script generation failed: {e}") from e

def authorization():
    auth = riva.client.Auth(
                uri= "grpc.nvcf.nvidia.com:443",
                use_ssl = True,
                metadata_args =[("function-id", "877104f7-e885-42b9-8de8-f6e4c6303969"),("authorization", f"Bearer {NVIDIA_API_KEY}")]
            )
    tts_service = riva.client.SpeechSynthesisService(auth)
    return tts_service