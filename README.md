# Laravel 학습

Notion 페이지 [Laravel](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf)의 방향대로 만든 학습 저장소입니다. Blade와 Eloquent로 게시판을 만들고, 같은 데이터를 Sanctum API로 다시 엽니다. Django, Rails 게시판과 나란히 읽습니다.

문서는 `study0.md`부터 `study10.md`, 마지막에 `studyFinal.md` 순서입니다.

| 폴더 | 하는 일 | 주소 |
|---|---|---|
| `demo/` | study1~10이 쌓인 Laravel 앱 | http://127.0.0.1:8000 |
| `project/` | studyFinal 학습 서재. 모델 이름은 Note | http://127.0.0.1:8001 |
| `js/demo/` | demo API를 부르는 JavaScript | http://127.0.0.1:5173 |
| `ts/demo/` | 같은 화면의 TypeScript | http://127.0.0.1:5174 |
| `js/project/` | project API를 부르는 JavaScript | http://127.0.0.1:5180 |
| `ts/project/` | 같은 화면의 TypeScript | http://127.0.0.1:5181 |

JS와 TS는 Laravel 코드를 수정하지 않습니다. 각자 폴더에서 따로 실행합니다.

## 실행

이 저장소를 만든 환경은 PHP 8.4.25, Composer 2.10.3, Laravel 13.38.0, Node.js 24.14.0입니다. Windows에는 PHP가 기본으로 없습니다. winget 패키지 `PHP.PHP.8.4`와 [Composer](https://getcomposer.org/)를 설치한 뒤 새 터미널에서 확인합니다.

```powershell
php -v
composer -V
```

```powershell
cd demo
composer install
copy .env.example .env
php artisan key:generate
php artisan migrate
php artisan db:seed
php artisan serve --host=127.0.0.1 --port=8000
```

`project`는 같은 순서이고 포트만 8001입니다.

```powershell
cd js/demo
npm start
```

```powershell
cd ts/demo
npm install
npm run dev
```

`js/project`와 `ts/project`도 각 폴더에서 같은 명령입니다. 포트는 패키지 설정에 들어 있습니다.

테스트는 각 Laravel 앱에서 `php artisan test`, JS는 `npm test`, TS는 `npm test`입니다.

## 이 저장소에서 만든 것

- Blade 게시판: 글 CRUD, 댓글, 세션 로그인, 작성자만 수정·삭제
- JSON API: `/api/v1`, 중첩 댓글, 검색, 페이지
- API 로그인 Sanctum 토큰. HTML은 세션을 유지합니다
- `config/cors.php`로 위 클라이언트 포트만 허용
- 학습 서재: 노트와 태그. 게시판과 URL, 화면 구조가 다름

샘플 계정 `mina@example.com` / `password123`은 로컬 학습용입니다. 비밀번호 재설정, 이메일 인증, 2단계 인증은 없고 Jetstream도 쓰지 않습니다. Breeze가 생성하는 라우트와 대응 관계만 문서에 적습니다.

`.env`, SQLite 파일, `vendor/`, `node_modules/`는 커밋하지 않습니다.
