'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { AttendeeSelector } from './AttendeeSelector';
import { CalendarEvent } from '@/types/calendar';
import { FamilyMember } from '@/types/family';

interface EventFormProps {
  members: FamilyMember[];
  initialData?: Partial<CalendarEvent>;
  onSubmit: (data: Omit<CalendarEvent, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  onCancel: () => void;
  familyId: string;
  createdBy: string;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export function EventForm({ members, initialData, onSubmit, onCancel, familyId, createdBy }: EventFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [startDate, setStartDate] = useState(
    initialData?.startDate
      ? new Date(initialData.startDate).toISOString().slice(0, 16)
      : new Date().toISOString().slice(0, 16)
  );
  const [endDate, setEndDate] = useState(
    initialData?.endDate
      ? new Date(initialData.endDate).toISOString().slice(0, 16)
      : new Date(Date.now() + 3600000).toISOString().slice(0, 16)
  );
  const [allDay, setAllDay] = useState(initialData?.allDay || false);
  const [location, setLocation] = useState(initialData?.location || '');
  const [color, setColor] = useState(initialData?.color || '#3b82f6');
  const [attendeeIds, setAttendeeIds] = useState<string[]>(
    initialData?.attendees?.map((a) => a.uid) || []
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('タイトルを入力してください');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      const selectedAttendees = members
        .filter((m) => attendeeIds.includes(m.uid))
        .map((m) => ({
          uid: m.uid,
          displayName: m.displayName,
          photoURL: m.photoURL,
          status: 'pending' as const,
        }));

      await onSubmit({
        familyId,
        title: title.trim(),
        description: description.trim() || undefined,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        allDay,
        location: location.trim() || undefined,
        color,
        attendees: selectedAttendees,
        createdBy,
      });
    } catch (err) {
      setError('保存に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-200">
          {error}
        </div>
      )}

      <Input
        label="タイトル *"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="イベントのタイトル"
        required
      />

      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="allDay"
          checked={allDay}
          onChange={(e) => setAllDay(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="allDay" className="text-sm font-medium text-gray-700">終日</label>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">開始</label>
          <input
            type={allDay ? 'date' : 'datetime-local'}
            value={allDay ? startDate.slice(0, 10) : startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">終了</label>
          <input
            type={allDay ? 'date' : 'datetime-local'}
            value={allDay ? endDate.slice(0, 10) : endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      <Input
        label="場所"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        placeholder="場所（任意）"
      />

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">説明</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="説明（任意）"
          rows={3}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">カラー</label>
        <div className="flex gap-2">
          {COLORS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setColor(c)}
              className={`h-7 w-7 rounded-full transition-all ${
                color === c ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''
              }`}
              style={{ backgroundColor: c }}
            />
          ))}
        </div>
      </div>

      <AttendeeSelector
        members={members}
        selectedIds={attendeeIds}
        onChange={setAttendeeIds}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" loading={submitting}>
          {initialData?.title ? '更新' : '作成'}
        </Button>
      </div>
    </form>
  );
}
