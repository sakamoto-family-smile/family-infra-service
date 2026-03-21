export interface Family {
  id: string;
  name: string;
  members: FamilyMember[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface FamilyMember {
  uid: string;
  displayName: string;
  photoURL: string | null;
  email: string | null;
  role: 'admin' | 'member';
  joinedAt: Date;
}

export interface FamilyInvite {
  id: string;
  familyId: string;
  familyName: string;
  invitedBy: string;
  invitedEmail: string;
  status: 'pending' | 'accepted' | 'declined';
  createdAt: Date;
  expiresAt: Date;
}
