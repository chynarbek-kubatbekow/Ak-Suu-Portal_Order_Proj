# Деплой Ak-Suu Portal

Один код сайта, две среды запуска. Базы и фотографии между ними автоматически не копируются.

| Вариант | База | Фотографии | Когда выбирать |
| --- | --- | --- | --- |
| Render / другой Python-хостинг | SQLite на постоянном диске | Тот же диск | Небольшой сайт без отдельной БД |
| Render / другой Python-хостинг | Neon PostgreSQL через `DATABASE_URL` | Постоянный диск | Рекомендуемый вариант для Django и админки |
| Cloudflare Python Workers | D1, binding `DB` | В D1, до 1 МиБ на фотографию | Без подключения R2 |

В этой реализации Neon поддерживается на обычном Python-хостинге. Добавление `DATABASE_URL` в Worker **не переключает его на Neon**: драйвер PostgreSQL для обычного Python нельзя просто перенести в среду Workers. Worker использует D1, и при конфликте настроек выдаёт понятную ошибку.

У `django-cf` нет полноценных транзакций/отката, есть ограничения ORM и админки. Разработчики адаптера рекомендуют Workers Paid для production: Django и проверка паролей могут превышать CPU-лимит бесплатного тарифа. Для проекта с редактированием новостей Render + Neon проще поддерживать. [Ограничения адаптера](https://github.com/cloudflare/workers-py/tree/main/packages/django-cf#limitations).

Проверенная сборка занимает около **26,6 МиБ без сжатия / 6,1 МиБ в gzip**. С 4 сентября 2026 года Cloudflare отменил прежние gzip-лимиты 3/10 МБ; действует лимит 64 МиБ без сжатия. Пакет укладывается в него. Рекомендация платного Workers относится к CPU/запросам Django, а не к размеру этой сборки. [Обновление лимитов](https://developers.cloudflare.com/changelog/post/2026-09-04-increased-worker-size-limit/).

## Общие переменные

В панели хостинга вводить каждую переменную отдельно, без кавычек вокруг значения.

| Переменная | Production |
| --- | --- |
| `SECRET_KEY` | Случайная длинная строка; секрет, постоянный между деплоями |
| `DEBUG` | `0` |
| `ALLOWED_HOSTS` | Точные домены через запятую, без `https://` и путей |
| `CSRF_TRUSTED_ORIGINS` | Например `https://portal.example.com`; при нескольких доменах — через запятую |

Сгенерировать секрет локально: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Для `SECRET_KEY` и временного `DEPLOY_TOKEN` генерировать **разные** значения. Не помещать их в GitHub, команды с аргументами или переписку.

Настройки читаются из окружения процесса на Render и из bindings на Workers. `.env.example` — образец для обычного хостинга; `.dev.vars.example` — только для локального Wrangler. Файл `.env` автоматически не загружается. Для локального запуска с ним можно использовать `uv run --env-file .env python manage.py runserver` в подготовленном Python-окружении.

## Render: пока без Neon

В репозитории есть `render.yaml` с SQLite и диском `/var/data`. Этот Blueprint **выбирает платный план `starter` и диск 1 ГБ**; он ничего не создаёт до применения в Render. На бесплатном сервисе постоянного диска нет, и SQLite/загрузки теряются при пересоздании сервиса. [Документация дисков Render](https://render.com/docs/disks).

Настройки существующего Web Service:

```text
Build Command: bash build.sh
Start Command: bash start.sh
```

Environment:

```dotenv
PYTHON_VERSION=3.13.5
DEBUG=0
SECRET_KEY=<свой случайный секрет>
SQLITE_PATH=/var/data/db.sqlite3
MEDIA_ROOT=/var/data/media
SERVE_LOCAL_MEDIA=1
WEB_CONCURRENCY=2
```

Добавить постоянный диск с Mount Path `/var/data`. `ALLOWED_HOSTS` для адреса Render подхватывается из `RENDER_EXTERNAL_HOSTNAME`; собственный домен добавить явно. Для собственного домена также указать `CSRF_TRUSTED_ORIGINS`.

`build.sh` устанавливает зависимости и собирает статику без доступа к БД. `start.sh` создаёт каталоги на диске, применяет миграции (они создадут файл SQLite и таблицы) и запускает Gunicorn. Если миграции не прошли, сервер не стартует. При нескольких экземплярах PostgreSQL миграции лучше выполнять один раз отдельным pre-deploy заданием.

Администратор создаётся в Shell Render:

```bash
python manage.py createsuperuser
```

На Render фотографии новостей размером до 5 МиБ доступны по `/media/news/...` и хранятся на диске. На другом хостинге можно отдать `/media/` через nginx, указав `SERVE_LOCAL_MEDIA=0`.

## Neon позже: подключение через env

1. В Neon создать проект и базу, выбрать регион рядом с Render.
2. В **Connect** скопировать PostgreSQL connection string (без оболочки `psql '...'`).
3. В Render добавить секрет `DATABASE_URL`:

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DB?sslmode=require
DB_CONN_MAX_AGE=0
```

Сохранить TLS-параметры из строки Neon, в том числе `channel_binding=require`, если он присутствует. Можно использовать pooled URL; server-side cursors отключены для совместимости с транзакционным пулером. Для миграций предпочтителен direct URL, если Neon рекомендует его для выбранной операции. [Инструкция Neon для Django](https://neon.com/docs/guides/django).

4. Не задавать `DB_BACKEND=sqlite`: при наличии URL PostgreSQL выбирается автоматически. `SQLITE_PATH` больше не используется.
5. Повторный деплой применит миграции в новой базе. **Это создаёт схему, но не переносит ваши старые новости, пользователей и пароли.** Перед переключением сохранить резервную копию и отдельно перенести данные. Диск или объектное хранилище по-прежнему нужны для фотографий.

Для отказа от платного диска на Render потребуется отдельно настроить внешнее хранилище фотографий; одного Neon для этого недостаточно.

## Cloudflare: только D1, без R2

### 1. Создать базу

В Cloudflare открыть **Storage & Databases → D1 SQL Database → Create Database**. Название: `aksuu-portal-db`. Скопировать Database ID.

В `cloudflare/wrangler.jsonc` заменить `REPLACE_WITH_D1_DATABASE_ID` этим ID. Сохранить binding `DB`. ID не является паролем и может быть в репозитории. Для D1 не нужны `DATABASE_URL`, `SQLITE_PATH`, логин или пароль. [Создание и привязка D1](https://developers.cloudflare.com/d1/get-started/).

Альтернатива через CLI из папки `cloudflare` после `npm ci`:

```bash
npx wrangler login
npx wrangler d1 create aksuu-portal-db
```

Не создавать второй binding, если CLI предлагает изменить конфигурацию: в проекте уже есть `DB`, нужно подставить его ID.

### 2. Фотографии без отдельного хранилища

R2 не нужен: фотографии из админки сохраняются в таблице `myapp_uploadedimage` той же D1. Дополнительный bucket, binding `MEDIA` и подключение биллинга R2 не требуются. Фотографии выдаются по `/media/news/...`, а изображения из репозитория — через Workers Static Assets.

Лимит одной загружаемой фотографии — **1 МиБ (1 048 576 байт)**. Большую фотографию нужно уменьшить перед загрузкой; поддерживаются JPG, PNG, WebP и GIF. Файлы хранятся в base64: это примерно на треть увеличивает их размер, но позволяет использовать стандартный Django ORM с D1. Строка остаётся меньше лимита D1 в 2 000 000 байт. Это вариант для небольшого количества новостей, не для больших фотогалерей. [Лимиты D1](https://developers.cloudflare.com/d1/platform/limits/).

У D1 есть бесплатные квоты. Удаление R2 не отменяет отдельные лимиты CPU и запросов Workers; работу Django в бесплатном тарифе нужно проверять на реальном аккаунте. [Квоты D1](https://developers.cloudflare.com/d1/platform/pricing/).

Миграция `0005_uploadedimage` создаёт таблицу изображений. Если прежний вариант с R2 уже использовался, его файлы автоматически в D1 не переносятся — сохраните их и загрузите заново через админку. Удаление/замена новости автоматически не удаляет прежний файл (как и в обычном Django FileField); старые изображения нужно учитывать при контроле размера базы.

### 3. Настроить сборку из GitHub

В **Workers & Pages → aksuu-portal → Settings → Build**:

```text
Root directory: /
Build command: bash cloudflare/build.sh
Deploy command: bash cloudflare/deploy.sh
```

В **Build Variables and Secrets**:

```dotenv
PYTHON_VERSION=3.13.5
SKIP_DEPENDENCY_INSTALL=1
```

Скрипт сам устанавливает uv, получает управляемую сборку Python с SQLite, устанавливает Python/Node-зависимости и собирает статику. Профиль сборки Django использует dummy database: удалённая D1 и секреты приложения при сборке не нужны. Удалить прежнюю Deploy command с Gunicorn.

### 4. Настроить runtime Environment

В **Settings → Variables and Secrets** (это отдельный раздел, не Build):

| Имя | Тип | Значение |
| --- | --- | --- |
| `SECRET_KEY` | Secret | Свой случайный секрет |
| `DEBUG` | Text | `0` |
| `ALLOWED_HOSTS` | Text | `aksuu-portal.ВАШ-ПОДДОМЕН.workers.dev` и собственный домен, если есть |
| `CSRF_TRUSTED_ORIGINS` | Text | `https://aksuu-portal.ВАШ-ПОДДОМЕН.workers.dev` и собственный origin |
| `DEPLOY_TOKEN` | Secret | Отдельный случайный токен, минимум 32 символа; временно для обслуживания |

Указанный домен заменить фактическим адресом Worker. `DB_BACKEND` можно не задавать: в Workers используется D1. Не добавлять `DATABASE_URL`. После добавления bindings/секретов применить изменения и выполнить деплой. Binding D1 `DB` берётся из `cloudflare/wrangler.jsonc`, а не из текстовых env. Привязки R2 `MEDIA` в новой конфигурации нет.

### 5. Применить миграции и создать администратора

После первого успешного деплоя выполнить **на своём компьютере из корня репозитория**:

```bash
python scripts/cloudflare_manage.py https://ВАШ-WORKER.workers.dev migrate
python scripts/cloudflare_manage.py https://ВАШ-WORKER.workers.dev create-admin
```

Программа спросит `DEPLOY_TOKEN`, а для администратора — имя, email и новый пароль (ввод секрета/пароля скрыт). Миграции создадут таблицы и начальные новости. Создание администратора не перезаписывает существующий аккаунт. После этого проверить главную, `/news/`, `/admin/`, редактирование новости и загрузку фото.

**Удалить `DEPLOY_TOKEN` из runtime secrets и применить изменения**, когда настройка закончена. Без него служебные адреса возвращают 404. Для будущих изменений схемы временно добавить новый токен и повторить `migrate`; повторно создавать администратора не требуется. Не запускать два процесса миграции одновременно. Перед изменениями схемы существующей D1 сделать резервную копию: адаптер не обеспечивает откат транзакций.

Миграции запускаются отдельной операцией после публикации Worker, а не при каждом запросе. `wrangler d1 migrations apply` здесь не используется: историю миграций ведёт Django.

## Локальная проверка Cloudflare

Нужны Python 3.13, Node.js и uv 0.12.3 или новее. Из корня:

```bash
uv run --project cloudflare python scripts/build_cloudflare.py
cd cloudflare
npm ci
# Скопировать .dev.vars.example в .dev.vars.
uv run pywrangler dev
```

Wrangler использует локальную D1, в том числе для фотографий. Во втором терминале из корня:

```bash
python scripts/cloudflare_manage.py http://localhost:8787 migrate
python scripts/cloudflare_manage.py http://localhost:8787 create-admin
```

Не использовать `--remote` для этой проверки: локальная проверка не должна менять production-базу. Рабочие файлы и кэши исключены из Git. В Worker попадают только код приложения и шаблоны; `.env`, локальная SQLite и пользовательские загрузки туда не копируются.

Проверка полного сценария: задать локальный `DEPLOY_TOKEN` и выполнить `python scripts/smoke_cloudflare.py` из Python-окружения с Pillow. Скрипт допускает только localhost, создаёт тестового администратора и новость в локальной D1, проверяет вход, статику и загрузку/чтение PNG из базы. Тестовые записи остаются только в локальной базе Wrangler.

На Windows инструменты Pyodide/uv могут некорректно обрабатывать пути с пробелами и апострофами. При такой ошибке использовать рабочую копию в простом пути, например `C:\work\aksuu`, и каталоги `UV_CACHE_DIR`/`UV_PYTHON_INSTALL_DIR` без пробелов. Это ограничение локальных инструментов; Cloudflare Builds работает на Linux.

## Другой Python-хостинг

Python 3.13, `pip install -r requirements.txt`, сборка `bash build.sh`, запуск `bash start.sh`. Хостинг должен задавать `PORT` (по умолчанию 8000). Для production указать `DEBUG=0`, `SECRET_KEY`, домены и PostgreSQL URL либо постоянный путь SQLite. За доверенным HTTPS reverse proxy отдельно настроить `SECURE_PROXY_SSL_HEADER`; в Render настройка уже включается автоматически.

## Что проверено при подготовке

- 20 тестов Django: страницы, конфигурация баз, отсутствие SQLite при сборке, защита обслуживания, хранение изображений в базе и ограничения размера.
- Сборка статики для обоих хостингов; создание каталогов и применение миграций к новой временной SQLite.
- Локальный Worker с `DEBUG=0`: миграции D1, создание администратора, вход, сохранение новости, запись/чтение фото из D1 без R2, статика.
- `wrangler deploy --dry-run`: пакет формируется успешно, без публикации.
- Конфигурация PostgreSQL и загрузка драйвера проверены без подключения к реальной Neon.

Реальный production-деплой, настройки аккаунтов и подключение Neon ещё не выполнялись. Перед запуском необходимо создать D1, указать Database ID и runtime secrets, затем отправить изменения в GitHub.
