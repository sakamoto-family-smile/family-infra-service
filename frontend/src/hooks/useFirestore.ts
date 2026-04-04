'use client';

import { useState, useEffect } from 'react';
import {
  collection,
  doc,
  query,
  onSnapshot,
  DocumentData,
  QueryConstraint,
  DocumentReference,
  CollectionReference,
  Query,
  Timestamp,
} from 'firebase/firestore';
import { db } from '@/lib/firebase';

function convertTimestamps(data: DocumentData): DocumentData {
  const result: DocumentData = {};
  for (const key in data) {
    const value = data[key];
    if (value instanceof Timestamp) {
      result[key] = value.toDate();
    } else if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[key] = convertTimestamps(value);
    } else if (Array.isArray(value)) {
      result[key] = value.map((item) =>
        item && typeof item === 'object' ? convertTimestamps(item) : item
      );
    } else {
      result[key] = value;
    }
  }
  return result;
}

interface UseFirestoreDocumentResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useFirestoreDocument<T>(
  path: string
): UseFirestoreDocumentResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!path) {
      setLoading(false);
      return;
    }

    const docRef = doc(db, path) as DocumentReference<DocumentData>;

    const unsubscribe = onSnapshot(
      docRef,
      (snapshot) => {
        if (snapshot.exists()) {
          const rawData = snapshot.data();
          setData({ id: snapshot.id, ...convertTimestamps(rawData) } as T);
        } else {
          setData(null);
        }
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [path]);

  return { data, loading, error };
}

interface UseFirestoreCollectionResult<T> {
  data: T[];
  loading: boolean;
  error: Error | null;
}

export function useFirestoreCollection<T>(
  collectionPath: string,
  constraints: QueryConstraint[] = []
): UseFirestoreCollectionResult<T> {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!collectionPath) {
      setLoading(false);
      return;
    }

    const colRef = collection(db, collectionPath) as CollectionReference<DocumentData>;
    const q: Query<DocumentData> = constraints.length > 0
      ? query(colRef, ...constraints)
      : colRef;

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const docs = snapshot.docs.map((docSnap) => ({
          id: docSnap.id,
          ...convertTimestamps(docSnap.data()),
        })) as T[];
        setData(docs);
        setLoading(false);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collectionPath, JSON.stringify(constraints)]);

  return { data, loading, error };
}
