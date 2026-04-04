'use client';

import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { useAuth } from '@/hooks/useAuth';
import { Avatar } from '@/components/ui/Avatar';

const settingsItems = [
  {
    href: '/settings/profile',
    title: 'プロフィール',
    description: '名前・アバターを変更',
    icon: '👤',
  },
  {
    href: '/settings/family',
    title: '家族設定',
    description: '家族メンバーを管理',
    icon: '👨‍👩‍👧‍👦',
  },
];

export default function SettingsPage() {
  const { user, signOut } = useAuth();

  return (
    <div className="flex flex-col h-full">
      <Header title="設定" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-4">
            <Avatar
              src={user?.photoURL}
              name={user?.displayName || user?.email || 'U'}
              size="xl"
            />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {user?.displayName || 'ユーザー'}
              </h2>
              <p className="text-sm text-gray-500">{user?.email}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {settingsItems.map((item, index) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors ${
                index !== settingsItems.length - 1 ? 'border-b border-gray-100' : ''
              }`}
            >
              <span className="text-2xl">{item.icon}</span>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.title}</p>
                <p className="text-sm text-gray-500">{item.description}</p>
              </div>
              <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <button
            onClick={() => void signOut()}
            className="flex w-full items-center gap-4 px-5 py-4 hover:bg-red-50 transition-colors text-left"
          >
            <span className="text-2xl">🚪</span>
            <div className="flex-1">
              <p className="font-medium text-red-600">ログアウト</p>
              <p className="text-sm text-gray-500">アカウントからログアウトします</p>
            </div>
          </button>
        </div>

        <p className="text-center text-xs text-gray-400">
          Family Hub v0.1.0
        </p>
      </div>
    </div>
  );
}
