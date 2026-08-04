"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Loader2, MessageSquare, User, Bot } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const questionInputRef = useRef<HTMLTextAreaElement>(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!company.trim() || !question.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setIsLoading(true);
    setError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/chat/`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          company: company.trim(),
          question: question,
        }),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to get AI response");
      }

      const data = await response.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError("Failed to get AI response. Please try again.");
      console.error("Error sending message:", err);
    } finally {
      setIsLoading(false);
      questionInputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center gap-3">
          <MessageSquare className="w-6 h-6 text-primary" />
          <h1 className="text-xl font-bold text-text-primary">AI Equity Analyst</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Company Input */}
        <div className="w-80 border-r border-border bg-card p-6 flex flex-col">
          <h2 className="text-sm font-semibold text-text-primary mb-4">
            Company Analysis
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Company Symbol
              </label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g., TCS, RELIANCE"
                className="input-base w-full"
                disabled={isLoading}
              />
            </div>
            <div className="text-xs text-text-tertiary">
              Enter the company ticker symbol to analyze specific stocks.
            </div>
          </div>
        </div>

        {/* Right Side - Conversation */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Bot className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-2xl font-bold text-text-primary mb-2">
                  AI Equity Research
                </h2>
                <p className="text-text-tertiary max-w-md mb-4">
                  Enter a company symbol and ask questions about its financials,
                  news, or investment outlook.
                </p>
                <div className="text-sm text-text-tertiary">
                  Try: <span className="text-primary font-medium">TCS</span> -{" "}
                  <span className="text-primary font-medium">
                    Should I invest?
                  </span>
                </div>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4" />
                      </div>
                    )}
                    <div
                      className={`max-w-2xl rounded-2xl px-4 py-3 ${
                        message.role === "user"
                          ? "bg-primary text-white"
                          : "bg-card border border-border"
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>
                    </div>
                    {message.role === "user" && (
                      <div className="w-8 h-8 rounded-full bg-success/20 text-success flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0">
                      <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                    <div className="bg-card border border-border rounded-2xl px-4 py-3">
                      <p className="text-sm text-text-tertiary">Analyzing...</p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="px-6 pb-2">
              <div className="bg-error/10 border border-error text-error px-4 py-3 rounded-lg">
                {error}
              </div>
            </div>
          )}

          {/* Question Input */}
          <div className="p-6 border-t border-border bg-card">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-3">
                <textarea
                  ref={questionInputRef}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about the company's financials, news, or investment outlook..."
                  rows={1}
                  className="input-base flex-1 resize-none min-h-[48px] max-h-32"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !company.trim() || !question.trim()}
                  className="btn-primary flex items-center justify-center w-12 h-12 flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
              <div className="text-xs text-text-tertiary mt-2">
                Press <span className="font-medium">Enter</span> to send,{" "}
                <span className="font-medium">Shift + Enter</span> for newline
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
