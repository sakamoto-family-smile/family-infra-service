'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  collection,
  query,
  orderBy,
  onSnapshot,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  serverTimestamp,
  Timestamp,
} from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { useAuth } from './useAuth';
import { TodoItem, TodoList, TodoPriority, TodoStatus } from '@/types/todo';

interface UseTodoListsResult {
  todoLists: TodoList[];
  loading: boolean;
  error: Error | null;
  createList: (data: Pick<TodoList, 'title' | 'description' | 'color' | 'icon'>) => Promise<string>;
  updateList: (listId: string, data: Partial<TodoList>) => Promise<void>;
  deleteList: (listId: string) => Promise<void>;
}

export function useTodoLists(familyId: string): UseTodoListsResult {
  const { user } = useAuth();
  const [todoLists, setTodoLists] = useState<TodoList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!familyId) {
      setLoading(false);
      return;
    }

    const listsRef = collection(db, `families/${familyId}/todo_lists`);
    const q = query(listsRef, orderBy('createdAt', 'asc'));

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const lists = snapshot.docs.map((docSnap) => {
          const data = docSnap.data();
          return {
            id: docSnap.id,
            ...data,
            createdAt: data.createdAt instanceof Timestamp ? data.createdAt.toDate() : new Date(),
            updatedAt: data.updatedAt instanceof Timestamp ? data.updatedAt.toDate() : new Date(),
          } as TodoList;
        });
        setTodoLists(lists);
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [familyId]);

  const createList = async (
    data: Pick<TodoList, 'title' | 'description' | 'color' | 'icon'>
  ): Promise<string> => {
    if (!user) throw new Error('User not authenticated');
    const listsRef = collection(db, `families/${familyId}/todo_lists`);
    const docRef = await addDoc(listsRef, {
      ...data,
      familyId,
      memberIds: [user.uid],
      createdBy: user.uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
    return docRef.id;
  };

  const updateList = async (listId: string, data: Partial<TodoList>): Promise<void> => {
    const docRef = doc(db, `families/${familyId}/todo_lists`, listId);
    await updateDoc(docRef, { ...data, updatedAt: serverTimestamp() });
  };

  const deleteList = async (listId: string): Promise<void> => {
    const docRef = doc(db, `families/${familyId}/todo_lists`, listId);
    await deleteDoc(docRef);
  };

  return { todoLists, loading, error, createList, updateList, deleteList };
}

interface UseTodoItemsResult {
  items: TodoItem[];
  loading: boolean;
  error: Error | null;
  createItem: (data: Pick<TodoItem, 'title' | 'description' | 'priority' | 'dueDate' | 'assigneeIds'>) => Promise<string>;
  updateItem: (itemId: string, data: Partial<TodoItem>) => Promise<void>;
  completeItem: (itemId: string) => Promise<void>;
  deleteItem: (itemId: string) => Promise<void>;
}

export function useTodoItems(familyId: string, listId: string): UseTodoItemsResult {
  const { user } = useAuth();
  const [items, setItems] = useState<TodoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!familyId || !listId) {
      setLoading(false);
      return;
    }

    const itemsRef = collection(db, `families/${familyId}/todo_lists/${listId}/todo_items`);
    const q = query(itemsRef, orderBy('createdAt', 'asc'));

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const todoItems = snapshot.docs.map((docSnap) => {
          const data = docSnap.data();
          return {
            id: docSnap.id,
            ...data,
            createdAt: data.createdAt instanceof Timestamp ? data.createdAt.toDate() : new Date(),
            updatedAt: data.updatedAt instanceof Timestamp ? data.updatedAt.toDate() : new Date(),
            dueDate: data.dueDate instanceof Timestamp ? data.dueDate.toDate() : undefined,
            completedAt: data.completedAt instanceof Timestamp ? data.completedAt.toDate() : undefined,
          } as TodoItem;
        });
        setItems(todoItems);
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [familyId, listId]);

  const createItem = async (
    data: Pick<TodoItem, 'title' | 'description' | 'priority' | 'dueDate' | 'assigneeIds'>
  ): Promise<string> => {
    if (!user) throw new Error('User not authenticated');
    const itemsRef = collection(db, `families/${familyId}/todo_lists/${listId}/todo_items`);
    const docRef = await addDoc(itemsRef, {
      ...data,
      listId,
      familyId,
      status: 'pending' as TodoStatus,
      createdBy: user.uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
    return docRef.id;
  };

  const updateItem = async (itemId: string, data: Partial<TodoItem>): Promise<void> => {
    const docRef = doc(db, `families/${familyId}/todo_lists/${listId}/todo_items`, itemId);
    await updateDoc(docRef, { ...data, updatedAt: serverTimestamp() });
  };

  const completeItem = async (itemId: string): Promise<void> => {
    if (!user) throw new Error('User not authenticated');
    const docRef = doc(db, `families/${familyId}/todo_lists/${listId}/todo_items`, itemId);
    await updateDoc(docRef, {
      status: 'completed' as TodoStatus,
      completedAt: serverTimestamp(),
      completedBy: user.uid,
      updatedAt: serverTimestamp(),
    });
  };

  const deleteItem = async (itemId: string): Promise<void> => {
    const docRef = doc(db, `families/${familyId}/todo_lists/${listId}/todo_items`, itemId);
    await deleteDoc(docRef);
  };

  return { items, loading, error, createItem, updateItem, completeItem, deleteItem };
}
