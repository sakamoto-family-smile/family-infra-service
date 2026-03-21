'use client';

import Link from 'next/link';
import { CalendarEvent } from '@/types/calendar';
import { formatDate, formatTime } from '@/lib/utils';
import { Avatar } from '@/components/ui/Avatar';

interface EventCardProps {
  event: CalendarEvent;
  onClick?: () => void;
}

export function EventCard({ event, onClick }: EventCardProps) {
  const color = event.color || '#3b82f6';

  return (
    <div
      onClick={onClick}
      className="group rounded-xl bg-white border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer overflow-hidden"
    >
      <div className="h-1" style={{ backgroundColor: color }} />
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
          {event.title}
        </h3>

        <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
          <svg className="h-4 w-4 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
              clipRule="evenodd"
            />
          </svg>
          <span>
            {event.allDay
              ? formatDate(event.startDate)
              : `${formatDate(event.startDate)} ${formatTime(event.startDate)}`}
          </span>
        </div>

        {event.location && (
          <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
            <svg className="h-4 w-4 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="truncate">{event.location}</span>
          </div>
        )}

        {event.description && (
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{event.description}</p>
        )}

        {event.attendees.length > 0 && (
          <div className="mt-3 flex items-center gap-1">
            <div className="flex -space-x-2">
              {event.attendees.slice(0, 4).map((attendee) => (
                <Avatar
                  key={attendee.uid}
                  src={attendee.photoURL}
                  name={attendee.displayName}
                  size="xs"
                  className="ring-2 ring-white"
                />
              ))}
            </div>
            {event.attendees.length > 4 && (
              <span className="text-xs text-gray-500 ml-1">+{event.attendees.length - 4}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
