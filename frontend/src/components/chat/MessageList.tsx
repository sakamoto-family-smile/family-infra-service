'use client';

import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { Loading } from '@/components/ui/Loading';
import { ChatMessage } from '@/types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  currentUserId: string;
  loading?: boolean;
  onReact?: (messageId: string, emoji: string) => void;
}

export function MessageList({ messages, currentUserId, loading, onReact }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <Loading text="メッセージを読み込み中..." />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 text-sm">まだメッセージはありません</p>
          <p className="text-gray-400 text-xs mt-1">最初のメッセージを送ってみましょう！</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto py-4 space-y-1">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          isOwn={message.senderId === currentUserId}
          onReact={onReact}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
