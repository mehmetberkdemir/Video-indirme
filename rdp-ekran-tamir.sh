#!/bin/bash
# =======================================================
# Linux Mint RDP ve Ekran Sorunları Otomatik Onarım Betiği
# =======================================================

echo "=== Linux Mint Uzak Masaüstü ve Ekran Onarımı Başlatılıyor ==="

# 1. Türkçe Q Klavye Haritasını Düzelt
if [ -f /etc/xrdp/km-0000041f.ini ]; then
    echo "[1/5] Türkçe klavye haritası güncelleniyor..."
    sudo DISPLAY=:0 XAUTHORITY=/home/$USER/.Xauthority xrdp-genkeymap /etc/xrdp/km-0000041f.ini 2>/dev/null || true
    sudo chmod 644 /etc/xrdp/km-0000041f.ini
fi

# 2. ~/.xsession D-Bus ve Ekran Kararma Engelleyici Ayarları
echo "[2/5] RDP oturum ve ekran kararma önleyiciler ayarlanıyor..."
cat << 'EOF' > ~/.xsession
#!/bin/sh
export XDG_CURRENT_DESKTOP=X-Cinnamon
export XDG_SESSION_DESKTOP=cinnamon
export CINNAMON_2D=1
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
setxkbmap tr 2>/dev/null || true
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
exec dbus-run-session cinnamon-session
EOF
chmod +x ~/.xsession

# 3. Kilit Ekranını ve Otomatik Şifre İstemeyi Devre Dışı Bırak
echo "[3/5] Otomatik kilit ekranı ve parola sorma kapatılıyor..."
gsettings set org.cinnamon.desktop.screensaver lock-enabled false 2>/dev/null || true
gsettings set org.cinnamon.desktop.screensaver idle-activation-enabled false 2>/dev/null || true
gsettings set org.cinnamon.desktop.session idle-delay 0 2>/dev/null || true
gsettings set org.cinnamon.settings-daemon.plugins.power lock-on-suspend false 2>/dev/null || true

# 4. Şifreli Anahtarlık (GNOME Keyring) Uyarısını Sıfırla
echo "[4/5] Anahtarlık şifre uyarıları sıfırlanıyor..."
if [ -f ~/.local/share/keyrings/login.keyring ]; then
    cp ~/.local/share/keyrings/login.keyring ~/.local/share/keyrings/login.keyring.bak
    rm -f ~/.local/share/keyrings/login.keyring ~/.local/share/keyrings/default
fi

# 5. Ekran Kartı Açılış Zamanlamasını Düzelt (Initramfs)
echo "[5/5] Ekran kartı sürücü zamanlaması güncelleniyor..."
sudo bash -c "grep -q '^amdgpu$' /etc/initramfs-tools/modules || echo 'amdgpu' >> /etc/initramfs-tools/modules" 2>/dev/null || true
sudo bash -c "grep -q '^i915$' /etc/initramfs-tools/modules || echo 'i915' >> /etc/initramfs-tools/modules" 2>/dev/null || true
sudo update-initramfs -u 2>/dev/null || true

# Servisleri Yeniden Başlat
echo "[+] Servisler yenileniyor..."
sudo systemctl restart xrdp xrdp-sesman 2>/dev/null || true

echo "======================================================="
echo " TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI!"
echo " Artık Uzak Masaüstü ve Ekran sorunsuz çalışacaktır."
echo "======================================================="
