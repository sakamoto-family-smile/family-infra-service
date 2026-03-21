'use client';

import { useParams, useRouter } from 'next/navigation';
import { useChat } from '@/hooks/useChat';
import { useFirestoreDocument } from '@/hooks/useFirestore';
import { useAuth } from '@/hooks/useAuth';
import { MessageList } from '@/components/chat/MessageList';
import { MessageInput } from '@/components/chat/MessageInput';
import { Loading } from '@/components/ui/Loading';
import { ChatRoom } from '@/types/chat';
import Link from 'next/link';

export default function ChatRoomPage() {
  const params = useParams();
  const router = useRouter();
  const roomId = params.roomId as string;
  const { user } = useAuth();

  const { data: room, loading: roomLoading } = useFirestoreDocument<ChatRoom>(`chat_rooms/${roomId}`);
  const { messages, loading: messagesLoading, sendMessage, addReaction } = useChat(roomId);

  if (roomLoading) {
    return <Loading fullScreen />;
  }

  if (!room) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <p className="text-gray-500">チャットルームが見つかりません</p>
        <Link href="/chat" className="mt-4 text-blue-600 hover:underline text-sm">
          チャット一覧に戻る
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <button
          onClick={() => router.back()}
          className="rounded-full p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700 md:hidden"
        >
          <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600 font-semibold">
          {room.name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h2 className="font-semibold text-gray-900">{room.name}</h2>
          <p className="text-xs text-gray-500">{room.members.length}人のメンバー</p>
        </div>
      </div>

      <MessageList
        messages={messages}
        currentUserId={user?.uid || ''}
        loading={messagesLoading}
        onReact={addReaction}
      />

      <MessageInput onSend={sendMessage} />
    </div>
  );
}
