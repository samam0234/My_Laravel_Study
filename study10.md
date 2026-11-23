# study10 · 배포·기초 정리

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

자산 빌드와 Laravel 운영 설정을 연결하고 첫 배포 점검 기준을 세운다.

## ② 📖 이론

개발 서버는 학습 도구이며 운영은 Nginx와 PHP-FPM 같은 지속 실행 환경을 사용한다. npm run build가 Vue·CSS를 public/build와 manifest로 만들고 Laravel의 @vite가 파일 이름을 찾는다. 도메인은 서버 주소의 이름표, DNS는 주소록, HTTPS 인증서는 통신 상대와 암호화 연결을 확인하는 증명서다.

PHP 소스 전체를 웹 루트에 놓지 않고 public만 공개한다. DB 비밀번호·APP_KEY는 배포 환경에 주입한다. APP_KEY는 기존 암호화 데이터와 연결되므로 매 배포 재생성하지 않는다. SQLite는 파일 권한·영속 디스크가 필요하고 여러 인스턴스 운영은 서버 DB를 선택한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. 로컬에서 composer install, npm ci, npm run build, php artisan test를 통과시킨다.
2. Linux 서버에 PHP 8.4와 필요한 확장, Composer, Nginx/PHP-FPM을 준비한다. Node는 빌드 단계에만 필요하다.
3. 운영 환경변수를 넣고 기존 APP_KEY를 보존한다. 운영 DB 계정은 해당 DB에 필요한 권한만 갖는다.
4. composer install --no-dev --optimize-autoloader, migrate --force, php artisan optimize를 실행한다. 캐시는 새 서버 환경에서 만든다.
5. Nginx root를 앱의 public으로 지정하고 storage와 bootstrap/cache만 실행 계정이 쓸 수 있게 한다. 777 권한으로 해결하지 않는다.
6. 도메인 A/AAAA 레코드와 인증서를 설정한다. HTTP에서 HTTPS로 이동하고 보안 쿠키를 켠다.
7. /health와 /up, 로그인·CRUD·권한 거부·로그를 점검한다. study16에서는 이 순서를 Docker와 CI/CD로 옮긴다.

### 실행 명령

```powershell
cd project
npm ci
npm run build
php artisan test --compact
# 아래 명령은 운영 환경변수를 주입한 배포 서버에서 수행
composer install --no-dev --prefer-dist --optimize-autoloader --no-interaction
php artisan migrate --force
php artisan optimize
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `project/docker/nginx.conf` 전체 코드

[project/docker/nginx.conf](project/docker/nginx.conf)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```text
server {
    listen 80;
    server_name _;
    root /var/www/html/public;
    index index.php;
    client_max_body_size 1m;
    add_header X-Content-Type-Options nosniff always;
    location / { try_files $uri $uri/ /index.php?$query_string; }
    location = /index.php {
        include fastcgi_params;
        fastcgi_pass app:9000;
        fastcgi_param SCRIPT_FILENAME /var/www/html/public/index.php;
        fastcgi_read_timeout 120s;
        fastcgi_buffering off;
    }
    location ~ \.php$ { return 404; }
    location ~ /\. { deny all; }
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 2 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 3 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 4 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 5 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 10 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 11 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 12 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 13 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 14 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 15 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 16 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/docker/production.env.example` 전체 코드

[project/docker/production.env.example](project/docker/production.env.example)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```dotenv
APP_NAME=StudyShelf
APP_ENV=production
APP_KEY=base64:replace-with-php-artisan-key-generate-show
APP_DEBUG=false
APP_URL=https://study.example.com
LOG_CHANNEL=stderr
LOG_LEVEL=warning
DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE=study
DB_USERNAME=study
DB_PASSWORD=replace-with-random-password
POSTGRES_DB=study
POSTGRES_USER=study
POSTGRES_PASSWORD=replace-with-same-db-password
SESSION_DRIVER=database
SESSION_SECURE_COOKIE=true
CACHE_STORE=database
QUEUE_CONNECTION=database
DB_QUEUE_RETRY_AFTER=150
FILESYSTEM_DISK=local
MAIL_MAILER=log
MAIL_FROM_ADDRESS=study@example.com
MAIL_FROM_NAME=StudyShelf
AI_DRIVER=mock
AI_URL=http://host.docker.internal:11434
AI_MODEL=gemma4:12b
BROADCAST_CONNECTION=log
REVERB_APP_ID=study
REVERB_APP_KEY=replace-public-key
REVERB_APP_SECRET=replace-secret
REVERB_HOST=reverb
REVERB_PORT=8080
REVERB_SCHEME=http
REVERB_ALLOWED_ORIGINS=study.example.com
CORS_ORIGIN=https://study.example.com
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 2 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 3 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 4 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 5 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 6 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 7 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 8 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 9 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 10 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 11 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 12 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 13 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 14 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 15 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 16 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 17 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 18 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 19 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 20 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 21 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 22 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 23 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 24 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 25 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 26 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 27 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 28 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 29 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 30 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 31 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 32 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 33 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 34 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 35 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 36 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 37 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |


## ④ 🔗 연동 포인트

배포 서버의 DB·메일·파일 디스크는 환경변수와 영속 저장소로 잇는다. 다음 midpoint에서는 기초의 CRUD·로그인·댓글을 하나의 서비스로 검수한다. 실제 외부 호스트 배포는 자격증명이 제공되지 않아 실행하지 않았으며 절차와 코드의 준비 상태를 구분한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 500인데 상세 메시지 없음 | 운영 APP_DEBUG=false의 정상적인 정보 제한 | 서버 로그와 requestId로 원인 확인 |
| CSS·Vue가 안 보임 | public/build 누락 또는 잘못된 document root | 빌드 산출물 포함과 public 경로 확인 |
| DB 쓰기 실패 | 권한·DB_HOST·자격증명 불일치 | 접속 대상과 최소 권한 확인 후 재시도 |

## ⑥ 직접 해보기

1. 운영 예시에서 로컬과 다른 환경변수 5개를 적는다.
2. 빌드 manifest에 app.js와 docs.js 진입점이 있는지 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 빌드·테스트를 통과시켰다.
- [ ] APP_DEBUG=false와 HTTPS 쿠키를 설정했다.
- [ ] APP_KEY·DB·파일 저장소를 보존한다.
- [ ] 배포 후 로그인·등록·삭제·403·로그를 점검한다.
- [ ] 복구할 이전 이미지·코드와 DB 백업이 있다.

## ⑧ 다음 단계 연결

자산 빌드와 Laravel 운영 설정을 연결하고 첫 배포 점검 기준을 세운다. 이 결과를 [studyMidpoint.md](studyMidpoint.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/deployment)
