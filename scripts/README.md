# scripts

インフラ・CI/CD セットアップ用スクリプト集。

---

## setup_wif.sh

GitHub Actions から GCP へ**キーレス認証**するための Workload Identity Federation (WIF) をセットアップするスクリプトです。

### 前提条件

| ツール | 確認コマンド |
|--------|-------------|
| gcloud CLI | `gcloud version` |
| GitHub CLI (gh) | `gh version` |

```bash
# gcloud へのログイン
gcloud auth login

# gh へのログイン
gh auth login
```

### ファイル構成

```
scripts/
├── README.md
├── setup_wif.sh          # セットアップスクリプト
├── setup_wif.env.example # パラメーター設定テンプレート（git管理対象）
└── setup_wif.env         # パラメーター設定（git管理外・要作成）
```

### 使い方

**1. envファイルを作成する**

```bash
cp scripts/setup_wif.env.example scripts/setup_wif.env
```

**2. envファイルを編集する**

```bash
vi scripts/setup_wif.env
```

| 変数 | 説明 | デフォルト値 |
|------|------|-------------|
| `GITHUB_ORG` | GitHub Organization名 | `sakamoto-family-smile` |
| `GITHUB_REPO` | GitHubリポジトリ名 | `family-infra-service` |
| `GCP_PROJECTS` | GCPプロジェクトID（カンマ区切り、prod/devの順） | `youyaku-ai,youyaku-ai-dev` |
| `GITHUB_ENVS` | GitHub Environment名（カンマ区切り、prod/devの順） | `prod,dev` |
| `POOL_ID` | Workload Identity Pool ID | `github-actions-pool` |
| `PROVIDER_ID` | Workload Identity Provider ID | `github-actions-provider` |
| `SA_NAME` | サービスアカウント名 | `github-actions-sa` |

**3. スクリプトを実行する**

```bash
./scripts/setup_wif.sh
```

実行中に `DB_PASSWORD` の入力を求められます（prod/dev それぞれ）。

### スクリプトが行うこと

1. **GCP API の有効化** — IAM, STS, IAM Credentials, Cloud Resource Manager
2. **Workload Identity Pool の作成** — 既存の場合はスキップ
3. **Workload Identity Provider の作成** — GitHub OIDC と連携、既存の場合はスキップ
4. **サービスアカウントの作成** — 既存の場合はスキップ
5. **IAM ロールの付与** — `roles/editor`, `roles/iam.serviceAccountTokenCreator`, `roles/storage.admin`
6. **WIF バインディングの設定** — リポジトリ単位でアクセスを限定
7. **GitHub Variables の設定** — `WIF_PROVIDER`, `GCP_SA_EMAIL` を各 Environment に登録
8. **GitHub Secrets の設定** — `DB_PASSWORD` を各 Environment に登録

### GitHub に設定される値

実行後、GitHub リポジトリの **Settings → Environments** に以下が設定されます。

| 種別 | キー | 説明 |
|------|------|------|
| Variable | `WIF_PROVIDER` | WIF プロバイダーのリソース名 |
| Variable | `GCP_SA_EMAIL` | サービスアカウントのメールアドレス |
| Secret | `DB_PASSWORD` | データベースパスワード |

### 注意事項

- `setup_wif.env` は `.gitignore` により git 管理対象外です。リポジトリにコミットしないでください。
- 付与する `roles/editor` は広めの権限です。Terraform で操作するリソースが確定したら最小権限に絞ることを推奨します。
- スクリプトは冪等です。再実行しても既存リソースはスキップされます。
