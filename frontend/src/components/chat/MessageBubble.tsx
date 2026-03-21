'use client';

import { Avatar } from '@/components/ui/Avatar';
import { ChatMessage } from '@/types/chat';
import { formatTime } from '@/lib/utils';

interface MessageBubbleProps {
  message: ChatMessage;
  isOwn: boolean;
  onReact?: (messageId: string, emoji: string) => void;
}

export function MessageBubble({ message, isOwn, onReact }: MessageBubbleProps) {
  if (message.deleted) {
    return (
      <div className="flex items-center gap-2 px-4 py-1">
        <span className="text-sm italic text-gray-400">このメッセージは削除されました</span>
      </div>
    );
  }

  return (
    <div className={`flex items-end gap-2 px-4 py-1 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
      {!isOwn && (
        <Avatar
          src={message.senderPhotoURL}
          name={message.senderName}
          size="xs"
          className="flex-shrink-0"
        />
      )}

      <div className={`flex flex-col max-w-[70%] ${isOwn ? 'items-end' : 'items-start'}`}>
        {!isOwn && (
          <span className="mb-1 text-xs text-gray-500 px-1">{message.senderName}</span>
        )}

        <div
          className={`relative rounded-2xl px-4 py-2 ${
            isOwn
              ? 'bg-blue-600 text-white rounded-br-sm'
              : 'bg-white text-gray-900 rounded-bl-sm shadow-sm border border-gray-100'
          }`}
        >
          {message.type === 'text' && (
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
          )}
          {message.type === 'image' && message.imageURL && (
            <img
              src={message.imageURL}
              alt="Image"
              className="max-w-full rounded-lg"
            />
          )}
        </div>

        {message.reactions.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {message.reactions.map((reaction) => (
              <button
                key={reaction.emoji}
                onClick={() => onReact?.(message.id, reaction.emoji)}
                className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs hover:bg-gray-200"
              >
                <span>{reaction.emoji}</span>
                <span className="text-gray-600">{reaction.userIds.length}</span>
              </button>
            ))}
          </div>
        )}

        <span className={`mt-1 text-xs text-gray-400 px-1`}>
          {formatTime(message.createdAt)}
        </span>
      </div>
    </div>
  );
}
