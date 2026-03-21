'use client';

import { useParams, useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { Loading } from '@/components/ui/Loading';
import { formatDate, formatTime } from '@/lib/utils';
import { CalendarEvent } from '@/types/calendar';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;
  const [event, setEvent] = useState<CalendarEvent | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const data = await api.get<CalendarEvent>(`/api/v1/calendar/events/${eventId}`);
        setEvent(data);
      } catch (err) {
        console.error('Failed to fetch event', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvent();
  }, [eventId]);

  if (loading) return <Loading fullScreen />;

  if (!event) {
    return (
      <div className="flex h-full flex-col">
        <Header />
        <div className="flex flex-1 items-center justify-center flex-col gap-4">
          <p className="text-gray-500">イベントが見つかりません</p>
          <Button variant="secondary" onClick={() => router.back()}>戻る</Button>
        </div>
      </div>
    );
  }

  const color = event.color || '#3b82f6';

  return (
    <div className="flex flex-col h-full">
      <Header />

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        <button
          onClick={() => router.back()}
          className="mb-4 flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          カレンダーに戻る
        </button>

        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="h-2" style={{ backgroundColor: color }} />
          <div className="p-6 space-y-5">
            <h1 className="text-2xl font-bold text-gray-900">{event.title}</h1>

            <div className="space-y-3">
              <div className="flex items-start gap-3 text-sm">
                <svg className="h-5 w-5 flex-shrink-0 text-gray-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-gray-900">
                    {event.allDay
                      ? formatDate(event.startDate)
                      : `${formatDate(event.startDate)} ${formatTime(event.startDate)}`}
                  </p>
                  {!event.allDay && new Date(event.startDate).toDateString() !== new Date(event.endDate).toDateString() && (
                    <p className="text-gray-500 mt-0.5">
                      〜 {formatDate(event.endDate)} {formatTime(event.endDate)}
                    </p>
                  )}
                </div>
              </div>

              {event.location && (
                <div className="flex items-center gap-3 text-sm">
                  <svg className="h-5 w-5 flex-shrink-0 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-900">{event.location}</span>
                </div>
              )}
            </div>

            {event.description && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">説明</h3>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">{event.description}</p>
              </div>
            )}

            {event.attendees.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">参加者 ({event.attendees.length}人)</h3>
                <div className="space-y-2">
                  {event.attendees.map((attendee) => (
                    <div key={attendee.uid} className="flex items-center gap-3">
                      <Avatar src={attendee.photoURL} name={attendee.displayName} size="sm" />
                      <span className="text-sm text-gray-900">{attendee.displayName}</span>
                      <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${
                        attendee.status === 'accepted' ? 'bg-green-100 text-green-700' :
                        attendee.status === 'declined' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {attendee.status === 'accepted' ? '参加' :
                         attendee.status === 'declined' ? '不参加' : '未回答'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
