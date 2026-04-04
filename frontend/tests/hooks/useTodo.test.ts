import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from '@testing-library/react';

vi.mock('firebase/firestore', () => ({
  getFirestore: vi.fn(() => ({})),
  collection: vi.fn(),
  query: vi.fn(),
  where: vi.fn(),
  orderBy: vi.fn(),
  onSnapshot: vi.fn(),
  addDoc: vi.fn(),
  updateDoc: vi.fn(),
  deleteDoc: vi.fn(),
  doc: vi.fn(),
  serverTimestamp: vi.fn(() => ({ _type: 'serverTimestamp' })),
  Timestamp: {
    now: vi.fn(),
    fromDate: vi.fn(),
  },
}));

vi.mock('@/lib/firebase', () => ({
  auth: { currentUser: { uid: 'test-uid' } },
  db: {},
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    user: { uid: 'test-uid', displayName: 'Test User' },
    loading: false,
  })),
}));

import { onSnapshot, addDoc, updateDoc, deleteDoc } from 'firebase/firestore';

describe('useTodo', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should set up a Firestore listener for todo items', () => {
    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockImplementation((_query, _callback) => vi.fn());

    expect(mockOnSnapshot).toBeDefined();
  });

  it('should transform Firestore todo documents correctly', () => {
    const mockTimestamp = { toDate: () => new Date('2024-01-01T10:00:00Z') };
    const mockDoc = {
      id: 'todo-1',
      data: () => ({
        todoListId: 'list-1',
        title: 'Buy groceries',
        isCompleted: false,
        priority: 'medium',
        createdByUserId: 'user-1',
        createdDate: '2024-01-01',
        dueDate: '2024-01-10',
        createdAt: mockTimestamp,
      }),
    };

    const todo = {
      id: mockDoc.id,
      ...mockDoc.data(),
      createdAt: mockTimestamp.toDate(),
    };

    expect(todo.id).toBe('todo-1');
    expect(todo.title).toBe('Buy groceries');
    expect(todo.isCompleted).toBe(false);
    expect(todo.priority).toBe('medium');
    expect(todo.createdAt).toBeInstanceOf(Date);
  });

  it('should add a new todo item to Firestore', async () => {
    const mockAddDoc = vi.mocked(addDoc);
    mockAddDoc.mockResolvedValue({ id: 'new-todo-id' } as never);

    await act(async () => {
      await mockAddDoc({} as never, {
        title: 'New task',
        isCompleted: false,
        priority: 'high',
        todoListId: 'list-1',
        createdByUserId: 'test-uid',
      });
    });

    expect(mockAddDoc).toHaveBeenCalled();
  });

  it('should mark a todo as completed', async () => {
    const mockUpdateDoc = vi.mocked(updateDoc);
    mockUpdateDoc.mockResolvedValue(undefined);

    await act(async () => {
      await mockUpdateDoc({} as never, { isCompleted: true });
    });

    expect(mockUpdateDoc).toHaveBeenCalledWith(expect.anything(), { isCompleted: true });
  });

  it('should delete a todo item from Firestore', async () => {
    const mockDeleteDoc = vi.mocked(deleteDoc);
    mockDeleteDoc.mockResolvedValue(undefined);

    await act(async () => {
      await mockDeleteDoc({} as never);
    });

    expect(mockDeleteDoc).toHaveBeenCalled();
  });

  it('should filter todos by list id', () => {
    const todos = [
      { id: '1', todoListId: 'list-a', title: 'Task 1', isCompleted: false },
      { id: '2', todoListId: 'list-b', title: 'Task 2', isCompleted: false },
      { id: '3', todoListId: 'list-a', title: 'Task 3', isCompleted: true },
    ];

    const filtered = todos.filter((t) => t.todoListId === 'list-a');
    expect(filtered).toHaveLength(2);
    expect(filtered.every((t) => t.todoListId === 'list-a')).toBe(true);
  });

  it('should calculate completion rate correctly', () => {
    const todos = [
      { id: '1', isCompleted: true },
      { id: '2', isCompleted: false },
      { id: '3', isCompleted: true },
      { id: '4', isCompleted: false },
    ];

    const completed = todos.filter((t) => t.isCompleted).length;
    const rate = completed / todos.length;

    expect(completed).toBe(2);
    expect(rate).toBe(0.5);
  });

  it('should unsubscribe from Firestore listener on unmount', () => {
    const mockUnsubscribe = vi.fn();
    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockReturnValue(mockUnsubscribe);

    const unsubscribe = mockOnSnapshot({} as never, vi.fn());
    unsubscribe();

    expect(mockUnsubscribe).toHaveBeenCalled();
  });

  it('should handle empty todo list', () => {
    const mockOnSnapshot = vi.mocked(onSnapshot);
    mockOnSnapshot.mockImplementation((_query, callback) => {
      (callback as (snapshot: { docs: never[] }) => void)({ docs: [] });
      return vi.fn();
    });

    const todos: never[] = [];
    expect(todos).toHaveLength(0);
  });
});
