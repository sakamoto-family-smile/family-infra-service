'use client';

import { useState, useEffect } from 'react';
import { collection, doc, addDoc, getDoc, updateDoc, arrayUnion, arrayRemove, serverTimestamp } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { useAuth } from './useAuth';
import { Family, FamilyMember } from '@/types/family';

interface UseFamilyResult {
  family: Family | null;
  loading: boolean;
  error: Error | null;
  createFamily: (name: string) => Promise<string>;
  updateFamily: (familyId: string, data: Partial<Family>) => Promise<void>;
  addMember: (familyId: string, member: FamilyMember) => Promise<void>;
  removeMember: (familyId: string, uid: string) => Promise<void>;
}

export function useFamily(familyId?: string): UseFamilyResult {
  const { user } = useAuth();
  const [family, setFamily] = useState<Family | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!familyId) {
      setLoading(false);
      return;
    }

    const fetchFamily = async () => {
      try {
        const docRef = doc(db, 'families', familyId);
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          setFamily({ id: docSnap.id, ...docSnap.data() } as Family);
        } else {
          setFamily(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch family'));
      } finally {
        setLoading(false);
      }
    };

    fetchFamily();
  }, [familyId]);

  const createFamily = async (name: string): Promise<string> => {
    if (!user) throw new Error('User not authenticated');

    const familiesRef = collection(db, 'families');
    const newFamily = {
      name,
      members: [
        {
          uid: user.uid,
          displayName: user.displayName || 'Unknown',
          photoURL: user.photoURL,
          email: user.email,
          role: 'admin',
          joinedAt: new Date(),
        },
      ],
      createdBy: user.uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    };

    const docRef = await addDoc(familiesRef, newFamily);
    return docRef.id;
  };

  const updateFamily = async (id: string, data: Partial<Family>): Promise<void> => {
    const docRef = doc(db, 'families', id);
    await updateDoc(docRef, { ...data, updatedAt: serverTimestamp() });
  };

  const addMember = async (id: string, member: FamilyMember): Promise<void> => {
    const docRef = doc(db, 'families', id);
    await updateDoc(docRef, {
      members: arrayUnion(member),
      updatedAt: serverTimestamp(),
    });
  };

  const removeMember = async (id: string, uid: string): Promise<void> => {
    const docRef = doc(db, 'families', id);
    const docSnap = await getDoc(docRef);
    if (!docSnap.exists()) return;

    const currentMembers: FamilyMember[] = docSnap.data().members || [];
    const memberToRemove = currentMembers.find((m) => m.uid === uid);
    if (!memberToRemove) return;

    await updateDoc(docRef, {
      members: arrayRemove(memberToRemove),
      updatedAt: serverTimestamp(),
    });
  };

  return { family, loading, error, createFamily, updateFamily, addMember, removeMember };
}
