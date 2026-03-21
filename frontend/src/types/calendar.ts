export interface CalendarEvent {
  id: string;
  familyId: string;
  title: string;
  description?: string;
  startDate: Date;
  endDate: Date;
  allDay: boolean;
  location?: string;
  attendees: EventAttendee[];
  color?: string;
  recurrence?: EventRecurrence;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface EventAttendee {
  uid: string;
  displayName: string;
  photoURL: string | null;
  status: 'accepted' | 'declined' | 'tentative' | 'pending';
}

export interface EventRecurrence {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  endDate?: Date;
  count?: number;
  daysOfWeek?: number[];
}

export type CalendarView = 'month' | 'week' | 'day';
