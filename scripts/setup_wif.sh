#!/bin/bash
# ============================================================
# Workload Identity Federation (WIF) セットアップスクリプト
# GCP + GitHub Actions 連携用
#
# 使い方:
#   cp scripts/setup_wif.env.example scripts/setup_wif.env
#   # setup_wif.env の値を編集する
#   chmod +x scripts/setup_wif.sh
#   ./scripts/setup_wif.sh
# ============================================================

set -euo pipefail

# ============================================================
# envファイルの読み込み
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/setup_wif.env"

if [ ! -f "${ENV_FILE}" ]; then
  echo "[ERROR] ${ENV_FILE} が見つかりません"
  echo "  cp scripts/setup_wif.env.example scripts/setup_wif.env"
  echo "  を実行して値を設定してください"
  exit 1
fi

# shellcheck source=scripts/setup_wif.env
source "${ENV_FILE}"

# カンマ区切り文字列を配列に変換
IFS=',' read -ra GCP_PROJECTS <<< "${GCP_PROJECTS}"
IFS=',' read -ra GITHUB_ENVS  <<< "${GITHUB_ENVS}"

# 必須変数チェック
: "${GITHUB_ORG:?setup_wif.env に GITHUB_ORG を設定してください}"
: "${GITHUB_REPO:?setup_wif.env に GITHUB_REPO を設定してください}"
: "${POOL_ID:?setup_wif.env に POOL_ID を設定してください}"
: "${PROVIDER_ID:?setup_wif.env に PROVIDER_ID を設定してください}"
: "${SA_NAME:?setup_wif.env に SA_NAME を設定してください}"

# ============================================================
# カラー出力
# ============================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ============================================================
# 前提チェック
# ============================================================
check_prerequisites() {
  info "前提ツールのチェック..."

  command -v gcloud >/dev/null 2>&1 || error "gcloud がインストールされていません"
  command -v gh     >/dev/null 2>&1 || error "gh (GitHub CLI) がインストールされていません"

  gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@" \
    || error "gcloud にログインしていません。'gcloud auth login' を実行してください"

  gh auth status >/dev/null 2>&1 \
    || error "gh にログインしていません。'gh auth login' を実行してください"

  info "前提チェック OK"
}

# ============================================================
# 1プロジェクト分のWIFセットアップ
# ============================================================
setup_project() {
  local PROJECT_ID="$1"
  local GITHUB_ENV="$2"

  echo ""
  info "========================================"
  info "プロジェクト: ${PROJECT_ID} (env: ${GITHUB_ENV})"
  info "========================================"

  # プロジェクト番号の取得
  PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)" 2>/dev/null) \
    || error "プロジェクト '${PROJECT_ID}' が見つかりません。プロジェクトIDを確認してください"
  info "プロジェクト番号: ${PROJECT_NUMBER}"

  # 必要なAPIの有効化
  info "必要なAPIを有効化中..."
  gcloud services enable \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iamcredentials.googleapis.com \
    sts.googleapis.com \
    --project="${PROJECT_ID}"
  info "API有効化 完了"

  # ---- Workload Identity Pool ----
  info "Workload Identity Pool を確認/作成中..."
  if gcloud iam workload-identity-pools describe "${POOL_ID}" \
      --project="${PROJECT_ID}" \
      --location=global \
      --format="value(name)" >/dev/null 2>&1; then
    warn "Pool '${POOL_ID}' は既に存在します。スキップします"
  else
    gcloud iam workload-identity-pools create "${POOL_ID}" \
      --project="${PROJECT_ID}" \
      --location=global \
      --display-name="GitHub Actions Pool" \
      --description="Workload Identity Pool for GitHub Actions"
    info "Pool 作成完了"
  fi

  # ---- Workload Identity Provider ----
  info "Workload Identity Provider を確認/作成中..."
  if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
      --project="${PROJECT_ID}" \
      --location=global \
      --workload-identity-pool="${POOL_ID}" \
      --format="value(name)" >/dev/null 2>&1; then
    warn "Provider '${PROVIDER_ID}' は既に存在します。スキップします"
  else
    gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
      --project="${PROJECT_ID}" \
      --location=global \
      --workload-identity-pool="${POOL_ID}" \
      --display-name="GitHub Actions Provider" \
      --issuer-uri="https://token.actions.githubusercontent.com" \
      --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
      --attribute-condition="assertion.repository_owner == '${GITHUB_ORG}'"
    info "Provider 作成完了"
  fi

  # ---- サービスアカウント ----
  SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
  info "サービスアカウントを確認/作成中: ${SA_EMAIL}"
  if gcloud iam service-accounts describe "${SA_EMAIL}" \
      --project="${PROJECT_ID}" >/dev/null 2>&1; then
    warn "サービスアカウント '${SA_EMAIL}' は既に存在します。スキップします"
  else
    gcloud iam service-accounts create "${SA_NAME}" \
      --project="${PROJECT_ID}" \
      --display-name="GitHub Actions Service Account" \
      --description="Used by GitHub Actions via WIF"
    info "サービスアカウント作成完了"
  fi

  # ---- サービスアカウントへのIAMロール付与 ----
  info "IAMロールを付与中..."
  local ROLES=(
    "roles/editor"
    "roles/iam.serviceAccountTokenCreator"
    "roles/storage.admin"
  )
  for ROLE in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
      --member="serviceAccount:${SA_EMAIL}" \
      --role="${ROLE}" \
      --condition=None \
      --quiet >/dev/null
    info "  付与: ${ROLE}"
  done

  # ---- WIF バインディング ----
  info "WIF バインディングを設定中..."
  POOL_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}"

  gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_RESOURCE}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}" \
    --quiet >/dev/null
  info "WIF バインディング完了"

  # ---- WIF_PROVIDER の値を生成 ----
  WIF_PROVIDER_VALUE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"

  # ---- GitHub Environment Variables の設定 ----
  info "GitHub Environment Variables を設定中 (env: ${GITHUB_ENV})..."

  gh variable set WIF_PROVIDER \
    --repo="${GITHUB_ORG}/${GITHUB_REPO}" \
    --env="${GITHUB_ENV}" \
    --body="${WIF_PROVIDER_VALUE}"
  info "  WIF_PROVIDER 設定完了"

  gh variable set GCP_SA_EMAIL \
    --repo="${GITHUB_ORG}/${GITHUB_REPO}" \
    --env="${GITHUB_ENV}" \
    --body="${SA_EMAIL}"
  info "  GCP_SA_EMAIL 設定完了"

  echo ""
  info "========================================"
  info "${PROJECT_ID} のセットアップ完了"
  info "  WIF_PROVIDER : ${WIF_PROVIDER_VALUE}"
  info "  GCP_SA_EMAIL : ${SA_EMAIL}"
  info "========================================"
}

# ============================================================
# DB_PASSWORD の設定
# ============================================================
setup_db_password() {
  echo ""
  info "========================================"
  info "DB_PASSWORD の設定"
  info "========================================"

  for GITHUB_ENV in "${GITHUB_ENVS[@]}"; do
    echo -n "DB_PASSWORD (env: ${GITHUB_ENV}) を入力してください: "
    read -rs DB_PASS
    echo ""

    if [ -z "${DB_PASS}" ]; then
      warn "DB_PASSWORD が空です。スキップします (env: ${GITHUB_ENV})"
      continue
    fi

    echo "${DB_PASS}" | gh secret set DB_PASSWORD \
      --repo="${GITHUB_ORG}/${GITHUB_REPO}" \
      --env="${GITHUB_ENV}"
    info "DB_PASSWORD 設定完了 (env: ${GITHUB_ENV})"
  done
}

# ============================================================
# メイン処理
# ============================================================
main() {
  echo ""
  echo "============================================================"
  echo " Workload Identity Federation セットアップ"
  echo " GitHub Repo : ${GITHUB_ORG}/${GITHUB_REPO}"
  echo "============================================================"
  echo ""

  check_prerequisites

  # prod / dev それぞれセットアップ
  for i in "${!GCP_PROJECTS[@]}"; do
    setup_project "${GCP_PROJECTS[$i]}" "${GITHUB_ENVS[$i]}"
  done

  # DB_PASSWORD の設定
  setup_db_password

  echo ""
  info "============================================================"
  info "全セットアップ完了！"
  info "GitHub Actions の terraform plan CI を再実行してください"
  info "============================================================"
}

main "$@"
