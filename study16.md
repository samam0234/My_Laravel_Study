# study16 · 운영·CI/CD

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

Docker 이미지·DB·워커를 연결하고 자동 검사·배포·백업 절차를 만든다.

## ② 📖 이론

Docker 이미지는 실행에 필요한 파일·확장을 고정하는 상자이고 볼륨은 상자를 교체해도 남는 데이터 보관함이다. assets 단계는 Vue를 빌드하고 app 단계는 PHP-FPM과 런타임 의존성을 설치한다. web 단계는 같은 public 산출물을 Nginx에 넣는다. 최종 서재는 app/web/worker/scheduler와 PostgreSQL로 운영하고 Reverb는 realtime profile로 추가한다.

CI는 main push/PR에서 두 앱의 빌드·테스트·감사와 문서 정합성을 검사한다. DB 작업은 PostgreSQL·MariaDB에서도 같은 테스트를 실행한다. Deploy는 CI 성공 또는 수동 실행에서 DEPLOY_ENABLED=true일 때만 정확한 커밋 이미지 두 개를 GHCR에 올리고 서버로 배포한다. 서버 자격증명은 저장소 코드에 넣지 않는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. Docker 엔진이 실행 중인지 docker info로 확인하고 app/web 대상을 각각 빌드한다. 현재 로컬 환경에서는 엔진이 꺼져 있으므로 컨테이너 실행 검증은 미완료다.
2. 서버의 /srv/laravel-study에 저장소와 compose.production.yaml을 준비한다. .env.production은 production.env.example을 복사해 실제 값으로 채우고 서버에서만 보관한다. APP_KEY·DB 암호는 비밀 저장소에서 주입한다.
3. IMAGE에 정확한 이미지 태그를 지정한다. 비공개 GHCR 패키지라면 서버에 읽기 전용 인증을 먼저 설정한다. DB·private-files 볼륨의 백업·소유권을 확인한다.
4. GitHub production 환경에 DEPLOY_SSH_KEY, DEPLOY_KNOWN_HOSTS, DEPLOY_TARGET을 설정한다. 호스트 키는 신뢰 경로로 확인하고 StrictHostKeyChecking을 끄지 않는다. DEPLOY_ENABLED 저장소 변수와 선택적 Reverb 공개 빌드값을 설정한다.
5. 배포는 image pull→migrate --force→서비스 교체→/health 점검 순서다. 새/구 버전이 공존해도 가능한 확장형 스키마 변경을 사용한다. worker는 새 컨테이너로 교체한다.
6. 로그는 stderr로 모으고 5xx 비율·지연·DB 연결·큐 backlog·디스크 사용량·업로드 실패율을 모니터링한다. requestId로 요청과 오류를 연결한다.
7. backup.ps1은 PostgreSQL dump와 비공개 파일 tar를 복사한다. APP_KEY는 별도로 보관한다. 다른 디렉터리/서버에 암호화해 복제하고 보관 기간을 정한다.
8. 복원은 먼저 격리 DB와 빈 파일 볼륨에서 한다. pg_restore 대신 plain SQL에는 psql을 사용한다. 기록 건수·소유권·파일 해시·로그인·요약을 확인한 뒤 전환한다. 운영 DB를 바로 덮어쓰지 않는다.

### 실행 명령

```powershell
docker build -f project/Dockerfile --target app -t study-app project
docker build -f project/Dockerfile --target web -t study-web project
# 운영 서버: IMAGE에 -app/-web 접미사 직전까지의 태그 설정
$env:IMAGE="ghcr.io/OWNER/my_laravel_study:COMMIT_SHA"
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml pull
docker compose -f compose.production.yaml run --rm app php artisan migrate --force
docker compose -f compose.production.yaml up -d
curl.exe -f http://127.0.0.1:8088/health
powershell -File tools/backup.ps1
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `project/Dockerfile` 전체 코드

[project/Dockerfile](project/Dockerfile)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```dockerfile
FROM node:24-alpine AS assets
WORKDIR /src
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY vite.config.js ./
COPY resources ./resources
ARG VITE_REVERB_APP_KEY
ARG VITE_REVERB_HOST
ARG VITE_REVERB_PORT=443
ARG VITE_REVERB_SCHEME=https
RUN npm run build

FROM php:8.4-fpm-alpine AS app
RUN apk add --no-cache icu-dev libzip-dev oniguruma-dev postgresql-dev sqlite-dev \
    && docker-php-ext-install pdo_pgsql pdo_mysql pdo_sqlite intl zip mbstring pcntl opcache
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /var/www/html
COPY composer.* ./
RUN composer install --no-dev --prefer-dist --no-interaction --no-scripts --no-autoloader
COPY . .
COPY --from=assets /src/public/build ./public/build
RUN composer dump-autoload --no-dev --optimize --no-scripts && php artisan package:discover \
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data
EXPOSE 9000
CMD ["php-fpm"]

FROM nginx:1.28-alpine AS web
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=app /var/www/html/public /var/www/html/public
EXPOSE 80
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | Docker 빌드 단계와 기반 이미지를 선택한다. |
| 2 | 다음 명령의 컨테이너 작업 디렉터리를 지정한다. |
| 3 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 4 | 이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다. |
| 5 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 6 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 7 | 브라우저 공개값 등 빌드 인수를 선언한다. 비밀값은 넣지 않는다. |
| 8 | 브라우저 공개값 등 빌드 인수를 선언한다. 비밀값은 넣지 않는다. |
| 9 | 브라우저 공개값 등 빌드 인수를 선언한다. 비밀값은 넣지 않는다. |
| 10 | 브라우저 공개값 등 빌드 인수를 선언한다. 비밀값은 넣지 않는다. |
| 11 | 이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다. |
| 12 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 13 | Docker 빌드 단계와 기반 이미지를 선택한다. |
| 14 | 이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다. |
| 15 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 16 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 17 | 다음 명령의 컨테이너 작업 디렉터리를 지정한다. |
| 18 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 19 | 이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다. |
| 20 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 21 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 22 | 이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 런타임을 권한이 제한된 사용자로 전환한다. |
| 25 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 26 | 컨테이너가 시작할 프로세스와 실행 인수를 정의한다. |
| 27 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 28 | Docker 빌드 단계와 기반 이미지를 선택한다. |
| 29 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 30 | 소스 또는 이전 단계 산출물을 이미지 안으로 복사한다. |
| 31 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |


### `compose.production.yaml` 전체 코드

[compose.production.yaml](compose.production.yaml)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```yaml
name: laravel-study
x-app: &app
  image: ${IMAGE:?Set IMAGE}-app
  env_file: .env.production
  restart: unless-stopped
  volumes: ["private-files:/var/www/html/storage/app"]
  depends_on:
    db:
      condition: service_healthy
services:
  app:
    <<: *app
  worker:
    <<: *app
    command: [php, artisan, queue:work, --sleep=3, --tries=3, --timeout=100]
  scheduler:
    <<: *app
    command: [php, artisan, schedule:work]
  reverb:
    <<: *app
    profiles: [realtime]
    command: [php, artisan, reverb:start, --host=0.0.0.0, --port=8080]
    ports: ["127.0.0.1:8080:8080"]
  web:
    image: ${IMAGE:?Set IMAGE}-web
    restart: unless-stopped
    ports: ["127.0.0.1:8088:80"]
    depends_on: [app]
  db:
    image: postgres:17-alpine
    env_file: .env.production
    restart: unless-stopped
    volumes: ["production-db:/var/lib/postgresql/data"]
    healthcheck:
      test: [CMD-SHELL, "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      retries: 10
volumes:
  private-files:
  production-db:
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 2 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 3 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 4 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 5 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 6 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 7 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 8 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 9 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 10 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 11 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 12 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 13 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 14 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 15 | 컨테이너가 시작할 프로세스와 실행 인수를 정의한다. |
| 16 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 17 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 18 | 컨테이너가 시작할 프로세스와 실행 인수를 정의한다. |
| 19 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 20 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 21 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 22 | 컨테이너가 시작할 프로세스와 실행 인수를 정의한다. |
| 23 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 24 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 25 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 26 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 27 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 28 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 29 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 30 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 31 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 32 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 33 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 34 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 35 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 36 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 37 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 38 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 39 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 40 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |


### `.github/workflows/ci.yml` 전체 코드

[.github/workflows/ci.yml](.github/workflows/ci.yml)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: [demo, project]
    defaults:
      run:
        working-directory: ${{ matrix.app }}
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.4'
          extensions: mbstring, intl, pdo_sqlite, pdo_mysql, pdo_pgsql
          coverage: none
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: npm
          cache-dependency-path: ${{ matrix.app }}/package-lock.json
      - run: composer install --prefer-dist --no-interaction
      - run: cp .env.example .env
      - run: php artisan key:generate
      - run: npm ci --no-audit --no-fund
      - run: npm run build
      - run: php artisan test --compact
      - run: composer audit
      - run: npm audit --omit=dev
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python tools/check_course.py
  database:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: [demo, project]
        driver: [pgsql, mariadb]
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_DB: study
          POSTGRES_USER: study
          POSTGRES_PASSWORD: study-test-password
        ports: ['5432:5432']
        options: --health-cmd "pg_isready -U study -d study" --health-interval 5s --health-retries 10
      mariadb:
        image: mariadb:11.8
        env:
          MARIADB_DATABASE: study
          MARIADB_USER: study
          MARIADB_PASSWORD: study-test-password
          MARIADB_RANDOM_ROOT_PASSWORD: 'yes'
        ports: ['3306:3306']
        options: --health-cmd "healthcheck.sh --connect --innodb_initialized" --health-interval 5s --health-retries 10
    env:
      DB_CONNECTION: ${{ matrix.driver }}
      DB_HOST: 127.0.0.1
      DB_PORT: ${{ matrix.driver == 'pgsql' && '5432' || '3306' }}
      DB_DATABASE: study
      DB_USERNAME: study
      DB_PASSWORD: study-test-password
    defaults:
      run:
        working-directory: ${{ matrix.app }}
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.4'
          extensions: mbstring, intl, pdo_pgsql, pdo_mysql
          coverage: none
      - run: composer install --prefer-dist --no-interaction
      - run: cp .env.example .env
      - run: php artisan key:generate
      - run: php artisan test --compact
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 2 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 3 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 4 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 5 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 6 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 7 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 8 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 9 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 10 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 11 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 12 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 13 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 14 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 15 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 16 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 17 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 18 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 19 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 20 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 21 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 22 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 23 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 24 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 25 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 26 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 27 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 28 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 29 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 30 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 31 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 32 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 33 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 34 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 35 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 36 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 37 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 38 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 39 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 40 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 41 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 42 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 43 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 44 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 45 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 46 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 47 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 48 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 49 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 50 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 51 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 52 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 53 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 54 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 55 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 56 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 57 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 58 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 59 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 60 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 61 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 62 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 63 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 64 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 65 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 66 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 67 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 68 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 69 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 70 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 71 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 72 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 73 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 74 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 75 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 76 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 77 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 78 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 79 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 80 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 81 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 82 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 83 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 84 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 85 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 86 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 87 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |


### `.github/workflows/deploy.yml` 전체 코드

[.github/workflows/deploy.yml](.github/workflows/deploy.yml)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```yaml
name: Deploy
on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  packages: write
concurrency:
  group: production
  cancel-in-progress: false
jobs:
  publish:
    if: >-
      vars.DEPLOY_ENABLED == 'true' &&
      ((github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main') ||
      (github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.event == 'push' &&
      github.event.workflow_run.head_repository.full_name == github.repository))
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.image.outputs.image }}
      sha: ${{ steps.image.outputs.sha }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_sha || github.sha }}
      - id: image
        shell: bash
        run: |
          echo "image=ghcr.io/${GITHUB_REPOSITORY,,}:$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
          echo "sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: project
          target: app
          push: true
          tags: ${{ steps.image.outputs.image }}-app
          build-args: |
            VITE_REVERB_APP_KEY=${{ vars.REVERB_PUBLIC_KEY }}
            VITE_REVERB_HOST=${{ vars.REVERB_PUBLIC_HOST }}
      - uses: docker/build-push-action@v6
        with:
          context: project
          target: web
          push: true
          tags: ${{ steps.image.outputs.image }}-web
          build-args: |
            VITE_REVERB_APP_KEY=${{ vars.REVERB_PUBLIC_KEY }}
            VITE_REVERB_HOST=${{ vars.REVERB_PUBLIC_HOST }}
  deploy:
    needs: publish
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy exact image and check health
        env:
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          KNOWN_HOSTS: ${{ secrets.DEPLOY_KNOWN_HOSTS }}
          TARGET: ${{ secrets.DEPLOY_TARGET }}
          IMAGE: ${{ needs.publish.outputs.image }}
          RELEASE_SHA: ${{ needs.publish.outputs.sha }}
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts
          ssh "$TARGET" "cd /srv/laravel-study && git fetch origin main && git checkout --detach '$RELEASE_SHA' && export IMAGE='$IMAGE' && docker compose -f compose.production.yaml pull && docker compose -f compose.production.yaml run --rm app php artisan migrate --force && docker compose -f compose.production.yaml up -d && curl --retry 10 --retry-connrefused --retry-delay 2 --fail http://127.0.0.1:8088/health"
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 2 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 3 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 4 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 5 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 6 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 7 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 8 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 9 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 10 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 11 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 12 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 13 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 14 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 15 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 16 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 17 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 18 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 19 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 20 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 21 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 22 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 23 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 24 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 25 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 26 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 27 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 28 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 29 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 30 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 31 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 32 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 33 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 34 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 35 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 36 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 37 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 38 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 39 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 40 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 41 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 42 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 43 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 44 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 45 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 46 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 47 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 48 | 워크플로에서 재사용할 GitHub Action을 선택한다. |
| 49 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 50 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 51 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 52 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 53 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 54 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 55 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 56 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 57 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 58 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 59 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 60 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 61 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 62 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 63 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 64 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 65 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 66 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 67 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 68 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 69 | CI 또는 배포 단계에서 실행할 명령을 선언한다. |
| 70 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 71 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 72 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 73 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 74 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |


### `tools/backup.ps1` 전체 코드

[tools/backup.ps1](tools/backup.ps1)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```powershell
param([string]$Destination = (Join-Path $PSScriptRoot '../backups'))
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sql = Join-Path $Destination ($stamp + '.sql')
$composeFile = Join-Path $PSScriptRoot '../compose.production.yaml'
docker compose -f $composeFile exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" -f /tmp/study-backup.sql'
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL backup failed' }
docker compose -f $composeFile cp db:/tmp/study-backup.sql $sql
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL backup copy failed' }
docker compose -f $composeFile exec -T app tar czf /tmp/study-files.tar.gz -C /var/www/html/storage/app .
if ($LASTEXITCODE -ne 0) { throw 'Private file backup failed' }
docker compose -f $composeFile cp app:/tmp/study-files.tar.gz (Join-Path $Destination ($stamp + '-files.tar.gz'))
if ($LASTEXITCODE -ne 0) { throw 'Private file backup copy failed' }
Write-Output "DB backup: $sql"
Write-Output 'Also snapshot the private-files volume and store APP_KEY separately in your secret manager.'
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 2 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 3 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 4 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 5 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 6 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 7 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 8 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 9 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 10 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 11 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 12 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 13 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 14 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 15 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 16 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |


## ④ 🔗 연동 포인트

배포된 웹·워커는 같은 환경변수·DB·private-files를 사용한다. HTTPS는 호스트의 Caddy/Nginx에서 8088로 역방향 프록시하고 실시간은 8080에 별도 wss 호스트를 연결한다. 다음 단계의 Reverb도 같은 인증·권한 규칙을 사용한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| Docker daemon 연결 실패 | Desktop/엔진이 꺼짐 | Docker 실행 후 docker info 확인 |
| worker에서 파일 없음 | app과 worker의 private-files 볼륨이 다름 | 동일 named volume 마운트 확인 |
| 자동 배포가 실행 안 됨 | DEPLOY_ENABLED·CI 결과·production 환경 미설정 | Actions 조건과 저장소 변수·비밀값을 확인 |

## ⑥ 직접 해보기

1. compose config로 변수·볼륨·서비스 구성을 검증한다.
2. 격리 DB에 백업을 복원해 사용자·문서·파일 수를 대조한다.
3. 실패한 health 점검에서 이전 이미지로 원복할 명령을 적는다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] Docker app/web 이미지 빌드·헬스를 실제 실행해 기록한다.
- [ ] CI 빌드·SQLite·PostgreSQL·MariaDB 결과를 확인한다.
- [ ] 운영 비밀값과 HTTPS·호스트 키를 설정한다.
- [ ] 로그·큐·디스크 경보 기준을 정한다.
- [ ] DB·파일·APP_KEY 백업과 격리 복원 시험을 수행한다.
- [ ] 데이터를 지우는 down -v를 운영에서 실행하지 않는다.

## ⑧ 다음 단계 연결

Docker 이미지·DB·워커를 연결하고 자동 검사·배포·백업 절차를 만든다. 이 결과를 [study17.md](study17.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://docs.docker.com/build/building/multi-stage/)
- [공식 문서 2](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/using-secrets-in-github-actions)
