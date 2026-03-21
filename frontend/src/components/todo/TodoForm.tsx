'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { TodoItem, TodoPriority } from '@/types/todo';
import { FamilyMember } from '@/types/family';

interface TodoFormProps {
  members?: FamilyMember[];
  initialData?: Partial<TodoItem>;
  onSubmit: (data: Pick<TodoItem, 'title' | 'description' | 'priority' | 'dueDate' | 'assigneeIds'>) => Promise<void>;
  onCancel: () => void;
}

export function TodoForm({ members, initialData, onSubmit, onCancel }: TodoFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [priority, setPriority] = useState<TodoPriority>(initialData?.priority || 'medium');
  const [dueDate, setDueDate] = useState(
    initialData?.dueDate ? new Date(initialData.dueDate).toISOString().slice(0, 10) : ''
  );
  const [assigneeIds, setAssigneeIds] = useState<string[]>(initialData?.assigneeIds || []);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('タイトルを入力してください');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        dueDate: dueDate ? new Date(dueDate) : undefined,
        assigneeIds,
      });
    } catch (err) {
      setError('保存に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleAssignee = (uid: string) => {
    setAssigneeIds((prev) =>
      prev.includes(uid) ? prev.filter((id) => id !== uid) : [...prev, uid]
    );
  };

  const priorities: { value: TodoPriority; label: string; className: string }[] = [
    { value: 'low', label: '低', className: 'border-gray-300 text-gray-600' },
    { value: 'medium', label: '中', className: 'border-yellow-300 text-yellow-600' },
    { value: 'high', label: '高', className: 'border-red-300 text-red-600' },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-200">
          {error}
        </div>
      )}

      <Input
        label="タスク名 *"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="何をしますか？"
        required
      />

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">説明</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="詳細（任意）"
          rows={2}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">優先度</label>
        <div className="flex gap-2">
          {priorities.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setPriority(p.value)}
              className={`flex-1 rounded-md border-2 px-3 py-2 text-sm font-medium transition-all ${
                priority === p.value
                  ? `${p.className} bg-opacity-10`
                  : 'border-gray-200 text-gray-500 hover:border-gray-300'
              }`}
              style={priority === p.value ? { borderColor: 'currentColor' } : {}}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">期限</label>
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {members && members.length > 0 && (
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">担当者</label>
          <div className="flex flex-wrap gap-2">
            {members.map((member) => (
              <button
                key={member.uid}
                type="button"
                onClick={() => toggleAssignee(member.uid)}
                className={`rounded-full px-3 py-1 text-sm border transition-all ${
                  assigneeIds.includes(member.uid)
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                }`}
              >
                {member.displayName}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" loading={submitting}>
          {initialData?.title ? '更新' : '追加'}
        </Button>
      </div>
    </form>
  );
}
