'use client';

import { TodoItem as TodoItemType } from '@/types/todo';
import { PriorityBadge } from './PriorityBadge';
import { Avatar } from '@/components/ui/Avatar';
import { formatDate } from '@/lib/utils';

interface TodoItemProps {
  item: TodoItemType;
  memberMap?: Record<string, { displayName: string; photoURL: string | null }>;
  onComplete?: (id: string) => void;
  onDelete?: (id: string) => void;
  onEdit?: (item: TodoItemType) => void;
}

export function TodoItem({ item, memberMap, onComplete, onDelete, onEdit }: TodoItemProps) {
  const isCompleted = item.status === 'completed';

  return (
    <div
      className={`group flex items-start gap-3 rounded-lg border p-3 transition-all ${
        isCompleted ? 'bg-gray-50 border-gray-100 opacity-60' : 'bg-white border-gray-200 hover:border-blue-200 hover:shadow-sm'
      }`}
    >
      <button
        onClick={() => !isCompleted && onComplete?.(item.id)}
        disabled={isCompleted}
        className={`mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
          isCompleted
            ? 'border-green-500 bg-green-500 cursor-default'
            : 'border-gray-300 hover:border-blue-500 cursor-pointer'
        }`}
        aria-label={isCompleted ? '完了済み' : '完了にする'}
      >
        {isCompleted && (
          <svg className="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </button>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4 className={`text-sm font-medium ${isCompleted ? 'line-through text-gray-400' : 'text-gray-900'}`}>
            {item.title}
          </h4>
          <div className="flex items-center gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            {onEdit && !isCompleted && (
              <button
                onClick={() => onEdit(item)}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              >
                <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(item.id)}
                className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-500"
              >
                <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>

        {item.description && (
          <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">{item.description}</p>
        )}

        <div className="mt-2 flex flex-wrap items-center gap-2">
          <PriorityBadge priority={item.priority} />

          {item.dueDate && (
            <span className={`text-xs ${new Date(item.dueDate) < new Date() && !isCompleted ? 'text-red-500 font-medium' : 'text-gray-500'}`}>
              {formatDate(item.dueDate)}
            </span>
          )}

          {item.assigneeIds.length > 0 && memberMap && (
            <div className="flex -space-x-1">
              {item.assigneeIds.slice(0, 3).map((uid) => {
                const member = memberMap[uid];
                return member ? (
                  <Avatar key={uid} src={member.photoURL} name={member.displayName} size="xs" className="ring-2 ring-white" />
                ) : null;
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
