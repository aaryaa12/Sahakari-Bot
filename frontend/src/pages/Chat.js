import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { chatAPI, documentsAPI } from "../services/api";
import logo from "../assets/logo.png";

const Chat = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [docStatus, setDocStatus] = useState(null);
  const [animateTitle, setAnimateTitle] = useState(true);
  const [profileOpen, setProfileOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const statusLabel = docStatus?.has_documents
    ? `${docStatus.files_count} document${
        docStatus.files_count !== 1 ? "s" : ""
      } indexed`
    : docStatus?.folder_count > 0
    ? `${docStatus.folder_count} file${
        docStatus.folder_count !== 1 ? "s" : ""
      } found`
    : docStatus
    ? "No documents yet"
    : "Checking documents...";
  const statusIcon = docStatus?.has_documents
    ? "✅"
    : docStatus?.folder_count > 0
    ? "⚠️"
    : "📂";
  const canReload =
    docStatus && !docStatus.has_documents && docStatus.folder_count > 0;
  const userInitial = user?.username?.[0]?.toUpperCase() || "U";

  useEffect(() => {
    loadDocumentStatus();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => setAnimateTitle(false), 2600);
    return () => clearTimeout(timeout);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadDocumentStatus = async () => {
    try {
      const statusResponse = await documentsAPI.status();
      console.log("📊 Document Status:", statusResponse.data);
      setDocStatus(statusResponse.data);
    } catch (error) {
      console.error("❌ Error loading document status:", error);
      // Set default status on error
      setDocStatus({
        has_documents: false,
        folder_count: 0,
        files_count: 0,
      });
    }
  };

  const handleReloadDocuments = async () => {
    try {
      setLoading(true);
      await documentsAPI.reload(false);
      await loadDocumentStatus();
      const successMsg = {
        id: Date.now(),
        type: "system",
        content: "✅ Documents reloaded successfully!",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, successMsg]);
    } catch (error) {
      const errorMsg = {
        id: Date.now(),
        type: "error",
        content:
          error.response?.data?.detail ||
          "Failed to reload documents. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const sendMessage = async (message) => {
    if (!message.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: message.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const history = messages
        .filter((msg) => msg.type === "user" || msg.type === "bot")
        .slice(-8)
        .map((msg) => ({
          role: msg.type === "user" ? "user" : "assistant",
          content: msg.content,
        }));

      const response = await chatAPI.query({ query: message.trim(), history });
      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.data.answer,
        citations: response.data.citations,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: "error",
        content:
          error.response?.data?.detail ||
          "Failed to get response. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    await sendMessage(input);
  };

  const handlePromptClick = async (prompt) => {
    setInput(prompt);
    await sendMessage(prompt);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0b1220] text-slate-100">
      {/* Header */}
      <header className="bg-[#0b1220]/80 border-b border-slate-900 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="flex flex-wrap gap-4 justify-between items-center py-3">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center shadow-sm overflow-hidden">
                <img
                  src={logo}
                  alt="Sahakari Bot"
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="space-y-0.5">
                <h1 className="text-sm font-semibold text-slate-100 tracking-tight">
                  Sahakari Bot
                </h1>
                <p className="text-[11px] text-slate-400 flex items-center gap-2">
                  <span>{statusIcon}</span>
                  {statusLabel}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {canReload && (
                <button
                  onClick={handleReloadDocuments}
                  disabled={loading}
                  className="px-3 py-1.5 text-xs font-medium text-slate-200 bg-slate-800 rounded-lg hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:opacity-50"
                  title="Reload documents from folder"
                >
                  Reload
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
        <div className="max-w-3xl w-full mx-auto">
          {messages.length === 0 ? (
            <div className="text-center mt-10 sm:mt-16">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-slate-900 rounded-3xl mb-8 shadow-lg overflow-hidden mx-auto">
                <img
                  src={logo}
                  alt="Sahakari Bot"
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-slate-400 text-sm sm:text-base mb-2">
                Hi, {user?.username || "there"}
              </p>
              <h2
                className={`text-2xl sm:text-3xl font-semibold text-slate-100 mb-3 inline-block max-w-full ${
                  animateTitle ? "typing-once" : ""
                }`}
                style={animateTitle ? { "--chars": 29 } : undefined}
              >
                Can I help you with anything?
              </h2>
              <p className="text-slate-400 mb-8 max-w-xl mx-auto text-sm sm:text-base">
                Get clear, citation-backed answers on compliance, audits, and
                risk controls. Ask anything about your policy library to get
                started.
              </p>
              {!docStatus?.has_documents && (
                <div className="max-w-xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-4 mb-6 text-left shadow-sm">
                  {docStatus?.folder_count > 0 ? (
                    <div>
                      <p className="text-sm text-slate-300 mb-2">
                        ⚠️ Found {docStatus.folder_count} file
                        {docStatus.folder_count !== 1 ? "s" : ""} in your
                        folder, but they are not processed yet.
                      </p>
                      <button
                        onClick={handleReloadDocuments}
                        disabled={loading}
                        className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-full font-medium transition disabled:opacity-50"
                      >
                        {loading ? "Processing..." : "Process documents"}
                      </button>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-300">
                      ⚠️ No documents found. Add files to{" "}
                      <code className="bg-slate-800 px-1 rounded">
                        data/documents/
                      </code>{" "}
                      folder and restart the server or click reload.
                    </p>
                  )}
                </div>
              )}
              <div className="grid gap-3 sm:grid-cols-3 max-w-3xl mx-auto text-left">
                {[
                  "Which policies define incident response timelines?",
                  "Summarize our vendor risk assessment requirements.",
                  "What controls cover data retention and deletion?",
                ].map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => handlePromptClick(prompt)}
                    className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-sm text-slate-200 shadow-sm text-left hover:border-blue-500/40 hover:bg-slate-800 transition"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 pb-6">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className="w-full"
                >
                  <div
                    className={`max-w-3xl mx-auto px-4 sm:px-6 flex ${
                      msg.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.type === "user" ? (
                      <div className="flex items-end gap-3 max-w-[78%]">
                        <div className="bg-slate-900 border border-slate-800 rounded-2xl px-4 py-3 text-sm sm:text-base text-slate-100 shadow-sm">
                          <p className="whitespace-pre-wrap leading-relaxed">
                            {msg.content}
                          </p>
                        </div>
                        <div className="w-8 h-8 rounded-full bg-blue-500 text-white text-xs font-semibold flex items-center justify-center">
                          {userInitial}
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start gap-3 w-full">
                        <div className="w-8 h-8 min-w-[32px] rounded-full bg-slate-100 text-slate-900 flex items-center justify-center overflow-hidden">
                          {msg.type === "error" ? (
                            <span className="text-xs font-semibold">!</span>
                          ) : (
                            <img
                              src={logo}
                              alt="Sahakari Bot"
                              className="w-4 h-4 object-contain"
                            />
                          )}
                        </div>
                        <div className="text-sm sm:text-base text-slate-100 leading-relaxed flex-1">
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="max-w-3xl mx-auto px-4 sm:px-6 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-900 flex items-center justify-center overflow-hidden">
                    <img src={logo} alt="Sahakari Bot" className="w-4 h-4 object-contain" />
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-[#0b1220] border-t border-slate-800">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4">
          <form
            onSubmit={handleSend}
            className="bg-slate-950 border border-slate-800 rounded-2xl shadow-sm p-2 flex items-end gap-2"
          >
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Message Sahakari Bot..."
              className="flex-1 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none resize-none bg-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? (
                <svg
                  className="w-5 h-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19V5m0 0l-6 6m6-6l6 6"
                  />
                </svg>
              )}
            </button>
          </form>
          <p className="text-[11px] text-slate-500 mt-3 text-center">
            Sahakari Bot can make mistakes. Verify critical information.
          </p>
        </div>
      </div>

      {/* Bottom-left profile */}
      <div className="fixed bottom-4 left-4 z-20 animate-float-slow">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-lg w-64 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:border-blue-500/40">
          <button
            type="button"
            onClick={() => setProfileOpen((prev) => !prev)}
            className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/80 rounded-2xl transition"
            aria-expanded={profileOpen}
          >
            <span className="w-9 h-9 rounded-full bg-slate-100 text-slate-900 text-xs font-semibold flex items-center justify-center">
              {userInitial}
            </span>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-100 truncate">
                {user?.username || "User"}
              </p>
              <p className="text-xs text-slate-400 truncate">
                {user?.email || "Signed in"}
              </p>
            </div>
            <svg
              className={`w-4 h-4 text-slate-400 ml-auto transition ${
                profileOpen ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          {profileOpen && (
            <div className="border-t border-slate-800 px-2 py-2">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-200 hover:text-white hover:bg-slate-800 rounded-lg transition"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
                  />
                </svg>
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;
