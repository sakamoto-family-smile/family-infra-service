import { TodoPriority } from '@/types/todo';

interface PriorityBadgeProps {
  priority: TodoPriority;
  size?: 'sm' | 'md';
}

const priorityConfig: Record<TodoPriority, { label: string; className: string }> = {
  low: {
    label: '低',
    className: 'bg-gray-100 text-gray-600',
  },
  medium: {
    label: '中',
    className: 'bg-yellow-100 text-yellow-700',
  },
  high: {
    label: '高',
    className: 'bg-red-100 text-red-700',
  },
};

export function PriorityBadge({ priority, size = 'sm' }: PriorityBadgeProps) {
  const config = priorityConfig[priority];

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${config.className} ${
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      }`}
    >
      {config.label}
    </span>
  );
}
