from pathlib import Path
from course_content import LESSONS
root=Path(__file__).resolve().parents[1]
rows='\n'.join(f"| [study{x['number']}](study{x['number']}.md) | {x['title']} | {'demo' if x['number'] in [str(i) for i in range(11)]+['Midpoint'] else 'project'} |" for x in LESSONS)
text='''# Laravel 학습 · Vue와 단일 풀스택

[Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf)을 기준으로 Laravel + Vue 하나의 구성으로 공부한다. 독립 js/ts 실습은 제거하고 Vue 소스를 각 Laravel 앱 안에 둔다. 운영은 심화 `project/` 하나를 배포한다.

| 위치 | 결과 | 주소 |
|---|---|---|
| `demo/` | 기초·중간 게시판, 회원·글·태그·댓글 | http://127.0.0.1:8000/app |
| `project/` | 심화 서재, 노트·태그·문서 요약·근거 질문 | http://127.0.0.1:8001/app |
| 각 앱 `/` | Blade 첫 화면·세션 화면 진입 | 같은 PHP 서버 |
| 각 앱 `/api-docs` | 로컬 Swagger UI | 같은 PHP 서버 |
| 각 앱 `/openapi.json` | OpenAPI 3.0.3 원문 | 같은 PHP 서버 |

PHP가 요청·인증·DB·AI 중계를 맡고 Vue는 같은 앱의 화면이다. Vite는 개발 자산 서버와 빌드 도구이며 별도 프론트 배포 서버를 만들지 않는다.

## 학습 순서

각 파일은 목표 → 이론(이유·개념·비유) → 전체 코드·줄별 설명 → 연동 → 오류 노트 → 직접 해보기 2~3개 → ☐ 체크리스트 → 다음 단계 순서다. 기존 study 파일을 덮어쓰고 누락된 구간을 추가했다.

| 문서 | 주제 | 실습 앱 |
|---|---|---|
'''+rows+'''

## Windows에서 실행

이 작업에서 PHP 8.4.25, Composer 2.10.3, Node 24.14.0을 사용했다. 잠금 파일의 Laravel은 13.43.0이다. Vue·Pinia·폼·UI 라이브러리는 각 앱의 package-lock.json으로 재현한다. PHP의 mbstring/fileinfo/openssl/pdo_sqlite 등을 활성화한다. 서버 DB는 pdo_pgsql 또는 pdo_mysql도 필요하다.

```powershell
php -v
composer -V
node -v
cd project
composer install
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path database/database.sqlite)) { New-Item -ItemType File database/database.sqlite | Out-Null }
if (-not (Select-String -Path .env -Pattern '^APP_KEY=.+')) { php artisan key:generate }
php artisan migrate
npm ci
npm run build
php artisan serve --host=127.0.0.1 --port=8001
```

브라우저에서 http://127.0.0.1:8001/app 을 연다. 기초는 같은 순서에서 `cd demo`, 포트 `8000`을 사용한다. 기존 APP_KEY는 유지하고 `.env`를 덮어쓰지 않는다. 학습 DB를 초기화하는 migrate:fresh는 실행하지 않는다.

개발 자동 새로고침은 별도 터미널에서 해당 앱의 `npm run dev`를 실행한다. 브라우저는 계속 PHP의 `/app` 주소로 접속한다. 두 앱의 Vite를 동시에 켠다면 서로 다른 dev 포트를 지정한다.

직접 회원가입할 수 있다. 선택적으로 로컬에서만 `php artisan db:seed`를 실행하면 기존 학습 계정 `mina@example.com` / `password123`이 준비된다. 이 계정은 운영에 만들지 않는다. Vue 토큰은 메모리에만 보관하므로 새로고침하면 다시 로그인한다. Blade 세션과 Vue Bearer 로그인은 따로 수행한다.

## 문서 요약·질문

project에서 별도 터미널로 워커를 실행한다.

```powershell
cd project
php artisan queue:work --tries=3 --timeout=100
```

기본 `AI_DRIVER=mock`은 외부 모델 없이 파이프라인을 연습하며 결과에 `[mock 실습]`을 표시한다. `/app`에서 UTF-8 TXT/MD(최대100KB)를 올린 뒤 문서 목록을 새로고침하고 질문한다. 파일·질문·MCP는 소유자만 접근한다. 실제 모델은 Ollama를 실행하고 `.env`의 AI_DRIVER=ollama, AI_URL, AI_MODEL을 지정한 뒤 PHP/worker를 재시작한다. 요약은 앞4000자, 질문은 어휘 검색 상위3개 청크를 사용한다.

DocuForge의 요약·근거 답변·히스토리라는 학습 목적을 Laravel 안에 옮겼다. PDF/DOCX/PPTX·OCR·임베딩 검색은 이 예제에 포함하지 않는다. [study18](study18.md)에 프롬프트·NDJSON→SSE·MCP 서버/클라이언트 전체 코드가 있다.

## API 계약과 외부 설정

- 기준은 [공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e)의 `/api`다. `/api/v1`은 이전 학습 호환 경로로 보존한다.
- 표준 목록은 data + meta.page/limit/total/totalPages/q, 날짜는 camelCase UTC ISO 8601, 오류는 error.code/message/fields/requestId다. 표준 검증은400, 기존 v1 검증은422다.
- 가입 `/api/auth/signup`은 nickname/email/password(12자 이상), 로그인은 `/api/auth/login`, 본인은 `/api/auth/me`, 로그아웃은 `/api/auth/logout`이다. Sanctum 토큰은1시간 만료다.
- 두 앱 모두 `/api/posts`와 댓글 계약을 제공한다. project는 내부 Note를 같은 계약으로 직렬화한다. Blade 경로는 `/notes`다.
- Stripe는 테스트 Checkout·서명 웹훅 수신 기록, OAuth는 GitHub의 Blade 세션이다. 결제에 따른 유료 권한 상태 머신은 구현하지 않는다.
- 메일 기본값은log, 실시간 기본값은log다. 실제 SMTP·Reverb·Stripe·OAuth 연결은 study13·17의 환경값과 공급자 설정을 따른다.
- CORS_ORIGIN으로 허용 출처를 지정한다. 비밀번호·API 비밀키를 VITE_ 변수에 넣지 않는다.

## 검증과 운영

```powershell
# 각 앱에서 실행
php artisan test --compact
npm run build
composer audit
npm audit --omit=dev
# 저장소 루트에서 실행
python tools/render_course.py
python tools/check_course.py
docker compose --profile postgres --profile mariadb --profile mongo config --quiet
```

[검증 기록](docs/verification.md)에 실제 결과와 미검증 범위를 분리한다. [노션 매핑](docs/notion-coverage.md)에 추가 체크5개와 배치 위치를 보존했다. **못 넣은 추가 체크 항목은 없다.**

[study11](study11.md)은 PostgreSQL/MariaDB 전환·Mongo 선택 예제, [study16](study16.md)은 Docker·CI/CD·백업, [studyFinal](studyFinal.md)은 최종 구성과 배포 체크리스트다. 로컬 Docker 엔진·외부 계정·실모델·원격 호스트가 준비되지 않은 항목은 실행 성공으로 기록하지 않는다.

`.env*` 실값·DB 파일·vendor·node_modules·백업·생성 자산은 제외하고 `.env.example`, composer.lock, package-lock.json을 커밋한다. 배포에서는 private-files와 DB 볼륨, APP_KEY를 보존한다.
'''
(root/'README.md').write_text(text,encoding='utf-8')
for app in ['demo','project']:
    (root/app/'README.md').write_text(f'''# Laravel {'기초 회원 게시판' if app=='demo' else '심화 AI 학습 서재'}

실행·학습 순서·환경변수·검증 결과는 [루트 README](../README.md)를 따른다.

- PHP 8.4 + Laravel 13, 앱 내부 Vue + Pinia + vee-validate + Bootstrap
- 화면 `/app`, Blade `/`, 기준 API `/api`, Swagger `/api-docs`
- 포트 {'8000' if app=='demo' else '8001'}, 로컬 SQLite, 메모리 DB 테스트
- `composer install`, `.env` 준비와 키 보존, `php artisan migrate`, `npm ci`, `npm run build`, `php artisan serve`
- `php artisan test --compact`, `composer audit`, `npm audit --omit=dev`
- `.env`·DB·업로드·토큰은 Git에 넣지 않는다.

[요구사항 매핑](../docs/notion-coverage.md) · [검증 기록](../docs/verification.md)
''',encoding='utf-8')
