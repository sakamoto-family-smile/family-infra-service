'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { ChatRoomCard } from '@/components/chat/ChatRoomCard';
import { Loading } from '@/components/ui/Loading';
import { Button } from '@/components/ui/Button';
import { useFirestoreCollection } from '@/hooks/useFirestore';
import { useAuth } from '@/hooks/useAuth';
import { ChatRoom } from '@/types/chat';

export default function ChatPage() {
  const { user } = useAuth();
  const { data: rooms, loading } = useFirestoreCollection<ChatRoom>('chat_rooms');

  if (loading) {
    return (
      <div className="flex h-full flex-col">
        <Header title="チャット" />
        <div className="flex flex-1 items-center justify-center">
          <Loading text="チャットルームを読み込み中..." />
        </div>
      </div>
    );
  }

  const userRooms = rooms.filter(
    (room) => user && room.members.includes(user.uid)
  );

  return (
    <div className="flex h-full flex-col">
      <Header title="チャット" />

      <div className="flex-1 p-4 md:p-6 space-y-4">
        {userRooms.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="text-5xl mb-4">💬</div>
            <h3 className="text-lg font-semibold text-gray-900">チャットルームがありません</h3>
            <p className="mt-2 text-sm text-gray-500">
              家族メンバーとチャットを始めましょう
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {userRooms.map((room) => (
              <ChatRoomCard key={room.id} room={room} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
