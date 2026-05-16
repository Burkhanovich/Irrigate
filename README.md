# IrriGate — Aqlli Sug'orish Platformasi

Django MVT arxitekturasida qurilgan dala ekinlarini masofadan sug'orish va kuzatish tizimi.

## Texnik Stack

- **Backend:** Python 3.11, Django 4.2 LTS, Django Channels 4.0, Celery 5.3
- **Ma'lumotlar bazasi:** PostgreSQL 15 (TimescaleDB) / SQLite (dev)
- **Real vaqt:** Redis + Django Channels (WebSocket)
- **IoT:** MQTT (paho-mqtt + Eclipse Mosquitto)
- **Frontend:** Bootstrap 5.3, Chart.js 4, Leaflet.js 1.9
- **Deploy:** Docker Compose, Nginx, Gunicorn

## Tezkor ishga tushirish (Docker)

```bash
# 1. Repozitoriyani klonlash
git clone <repo-url>
cd irrigate

# 2. .env fayl yaratish
cp .env.example .env
# .env faylini tahrirlang (SECRET_KEY ni o'zgartiring)

# 3. Docker Compose bilan ishga tushirish
docker compose up -d

# 4. Migratsiyalar va demo ma'lumotlar
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_demo_data

# 5. Brauzerda ochish
# http://localhost
```

## Lokal ishga tushirish (SQLite + InMemory Channel)

```bash
# Virtual muhit yaratish
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Paketlarni o'rnatish
pip install -r requirements.txt

# Migratsiyalar
python manage.py migrate --settings=config.settings.development

# Demo ma'lumotlar yaratish
python manage.py create_demo_data --settings=config.settings.development

# Serverni ishga tushirish
python manage.py runserver --settings=config.settings.development
```

Brauzerda: `http://127.0.0.1:8000`

## Kirish ma'lumotlari (demo)

| Rol | Login | Parol |
|-----|-------|-------|
| Admin | admin | Admin1234! |
| Fermer | farmer | Farmer1234! |

## Loyiha tuzilmasi

```
irrigate/
├── apps/
│   ├── users/        — Foydalanuvchilar va autentifikatsiya
│   ├── farms/        — Ferma va dala boshqaruvi
│   ├── sensors/      — IoT sensorlar va o'lchovlar
│   ├── irrigation/   — Sug'orish jadvallari va boshqaruv
│   ├── monitoring/   — Dashboard va real vaqt kuzatuv
│   └── alerts/       — Ogohlantirishlar tizimi
├── config/           — Django sozlamalari, URL, ASGI, Celery
├── mqtt_listener/    — MQTT broker listener
├── templates/        — HTML shablonlar
├── docker-compose.yml
├── Dockerfile
└── nginx/nginx.conf
```

## Asosiy imkoniyatlar

- **Dashboard** — barcha fermalar, sensorlar va sug'orish holati bir sahifada
- **Real vaqt** — WebSocket orqali sensor ma'lumotlari 5 soniyada yangilanadi
- **Xarita** — Leaflet.js da barcha ferma markerlar va dala holati
- **Sug'orish jadvali** — vaqt, sensor yoki ob-havo bo'yicha avtomatik trigger
- **Qo'lda boshqarish** — ventillarni masofadan yoqish/o'chirish
- **Grafiklar** — tuproq namligi, harorat, suv sarfi (Chart.js)
- **Ogohlantirishlar** — past namlik, offline sensor, sug'orish xatosi
- **Hisobotlar** — sug'orish tarixi va suv sarfi statistikasi

## Docker xizmatlar

| Xizmat | Tavsif | Port |
|--------|--------|------|
| `web` | Django ASGI + Gunicorn | 8000 |
| `celery` | Asinxron vazifalar | — |
| `celery_beat` | Jadval bo'yicha vazifalar | — |
| `mqtt_listener` | IoT xabarlarni qabul qilish | — |
| `db` | PostgreSQL (TimescaleDB) | 5432 |
| `redis` | Celery broker + Channels | 6379 |
| `mqtt` | Mosquitto broker | 1883 |
| `nginx` | Reverse proxy | 80 |

## Celery vazifalar

```bash
# Celery worker
celery -A config worker -l info

# Celery beat (jadval)
celery -A config beat -l info

# MQTT tinglash
python manage.py mqtt_listen
```

## Muhit o'zgaruvchilari (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/irrigate_db
REDIS_URL=redis://localhost:6379/0
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```
