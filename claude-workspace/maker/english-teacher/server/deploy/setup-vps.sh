#!/usr/bin/env bash
# Cai cong VPS cho co giao tieng Anh tren VPS DA CO nginx + certbot (Tino, phuc vu mamnoncaynho.com). Chay lai duoc.
#   TUNNEL_PUBKEY="$(cat id_ed25519_engtunnel.pub)" bash setup-vps.sh      (chay bang root)
# Can cung thu muc: nginx-engteacher.conf. KHONG dong toi site khac, KHONG bat tuong lua.
set -euo pipefail
: "${TUNNEL_PUBKEY:?thieu TUNNEL_PUBKEY (khoa cong khai id_ed25519_engtunnel.pub cua may lab)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
HOST=$(grep -oP 'server_name\s+\K[^;]+' "$HERE/nginx-engteacher.conf")

# 1) nginx: sao luu, them site rieng, kiem cu phap truoc khi nap lai
BK="/root/backup/nginx-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK" && cp -a /etc/nginx "$BK/"
if [ ! -f /etc/nginx/sites-available/engteacher ]; then   # da co (certbot da them 443) thi giu nguyen
  install -m 644 "$HERE/nginx-engteacher.conf" /etc/nginx/sites-available/engteacher
fi
ln -sf /etc/nginx/sites-available/engteacher /etc/nginx/sites-enabled/engteacher
nginx -t
systemctl reload nginx

# 2) User duong ham: khong shell, khoa mat khau, chi duoc mo 127.0.0.1:18000 va :18003 (GatewayPorts no -> chi loopback)
id engtunnel >/dev/null 2>&1 || useradd --system --create-home --shell /usr/sbin/nologin engtunnel
passwd -l engtunnel >/dev/null
install -d -m 700 -o engtunnel -g engtunnel /home/engtunnel/.ssh
printf 'restrict,port-forwarding,permitlisten="127.0.0.1:18000",permitlisten="127.0.0.1:18003",command="/bin/false" %s\n' \
  "$TUNNEL_PUBKEY" > /home/engtunnel/.ssh/authorized_keys
chown engtunnel:engtunnel /home/engtunnel/.ssh/authorized_keys && chmod 600 /home/engtunnel/.ssh/authorized_keys

# 3) Chung chi HTTPS chi cho host nay (certbot da co tai khoan tu mamnoncaynho.com)
if ! certbot certificates 2>/dev/null | grep -q "Domains: $HOST"; then
  certbot --nginx -d "$HOST" --non-interactive --redirect
fi
nginx -t && systemctl reload nginx
echo "Xong. Kiem: curl -s -o /dev/null -w '%{http_code}' https://$HOST/  (404 = nginx + chung chi OK)"
