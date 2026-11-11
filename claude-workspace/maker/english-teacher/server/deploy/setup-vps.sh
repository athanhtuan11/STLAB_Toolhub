#!/usr/bin/env bash
# Cai cong VPS cho co giao tieng Anh (Ubuntu/Debian, chay bang root). Chay lai duoc.
#   PUBLIC_HOST=teacher.example.vn FRP_VERSION=<x.y.z> FRP_AUTH_TOKEN=... bash setup-vps.sh
# FRP_VERSION: lay ban phat hanh moi nhat (>= 2 tuan tuoi) tai https://github.com/fatedier/frp/releases
# File can o cung thu muc: Caddyfile, frps.toml.
set -euo pipefail
: "${PUBLIC_HOST:?thieu PUBLIC_HOST}" "${FRP_VERSION:?thieu FRP_VERSION}" "${FRP_AUTH_TOKEN:?thieu FRP_AUTH_TOKEN}"
[ "${#FRP_AUTH_TOKEN}" -ge 24 ] || { echo "FRP_AUTH_TOKEN phai >= 24 ky tu"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
ARCH=$(dpkg --print-architecture)   # amd64 | arm64

# 1) Caddy tu kho chinh thuc
if ! command -v caddy >/dev/null; then
  apt-get update -y && apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -y && apt-get install -y caddy
fi
install -m 644 "$HERE/Caddyfile" /etc/caddy/Caddyfile
mkdir -p /var/log/caddy && chown caddy:caddy /var/log/caddy
grep -q '^PUBLIC_HOST=' /etc/default/caddy 2>/dev/null && sed -i "s/^PUBLIC_HOST=.*/PUBLIC_HOST=$PUBLIC_HOST/" /etc/default/caddy \
  || echo "PUBLIC_HOST=$PUBLIC_HOST" >> /etc/default/caddy
mkdir -p /etc/systemd/system/caddy.service.d
printf '[Service]\nEnvironmentFile=/etc/default/caddy\n' > /etc/systemd/system/caddy.service.d/env.conf

# 2) frps (kiem sha256 theo file checksum cua ban phat hanh)
if [ "$(/usr/local/bin/frps --version 2>/dev/null || true)" != "$FRP_VERSION" ]; then
  T=$(mktemp -d); cd "$T"
  F="frp_${FRP_VERSION}_linux_${ARCH}.tar.gz"
  curl -fsSLO "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/${F}"
  curl -fsSLO "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_sha256_checksums.txt"
  grep " ${F}\$" frp_sha256_checksums.txt | sha256sum -c -
  tar xzf "$F" && install -m 755 "frp_${FRP_VERSION}_linux_${ARCH}/frps" /usr/local/bin/frps
  cd / && rm -rf "$T"
fi
install -d -m 750 /etc/frp && install -m 640 "$HERE/frps.toml" /etc/frp/frps.toml
umask 077; printf 'FRP_AUTH_TOKEN=%s\n' "$FRP_AUTH_TOKEN" > /etc/frp/frps.env
cat > /etc/systemd/system/frps.service <<'EOF'
[Unit]
Description=frps (cong co giao tieng Anh)
After=network-online.target
Wants=network-online.target
[Service]
EnvironmentFile=/etc/frp/frps.env
ExecStart=/usr/local/bin/frps -c /etc/frp/frps.toml
Restart=always
RestartSec=5
DynamicUser=yes
LogsDirectory=frps
[Install]
WantedBy=multi-user.target
EOF
sed -i 's#^log.to = .*#log.to = "/var/log/frps/frps.log"#' /etc/frp/frps.toml
chmod 644 /etc/frp/frps.toml; chmod 600 /etc/frp/frps.env

# 3) Tuong lua: chi SSH, HTTP/HTTPS (Caddy), 7000 (frpc tu may lab)
if command -v ufw >/dev/null; then
  ufw allow OpenSSH; ufw allow 80/tcp; ufw allow 443/tcp; ufw allow 7000/tcp; ufw --force enable
fi

systemctl daemon-reload
systemctl enable --now frps
systemctl restart caddy
systemctl --no-pager --lines=3 status frps caddy | grep -E "Active|frps|caddy" || true
echo "Xong. Kiem: curl -s -o /dev/null -w '%{http_code}' https://$PUBLIC_HOST/  (404 = Caddy chay, chung chi OK)"
