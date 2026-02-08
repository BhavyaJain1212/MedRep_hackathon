import whisper
import tempfile
import os

# Load model once at import time (using "base" for a good speed/accuracy balance)
_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(audio_file) -> str:
    """
    Transcribe audio using OpenAI's open-source Whisper model.
    
    Args:
        audio_file: A file-like object (e.g. from Flask request.files)
    
    Returns:
        The transcribed text as a string.
    """
    # Save to a temp file because whisper expects a file path
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        audio_file.save(tmp)
        tmp_path = tmp.name

    try:
        model = get_model()
        result = model.transcribe(tmp_path, fp16=False)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)
