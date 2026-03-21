'use client';

import Link from 'next/link';
import { ChatRoom } from '@/types/chat';
import { formatRelativeTime, truncate } from '@/lib/utils';

interface ChatRoomCardProps {
  room: ChatRoom;
  unreadCount?: number;
}

export function ChatRoomCard({ room, unreadCount }: ChatRoomCardProps) {
  return (
    <Link
      href={`/chat/${room.id}`}
      className="flex items-center gap-4 rounded-lg bg-white p-4 shadow-sm border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all"
    >
      <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 text-xl font-semibold">
        {room.name.charAt(0).toUpperCase()}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-semibold text-gray-900 truncate">{room.name}</h3>
          {room.lastMessageAt && (
            <span className="flex-shrink-0 text-xs text-gray-400">
              {formatRelativeTime(room.lastMessageAt)}
            </span>
          )}
        </div>

        <div className="flex items-center justify-between gap-2 mt-1">
          <p className="text-sm text-gray-500 truncate">
            {room.lastMessage
              ? truncate(room.lastMessage.content, 40)
              : room.description || 'まだメッセージはありません'}
          </p>
          {unreadCount !== undefined && unreadCount > 0 && (
            <span className="flex-shrink-0 rounded-full bg-blue-600 px-2 py-0.5 text-xs font-medium text-white">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </div>

        <p className="mt-1 text-xs text-gray-400">{room.members.length}人のメンバー</p>
      </div>
    </Link>
  );
}
