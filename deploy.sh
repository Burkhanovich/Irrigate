#!/bin/bash
# ══════════════════════════════════════════════
# IrriGate — VPS Deploy Skripti
# Ubuntu 22.04 / Debian 12 uchun
# Ishlatish: bash deploy.sh
# ══════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo -e "${GREEN}"
echo "  ___         _  ____       _       "
echo " |_ _|_ _ _ _(_)/ ___| __ _| |_ ___ "
echo "  | || '_| '_| | |  _ / _\` | __/ _ \\"
echo "  | || | | | | | |_| | (_| | ||  __/"
echo " |___|_| |_| |_|\____|\__,_|\__\___|"
echo -e "${NC}"
echo "  Aqlli Sug'orish Platformasi — Deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Docker tekshirish ──────────────────────
info "Docker tekshirilmoqda..."
if ! command -v docker &> /dev/null; then
    warn "Docker topilmadi. O'rnatilmoqda..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    success "Docker o'rnatildi"
else
    success "Docker mavjud: $(docker --version)"
fi

if ! docker compose version &> /dev/null 2>&1; then
    warn "Docker Compose plugin o'rnatilmoqda..."
    apt-get install -y docker-compose-plugin 2>/dev/null || \
    pip install docker-compose 2>/dev/null || \
    error "Docker Compose o'rnatib bo'lmadi. Qo'lda o'rnating."
fi
success "Docker Compose: $(docker compose version)"

# ── 2. Repo klonlash / yangilash ─────────────
REPO_URL="https://github.com/Burkhanovich/Irrigate.git"
APP_DIR="/opt/irrigate"

if [ -d "$APP_DIR/.git" ]; then
    info "Loyiha yangilanmoqda..."
    cd "$APP_DIR"
    git pull origin main
    success "Yangilandi"
else
    info "Loyiha yuklanmoqda..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
    success "Yuklandi: $APP_DIR"
fi

# ── 3. .env fayl ─────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
    warn ".env fayl topilmadi. .env.example dan nusxa olinmoqda..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"

    # SECRET_KEY avtomatik generatsiya
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s/CHANGE-THIS-TO-A-RANDOM-50-CHAR-STRING/$SECRET/" "$APP_DIR/.env"

    # Server IP ni aniqlash
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
    sed -i "s/your-server-ip,your-domain.com/$SERVER_IP/" "$APP_DIR/.env"

    success ".env fayl yaratildi (SERVER IP: $SERVER_IP)"
    warn "Agar domen bo'lsa: $APP_DIR/.env faylida ALLOWED_HOSTS ni yangilang"
else
    success ".env fayl mavjud"
fi

# ── 4. Firewall ───────────────────────────────
if command -v ufw &> /dev/null; then
    info "Firewall sozlanmoqda..."
    ufw allow 22/tcp  2>/dev/null || true
    ufw allow 80/tcp  2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    success "Portlar ochiq: 22 (SSH), 80 (HTTP), 443 (HTTPS)"
fi

# ── 5. Docker Compose ishga tushirish ────────
info "Servislar ishga tushirilmoqda..."
cd "$APP_DIR"

docker compose down --remove-orphans 2>/dev/null || true
docker compose pull  2>/dev/null || true
docker compose up -d --build

success "Barcha servislar ishga tushdi"

# ── 6. Holat tekshirish ───────────────────────
info "Servislar holati:"
docker compose ps

# ── 7. Demo data kuting ───────────────────────
info "Baza tayyorlanishi kutilmoqda (30 sekund)..."
sleep 30

# Web container log
echo ""
info "Web server loglari (oxirgi 20 qator):"
docker compose logs web --tail=20

# ── 8. Natija ────────────────────────────────
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "DEPLOY MUVAFFAQIYATLI YAKUNLANDI!"
echo ""
echo -e "  Sayt:    ${GREEN}http://${SERVER_IP}${NC}"
echo ""
echo -e "  Login:   ${YELLOW}admin${NC}     / ${YELLOW}Admin1234!${NC}"
echo -e "  Login:   ${YELLOW}farmer${NC}    / ${YELLOW}Farmer1234!${NC}"
echo ""
echo "  Foydali buyruqlar:"
echo "    docker compose logs -f web       # loglar"
echo "    docker compose restart web       # restart"
echo "    docker compose down              # to'xtatish"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
