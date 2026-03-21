'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Loading } from '@/components/ui/Loading';
import { TodoList } from '@/components/todo/TodoList';
import { TodoForm } from '@/components/todo/TodoForm';
import { useTodoItems, useTodoLists } from '@/hooks/useTodo';
import { TodoItem } from '@/types/todo';

const DEFAULT_FAMILY_ID = 'default_family';

export default function TodoListDetailPage() {
  const params = useParams();
  const router = useRouter();
  const listId = params.listId as string;

  const { todoLists, loading: listsLoading } = useTodoLists(DEFAULT_FAMILY_ID);
  const { items, loading: itemsLoading, createItem, completeItem, deleteItem } = useTodoItems(DEFAULT_FAMILY_ID, listId);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState<TodoItem | null>(null);

  const currentList = todoLists.find((l) => l.id === listId);

  if (listsLoading || itemsLoading) {
    return <Loading fullScreen />;
  }

  if (!currentList) {
    return (
      <div className="flex h-full flex-col">
        <Header />
        <div className="flex flex-1 items-center justify-center flex-col gap-4">
          <p className="text-gray-500">リストが見つかりません</p>
          <Button variant="secondary" onClick={() => router.back()}>戻る</Button>
        </div>
      </div>
    );
  }

  const handleCreateItem = async (data: Pick<TodoItem, 'title' | 'description' | 'priority' | 'dueDate' | 'assigneeIds'>) => {
    await createItem(data);
    setShowAddForm(false);
  };

  return (
    <div className="flex flex-col h-full">
      <Header title={currentList.title} />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            TODO一覧
          </button>
          <Button size="sm" onClick={() => setShowAddForm(true)}>
            + タスクを追加
          </Button>
        </div>

        <TodoList
          list={currentList}
          items={items}
          onCompleteItem={completeItem}
          onDeleteItem={deleteItem}
          onEditItem={setEditingItem}
        />
      </div>

      <Modal
        isOpen={showAddForm}
        onClose={() => setShowAddForm(false)}
        title="タスクを追加"
      >
        <TodoForm
          onSubmit={handleCreateItem}
          onCancel={() => setShowAddForm(false)}
        />
      </Modal>

      <Modal
        isOpen={!!editingItem}
        onClose={() => setEditingItem(null)}
        title="タスクを編集"
      >
        {editingItem && (
          <TodoForm
            initialData={editingItem}
            onSubmit={async (data) => {
              // Update logic would go here
              setEditingItem(null);
            }}
            onCancel={() => setEditingItem(null)}
          />
        )}
      </Modal>
    </div>
  );
}
