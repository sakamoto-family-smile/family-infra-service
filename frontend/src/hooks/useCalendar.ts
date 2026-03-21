'use client';

import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import { CalendarEvent } from '@/types/calendar';

interface UseCalendarResult {
  events: CalendarEvent[];
  loading: boolean;
  error: Error | null;
  createEvent: (data: Omit<CalendarEvent, 'id' | 'createdAt' | 'updatedAt'>) => Promise<CalendarEvent>;
  updateEvent: (id: string, data: Partial<CalendarEvent>) => Promise<CalendarEvent>;
  deleteEvent: (id: string) => Promise<void>;
  refetch: () => void;
}

export function useCalendar(familyId: string, year?: number, month?: number): UseCalendarResult {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchEvents = useCallback(async () => {
    if (!familyId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const params: Record<string, string | number> = { familyId };
      if (year !== undefined) params.year = year;
      if (month !== undefined) params.month = month;

      const data = await api.get<CalendarEvent[]>('/api/v1/calendar/events', { params });
      setEvents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch events'));
    } finally {
      setLoading(false);
    }
  }, [familyId, year, month]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const createEvent = async (
    data: Omit<CalendarEvent, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<CalendarEvent> => {
    const created = await api.post<CalendarEvent>('/api/v1/calendar/events', data);
    setEvents((prev) => [...prev, created]);
    return created;
  };

  const updateEvent = async (id: string, data: Partial<CalendarEvent>): Promise<CalendarEvent> => {
    const updated = await api.put<CalendarEvent>(`/api/v1/calendar/events/${id}`, data);
    setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
    return updated;
  };

  const deleteEvent = async (id: string): Promise<void> => {
    await api.delete(`/api/v1/calendar/events/${id}`);
    setEvents((prev) => prev.filter((e) => e.id !== id));
  };

  return { events, loading, error, createEvent, updateEvent, deleteEvent, refetch: fetchEvents };
}
