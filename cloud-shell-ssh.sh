#!/usr/bin/env bash
# Rootless OpenSSH server for Azure Cloud Shell, listening on 127.0.0.1:4444.
# Uses Microsoft's own openssh-server package, unpacked into $HOME.
# Usage: bash setup.sh "<YOUR_PUBLIC_SSH_KEY>"
set -euo pipefail

PUBKEY="${1:?usage: $0 'ssh-ed25519 AAAA... user@host'}"
PORT=4444
O="$HOME/.openssh"
REPO="https://packages.microsoft.com/azurelinux/3.0/prod/base/x86_64/Packages/o"

# Fetch and unpack the latest openssh-server RPM.
mkdir -p "$O"
if [ -z "$(find "$O" -type f -name sshd)" ]; then
    RPM="$(curl -fsSL "$REPO/" | grep -o 'openssh-server-[0-9][^"]*x86_64\.rpm' | sort -V | tail -1)"
    echo "[*] Fetching $RPM"
    curl -fsSL -o "$O/$RPM" "$REPO/$RPM"
    (cd "$O" && rpm2cpio "$RPM" | cpio -idm --quiet)
fi
SSHD="$(find "$O" -type f -name sshd | head -1)"
SESSION="$(find "$O" -type f -name sshd-session | head -1)"
SFTP="$(find "$O" -type f -name sftp-server | head -1)"

# Setup host key and user's SSH authorized key.
[ -f "$O/hostkey" ] || ssh-keygen -q -t ed25519 -N '' -f "$O/hostkey"
mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
grep -qxF "$PUBKEY" "$HOME/.ssh/authorized_keys" 2>/dev/null || echo "$PUBKEY" >> "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"

cat > "$O/sshd_config" <<EOF
Port $PORT
ListenAddress 127.0.0.1
HostKey $O/hostkey
PidFile $O/sshd.pid
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM no
Subsystem sftp $SFTP
${SESSION:+SshdSessionPath $SESSION}
EOF

# SSH sessions start with a clean environment, so they lose the Cloud Shell token
# endpoint. Copy it at login from another Cloud Shell process.
cat > "$O/auth.sh" <<'EOF'
# Import the Cloud Shell token endpoint into SSH sessions.
if [ -z "${MSI_ENDPOINT:-}" ]; then
  for _e in /proc/[0-9]*/environ; do
    if tr '\0' '\n' < "$_e" 2>/dev/null | grep -q '^MSI_ENDPOINT='; then
      while IFS= read -r -d '' _l; do
        case "$_l" in MSI_*|ACC_*|AZURE*) export "$_l" ;; esac
      done < "$_e"
      break
    fi
  done
  unset _e _l
fi
EOF
grep -qF '.openssh/auth.sh' "$HOME/.bashrc" 2>/dev/null || \
    echo '[ -f ~/.openssh/auth.sh ] && . ~/.openssh/auth.sh' >> "$HOME/.bashrc"

# (Re)start. Only the listener is named sshd; existing sessions (sshd-session) survive.
pkill -u "$USER" -x sshd && sleep 1 || true
"$SSHD" -f "$O/sshd_config"
echo "[+] sshd listening on 127.0.0.1:$PORT (stop: pkill -x sshd)"
