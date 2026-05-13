from enum import Enum
from chunking import chunk_text, clean_chunk, create_audio_chunks
import llm_engine as Ai_eg
import tempfile
import audio_generation as ag
from exceptions import *

class PipelineState(Enum):
    IDLE = "idle"
    GENERATING_SCRIPT = "generating_script"
    SCRIPT_READY = "script_ready"
    GENERATING_AUDIO = "generating_audio"
    DONE = "done"
    FAILED = "failed"
class PodcastPipeline:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.chunks = []

        self.state = PipelineState.IDLE

        self.full_podcast_script = ""

        self.final_audio_bytes = None

        self.last_error = None

    def initialize_pipeline(self):

        try:
            self.state = PipelineState.GENERATING_SCRIPT
            self.chunks = chunk_text(self.raw_text)

        except Exception as e :
            self.last_error = str(e)
            self.state = PipelineState.FAILED
            raise

    def generate_script(self,on_progress=None):
        if self.state != PipelineState.GENERATING_SCRIPT:
            raise RuntimeError(f"Cannot generate script from state: {self.state}")

        previous_context = ""
        for index, chunk in enumerate(self.chunks):
            current_index= index + 1
            if on_progress is not None:
                on_progress(current_index, len(self.chunks))
            try:
                generated_script = Ai_eg.request_transmission(previous_context+chunk)
                self.full_podcast_script += generated_script
                previous_context = generated_script[-150:]

            except Exception as e:
                self.state = PipelineState.FAILED
                self.last_error = f"Script generation failed on section {index + 1}: {e}"
                raise ScriptGenerationError(self.last_error) from e
        self.state = PipelineState.SCRIPT_READY

    def generate_audio(self, select_model, on_progress = None):
        if self.state != PipelineState.SCRIPT_READY:
            raise RuntimeError(f"Cannot generate audio from state: {self.state}")

        else:
            self.state = PipelineState.GENERATING_AUDIO
            try:
                clean_text = clean_chunk(self.full_podcast_script)
                audio_chunks = create_audio_chunks(clean_text)
                tts_service = Ai_eg.authorization()
                with  tempfile.TemporaryDirectory() as tem_dir:

                    for index, audio_chunk in enumerate(audio_chunks):
                        current_index = index + 1
                        if on_progress:
                            on_progress(current_index, len(audio_chunks))
                        audio_package = ag.generate_studio_audio(
                            tem_dir,
                            audio_chunk,
                            select_model,
                            tts_service,
                            index
                        )

                    complete_audio = ag.export_the_audio(tem_dir, audio_chunks)
                    self.final_audio_bytes = complete_audio
                self.state = PipelineState.DONE
                return self.final_audio_bytes

            except Exception as e:
                self.state = PipelineState.FAILED
                self.last_error = f"Audio Generation Failed {str(e)}"
                raise AudioGenerationError(self.last_error) from e
