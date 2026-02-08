import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Stethoscope, Users, Mic, MicOff, Loader2 } from "lucide-react";
import { sendQuery, transcribeAudio } from "../services/api";
import MedicalResponse from "../components/MedicalResponse"; // Import the new component

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <div className="typing-dot w-2 h-2 rounded-full bg-blue-400" />
      <div className="typing-dot w-2 h-2 rounded-full bg-blue-400" />
      <div className="typing-dot w-2 h-2 rounded-full bg-blue-400" />
    </div>
  );
}

function ChatBubble({ message }) {
  const isUser = message.role === "user";

  // Check if content is structured object or string
  const isStructured = typeof message.content === 'object' && message.content !== null;

  return (
    <div
      className={`animate-message-in flex gap-3 ${isUser ? "flex-row-reverse" : ""
        }`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser
          ? "bg-sky-500/20 text-sky-400"
          : "bg-blue-500/20 text-blue-400"
          }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser
          ? "bg-blue-500/20 text-slate-100 rounded-tr-md"
          : "glass-card text-slate-200 rounded-tl-md w-full"
          }`}
      >
        {isStructured ? (
          <MedicalResponse data={message.content} />
        ) : (
          <div>
            {message.content}
            {message.sources && message.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-navy-600/40">
                <p className="text-[11px] text-slate-400 mb-1">Sources:</p>
                <div className="flex flex-wrap gap-1">
                  {message.sources.map((s, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-[10px] rounded-full bg-navy-700/60 text-slate-400"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const SUGGESTIONS = [
  "Compare Atorvastatin vs Rosuvastatin for a diabetic patient",
  "What are the Jan Aushadhi alternatives for Clopidogrel?",
  "Can a patient take Metformin with Ibuprofen?",
  "Is Amlodipine covered under CGHS?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("doctor");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text) {
    const query = text || input.trim();
    if (!query) return;

    const userMsg = { role: "user", content: query };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendQuery(query, mode);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data, // Store full structured object
          // Sources are now inside the content object, but keeping this for backward compatibility if needed
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      let errorMsg;
      try {
        const res = await fetch("/api/health");
        if (res.ok) {
          errorMsg = "The AI model is temporarily rate-limited. Please wait a few seconds and try again.";
        } else {
          errorMsg = "Sorry, the backend is not connected yet. Please make sure the Flask server is running.";
        }
      } catch {
        errorMsg = "Sorry, the backend is not connected yet. Please make sure the Flask server is running.";
      }
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: errorMsg,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        setIsTranscribing(true);
        try {
          const { text } = await transcribeAudio(blob);
          if (text) setInput((prev) => (prev ? prev + " " + text : text));
        } catch (err) {
          console.error("Transcription failed:", err);
        } finally {
          setIsTranscribing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-navy-700/40">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">
            AI Medical Representative
          </h2>
          <p className="text-xs text-slate-400">
            Ask about drugs, interactions, pricing, or reimbursement
          </p>
        </div>
        {/* Mode toggle */}
        <div className="flex items-center gap-1 p-1 rounded-lg bg-navy-800 border border-navy-700/50">
          <button
            onClick={() => setMode("doctor")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "doctor"
              ? "bg-blue-500/20 text-blue-400"
              : "text-slate-400 hover:text-slate-300"
              }`}
          >
            <Stethoscope className="w-3.5 h-3.5" />
            Doctor
          </button>
          <button
            onClick={() => setMode("patient")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "patient"
              ? "bg-teal-500/20 text-teal-400"
              : "text-slate-400 hover:text-slate-300"
              }`}
          >
            <Users className="w-3.5 h-3.5" />
            Patient
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 mb-4 rounded-2xl bg-gradient-to-br from-blue-500/20 to-sky-500/10 flex items-center justify-center border border-blue-500/10">
              <Bot className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-200 mb-1">
              How can I help you today?
            </h3>
            <p className="text-sm text-slate-400 mb-6 max-w-md">
              I can provide drug information, check interactions, compare prices
              with Jan Aushadhi generics, and guide you through reimbursement
              options.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  className="text-left px-4 py-3 rounded-xl text-xs text-slate-300 glass-card hover:border-blue-500/30 transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <ChatBubble key={i} message={m} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-navy-700/40">
        <div className="flex items-end gap-3 max-w-3xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about any drug, interaction, or scheme..."
              className="w-full px-4 py-3 rounded-xl bg-navy-800 border border-navy-600/50 text-sm text-slate-200 placeholder-slate-500 resize-none input-glow focus:outline-none focus:border-blue-500/40 transition-all"
            />
          </div>
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={loading || isTranscribing}
            className={`flex items-center justify-center w-11 h-11 rounded-xl transition-all ${
              isRecording
                ? "bg-red-500/80 text-white animate-pulse hover:bg-red-600"
                : isTranscribing
                ? "bg-navy-700 text-slate-400 cursor-wait"
                : "bg-navy-700 text-slate-300 hover:bg-navy-600 hover:text-white"
            } disabled:opacity-40 disabled:cursor-not-allowed`}
            title={isRecording ? "Stop recording" : isTranscribing ? "Transcribing..." : "Voice input"}
          >
            {isTranscribing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRecording ? (
              <MicOff className="w-4 h-4" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-r from-blue-500 to-sky-500 text-white hover:from-blue-600 hover:to-sky-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
