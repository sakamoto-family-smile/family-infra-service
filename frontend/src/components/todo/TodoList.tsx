'use client';

import { TodoItem as TodoItemType, TodoList as TodoListType } from '@/types/todo';
import { TodoItem } from './TodoItem';
import { Loading } from '@/components/ui/Loading';

interface TodoListProps {
  list: TodoListType;
  items: TodoItemType[];
  loading?: boolean;
  memberMap?: Record<string, { displayName: string; photoURL: string | null }>;
  onCompleteItem?: (id: string) => void;
  onDeleteItem?: (id: string) => void;
  onEditItem?: (item: TodoItemType) => void;
}

export function TodoList({
  list,
  items,
  loading,
  memberMap,
  onCompleteItem,
  onDeleteItem,
  onEditItem,
}: TodoListProps) {
  const pendingItems = items.filter((item) => item.status !== 'completed');
  const completedItems = items.filter((item) => item.status === 'completed');

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loading text="タスクを読み込み中..." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {list.icon && <span className="text-2xl">{list.icon}</span>}
          <h2 className="text-lg font-semibold text-gray-900">{list.title}</h2>
        </div>
        <span className="text-sm text-gray-500">
          {pendingItems.length}件 / 全{items.length}件
        </span>
      </div>

      {pendingItems.length === 0 && completedItems.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-12 text-center">
          <p className="text-gray-500">タスクはまだありません</p>
          <p className="mt-1 text-sm text-gray-400">新しいタスクを追加しましょう</p>
        </div>
      )}

      {pendingItems.length > 0 && (
        <div className="space-y-2">
          {pendingItems.map((item) => (
            <TodoItem
              key={item.id}
              item={item}
              memberMap={memberMap}
              onComplete={onCompleteItem}
              onDelete={onDeleteItem}
              onEdit={onEditItem}
            />
          ))}
        </div>
      )}

      {completedItems.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-500">完了済み ({completedItems.length})</h3>
          {completedItems.map((item) => (
            <TodoItem
              key={item.id}
              item={item}
              memberMap={memberMap}
              onDelete={onDeleteItem}
            />
          ))}
        </div>
      )}
    </div>
  );
}
