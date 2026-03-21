export interface ChatRoom {
  id: string;
  name: string;
  description?: string;
  familyId: string;
  members: string[];
  lastMessage?: ChatMessage;
  lastMessageAt?: Date;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  id: string;
  roomId: string;
  senderId: string;
  senderName: string;
  senderPhotoURL: string | null;
  content: string;
  type: 'text' | 'image' | 'file';
  imageURL?: string;
  fileURL?: string;
  fileName?: string;
  reactions: MessageReaction[];
  replyTo?: string;
  createdAt: Date;
  updatedAt?: Date;
  deleted?: boolean;
}

export interface MessageReaction {
  emoji: string;
  userIds: string[];
}
