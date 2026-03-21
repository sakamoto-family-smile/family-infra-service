'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { CalendarGrid } from '@/components/calendar/CalendarGrid';
import { EventCard } from '@/components/calendar/EventCard';
import { EventForm } from '@/components/calendar/EventForm';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { useCalendar } from '@/hooks/useCalendar';
import { useAuth } from '@/hooks/useAuth';
import { CalendarEvent } from '@/types/calendar';
import { useRouter } from 'next/navigation';

export default function CalendarPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showEventForm, setShowEventForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;

  const familyId = 'default_family';
  const { events, loading, createEvent } = useCalendar(familyId, year, month);

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 2, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month, 1));
  };

  const handleCreateEvent = async (data: Omit<CalendarEvent, 'id' | 'createdAt' | 'updatedAt'>) => {
    await createEvent(data);
    setShowEventForm(false);
  };

  if (loading) {
    return (
      <div className="flex h-full flex-col">
        <Header title="カレンダー" />
        <div className="flex flex-1 items-center justify-center">
          <Loading />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="カレンダー" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={prevMonth}
              className="rounded-full p-2 text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </button>
            <h2 className="text-lg font-bold text-gray-900">
              {year}年{month}月
            </h2>
            <button
              onClick={nextMonth}
              className="rounded-full p-2 text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          <Button onClick={() => setShowEventForm(true)} size="sm">
            + 予定を追加
          </Button>
        </div>

        <CalendarGrid
          events={events}
          year={year}
          month={month}
          onDateClick={(date) => {
            setSelectedDate(date);
            setShowEventForm(true);
          }}
          onEventClick={(event) => router.push(`/calendar/${event.id}`)}
        />

        <div className="space-y-3">
          <h3 className="font-semibold text-gray-900">今月の予定</h3>
          {events.length === 0 ? (
            <p className="text-center text-sm text-gray-500 py-6">今月の予定はありません</p>
          ) : (
            events.map((event) => (
              <EventCard
                key={event.id}
                event={event}
                onClick={() => router.push(`/calendar/${event.id}`)}
              />
            ))
          )}
        </div>
      </div>

      <Modal
        isOpen={showEventForm}
        onClose={() => {
          setShowEventForm(false);
          setSelectedDate(null);
        }}
        title="予定を作成"
        size="lg"
      >
        <EventForm
          members={[]}
          familyId={familyId}
          createdBy={user?.uid || ''}
          onSubmit={handleCreateEvent}
          onCancel={() => setShowEventForm(false)}
        />
      </Modal>
    </div>
  );
}
