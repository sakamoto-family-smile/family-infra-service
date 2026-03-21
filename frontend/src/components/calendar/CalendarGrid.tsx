'use client';

import { useState } from 'react';
import { CalendarEvent } from '@/types/calendar';
import { EventCard } from './EventCard';

interface CalendarGridProps {
  events: CalendarEvent[];
  year: number;
  month: number;
  onDateClick?: (date: Date) => void;
  onEventClick?: (event: CalendarEvent) => void;
}

const DAYS_OF_WEEK = ['日', '月', '火', '水', '木', '金', '土'];

export function CalendarGrid({ events, year, month, onDateClick, onEventClick }: CalendarGridProps) {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const startDayOfWeek = firstDay.getDay();
  const daysInMonth = lastDay.getDate();

  const today = new Date();
  const todayStr = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;

  const getEventsForDate = (day: number) => {
    const date = new Date(year, month - 1, day);
    return events.filter((event) => {
      const eventStart = new Date(event.startDate);
      const eventEnd = new Date(event.endDate);
      return date >= new Date(eventStart.getFullYear(), eventStart.getMonth(), eventStart.getDate()) &&
             date <= new Date(eventEnd.getFullYear(), eventEnd.getMonth(), eventEnd.getDate());
    });
  };

  const cells: (number | null)[] = [
    ...Array(startDayOfWeek).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  while (cells.length % 7 !== 0) {
    cells.push(null);
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="grid grid-cols-7 border-b border-gray-200">
        {DAYS_OF_WEEK.map((day, i) => (
          <div
            key={day}
            className={`py-2 text-center text-xs font-medium ${
              i === 0 ? 'text-red-500' : i === 6 ? 'text-blue-500' : 'text-gray-500'
            }`}
          >
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7">
        {cells.map((day, index) => {
          if (day === null) {
            return <div key={`empty-${index}`} className="h-24 border-b border-r border-gray-100 bg-gray-50" />;
          }

          const dayEvents = getEventsForDate(day);
          const dateStr = `${year}-${month}-${day}`;
          const isToday = dateStr === todayStr;
          const dayOfWeek = (startDayOfWeek + day - 1) % 7;

          return (
            <div
              key={day}
              onClick={() => onDateClick?.(new Date(year, month - 1, day))}
              className={`h-24 border-b border-r border-gray-100 p-1 cursor-pointer hover:bg-blue-50 transition-colors overflow-hidden`}
            >
              <div className="flex justify-center">
                <span
                  className={`flex h-6 w-6 items-center justify-center rounded-full text-sm ${
                    isToday
                      ? 'bg-blue-600 text-white font-bold'
                      : dayOfWeek === 0
                      ? 'text-red-500'
                      : dayOfWeek === 6
                      ? 'text-blue-500'
                      : 'text-gray-700'
                  }`}
                >
                  {day}
                </span>
              </div>
              <div className="mt-0.5 space-y-0.5">
                {dayEvents.slice(0, 2).map((event) => (
                  <div
                    key={event.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      onEventClick?.(event);
                    }}
                    className="truncate rounded px-1 py-0.5 text-xs font-medium"
                    style={{
                      backgroundColor: event.color ? `${event.color}20` : '#3b82f620',
                      color: event.color || '#3b82f6',
                    }}
                  >
                    {event.title}
                  </div>
                ))}
                {dayEvents.length > 2 && (
                  <p className="text-xs text-gray-400 px-1">+{dayEvents.length - 2}件</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
