from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gen_ai_components.combined_chaining import chain, get_session_history, chain_user
from gen_ai_components.speech_to_text import transcribe_audio
from gen_ai_components.serp import serp_search

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/api/query", methods=["POST"])
def query():
    try:
        data = request.get_json()
        print(data)

        query_text = data.get("query")
        session_id = data.get("session_id", "default_session") # Get session_id

        # for now mode methodology is not set
        mode = data.get("mode")

        if mode == "doctor":
            # Get history manually
            chat_history = get_session_history(session_id)
            print(chat_history)
            
            # Invoke chain with manual history
            result = chain.invoke({
                "user_query": query_text,
                "history": chat_history.messages
            })
            
            
            # Add to history manually (Store summary to avoid huge JSONs)
            chat_history.add_user_message(query_text)
            chat_history.add_ai_message(result.summary)
        
            # Convert Pydantic model to dict for JSON serialization
            response_data = result.model_dump()
            
            return jsonify(response_data)
        
        elif mode == "patient":
            result = chain_user.invoke({
                "query": query_text,
            })
            response_data = result.model_dump()
            
            return jsonify(response_data)
        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio to text using open-source Whisper."""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        text = transcribe_audio(audio_file)

        if not text:
            return jsonify({"error": "Could not transcribe audio"}), 400

        return jsonify({"text": text})

    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def search():
    """Perform a web search using SerpAPI."""
    try:
        data = request.get_json()
        query_text = data.get("query")
        
        if not query_text:
            return jsonify({"error": "No query provided"}), 400
            
        results = serp_search(query_text, num=7)
        
        if isinstance(results, dict) and "error" in results:
            return jsonify(results), 500
            
        return jsonify({"results": results})

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)