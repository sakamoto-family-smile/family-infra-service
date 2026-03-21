export type TodoPriority = 'low' | 'medium' | 'high';
export type TodoStatus = 'pending' | 'in_progress' | 'completed';

export interface TodoList {
  id: string;
  familyId: string;
  title: string;
  description?: string;
  color?: string;
  icon?: string;
  memberIds: string[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TodoItem {
  id: string;
  listId: string;
  familyId: string;
  title: string;
  description?: string;
  status: TodoStatus;
  priority: TodoPriority;
  dueDate?: Date;
  assigneeIds: string[];
  tags?: string[];
  completedAt?: Date;
  completedBy?: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}
