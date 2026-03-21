'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Avatar } from '@/components/ui/Avatar';
import { Loading } from '@/components/ui/Loading';
import { useFamily } from '@/hooks/useFamily';
import { useAuth } from '@/hooks/useAuth';

const DEFAULT_FAMILY_ID = 'default_family';

export default function FamilySettingsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { family, loading, createFamily, updateFamily, removeMember } = useFamily(DEFAULT_FAMILY_ID);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviting, setInviting] = useState(false);
  const [familyName, setFamilyName] = useState('');
  const [editingName, setEditingName] = useState(false);

  if (loading) return <Loading fullScreen />;

  const isAdmin = family?.members.find((m) => m.uid === user?.uid)?.role === 'admin';

  const handleUpdateFamilyName = async () => {
    if (!family || !familyName.trim()) return;
    await updateFamily(family.id, { name: familyName.trim() });
    setEditingName(false);
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviting(true);
    try {
      // Invite logic would call backend API
      await new Promise((r) => setTimeout(r, 1000));
      setInviteEmail('');
      setShowInviteModal(false);
    } finally {
      setInviting(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header title="家族設定" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          設定に戻る
        </button>

        {!family ? (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
            <div className="text-5xl mb-4">👨‍👩‍👧‍👦</div>
            <h3 className="text-lg font-semibold text-gray-900">家族グループがありません</h3>
            <p className="mt-2 text-sm text-gray-500">家族グループを作成して、メンバーを招待しましょう</p>
            <Button
              className="mt-4"
              onClick={async () => {
                await createFamily('私の家族');
              }}
            >
              家族グループを作成
            </Button>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">家族グループ</h3>
              {editingName ? (
                <div className="flex gap-3">
                  <Input
                    value={familyName}
                    onChange={(e) => setFamilyName(e.target.value)}
                    placeholder="家族名"
                  />
                  <Button onClick={handleUpdateFamilyName}>保存</Button>
                  <Button variant="secondary" onClick={() => setEditingName(false)}>キャンセル</Button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xl font-bold text-gray-900">{family.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{family.members.length}人のメンバー</p>
                  </div>
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setFamilyName(family.name);
                        setEditingName(true);
                      }}
                    >
                      編集
                    </Button>
                  )}
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <h3 className="font-semibold text-gray-900">メンバー</h3>
                {isAdmin && (
                  <Button size="sm" onClick={() => setShowInviteModal(true)}>
                    + 招待
                  </Button>
                )}
              </div>

              <div className="divide-y divide-gray-100">
                {family.members.map((member) => (
                  <div key={member.uid} className="flex items-center gap-4 px-5 py-4">
                    <Avatar src={member.photoURL} name={member.displayName} size="sm" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900">{member.displayName}</p>
                      <p className="text-sm text-gray-500 truncate">{member.email}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        member.role === 'admin'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {member.role === 'admin' ? '管理者' : 'メンバー'}
                      </span>
                      {isAdmin && member.uid !== user?.uid && (
                        <button
                          onClick={() => removeMember(family.id, member.uid)}
                          className="text-xs text-red-500 hover:text-red-700"
                        >
                          削除
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      <Modal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        title="メンバーを招待"
      >
        <form onSubmit={handleInvite} className="space-y-4">
          <Input
            label="メールアドレス"
            type="email"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            placeholder="招待するメールアドレス"
            required
          />
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setShowInviteModal(false)}>
              キャンセル
            </Button>
            <Button type="submit" loading={inviting}>
              招待を送る
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
