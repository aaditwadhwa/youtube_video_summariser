import streamlit as st
import os
# from secret_key import googleapi_key
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


# os.environ['GOOGLE_API_KEY'] = googleapi_key
googleapi_key = st.secrets['GOOGLE_API_KEY']
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

def get_youtube_transcript(video_url: str) -> str:
    """
    Fetches the transcript for a given YouTube video URL.

    Args:
        video_url: The URL of the YouTube video.

    Returns:
        The transcript text as a single string, or None if it fails.
    """
    try:
        video_id = video_url.split("v=")[-1]
        
        st.info("Fetching transcript...")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    
        transcript_text = ""
        for entry in transcript_list:
            transcript_text += entry['text'] + " "

        st.success("Transcript fetched successfully!")
        return transcript_text
    
    except NoTranscriptFound:
        st.error("Sorry, no transcript was found for this video. It might be disabled or not available in English.")
        return None
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching the transcript: {e}")
        return None

def get_summary_from_llm(transcript_text: str) -> str:
    """
    Generates a summary for the given text using the Gemini model.

    Args:
        transcript_text: The text to be summarized.

    Returns:
        The generated summary as a string, or None if it fails.
    """
    try:
        st.info("Initializing language model...")
        

        prompt = PromptTemplate(
            template="""You are an expert video summarizer. Please provide a concise and engaging summary of the following transcript. Highlight the key points and main ideas with emojis.
            
            Transcript:
            "{transcript}"
            
            Summary:"""
        )


        chain = prompt | llm
        st.info("Generating summary...")
        result = chain.invoke({"transcript": transcript_text})
        
        st.success("Summary generated!")
        return result.content
    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")
        return None



st.set_page_config(page_title="YouTube Summarizer", layout="centered")
st.title("🎬 YouTube Video Summarizer")
st.write("Paste a YouTube video URL below and get a quick summary.")


youtube_url = st.text_input("Enter YouTube Video URL")

if st.button("Generate Summary"):
    if not youtube_url:
        st.warning("Please enter a YouTube video URL.")
    else:

        transcript = get_youtube_transcript(youtube_url)
        
        if transcript:
            # 2. Get Summary
            summary = get_summary_from_llm(transcript)
            
            if summary:
                # 3. Display Results
                st.subheader("📝 Summary")
                st.write(summary)
                
                with st.expander("View Full Transcript"):
                    st.text_area("", transcript, height=250)

