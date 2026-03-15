# Workspace Collaboration Platform

Modern ekip iş birliği ve proje yönetimi platformu. Django tabanlı backend, REST API, JWT kimlik doğrulama, Django Channels ile gerçek zamanlı güncellemeler, Celery hazır görev altyapısı ve modern üretkenlik odaklı bir dashboard içerir.

## Öne Çıkanlar

- Multi-workspace organizasyon mimarisi
- Rol tabanlı üyelik modeli: Admin, Manager, Member, Guest
- Projeler, görevler, alt görevler, yorumlar, ek dosyalar, etiketler
- Bildirim ve aktivite akışı
- JWT tabanlı API giriş noktaları
- Gerçek zamanlı WebSocket olayları
- PostgreSQL, Redis, Celery ve Docker desteği
- Modern açık tema dashboard arayüzü

## Teknoloji Yığını

- Python 3.12 hedefi
- Django
- Django REST Framework
- Simple JWT
- Django Channels
- Celery
- PostgreSQL destekli, SQLite fallback geliştirme modu
- Redis destekli, memory fallback geliştirme modu
- Django Templates + TailwindCSS

## Modüler Yapı

- accounts: profil, e-posta doğrulama, şifre sıfırlama tokenları
- organizations: workspace, üyelik, davet modeli, dashboard view
- teams: takım ve takım üyeliği
- projects: proje ve proje üyelikleri
- tasks: görev, alt görev, etiket
- comments: threaded yorum yapısı ve mention desteği
- notifications: uygulama içi bildirimler ve WebSocket consumer
- activity_logs: aksiyon geçmişi
- attachments: görev ve yorum dosya ekleri
- api: REST endpoint katmanı

## Proje Yapısı

```text
accounts/
organizations/
projects/
tasks/
comments/
notifications/
activity_logs/
teams/
attachments/
api/
templates/collab/
workspace/
```

## Çalıştırma

### Lokal geliştirme

1. Bağımlılıkları kurun.

```bash
pip install -r requirements.txt
```

2. Ortam dosyasını hazırlayın.

```bash
copy .env.example .env
```

3. Migrationları uygulayın.

```bash
python manage.py migrate
```

4. Geliştirme sunucusunu başlatın.

```bash
python manage.py runserver
```

5. İsterseniz Celery worker çalıştırın.

```bash
celery -A workspace worker -l info
```

### Docker ile

```bash
docker compose up --build
```

Bu yapı şu servisleri kaldırır:

- web: Daphne üzerinden ASGI uygulaması
- worker: Celery worker
- db: PostgreSQL 16
- redis: Redis 7

## Ortam Değişkenleri

Örnek dosya: [.env.example](.env.example)

Ana değişkenler:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- CSRF_TRUSTED_ORIGINS
- USE_POSTGRES
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT
- USE_REDIS
- REDIS_URL
- DEFAULT_FROM_EMAIL

## Arayüz

Yeni dashboard ana sayfada sunulur:

- Sol sidebar: workspace seçici, navigasyon, logout
- Üst navbar: global arama, hızlı görev oluşturma, bildirimler, avatar
- Görev görünümü: List, Board, Table, Calendar
- Task detail drawer: açıklama, durum, öncelik, atanan kişi, alt görevler, ekler, yorumlar, aktivite


## API

Swagger UI: /api/docs

Şema: /api/schema

Temel endpointler:

- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/password-reset/request
- POST /api/auth/password-reset/confirm
- POST /api/auth/email-verification/request
- POST /api/auth/email-verification/confirm
- GET /api/organizations
- GET /api/projects
- POST /api/projects
- GET /api/projects/{id}
- PUT/PATCH /api/projects/{id}
- GET /api/tasks
- POST /api/tasks
- GET /api/tasks/{id}
- PATCH /api/tasks/{id}
- POST /api/tasks/{id}/comments
- GET /api/notifications
- GET /api/search?q=...

## Roller ve Yetkiler

- Admin: tam erişim
- Manager: proje ve görev yönetimi
- Member: görev oluşturma ve düzenleme
- Guest: salt okunur erişim

API tarafında yazma işlemleri workspace rolüne göre sınırlandırılır. Okuma işlemlerinde guest rolü desteklenir.

## Veri Modeli Özeti

- User: Django auth user
- AccountProfile: avatar, status, locale, email verification state
- Organization
- WorkspaceMember
- OrganizationInvitation
- Team
- TeamMembership
- Project
- ProjectMembership
- Task
- SubTask
- Tag
- Comment
- Attachment
- Notification
- ActivityLog

## Gerçek Zamanlı Özellikler

WebSocket endpoint:

- /ws/organization/{organization_uuid}/

Yayınlanan olay tipleri:

- task.changed
- comment.created
- notification.created
- connection.ready
- presence.pong

## Performans Notları

- Görev ve proje sorgularında select_related / prefetch_related kullanılır
- Task ve Notification modellerinde indexler tanımlıdır
- DRF pagination varsayılan olarak aktiftir
- Redis açıksa cache, channel layer ve Celery broker olarak kullanılır

## Notlar

- Varsayılan geliştirme modu SQLite + in-memory cache ile çalışır.
- Production için PostgreSQL ve Redis açılması önerilir.
- Legacy core uygulaması runtime'dan tamamen çıkarıldı; sistem yalnızca yeni modüler yapı üzerinden çalışır.