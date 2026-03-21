'use client';

import { useAuth } from '@/hooks/useAuth';
import { Header } from '@/components/layout/Header';
import { Loading } from '@/components/ui/Loading';
import Link from 'next/link';

const quickLinks = [
  {
    href: '/chat',
    title: 'チャット',
    description: '家族とメッセージを交換',
    icon: '💬',
    color: 'bg-blue-50 border-blue-200',
    iconColor: 'text-blue-600',
  },
  {
    href: '/calendar',
    title: 'カレンダー',
    description: '予定を確認・登録',
    icon: '📅',
    color: 'bg-green-50 border-green-200',
    iconColor: 'text-green-600',
  },
  {
    href: '/todo',
    title: 'TODO',
    description: 'タスクを管理',
    icon: '✅',
    color: 'bg-yellow-50 border-yellow-200',
    iconColor: 'text-yellow-600',
  },
  {
    href: '/settings',
    title: '設定',
    description: 'プロフィール・家族設定',
    icon: '⚙️',
    color: 'bg-purple-50 border-purple-200',
    iconColor: 'text-purple-600',
  },
];

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) {
    return <Loading fullScreen />;
  }

  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 12 ? 'おはようございます' : hour < 17 ? 'こんにちは' : 'こんばんは';

  return (
    <div className="flex flex-col h-full">
      <Header title="ダッシュボード" />

      <div className="flex-1 p-4 md:p-6 space-y-6">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 text-white">
          <p className="text-blue-100 text-sm">{greeting}！</p>
          <h2 className="mt-1 text-2xl font-bold">
            {user?.displayName || user?.email?.split('@')[0]}さん
          </h2>
          <p className="mt-2 text-blue-100 text-sm">
            {now.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            メニュー
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {quickLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`flex flex-col items-start gap-2 rounded-xl border p-4 transition-all hover:shadow-md ${link.color}`}
              >
                <span className={`text-2xl ${link.iconColor}`}>{link.icon}</span>
                <div>
                  <h4 className="font-semibold text-gray-900">{link.title}</h4>
                  <p className="text-xs text-gray-500 mt-0.5">{link.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4">今日のスケジュール</h3>
          <p className="text-sm text-gray-500 text-center py-4">
            今日の予定はありません
          </p>
          <Link href="/calendar" className="block text-center text-sm text-blue-600 hover:underline mt-2">
            カレンダーを見る →
          </Link>
        </div>
      </div>
    </div>
  );
}
