#!/usr/bin/env bash
set -Eeuo pipefail

target_ref=${1:?pass an image digest}
deploy_dir=${2:?pass the deployment directory}
site=elsakr.arab-erp.com
[[ $target_ref =~ ^ghcr\.io/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$ ]] || exit 2
cd "$deploy_dir"
[[ -f .env && -f compose.yaml && -f next.compose.yaml && -f next.apps.txt ]] || {
  echo 'Missing deployment configuration' >&2; exit 2;
}
set -a
source .env
set +a
: "${DB_PASSWORD:?}"
: "${ADMIN_PASSWORD:?}"

exec 9>.rollout.lock
flock -n 9 || { echo 'Another rollout is in progress' >&2; exit 1; }
compose() { docker compose -p elsakr -f compose.yaml "$@"; }
backend() { compose exec -T backend "$@"; }
old_ref=${APP_IMAGE:-}
old_compose=$(mktemp)
cp compose.yaml "$old_compose"
backup_dir=
first_install=0
if [[ -z $old_ref || $old_ref == pending ]]; then
  # A failed first rollout may already have created the site. Adopt its image
  # so a retry backs up that site and can roll back after a later failure.
  old_container=$(docker ps -q \
    --filter label=com.docker.compose.project=elsakr \
    --filter label=com.docker.compose.service=backend | head -1)
  if [[ -n $old_container ]] && docker exec "$old_container" \
    test -f "/home/frappe/frappe-bench/sites/$site/site_config.json"; then
    old_ref=$(docker inspect -f '{{.Config.Image}}' "$old_container")
  else
    first_install=1
  fi
elif ! docker image inspect "$old_ref" >/dev/null 2>&1; then
  echo "Previous image is unavailable: $old_ref" >&2
  exit 1
fi

set_image() {
  local image=$1 tmp
  tmp=$(mktemp .env.XXXXXX)
  grep -v '^APP_IMAGE=' .env > "$tmp" || true
  printf 'APP_IMAGE=%s\n' "$image" >> "$tmp"
  chmod 660 "$tmp"
  mv "$tmp" .env
  export APP_IMAGE=$image
}

healthy() {
  local service cid
  for service in backend frontend websocket queue-short queue-long scheduler; do
    cid=$(compose ps -q "$service")
    [[ -n $cid && $(docker inspect -f '{{.State.Status}}' "$cid") == running ]] || return 1
  done
  [[ $(curl -fsS --max-time 8 http://127.0.0.1:8000/api/method/ping | tr -d '\n ') == '{"message":"pong"}' ]]
}

wait_healthy() {
  local end=$((SECONDS + 180))
  until healthy && { sleep 5; healthy; }; do
    (( SECONDS < end )) || return 1
    sleep 5
  done
}

rollback() {
  echo 'Deployment failed; restoring previous image and site backup' >&2
  if (( first_install )); then
    echo 'First install has no prior site; leaving containers for diagnosis' >&2
    return 1
  fi
  cp "$old_compose" compose.yaml
  set_image "$old_ref"
  compose up -d --pull never || return 1
  if [[ -n $backup_dir ]]; then
    local db public private root=/home/frappe/frappe-bench/sites/$site/private/backups/$backup_dir
    db=$(backend bash -lc "find '$root' -maxdepth 1 -name '*-database.sql.gz' -print -quit")
    public=$(backend bash -lc "find '$root' -maxdepth 1 -name '*-files.tgz' ! -name '*-private-files.tgz' -print -quit")
    private=$(backend bash -lc "find '$root' -maxdepth 1 -name '*-private-files.tgz' -print -quit")
    [[ -n $db && -n $public && -n $private ]] || return 1
    backend bench --site "$site" restore "$db" --with-public-files "$public" \
      --with-private-files "$private" --db-root-password "$DB_PASSWORD" --force || return 1
    backend bench --site "$site" enable-scheduler || return 1
    backend bench --site "$site" clear-cache || return 1
    backend bench --site "$site" set-maintenance-mode off || return 1
  fi
  wait_healthy
}

# Pulling first leaves the live site untouched if the registry is unavailable.
export APP_IMAGE=$target_ref
docker compose -p elsakr -f next.compose.yaml pull || exit 1
if (( ! first_install )); then
  backup_dir=deploy-$(date -u +%Y%m%dT%H%M%SZ)-${target_ref: -12}
  backend bench --site "$site" set-maintenance-mode on
  if ! backend bench --site "$site" backup --with-files --compress \
    --backup-path "/home/frappe/frappe-bench/sites/$site/private/backups/$backup_dir"; then
    backend bench --site "$site" set-maintenance-mode off || true
    exit 1
  fi
fi

roll_forward() {
  cp "$deploy_dir/next.compose.yaml" compose.yaml || return 1
  compose up -d --pull never || return 1
  if (( first_install )); then
    backend bench new-site "$site" --db-root-password "$DB_PASSWORD" \
      --admin-password "$ADMIN_PASSWORD" --mariadb-user-host-login-scope '%' \
      --set-default || return 1
  fi
  mapfile -t desired < next.apps.txt
  [[ ${#desired[@]} -gt 0 ]] || return 1
  available=$(backend cat sites/apps.txt) || return 1
  installed=$(backend bench --site "$site" list-apps -f json) || return 1
  for app in "${desired[@]}"; do
    grep -qx "$app" <<< "$available" || return 1
    if ! jq -e --arg site "$site" --arg app "$app" '.[$site] | index($app)' <<< "$installed" >/dev/null; then
      backend bench --site "$site" install-app "$app" || return 1
    fi
  done
  backend bench --site "$site" migrate || return 1
  if (( first_install )); then
    backend bench --site "$site" enable-scheduler || return 1
  fi
  backend bench --site "$site" clear-cache || return 1
  backend bench --site "$site" set-maintenance-mode off || return 1
  wait_healthy
}
if ! roll_forward; then
  rollback || echo 'Automatic rollback failed; inspect containers and backup immediately' >&2
  rm -f "$old_compose"
  exit 1
fi

set_image "$target_ref"
printf '%s\n' "$target_ref" > .current-image
rm -f "$old_compose" next.compose.yaml next.apps.txt
echo "Deployment complete: $target_ref"
