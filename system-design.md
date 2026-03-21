# 家族向け Web サービス — システム設計書

> **目的**: 本ドキュメントは、家族向け Web サービスのデータ基盤・アプリケーション構成・データスキーマを包括的にまとめた設計書です。
> **用途**: 実装エージェントへの引き継ぎ資料として使用します。

-----

## 1. サービス概要

### 1.1 サービスの目的

家族間のコミュニケーションとタスク管理を一元化する Web サービス。

### 1.2 主要機能

|機能   |概要                                     |
|-----|---------------------------------------|
|チャット |家族間のリアルタイムメッセージング。画像添付・リアクション・既読管理に対応  |
|カレンダー|家族の予定管理。繰り返しイベント・終日イベント・リマインダー・参加者管理に対応|
|TODO |共有タスク管理。リスト分類・担当者アサイン・優先度・期限管理に対応      |

### 1.3 技術スタック概要

|レイヤー   |技術                                                           |
|-------|-------------------------------------------------------------|
|フロントエンド|React / Next.js（SPA）                                         |
|バックエンド |Python（FastAPI）on Cloud Run                                  |
|認証     |Firebase Authentication                                      |
|データストア |Firestore / Cloud SQL（PostgreSQL） / Cloud Storage            |
|データ基盤  |BigQuery + dbt（Cloud Workflows + Cloud Scheduler でオーケストレーション）|
|インフラ   |GCP（プロジェクト: youyaku-ai / youyaku-ai-dev）                    |

-----

## 2. GCP アプリケーション構成

### 2.1 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│  クライアント                                            │
│  Web ブラウザ（React / Next.js SPA）                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼────────────────────────────────────┐
│  エッジ / 配信                                           │
│  Firebase Hosting │ Cloud Load Balancing │ Cloud CDN     │
│  Cloud Armor（WAF / DDoS 防御）                          │
└──────┬─────────────────────────────┬────────────────────┘
       │ API リクエスト                │ 認証トークン
       ▼                             ▼
┌──────────────────────┐  ┌────────────────────────────┐
│  バックエンド          │  │  認証                       │
│                      │  │  Firebase Authentication    │
│  Cloud Run           │  │  Google / Email / Apple     │
│  Python + FastAPI    │  │  ID Token (JWT) 発行        │
│  REST API サーバー    │  └────────────────────────────┘
│                      │
│  Cloud Functions     │  ← Firestore トリガー / 通知送信 / 画像リサイズ
│  Cloud Tasks         │  ← リマインダー配信 / バッチ処理
│  FCM                 │  ← プッシュ通知
└──────────┬───────────┘
           │ 読み書き
           ▼
┌─────────────────────────────────────────────────────────┐
│  データストア                                             │
│                                                         │
│  Firestore          Cloud SQL          Cloud Storage    │
│  (リアルタイム)      (PostgreSQL)       (メディア)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 各コンポーネントの役割

#### 2.2.1 フロントエンド

- **Firebase Hosting** で静的ファイルを配信（Cloud CDN によるキャッシュ付き）
- React / Next.js の SPA として構築
- Firestore SDK を使ってチャット・TODO のリアルタイム同期を直接行う
- Firebase Auth SDK でクライアント側認証を処理

#### 2.2.2 認証（Firebase Authentication）

認証フローは以下の通り:

1. クライアントが Firebase Auth SDK で認証（Google / Email / Apple Sign-In）
1. Firebase から ID Token（JWT）を取得
1. API リクエスト時に `Authorization: Bearer <ID Token>` ヘッダーに付与
1. Cloud Run（FastAPI）側で `firebase-admin` SDK を用いて JWT を検証
1. トークンから `uid` を取得し、Cloud SQL の `users` テーブルで `family_id` を参照して権限チェック

#### 2.2.3 バックエンド（Cloud Run — Python / FastAPI）

メインの REST API サーバー。サーバーレスでオートスケール。

主要ライブラリ:

|ライブラリ                       |用途                      |
|----------------------------|------------------------|
|`fastapi`                   |Web フレームワーク             |
|`uvicorn`                   |ASGI サーバー               |
|`firebase-admin`            |JWT 検証 / Firestore 操作   |
|`sqlalchemy` + `asyncpg`    |Cloud SQL（PostgreSQL）ORM|
|`cloud-sql-python-connector`|Cloud SQL 接続            |
|`google-cloud-storage`      |GCS 操作                  |
|`google-cloud-tasks`        |Cloud Tasks キュー操作       |

主要 API エンドポイント:

|メソッド|パス                               |概要              |
|----|---------------------------------|----------------|
|POST|`/api/v1/auth/verify`            |トークン検証          |
|GET |`/api/v1/families/:id`           |家族情報取得          |
|CRUD|`/api/v1/families/:id/members`   |メンバー管理          |
|CRUD|`/api/v1/families/:id/chat-rooms`|チャットルーム管理       |
|CRUD|`/api/v1/families/:id/events`    |カレンダーイベント       |
|POST|`/api/v1/media/upload`           |ファイルアップロード → GCS|


> **注記**: チャットメッセージ・TODO の CRUD は Firestore SDK でクライアントから直接操作する（Firestore Security Rules で認可制御）。

#### 2.2.4 Cloud Functions（Python）

|トリガー                               |処理内容                 |
|-----------------------------------|---------------------|
|Firestore `messages` の `onCreate`  |FCM 経由でチャット通知を送信     |
|Firestore `todo_items` の `onUpdate`|担当者変更時に通知            |
|Cloud Storage の `onFinalize`       |アップロード画像のリサイズ・サムネイル生成|

#### 2.2.5 Cloud Tasks

|ジョブ        |処理内容                                    |
|-----------|----------------------------------------|
|リマインダー配信   |カレンダーイベントの `reminder_minutes` に基づきスケジュール|
|TODO 期限アラート|`due_date` の前日に通知                       |
|データエクスポート  |家族データの JSON エクスポート生成 → GCS              |

#### 2.2.6 セキュリティ

|コンポーネント                 |役割                 |
|------------------------|-------------------|
|Cloud Armor             |WAF / DDoS 防御      |
|Cloud Load Balancing    |API トラフィック分散       |
|Secret Manager          |API キー・DB パスワード等の管理|
|Firestore Security Rules|クライアント直接アクセスの認可制御  |

-----

## 3. データ設計

### 3.1 保存先の設計方針

|保存先                       |選定理由                              |対象データ                                  |
|--------------------------|----------------------------------|---------------------------------------|
|**Firestore**             |リアルタイム同期が必要。ドキュメント単位の読み書きが高速      |チャットメッセージ、リアクション、TODO リスト、TODO アイテム    |
|**Cloud SQL (PostgreSQL)**|リレーショナル整合性が必要。JOIN・トランザクションが頻繁に発生 |ユーザー、家族グループ、チャットルーム、カレンダーイベント、メディアメタデータ|
|**Cloud Storage (GCS)**   |非構造化バイナリデータ。サイズが大きく DB に入れるべきでないもの|プロフィール画像、チャット添付画像、家族アイコン、エクスポートファイル    |

### 3.2 テーブル / コレクション一覧

|名前                        |保存先      |機能   |概要                    |
|--------------------------|---------|-----|----------------------|
|`families`                |Cloud SQL|共通   |家族グループ管理              |
|`users`                   |Cloud SQL|共通   |ユーザー情報                |
|`chat_rooms`              |Cloud SQL|チャット |チャットルームのメタ情報          |
|`messages`                |Firestore|チャット |メッセージ本文（リアルタイム同期）     |
|`message_reactions`       |Firestore|チャット |リアクション（スタンプ）          |
|`calendar_events`         |Cloud SQL|カレンダー|予定・イベント               |
|`calendar_event_attendees`|Cloud SQL|カレンダー|イベント参加者               |
|`todo_lists`              |Firestore|TODO |TODO リスト              |
|`todo_items`              |Firestore|TODO |個別タスク                 |
|`media_files`             |Cloud SQL|共通   |メディアファイルのメタ情報（実体は GCS）|

### 3.3 エンティティ関連図

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   families  │────▶│    users     │────▶│  chat_rooms │
│  (CloudSQL) │     │  (CloudSQL)  │     │ (CloudSQL)  │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       │              ┌────┴─────┐         ┌────┴──────────┐
       │              │          │         │               │
       ▼              ▼          ▼         ▼               ▼
┌────────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│  calendar  │ │   todos   │ │ todo   │ │ messages │ │  media   │
│  _events   │ │           │ │ _items │ │(Firestore│ │  (GCS)   │
│ (CloudSQL) │ │(Firestore)│ │(Fire..)│ │         )│ │          │
└────────────┘ └───────────┘ └────────┘ └──────────┘ └──────────┘
```

-----

### 3.4 Cloud SQL スキーマ定義

#### 3.4.1 families テーブル

```sql
CREATE TABLE families (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    invite_code     VARCHAR(20) NOT NULL UNIQUE,
    plan            VARCHAR(20) NOT NULL DEFAULT 'free',
    icon_url        VARCHAR(500),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 3.4.2 users テーブル

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    firebase_uid    VARCHAR(128) NOT NULL UNIQUE,
    display_name    VARCHAR(50) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(500),
    role            VARCHAR(20) NOT NULL DEFAULT 'member',
    date_of_birth   DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 3.4.3 chat_rooms テーブル

```sql
CREATE TABLE chat_rooms (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    name            VARCHAR(100) NOT NULL,
    type            VARCHAR(20) NOT NULL,
    created_by      UUID NOT NULL REFERENCES users(id),
    last_message_at TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 3.4.4 calendar_events テーブル

```sql
CREATE TABLE calendar_events (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id         UUID NOT NULL REFERENCES families(id),
    created_by        UUID NOT NULL REFERENCES users(id),
    title             VARCHAR(200) NOT NULL,
    description       TEXT,
    start_at          TIMESTAMP NOT NULL,
    end_at            TIMESTAMP NOT NULL,
    is_all_day        BOOLEAN NOT NULL DEFAULT FALSE,
    location          VARCHAR(300),
    color             VARCHAR(7),
    recurrence_rule   VARCHAR(255),
    reminder_minutes  INTEGER,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 3.4.5 calendar_event_attendees テーブル

```sql
CREATE TABLE calendar_event_attendees (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id      UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    user_id       UUID NOT NULL REFERENCES users(id),
    status        VARCHAR(20) NOT NULL DEFAULT 'tentative',
    responded_at  TIMESTAMP,
    UNIQUE(event_id, user_id)
);
```

#### 3.4.6 media_files テーブル

```sql
CREATE TABLE media_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    uploaded_by     UUID NOT NULL REFERENCES users(id),
    gcs_path        VARCHAR(500) NOT NULL,
    file_name       VARCHAR(255) NOT NULL,
    content_type    VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    context_type    VARCHAR(20) NOT NULL,
    context_id      VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

-----

### 3.5 Firestore ドキュメント設計

#### 3.5.1 messages コレクション

**パス**: `chat_rooms/{roomId}/messages/{messageId}`

```json
{
    "message_id": "string",
    "room_id": "string",
    "sender_id": "string",
    "type": "text | image | stamp",
    "body": "string",
    "media_url": "string | null",
    "reply_to": "string | null",
    "is_deleted": "boolean",
    "read_by": ["string"],
    "created_at": "Timestamp",
    "updated_at": "Timestamp"
}
```

#### 3.5.2 todo_lists コレクション

**パス**: `families/{familyId}/todo_lists/{listId}`

```json
{
    "list_id": "string",
    "family_id": "string",
    "name": "string",
    "color": "string",
    "created_by": "string",
    "sort_order": "number",
    "is_archived": "boolean",
    "created_at": "Timestamp",
    "updated_at": "Timestamp"
}
```

#### 3.5.3 todo_items コレクション

**パス**: `families/{familyId}/todo_lists/{listId}/todo_items/{itemId}`

```json
{
    "item_id": "string",
    "list_id": "string",
    "title": "string",
    "description": "string | null",
    "is_completed": "boolean",
    "completed_at": "Timestamp | null",
    "completed_by": "string | null",
    "assigned_to": "string | null",
    "due_date": "Timestamp | null",
    "priority": "low | medium | high",
    "sort_order": "number",
    "created_by": "string",
    "created_at": "Timestamp",
    "updated_at": "Timestamp"
}
```

-----

### 3.6 Cloud Storage（GCS）設計

**バケット名**: `family-app-media-<env>`

```
gs://family-app-media-prod/
├── avatars/{user_id}/profile.webp
├── chat/{room_id}/{message_id}/image_001.webp
├── families/{family_id}/icon.webp
└── exports/{family_id}/{date}/data_export.json
```

-----

## 4. データ基盤構成

### 4.1 BigQuery レイヤー定義

|レイヤー   |名称           |テーブル例                                               |
|-------|-------------|-----------------------------------------------------|
|Layer 1|DWH / Staging|`raw_users`, `raw_orders`, `raw_events`, `raw_logs` |
|Layer 2|Data Mart    |`dim_users`, `fct_orders`, `fct_daily_active`       |
|Layer 3|Report / BI  |`rpt_daily_kpi`, `rpt_user_retention`, `rpt_revenue`|

-----

## 5. 環境構成

|環境  |用途   |GCP プロジェクト       |
|----|-----|-----------------|
|dev |開発・検証|`youyaku-ai-dev` |
|prod|本番   |`youyaku-ai`     |

-----

## 6. 実装の優先順位

|順序|対象                             |
|--|-------------------------------|
|1 |`backend/` (models + auth)     |
|2 |`backend/` (routers + services)|
|3 |`infra/`                       |
|4 |`firebase/`                    |
|5 |`functions/`                   |
|6 |`frontend/`                    |
|7 |`data-platform/`               |
|8 |`.github/workflows/`           |
