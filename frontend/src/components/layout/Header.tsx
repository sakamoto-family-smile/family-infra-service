'use client';

import { useAuth } from '@/hooks/useAuth';
import { Avatar } from '@/components/ui/Avatar';

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  const { user } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 px-4 h-16 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {title && (
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button className="relative rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
          </svg>
        </button>

        <Avatar
          src={user?.photoURL}
          name={user?.displayName || user?.email || 'U'}
          size="sm"
          className="cursor-pointer"
        />
      </div>
    </header>
  );
}
