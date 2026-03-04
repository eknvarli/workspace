Yet another project management system.

<img src="./screenshots/ss.png">

## PostgreSQL Kurulumu

Bu proje PostgreSQL kullanacak sekilde ayarlanmistir.

1. Bagimliliklari kurun:

```bash
pip install -r requirements.txt
```

2. `.env.example` dosyasini kopyalayip `.env` olusturun ve PostgreSQL bilgilerini duzenleyin:

```env
SECRET_KEY=your-secret-key
POSTGRES_DB=workspace_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

3. Veritabanini olusturun (ornek):

```sql
CREATE DATABASE workspace_db;
```

4. Migrationlari uygulayin:

```bash
python manage.py migrate
```

5. Uygulamayi baslatin:

```bash
python manage.py runserver
```