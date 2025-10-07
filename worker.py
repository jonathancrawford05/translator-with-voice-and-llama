import os
import io
import tempfile
from transformers import pipeline
from langchain_ollama import ChatOllama
from gtts import gTTS

# Initialize Whisper pipeline for Speech-to-Text (MULTILINGUAL)
print("Loading Whisper model (multilingual)...")
whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",  # Multilingual - supports both English and Russian
    chunk_length_s=30,
)
print("Whisper model loaded successfully")

# Initialize Ollama client for LLM processing
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

ollama_client = ChatOllama(
    model="llama3.2",
    base_url=OLLAMA_BASE_URL,
    temperature=0.0,
    max_tokens=4000,
)
print(f"Ollama client initialized with base URL: {OLLAMA_BASE_URL}")

# Translation prompt templates
PROMPTS = {
    "en-ru": """Translate the following English text into Russian. 
Reply ONLY with the Russian translation, no explanations, no formatting, no extra text.
English: {text}
Russian:""",
    
    "ru-en": """Translate the following Russian text into English.
Reply ONLY with the English translation, no explanations, no formatting, no extra text.
Russian: {text}
English:"""
}

# Output language mapping for gTTS
LANG_MAP = {
    "en-ru": "ru",  # Output is Russian
    "ru-en": "en"   # Output is English
}

# Input language mapping for Whisper STT
INPUT_LANG_MAP = {
    "en-ru": "english",  # Input is English
    "ru-en": "russian"   # Input is Russian
}


def speech_to_text(audio_binary, direction="en-ru"):
    """
    Convert speech audio to text using Whisper model (multilingual).
    
    Args:
        audio_binary: Binary audio data from the request
        direction: Translation direction to determine input language
        
    Returns:
        str: Transcribed text from the audio
    """
    try:
        # Get input language based on direction
        input_language = INPUT_LANG_MAP.get(direction, "english")
        
        # Create a temporary file to store the audio binary
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_binary)
            temp_audio_path = temp_audio.name
        
        # Transcribe the audio using Whisper with explicit language
        print(f"Transcribing audio file [language={input_language}, direction={direction}]: {temp_audio_path}")
        result = whisper_pipeline(
            temp_audio_path, 
            batch_size=8,
            generate_kwargs={"language": input_language}
        )
        text = result["text"]
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
        print(f"Recognized text [{input_language}]: {text}")
        return text
        
    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        return "Error transcribing audio"


def text_to_speech(text, voice="com", direction="en-ru"):
    """
    Convert text to speech using Google Text-to-Speech (gTTS).
    Language is determined by translation direction.
    
    Args:
        text: Text to convert to speech
        voice: Voice parameter (TLD for accent variant) - only used for English
        direction: Translation direction ('en-ru' or 'ru-en')
        
    Returns:
        bytes: Audio data in MP3 format
    """
    try:
        # Get output language based on direction
        output_lang = LANG_MAP.get(direction, "en")
        
        # Default voice if empty
        if voice == "" or voice == "default":
            voice = "com"

        print(f"Converting text to speech [lang={output_lang}, voice={voice}, direction={direction}]: {text[:50]}...")
        
        # Initialize gTTS with dynamic language
        # Note: TLD (accent) only applies to English
        if output_lang == "en":
            tts = gTTS(text=text, lang='en', tld=voice, slow=False)
        else:
            # Russian or other languages - TLD not applicable
            tts = gTTS(text=text, lang=output_lang, slow=False)
        
        # Save audio to bytes buffer in memory
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Read the bytes and return
        audio_content = audio_bytes.read()
        print(f"Text-to-speech conversion successful, audio size: {len(audio_content)} bytes")
        
        return audio_content
        
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return b""  # Return empty bytes on error


def llama_process_message(user_message, direction="en-ru"):
    """
    Process user message using Ollama LLM for translation.
    
    Args:
        user_message: User's input message
        direction: Translation direction ('en-ru' or 'ru-en')
        
    Returns:
        str: Translated text
    """
    try:
        # Get the appropriate prompt template
        prompt_template = PROMPTS.get(direction, PROMPTS["en-ru"])
        prompt = prompt_template.format(text=user_message)
        
        print(f"Processing message with Ollama [direction={direction}]: {user_message[:100]}...")
        
        # Call Ollama using LangChain's ChatOllama
        messages = [
            {"role": "system", "content": "You are a professional translator. Translate accurately and only provide the translation."},
            {"role": "user", "content": prompt}
        ]
        
        # Invoke the model
        response = ollama_client.invoke(messages)
        
        # Extract the response text
        response_text = response.content.strip()
        
        print(f"Ollama response [{direction}]: {response_text[:100]}...")
        return response_text
        
    except Exception as e:
        print(f"Error in llama_process_message: {e}")
        return f"Sorry, I encountered an error processing your message: {str(e)}"
