"use client";

import { ChatMessage as ChatMessageType } from "@/types";
import { formatTime } from "@/utils/format";
import { Brain, User } from "lucide-react";
import CitationCard from "./CitationCard";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? "bg-primary/20 text-primary"
              : "bg-success/20 text-success"
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4" />
          ) : (
            <Brain className="w-4 h-4" />
          )}
        </div>
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-md ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block rounded-xl px-4 py-3 ${
            isUser
              ? "bg-primary text-white"
              : "bg-card border border-border text-text-primary"
          }`}
        >
          <p className="text-sm">{message.content}</p>
        </div>

        <p className="text-xs text-text-tertiary mt-2">
          {formatTime(message.timestamp)}
        </p>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 space-y-3">
            {message.citations.map((citation) => (
              <CitationCard key={citation.id} citation={citation} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
