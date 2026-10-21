#!/usr/bin/env bash
set -Eeuo pipefail

deploy_dir=/home/hassan/elsakr
runner_dir=/home/hassan/elsakr-runner
[[ $(id -un) == hassan ]] || { echo 'Run as hassan on the client machine' >&2; exit 2; }
getent group docker >/dev/null
mkdir -p "$deploy_dir" "$runner_dir"
chgrp docker "$deploy_dir" "$runner_dir"
chmod 2770 "$deploy_dir" "$runner_dir"

if [[ ! -e $deploy_dir/.env ]]; then
  umask 007
  cat > "$deploy_dir/.env" <<EOF
APP_IMAGE=pending
DB_PASSWORD=$(openssl rand -hex 32)
ADMIN_PASSWORD=$(openssl rand -hex 32)
EOF
  chgrp docker "$deploy_dir/.env"
  chmod 660 "$deploy_dir/.env"
fi

install -m 660 -g docker deploy/compose.yaml "$deploy_dir/compose.yaml"
install -m 660 -g docker deploy/runner.compose.yaml "$deploy_dir/runner.compose.yaml"
install -m 660 -g docker deploy/runner-entrypoint.sh "$deploy_dir/runner-entrypoint.sh"
echo "Runtime prepared in $deploy_dir. The generated Administrator password is in .env."
