'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
  addDoc,
  updateDoc,
  arrayUnion,
  arrayRemove,
  doc,
  serverTimestamp,
  Timestamp,
} from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { useAuth } from './useAuth';
import { ChatMessage, MessageReaction } from '@/types/chat';

interface UseChatResult {
  messages: ChatMessage[];
  loading: boolean;
  error: Error | null;
  sendMessage: (content: string, type?: ChatMessage['type']) => Promise<void>;
  addReaction: (messageId: string, emoji: string) => Promise<void>;
  removeReaction: (messageId: string, emoji: string) => Promise<void>;
}

export function useChat(roomId: string, messageLimit = 50): UseChatResult {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!roomId) {
      setLoading(false);
      return;
    }

    const messagesRef = collection(db, `chat_rooms/${roomId}/messages`);
    const q = query(messagesRef, orderBy('createdAt', 'asc'), limit(messageLimit));

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const msgs = snapshot.docs.map((docSnap) => {
          const data = docSnap.data();
          return {
            id: docSnap.id,
            ...data,
            createdAt: data.createdAt instanceof Timestamp
              ? data.createdAt.toDate()
              : new Date(data.createdAt),
            updatedAt: data.updatedAt instanceof Timestamp
              ? data.updatedAt.toDate()
              : data.updatedAt ? new Date(data.updatedAt) : undefined,
          } as ChatMessage;
        });
        setMessages(msgs);
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [roomId, messageLimit]);

  const sendMessage = useCallback(
    async (content: string, type: ChatMessage['type'] = 'text') => {
      if (!user || !roomId) return;

      const messagesRef = collection(db, `chat_rooms/${roomId}/messages`);
      await addDoc(messagesRef, {
        roomId,
        senderId: user.uid,
        senderName: user.displayName || 'Unknown',
        senderPhotoURL: user.photoURL,
        content,
        type,
        reactions: [],
        createdAt: serverTimestamp(),
        deleted: false,
      });
    },
    [user, roomId]
  );

  const addReaction = useCallback(
    async (messageId: string, emoji: string) => {
      if (!user || !roomId) return;

      const messageRef = doc(db, `chat_rooms/${roomId}/messages`, messageId);
      const newReaction: MessageReaction = { emoji, userIds: [user.uid] };
      await updateDoc(messageRef, { reactions: arrayUnion(newReaction) });
    },
    [user, roomId]
  );

  const removeReaction = useCallback(
    async (messageId: string, emoji: string) => {
      if (!user || !roomId) return;

      const messageRef = doc(db, `chat_rooms/${roomId}/messages`, messageId);
      const reactionToRemove: MessageReaction = { emoji, userIds: [user.uid] };
      await updateDoc(messageRef, { reactions: arrayRemove(reactionToRemove) });
    },
    [user, roomId]
  );

  return { messages, loading, error, sendMessage, addReaction, removeReaction };
}
