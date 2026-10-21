#!/usr/bin/env bash
set -Eeuo pipefail
cd /home/runner
mkdir -p /runner-state/_work
for file in .runner .credentials .credentials_rsaparams; do
  [[ -L $file ]] || ln -s "/runner-state/$file" "$file"
done
if [[ ! -f /runner-state/.runner ]]; then
  token_file=/runner-state/registration-token
  [[ -s $token_file ]] || { echo 'Runner registration token is missing' >&2; exit 1; }
  token=$(< "$token_file")
  ./config.sh --unattended --replace \
    --url https://github.com/00JIMMY00/elsakr_app \
    --token "$token" --name elsakr-hassan \
    --labels elsakr-deploy --work /runner-state/_work
  unset token
  rm -f "$token_file"
fi
exec ./run.sh
