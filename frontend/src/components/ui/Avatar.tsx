import Image from 'next/image';
import { getInitials } from '@/lib/utils';

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface AvatarProps {
  src?: string | null;
  name?: string | null;
  size?: AvatarSize;
  className?: string;
}

const sizeMap: Record<AvatarSize, { container: string; text: string; imageSize: number }> = {
  xs: { container: 'h-6 w-6', text: 'text-xs', imageSize: 24 },
  sm: { container: 'h-8 w-8', text: 'text-xs', imageSize: 32 },
  md: { container: 'h-10 w-10', text: 'text-sm', imageSize: 40 },
  lg: { container: 'h-12 w-12', text: 'text-base', imageSize: 48 },
  xl: { container: 'h-16 w-16', text: 'text-xl', imageSize: 64 },
};

const colors = [
  'bg-red-500',
  'bg-orange-500',
  'bg-yellow-500',
  'bg-green-500',
  'bg-blue-500',
  'bg-indigo-500',
  'bg-purple-500',
  'bg-pink-500',
];

function getColorFromName(name: string): string {
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

export function Avatar({ src, name, size = 'md', className = '' }: AvatarProps) {
  const { container, text, imageSize } = sizeMap[size];
  const initials = name ? getInitials(name) : '?';
  const bgColor = name ? getColorFromName(name) : 'bg-gray-400';

  return (
    <div
      className={`relative inline-flex items-center justify-center overflow-hidden rounded-full ${container} ${className}`}
    >
      {src ? (
        <Image
          src={src}
          alt={name || 'Avatar'}
          width={imageSize}
          height={imageSize}
          className="h-full w-full object-cover"
        />
      ) : (
        <div
          className={`flex h-full w-full items-center justify-center ${bgColor} text-white font-medium ${text}`}
        >
          {initials}
        </div>
      )}
    </div>
  );
}
