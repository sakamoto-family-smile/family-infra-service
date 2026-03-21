'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Loading } from '@/components/ui/Loading';
import { useTodoLists } from '@/hooks/useTodo';
import { TodoList } from '@/types/todo';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const ICONS = ['📋', '🏠', '🛒', '💼', '🎯', '📚', '🏃', '💊'];

const DEFAULT_FAMILY_ID = 'default_family';

export default function TodoPage() {
  const { todoLists, loading, createList } = useTodoLists(DEFAULT_FAMILY_ID);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [title, setTitle] = useState('');
  const [selectedColor, setSelectedColor] = useState(COLORS[0]);
  const [selectedIcon, setSelectedIcon] = useState(ICONS[0]);
  const [creating, setCreating] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      await createList({ title: title.trim(), color: selectedColor, icon: selectedIcon });
      setTitle('');
      setShowCreateForm(false);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full flex-col">
        <Header title="TODO" />
        <div className="flex flex-1 items-center justify-center">
          <Loading />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="TODO" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">リスト一覧</h2>
          <Button size="sm" onClick={() => setShowCreateForm(true)}>
            + 新しいリスト
          </Button>
        </div>

        {todoLists.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="text-5xl mb-4">✅</div>
            <h3 className="text-lg font-semibold text-gray-900">TODOリストがありません</h3>
            <p className="mt-2 text-sm text-gray-500">新しいリストを作成してみましょう</p>
            <Button className="mt-4" onClick={() => setShowCreateForm(true)}>
              リストを作成
            </Button>
          </div>
        ) : (
          <div className="grid gap-3">
            {todoLists.map((list) => (
              <Link
                key={list.id}
                href={`/todo/${list.id}`}
                className="flex items-center gap-4 rounded-xl bg-white border border-gray-200 p-4 hover:border-blue-200 hover:shadow-sm transition-all"
              >
                <div
                  className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl text-2xl"
                  style={{ backgroundColor: `${list.color || '#3b82f6'}15` }}
                >
                  {list.icon || '📋'}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900">{list.title}</h3>
                  {list.description && (
                    <p className="text-sm text-gray-500 truncate mt-0.5">{list.description}</p>
                  )}
                </div>
                <svg className="h-5 w-5 flex-shrink-0 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Modal
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="新しいリストを作成"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="リスト名"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="例: 買い物リスト"
            required
          />

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">アイコン</label>
            <div className="flex flex-wrap gap-2">
              {ICONS.map((icon) => (
                <button
                  key={icon}
                  type="button"
                  onClick={() => setSelectedIcon(icon)}
                  className={`h-10 w-10 rounded-lg text-xl transition-all ${
                    selectedIcon === icon ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-100'
                  }`}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">カラー</label>
            <div className="flex gap-2">
              {COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setSelectedColor(color)}
                  className={`h-7 w-7 rounded-full transition-all ${
                    selectedColor === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setShowCreateForm(false)}>
              キャンセル
            </Button>
            <Button type="submit" loading={creating}>
              作成
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
