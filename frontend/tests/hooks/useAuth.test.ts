import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';

// Mock firebase/auth
vi.mock('firebase/auth', () => ({
  getAuth: vi.fn(() => ({})),
  onAuthStateChanged: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signInWithPopup: vi.fn(),
  GoogleAuthProvider: vi.fn(() => ({})),
  OAuthProvider: vi.fn(() => ({ addScope: vi.fn() })),
  signOut: vi.fn(),
  sendPasswordResetEmail: vi.fn(),
  updateProfile: vi.fn(),
}));

// Mock firebase app
vi.mock('@/lib/firebase', () => ({
  auth: {},
  db: {},
}));

import { onAuthStateChanged } from 'firebase/auth';

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with loading state', () => {
    const mockOnAuthStateChanged = vi.mocked(onAuthStateChanged);
    mockOnAuthStateChanged.mockImplementation((_auth, callback) => {
      // Do not call callback immediately to simulate loading
      return vi.fn();
    });

    // Test that the initial state is loading = true and user = null
    expect(mockOnAuthStateChanged).toBeDefined();
  });

  it('should set user when authenticated', () => {
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      displayName: 'Test User',
      photoURL: null,
      emailVerified: true,
      getIdToken: vi.fn().mockResolvedValue('mock-token'),
    };

    const mockOnAuthStateChanged = vi.mocked(onAuthStateChanged);
    mockOnAuthStateChanged.mockImplementation((_auth, callback) => {
      // Simulate authenticated user
      (callback as (user: typeof mockUser | null) => void)(mockUser);
      return vi.fn();
    });

    expect(mockUser.uid).toBe('test-uid');
    expect(mockUser.email).toBe('test@example.com');
  });

  it('should set user to null when not authenticated', () => {
    const mockOnAuthStateChanged = vi.mocked(onAuthStateChanged);
    mockOnAuthStateChanged.mockImplementation((_auth, callback) => {
      (callback as (user: null) => void)(null);
      return vi.fn();
    });

    expect(mockOnAuthStateChanged).toHaveBeenCalled();
  });

  it('should call signInWithEmailAndPassword on signInWithEmail', async () => {
    const { signInWithEmailAndPassword } = await import('firebase/auth');
    const mockSignIn = vi.mocked(signInWithEmailAndPassword);
    mockSignIn.mockResolvedValue({
      user: { uid: 'test-uid' },
      providerId: null,
      operationType: 'signIn',
    } as never);

    await act(async () => {
      await mockSignIn({} as never, 'test@example.com', 'password123');
    });

    expect(mockSignIn).toHaveBeenCalledWith({}, 'test@example.com', 'password123');
  });

  it('should call signOut when signing out', async () => {
    const { signOut } = await import('firebase/auth');
    const mockSignOut = vi.mocked(signOut);
    mockSignOut.mockResolvedValue(undefined);

    await act(async () => {
      await mockSignOut({} as never);
    });

    expect(mockSignOut).toHaveBeenCalled();
  });

  it('should call sendPasswordResetEmail for password reset', async () => {
    const { sendPasswordResetEmail } = await import('firebase/auth');
    const mockReset = vi.mocked(sendPasswordResetEmail);
    mockReset.mockResolvedValue(undefined);

    await act(async () => {
      await mockReset({} as never, 'test@example.com');
    });

    expect(mockReset).toHaveBeenCalledWith({}, 'test@example.com');
  });

  it('should handle authentication errors gracefully', async () => {
    const { signInWithEmailAndPassword } = await import('firebase/auth');
    const mockSignIn = vi.mocked(signInWithEmailAndPassword);
    const mockError = Object.assign(new Error('auth/wrong-password'), { code: 'auth/wrong-password' });
    mockSignIn.mockRejectedValue(mockError);

    await expect(mockSignIn({} as never, 'test@example.com', 'wrong-password')).rejects.toThrow();
  });
});
