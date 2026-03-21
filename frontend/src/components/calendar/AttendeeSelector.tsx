'use client';

import { FamilyMember } from '@/types/family';
import { Avatar } from '@/components/ui/Avatar';

interface AttendeeSelectorProps {
  members: FamilyMember[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}

export function AttendeeSelector({ members, selectedIds, onChange }: AttendeeSelectorProps) {
  const toggle = (uid: string) => {
    if (selectedIds.includes(uid)) {
      onChange(selectedIds.filter((id) => id !== uid));
    } else {
      onChange([...selectedIds, uid]);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">参加者</label>
      <div className="flex flex-wrap gap-2">
        {members.map((member) => {
          const isSelected = selectedIds.includes(member.uid);
          return (
            <button
              key={member.uid}
              type="button"
              onClick={() => toggle(member.uid)}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium border transition-all ${
                isSelected
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
              }`}
            >
              <Avatar src={member.photoURL} name={member.displayName} size="xs" />
              <span>{member.displayName}</span>
              {isSelected && (
                <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
