"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Loader } from "lucide-react";
import ChatMessage from "@/components/chat/ChatMessage";
import { ChatMessage as ChatMessageType } from "@/types";
import { MOCK_CHAT_MESSAGES } from "@/utils/mockData";

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>(MOCK_CHAT_MESSAGES);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const suggestedPrompts = [
    "Should I buy Reliance?",
    "Compare TCS vs Infosys.",
    "Summarize HDFC Bank.",
    "Best dividend stocks.",
  ];

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      content: inputValue,
      role: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        content: `Based on your query about "${inputValue}", here's my analysis. The current market conditions suggest a balanced approach. Consider your risk tolerance and investment horizon before making any decisions.`,
        role: "assistant",
        timestamp: new Date().toISOString(),
        citations: [
          {
            id: "c1",
            title: "Latest Market Report",
            source: "Moneycontrol",
            url: "https://moneycontrol.com",
            publishedAt: new Date().toISOString(),
            snippet: "Current market analysis shows mixed signals...",
          },
        ],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <span className="text-2xl">🤖</span>
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              AI Equity Analyst
            </h1>
            <p className="text-text-tertiary mb-8 max-w-md">
              Ask me anything about Indian stocks, market trends, and investment strategies.
            </p>

            <div className="space-y-3 w-full max-w-md">
              <p className="text-sm text-text-tertiary mb-4">Try asking:</p>
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => {
                    setInputValue(prompt);
                  }}
                  className="w-full p-4 rounded-xl bg-card border border-border text-text-primary hover:border-primary/30 transition-all text-left text-sm hover:bg-sidebar"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-success/20 text-success flex items-center justify-center flex-shrink-0">
                  <Loader className="w-4 h-4 animate-spin" />
                </div>
                <div className="inline-block rounded-xl px-4 py-3 bg-card border border-border">
                  <p className="text-sm text-text-tertiary">Analyzing...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-6 border-t border-border bg-card">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Ask about stocks, sectors, or investment strategies..."
            className="input-base flex-1"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="btn-primary flex items-center justify-center w-12 h-12 flex-shrink-0"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
