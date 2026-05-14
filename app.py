
import streamlit as st
import audio_generation as ag
from enum import Enum
from chunking import chunk_text
from text_extraction import extract_text_from_pdf
import llm_engine as Ai_eg
from exceptions import *
from orchestrator import PipelineState, PodcastPipeline

st.set_page_config(
    page_title="PDF To Podcast AI",
    page_icon="🎙️",
    layout="centered"
)
st.title("Fantasto Bargh", text_alignment= "center")
st.subheader("Welcomes you",  text_alignment= "center")
st.write("Turn study materials, research papers, Text and documents into AI-generated podcast episodes.")
voices = ["Jason","Aria"]
select_model = st.selectbox("Select Model", voices)

tab_podcast, tab_audio_podcast = st.tabs(["🎙️ PDF To Podcast", "✍️ Text to Speech"])

with tab_audio_podcast:

    user_input = st.text_area("Enter your prompt")


    if st.button("Send"):

        # if st.button("Generate Audio"):
        if not user_input.strip():
            st.error("Please Enter the Text.")

        else:
            pipeline = PodcastPipeline(user_input)
            pipeline.full_podcast_script = user_input
            pipeline.state = PipelineState.SCRIPT_READY

            progress_bar_2 = st.progress(0)
            status_text_2 = st.empty()
            def update_progress_tts(current, total):
                progress_bar_2.progress(current / total)
                status_text_2.write(f"🎧 Generating audio {current} of {total}")

            final_text_to_audio = pipeline.generate_audio(select_model, on_progress=update_progress_tts)

            if final_text_to_audio is not None:
                st.subheader("Download Audio")

                st.audio(final_text_to_audio)

                st.success("Audio Generated Successfully!")

                st.download_button(
                    label="Download",
                    data = final_text_to_audio,
                    file_name="Fantasto-Bargh_audio.mp3",
                    mime="audio/mp3"
                )


with tab_podcast:
    uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
    )
    if uploaded_file:

        try:
            extracted_text = extract_text_from_pdf(uploaded_file)
        except PDFExtractionError as e:
            st.error(f"Error in Extracting Texts From PDF. {e}")
            st.stop()

        if st.button("Generate AI Podcast"):
            pipeline = PodcastPipeline(extracted_text)

            progress_bar= st.progress(0)
            status_text = st.empty()
            def update_script_ui(current, total):
                progress_bar.progress(current/total)
                status_text.write(f"Generating the Audio {current} section of {total}")
            def update_audio_ui(current, total):
                progress_bar.progress(current/total)
                status_text.write(f"Generating the Audio {current} section of {total}")
            try:

                pipeline.initialize_pipeline()
                pipeline.generate_script(on_progress=update_script_ui)

                if pipeline.state == PipelineState.SCRIPT_READY:
                    st.subheader("Generated Podcast Script")

                    with st.expander("View Generated Podcast Script"):
                        st.write(pipeline.full_podcast_script)

                    pipeline.generate_audio(select_model, on_progress=update_audio_ui)

            except Exception as e:
                st.error(f"Pipeline Halted : {str(e)}")
                st.stop()


            if pipeline.state == PipelineState.DONE:

                st.subheader("Download Audio")
                st.audio(pipeline.final_audio_bytes)
                st.success("Podcast Generated Successfully!")
                st.download_button(
                    label="Download",
                    data=pipeline.final_audio_bytes,
                    file_name="Fantasto-Bargh_podcast_audio.mp3",
                    mime="audio/mp3"
                )

st.write("Made with ❤️ by Fantasto Bargh")
