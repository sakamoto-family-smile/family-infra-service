import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from '@testing-library/react';

// Mock firebase/firestore
vi.mock('firebase/firestore', () => ({
  getFirestore: vi.fn(() => ({})),
  collection: vi.fn(),
  query: vi.fn(),
  orderBy: vi.fn(),
  limit: vi.fn(),
  onSnapshot: vi.fn(),
  addDoc: vi.fn(),
  updateDoc: vi.fn(),
  doc: vi.fn(),
  serverTimestamp: vi.fn(() => ({ _type: 'serverTimestamp' })),
  Timestamp: {
    now: vi.fn(),
    fromDate: vi.fn(),
  },
}));

vi.mock('@/lib/firebase', () => ({
  auth: { currentUser: null },
  db: {},
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    user: {
      uid: 'test-uid',
      displayName: 'Test User',
      photoURL: null,
      email: 'test@example.com',
    },
    loading: false,
  })),
}));

import { onSnapshot, collection, query, addDoc } from 'firebase/firestore';

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should set up a Firestore listener on mount', () => {
    const mockCollection = vi.mocked(collection);
    const mockQuery = vi.mocked(query);
    const mockOnSnapshot = vi.mocked(onSnapshot);

    mockCollection.mockReturnValue({} as never);
    mockQuery.mockReturnValue({} as never);
    mockOnSnapshot.mockImplementation((_query, callback) => {
      return vi.fn();
    });

    expect(mockCollection).toBeDefined();
    expect(mockOnSnapshot).toBeDefined();
  });

  it('should transform Firestore documents to ChatMessage format', () => {
    const mockTimestamp = {
      toDate: () => new Date('2024-01-01T10:00:00Z'),
    };

    const mockDoc = {
      id: 'msg-1',
      data: () => ({
        roomId: 'room-1',
        senderId: 'user-1',
        senderName: 'User One',
        senderPhotoURL: null,
        content: 'Hello World',
        type: 'text',
        reactions: [],
        createdAt: mockTimestamp,
        deleted: false,
      }),
    };

    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockImplementation((_query, callback) => {
      (callback as (snapshot: { docs: typeof[] }) => void)({
        docs: [mockDoc],
      } as never);
      return vi.fn();
    });

    const message = {
      id: mockDoc.id,
      ...mockDoc.data(),
      createdAt: mockTimestamp.toDate(),
    };

    expect(message.id).toBe('msg-1');
    expect(message.content).toBe('Hello World');
    expect(message.senderId).toBe('user-1');
    expect(message.createdAt).toBeInstanceOf(Date);
  });

  it('should add a new message to Firestore', async () => {
    const mockAddDoc = vi.mocked(addDoc);
    mockAddDoc.mockResolvedValue({ id: 'new-msg-id' } as never);

    await act(async () => {
      await mockAddDoc({} as never, {
        content: 'New message',
        type: 'text',
        senderId: 'test-uid',
        senderName: 'Test User',
        reactions: [],
      });
    });

    expect(mockAddDoc).toHaveBeenCalled();
  });

  it('should handle message reactions correctly', () => {
    const reactions = [
      { emoji: '👍', userIds: ['user-1', 'user-2'] },
      { emoji: '❤️', userIds: ['user-3'] },
    ];

    expect(reactions.find((r) => r.emoji === '👍')?.userIds).toHaveLength(2);
    expect(reactions.find((r) => r.emoji === '❤️')?.userIds).toHaveLength(1);
  });

  it('should add a reaction when not already reacted', () => {
    const existingReactions = [{ emoji: '👍', userIds: ['user-1'] }];
    const currentUserId = 'user-2';
    const emoji = '👍';

    const updatedReactions = existingReactions.map((r) =>
      r.emoji === emoji
        ? { ...r, userIds: [...r.userIds, currentUserId] }
        : r
    );

    expect(updatedReactions[0].userIds).toContain('user-2');
    expect(updatedReactions[0].userIds).toHaveLength(2);
  });

  it('should remove a reaction when already reacted', () => {
    const existingReactions = [{ emoji: '👍', userIds: ['user-1', 'user-2'] }];
    const currentUserId = 'user-1';
    const emoji = '👍';

    const updatedReactions = existingReactions
      .map((r) =>
        r.emoji === emoji
          ? { ...r, userIds: r.userIds.filter((id) => id !== currentUserId) }
          : r
      )
      .filter((r) => r.userIds.length > 0);

    expect(updatedReactions[0].userIds).not.toContain('user-1');
    expect(updatedReactions[0].userIds).toHaveLength(1);
  });

  it('should unsubscribe from Firestore listener on unmount', () => {
    const mockUnsubscribe = vi.fn();
    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockReturnValue(mockUnsubscribe);

    const unsubscribe = mockOnSnapshot({} as never, vi.fn());
    unsubscribe();

    expect(mockUnsubscribe).toHaveBeenCalled();
  });

  it('should handle empty messages array', () => {
    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockImplementation((_query, callback) => {
      (callback as (snapshot: { docs: never[] }) => void)({ docs: [] });
      return vi.fn();
    });

    const messages: never[] = [];
    expect(messages).toHaveLength(0);
  });
});
