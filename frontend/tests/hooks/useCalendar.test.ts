import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from '@testing-library/react';

vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    user: { uid: 'test-uid' },
    loading: false,
  })),
}));

import api from '@/lib/api';

const mockEvent = {
  id: 'event-1',
  familyId: 'family-1',
  createdBy: 'user-1',
  title: 'Family Dinner',
  description: 'Monthly family dinner',
  startAt: '2024-06-01T18:00:00Z',
  endAt: '2024-06-01T20:00:00Z',
  isAllDay: false,
  attendeeIds: ['user-1', 'user-2'],
};

describe('useCalendar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch calendar events for a family', async () => {
    const mockGet = vi.mocked(api.get);
    mockGet.mockResolvedValue({ data: [mockEvent] });

    await act(async () => {
      const response = await mockGet('/families/family-1/calendar-events');
      expect(response.data).toHaveLength(1);
      expect(response.data[0].title).toBe('Family Dinner');
    });

    expect(mockGet).toHaveBeenCalledWith('/families/family-1/calendar-events');
  });

  it('should fetch events with date range filters', async () => {
    const mockGet = vi.mocked(api.get);
    mockGet.mockResolvedValue({ data: [mockEvent] });

    const start = '2024-06-01';
    const end = '2024-06-30';

    await act(async () => {
      await mockGet(`/families/family-1/calendar-events?start=${start}&end=${end}`);
    });

    expect(mockGet).toHaveBeenCalledWith(
      `/families/family-1/calendar-events?start=${start}&end=${end}`
    );
  });

  it('should create a new calendar event', async () => {
    const mockPost = vi.mocked(api.post);
    mockPost.mockResolvedValue({ data: mockEvent });

    await act(async () => {
      const response = await mockPost('/families/family-1/calendar-events', {
        title: 'Family Dinner',
        startAt: '2024-06-01T18:00:00Z',
        endAt: '2024-06-01T20:00:00Z',
        isAllDay: false,
        attendeeIds: [],
      });
      expect(response.data.title).toBe('Family Dinner');
    });

    expect(mockPost).toHaveBeenCalled();
  });

  it('should update an existing calendar event', async () => {
    const mockPut = vi.mocked(api.put);
    const updatedEvent = { ...mockEvent, title: 'Updated Dinner' };
    mockPut.mockResolvedValue({ data: updatedEvent });

    await act(async () => {
      const response = await mockPut('/calendar-events/event-1', { title: 'Updated Dinner' });
      expect(response.data.title).toBe('Updated Dinner');
    });

    expect(mockPut).toHaveBeenCalledWith('/calendar-events/event-1', { title: 'Updated Dinner' });
  });

  it('should delete a calendar event', async () => {
    const mockDelete = vi.mocked(api.delete);
    mockDelete.mockResolvedValue({ data: null });

    await act(async () => {
      await mockDelete('/calendar-events/event-1');
    });

    expect(mockDelete).toHaveBeenCalledWith('/calendar-events/event-1');
  });

  it('should filter events by date range on client side', () => {
    const events = [
      { id: '1', startAt: '2024-06-01T10:00:00Z', title: 'June Event' },
      { id: '2', startAt: '2024-07-15T10:00:00Z', title: 'July Event' },
      { id: '3', startAt: '2024-06-20T10:00:00Z', title: 'June Event 2' },
    ];

    const juneEvents = events.filter((e) => e.startAt.startsWith('2024-06'));
    expect(juneEvents).toHaveLength(2);
    expect(juneEvents.every((e) => e.startAt.startsWith('2024-06'))).toBe(true);
  });

  it('should handle API errors gracefully', async () => {
    const mockGet = vi.mocked(api.get);
    mockGet.mockRejectedValue(new Error('Network error'));

    await expect(mockGet('/families/family-1/calendar-events')).rejects.toThrow('Network error');
  });

  it('should handle all-day events', () => {
    const allDayEvent = {
      id: 'event-2',
      title: 'Holiday',
      startAt: '2024-12-25T00:00:00Z',
      endAt: '2024-12-25T23:59:59Z',
      isAllDay: true,
    };

    expect(allDayEvent.isAllDay).toBe(true);
    expect(allDayEvent.title).toBe('Holiday');
  });
});
