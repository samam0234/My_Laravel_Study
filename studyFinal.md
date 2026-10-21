# studyFinal. 학습 서재

지금까지의 진도를 게시판이 아닌 사이트로 다시 조립합니다. `demo`는 글과 댓글이 쌓인 실습 앱이고, `project`는 `composer create-project`로 새로 만든 학습 서재입니다. 모델은 `Note`와 `Tag`입니다. 한 노트에 태그가 여러 개이고, 한 태그도 여러 노트에 붙습니다. 중간 테이블은 `note_tag`입니다.

들어 있는 것:

- 회원, 노트, 태그 모델과 마이그레이션. `user_id`는 fillable이 아니고, 관계로 저장합니다.
- Blade 화면의 노트 CRUD, 쉼표로 받은 태그 동기화, 제목·본문 검색, 태그 필터, 세션 로그인, 작성자만 수정·삭제
- `/api/v1` JSON, 태그 목록, 검색, 페이지, Sanctum 토큰
- CORS. `js/project`는 5180, `ts/project`는 5181에서 같은 API를 부릅니다

서버는 demo와 겹치지 않게 8001을 씁니다.

```powershell
cd project
composer install
copy .env.example .env
php artisan key:generate
php artisan migrate
php artisan db:seed
php artisan serve --host=127.0.0.1 --port=8001
```

`db:seed`는 `mina@example.com` / `password123`과 노트 “마이그레이션은 스키마의 기록이다”, “Blade는 서버가 그린다”를 만듭니다. 태그는 Eloquent, 스키마, Blade입니다. 이 계정은 로컬 학습용입니다. 비밀번호 재설정, 이메일 인증, 2단계 인증은 없습니다. Breeze와 Jetstream도 설치하지 않습니다.

`.env`, SQLite, `vendor/`, `node_modules/`는 저장소에 넣지 않습니다.

## 검증

`project`에서 `php artisan test`:

```
Tests:    9 passed (47 assertions)
Duration: 1.25s
```

`js/project`의 `node --test`는 3개 통과입니다. `ts/project`의 `npm test`는 4개 통과이고 `tsc --noEmit`과 `vite build`도 통과했습니다.

브라우저 자동화 도구는 이 환경에 없어서, 화면 클릭 대신 테스트와 HTTP 응답으로 확인합니다.

| 요청 | 결과 |
|---|---|
| GET / | 200, 본문에 학습 서재 |
| GET /notes | 200, 시드 제목과 Eloquent 태그 |
| GET /login | 200 |
| GET /notes/create (손님) | 302, Location http://127.0.0.1:8001/login |
| GET /up | 200 |
| GET /api/v1/notes?tag=Eloquent | total 1, 제목 “마이그레이션은 스키마의 기록이다”, 작성자 미나 |
| GET /api/v1/tags | Blade, Eloquent, 스키마 |
| POST /api/v1/login | token_type Bearer, 이름 미나, 토큰 길이 50 |
| POST /api/v1/logout | 204 |
| OPTIONS Origin http://127.0.0.1:5180 | 204, Allow-Origin 동일, Allow-Methods POST |

클라이언트는 `data`와 `meta.current_page`를 읽고, 태그는 문자열 배열로 받습니다. 새 노트의 `tags`는 쉼표 문자열입니다.
