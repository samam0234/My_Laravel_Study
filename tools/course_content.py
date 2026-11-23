"""한국어 학습 내용. render_course.py는 실제 소스 전체와 줄별 해설을 결합한다."""
LESSONS = []
def lesson(number, title, goal, theory, steps, links, errors, exercises, checks, files, commands='', extra=''):
    LESSONS.append(dict(number=str(number),title=title,goal=goal,theory=theory,steps=steps,links=links,errors=errors,exercises=exercises,checks=checks,files=files,commands=commands,extra=extra))

lesson(0,'환경 설정','PHP·Composer·Node를 확인하고 Laravel 안에 Vue를 두는 개발 환경을 재현한다.',
'''Laravel은 요청을 받아 PHP로 업무 규칙을 실행하는 풀스택 프레임워크다. Artisan은 반복 작업을 대신하는 작업대, Composer는 PHP 패키지 창고다. Vue는 같은 Laravel 프로젝트의 `resources/js`에서 화면 상태를 관리한다. Vite는 개발 중 변경을 전달하고 운영용 파일을 만든다. Node는 자산 빌드 때 사용하며 별도 서비스 서버를 배포하지 않는다.

이 저장소는 `demo/`(기초 게시판)와 `project/`(심화 서재)라는 두 학습 결과를 보존한다. 한 서비스를 운영할 때는 `project/` 하나만 배포한다. 루트 `js/`, `ts/`별 실습은 제거했다. Vue SFC 내부의 스크립트와 Vite 설정은 Vue 실행에 필요한 파일이다.

| 위치·용어 | 역할 |
|---|---|
| `routes/web.php`, `routes/api.php` | 웹 주소와 JSON 주소의 접수 창구 |
| `app/Http/Controllers` | 요청을 검증하고 서비스를 호출하는 컨트롤러 |
| `app/Models`, Eloquent | DB 행과 관계를 PHP 객체로 표현 |
| `database/migrations` | DB 구조 변경의 시간순 기록 |
| `resources/views`, Blade | 서버가 그리는 HTML 템플릿 |
| `resources/js`, Vue SFC | 브라우저의 화면·입력·비동기 상태 |
| `public` | 웹 서버가 외부에 공개하는 유일한 루트 |
| `storage/app/private` | 업로드·설정을 보관하는 비공개 디스크 |
| `.env`, `config` | 설치별 비밀값과 애플리케이션 설정 |
| `vendor`, `node_modules` | 잠금 파일로 재설치하는 의존성 |
| Service Container, Middleware, Policy | 의존성 제공, 요청 통과 규칙, 자원 권한 규칙 |''',
'''1. Windows에 PHP 8.4와 Composer 2, Node 24를 설치한다. `php --ini`로 실제 설정 파일을 찾고 `mbstring`, `openssl`, `fileinfo`, `pdo_sqlite`를 확인한다. SQL 서버 실습은 `pdo_pgsql` 또는 `pdo_mysql`도 필요하다.
2. 아래의 **새 프로젝트 명령은 빈 연습 폴더에서만** 사용한다. 현재 저장소의 `demo` 위에 다시 생성하지 않는다. 재현 실행은 README의 `composer install`부터 시작한다.
3. `.env.example`을 `.env`로 복사하고 `key:generate`를 한 번 실행한다. `.env`의 키·비밀번호는 커밋하지 않는다. 기존 `.env`가 있으면 먼저 내용을 보존한다.
4. SQLite 파일을 만든 뒤 마이그레이션한다. 시드는 로컬에서만 실행한다. `npm ci`는 커밋된 `package-lock.json`의 정확한 의존성을 설치한다.
5. 터미널 A는 PHP 서버, B는 `npm run dev`를 실행한다. 브라우저는 PHP 주소 `/app`을 연다. 운영은 `npm run build` 결과를 Laravel과 함께 제공한다.
6. VS Code 확장은 Laravel 공식 확장, PHP Intelephense, Vue - Official을 사용한다. 동일 기능의 PHP 언어 서버를 여러 개 켰다면 중복 진단을 점검한다.
7. `git init`, `.gitignore`, 첫 커밋으로 변경 이력을 시작한다. 이 저장소에는 이미 Git이 있으므로 다시 초기화할 필요가 없다.''',
'Git은 소스와 잠금 파일을 보관하고 `.env`·DB·생성 파일은 제외한다. 다음 단계는 같은 PHP 서버의 `/`를 통해 응답을 확인한다. API·메일·AI 키는 서버 환경변수로만 읽으며 `VITE_` 변수는 브라우저에 공개된다는 경계를 유지한다.',
[('php가 인식되지 않음','설치 경로가 PATH에 없음','PHP 경로를 PATH에 추가하고 새 터미널에서 php -v 확인'),('could not find driver','현재 CLI php.ini에 PDO 확장 미설정','php --ini, php -m 확인 후 필요한 확장을 활성화'),('No application encryption key','새 .env에 APP_KEY가 비어 있음','php artisan key:generate 실행; 기존 운영 키는 재생성하지 않음')],
['php artisan about의 버전을 잠금 파일과 대조한다.','민감하지 않은 APP_NAME을 변경하고 config:clear 후 화면에 반영한다.','git check-ignore .env가 .env를 제외하는지 앱 폴더에서 확인한다.'],
['Laravel 프로젝트 (composer create-project)','버전 명령과 필수 확장을 확인했다.','.env와 .gitignore의 역할을 설명할 수 있다.','개발 서버와 Vite를 서로 다른 터미널에서 실행했다.'],
['demo/composer.json','demo/.env.example','.gitignore','demo/vite.config.js'],
'''# 새 빈 연습 폴더에서 생성할 때
php -v
composer -V
node -v
composer create-project laravel/laravel sandbox "^13.0"
cd sandbox
git init
Copy-Item .env.example .env
php artisan key:generate
php artisan about
php artisan serve
# 이 저장소를 실행할 때는 README의 composer install, npm ci를 사용한다.''')

lesson(1,'Hello World와 기본 문법','라우트에서 Blade로 데이터를 전달하고 첫 화면을 렌더링한다.',
'''요청은 `public/index.php → bootstrap/app.php → 라우트 → 컨트롤러 → 뷰 → 응답`을 지난다. 식당에 비유하면 라우트는 메뉴 번호, 컨트롤러는 주문 담당자, Blade는 완성된 접시다. PHP 변수는 `$greeting`, 배열은 `['라우트', 'Blade']`, 객체 접근은 `->`를 쓴다. `return`은 결과를 호출자에게 돌려준다.

Blade의 `{{ $greeting }}`은 HTML을 이스케이프한다. `@foreach`는 반복, `$loop->iteration`은 1부터 시작하는 순서, `@if`는 조건이다. `@extends`는 공통 레이아웃을 선택하고 `@section`은 채울 부분을 지정한다. Vue의 `{{ value }}`는 브라우저 반응형 상태를 출력한다. Blade와 Vue 템플릿은 각각 `.blade.php`, `.vue`로 분리해 같은 중괄호를 서로 해석하지 않게 한다.''',
'''1. `demo`에서 서버를 실행하고 `/`를 연다. `Hello Laravel`과 기본 단위 목록이 보이는지 확인한다.
2. `HomeController`의 greeting 문자열을 바꾸고 저장한다. Blade를 감시하는 Vite 개발 서버가 실행 중이면 브라우저가 새로고침된다. PHP 클래스의 동작 자체는 다음 요청에서 반영된다.
3. 아래 전체 컨트롤러와 뷰를 짝으로 읽는다. 값의 이름을 바꾸면 전달 배열의 키와 뷰의 변수도 함께 바꿔야 한다.
4. 개발자도구 Network에서 문서 응답 200과 HTML 본문을 확인하고 Console에서 Vite 연결 오류를 확인한다. Elements의 HTML은 서버가 만든 결과다.''',
'컨트롤러가 전달하는 배열은 다음 단계 MVC의 데이터 계약이다. `/app` 링크는 같은 Laravel이 제공하는 Vue 화면으로 이동한다. Vite의 자산 주소와 API 주소는 다르며 API 상대 경로 `/api/posts`는 PHP 서버를 가리킨다.',
[('Undefined variable','뷰에 전달한 키와 변수명이 다름','컨트롤러 배열의 greeting/topics 키 확인'),('변경해도 화면 유지','개발 서버 미실행 또는 오래된 빌드','npm run dev 실행; 배포에서는 npm run build'),('View not found','뷰 경로와 점 표기 불일치','home은 resources/views/home.blade.php인지 확인')],
['topics에 새로운 핵심 용어를 하나 추가한다.','greeting에 <b>안녕</b>를 넣어 태그가 실행되지 않는 것을 확인한다.'],
['첫 화면에서 Hello Laravel을 확인했다.','Blade 변수·반복·레이아웃을 설명할 수 있다.','Network의 200과 Console을 확인했다.'],
['demo/app/Http/Controllers/HomeController.php','demo/resources/views/home.blade.php'],
'''cd demo
php artisan serve --host=127.0.0.1 --port=8000
# 별도 터미널에서 cd demo 후 npm run dev
curl.exe -i http://127.0.0.1:8000/''')

lesson(2,'핵심 구조','라우트·컨트롤러·모델·뷰의 책임을 나누고 호출 관계를 만든다.',
'''Laravel의 기본 업무 단위는 컨트롤러 액션과 Eloquent 모델이다. 컨트롤러에 HTML·SQL·파일 처리를 한꺼번에 넣으면 수정 범위가 커진다. 요청 검증은 컨트롤러 경계, 행과 관계는 모델, 공통 계산은 서비스, 표현은 Blade/Vue에 둔다. 서류를 창구·담당자·보관함으로 나누는 것과 같다.

`Request $request`는 컨테이너가 넣어 주는 객체다. `view('study.preferences', ['theme' => $value])`로 서버에서 뷰로 값을 보낸다. Blade 컴포넌트는 `:message="session('status')"`로 속성을 받는다. Vue의 props는 부모가 자식에게 보내는 읽기 전용 입력이고 이벤트는 자식이 변경 의도를 부모에게 알리는 방식이다. 이 과정은 같은 PHP 메모리의 함수 호출과 브라우저 HTTP 요청을 구분해야 이해된다.''',
'''1. `LearningController`의 preferences와 save를 읽고 조회·저장 액션을 나눈 이유를 확인한다.
2. 로그인한 상태로 `/study/preferences`를 연다. 컨트롤러가 파일에서 읽은 theme을 뷰에 넘긴다. 저장 구현은 다음 단계에서 자세히 다룬다.
3. 경로를 다루는 코드에서 사용자가 보낸 user_id를 쓰지 않고 인증 객체의 id를 쓴다. 단위 간 전달도 신뢰 경계를 넘어오면 검증한다.
4. `Controller`의 AuthorizesRequests 트레이트가 하위 컨트롤러에서 authorize를 제공하는지 확인한다.''',
'요청 객체 → 컨트롤러의 지역 변수 → 뷰의 입력값 → 폼 POST로 데이터가 왕복한다. 다음 단계에서는 이 값이 요청이 끝난 뒤에도 남도록 세션·파일·모델 저장을 연결한다.',
[('authorize 메서드 없음','기본 Controller에 권한 트레이트가 없음','AuthorizesRequests 사용 여부 확인'),('컴포넌트 속성이 문자열로 출력','PHP 표현식에 :가 빠짐',':message="session(...)"처럼 전달'),('로그인 없이 설정을 열면 이동함','auth 미들웨어가 보호함','먼저 회원가입·로그인하고 재시도')],
['컨트롤러가 넘기는 theme을 뷰에서 문장으로도 출력한다.','조회 액션과 저장 액션이 각각 언제 호출되는지 Network에서 찾는다.'],
['라우팅 / 컨트롤러 / 뷰','MVC 각 단위의 책임과 전달값을 설명했다.','컨트롤러의 의존성 주입과 일반 함수 호출을 구분했다.'],
['demo/app/Http/Controllers/Controller.php','demo/app/Http/Controllers/LearningController.php','demo/resources/views/study/preferences.blade.php'])

lesson(3,'데이터 다루기','요청 변수·세션·파일·모델·Vue 상태의 수명을 구분하고 저장한다.',
'''PHP 지역 변수는 한 요청 동안 살고, 세션은 같은 방문자의 여러 요청을 잇고, DB·파일은 서버 재시작 뒤에도 남는다. Vue의 `ref`는 브라우저 메모리의 관찰 가능한 상자다. Pinia의 ref는 여러 화면 함수에서 같은 상자를 사용하게 한다. 메모지·개인 서랍·서고의 차이로 기억한다.

Post 모델은 posts 테이블과 연결되고 user/comments 관계를 제공한다. `fillable`은 대량 할당 가능한 속성의 명단이며 `user_id`를 제외한다. `casts`의 array는 JSON 태그를 PHP 배열로 읽고 쓴다. Vue의 `v-model`은 입력값과 상태를 묶지만 서버 저장을 자동으로 하지 않는다. 저장 버튼의 HTTP 요청이 있어야 영속화된다. 토큰은 Pinia 메모리에만 두므로 새로고침하면 다시 로그인한다.''',
'''1. 테마 화면에서 dark를 선택해 POST한다. 세션의 theme과 비공개 JSON 파일에 같은 값이 들어간다.
2. 새 요청에서 컨트롤러가 파일을 읽어 선택 상태를 복원하는지 확인한다. 파일은 `storage/app/private/preferences/{본인 id}.json`이다.
3. Post의 tags JSON cast와 scopeSearch를 읽는다. 검색 값은 바인딩되어 SQL 문자열에 직접 붙지 않는다.
4. Pinia 스토어의 token/user ref를 읽고 응답 후 값이 바뀌는 위치를 찾는다. 비밀번호·토큰을 localStorage에 쓰는 코드는 추가하지 않는다.''',
'파일 저장은 DB 이전의 작은 영속화 실습이다. 다음 단계는 어떤 URL이 조회·변경을 호출하는지 정의한다. DB로 옮길 때도 화면 입력 이름과 서버 검증 규칙의 계약을 유지한다.',
[('새로고침하면 로그아웃됨','Vue 토큰이 메모리 저장 방식임','설계된 동작; 다시 로그인하거나 세션 방식의 Blade 화면 사용'),('파일 permission denied','storage 쓰기 권한 없음','애플리케이션 실행 계정에 storage 권한 부여'),('다른 사용자의 설정이 바뀜','파일 이름을 입력 user_id로 구성함','인증 객체의 id로만 경로 작성')],
['두 회원으로 각각 설정을 저장해 서로 다른 파일인지 확인한다.','tags의 JSON DB 값과 API 배열 값을 대조한다.','Vue 입력만 바꾸고 저장하지 않으면 DB가 변하지 않는 것을 확인한다.'],
['세션과 파일 저장을 재요청으로 확인했다.','v-model과 서버 저장의 차이를 설명했다.','fillable에 소유자 id를 넣지 않았다.'],
['demo/app/Models/Post.php','demo/app/Http/Controllers/LearningController.php','demo/resources/js/stores/auth.js'])

lesson(4,'라우팅과 요청 처리','정적·동적 URL, 쿼리, 응답과 오류 경로를 하나의 흐름으로 추적한다.',
'''라우터는 URL과 메서드의 조합을 액션으로 바꾼다. 같은 `/posts`라도 GET은 목록, POST는 등록이다. `/posts/{post}`는 경로 값, `?q=Laravel&page=2`는 조회 조건이다. Blade의 named route는 URL이 바뀌어도 이름으로 이동하게 하는 주소록이다.

모델 바인딩은 id를 모델로 찾고 없으면 404를 만든다. `/posts/create`를 동적 경로보다 먼저 등록해야 create가 id로 해석되지 않는다. 웹 요청은 리다이렉트와 HTML, API는 JSON과 상태 코드를 응답한다. 표준 API에서 숫자가 아닌 id는 400, 없는 숫자 id는 404다. bootstrap의 예외 응답 변환은 `/api`에만 적용하고 이전 `/api/v1` 동작은 유지한다.''',
'''1. `route:list --path=api`로 주소·메서드·인증 미들웨어를 확인한다.
2. `/posts`, `/posts/999999`, `/api/posts?q=Laravel&limit=1`, `/api/posts/not-a-number`를 요청한다.
3. 폼 action의 route 이름과 web.php 이름을 비교한다. Vue의 fetch는 상대 주소 `/api/posts`를 쓰므로 프론트·백엔드 경로가 한 서버에서 만난다.
4. 없는 웹 주소의 HTML 404와 없는 API 주소의 `error.code=NOT_FOUND`를 대조한다. 오류마다 requestId를 헤더와 로그에서 찾는다.''',
'URL 쿼리 → Request → 검색 scope → 페이지 JSON → Vue 목록으로 이어진다. 다음 단계에서는 GET 조회와 POST/PATCH 입력을 분리하고 실패 응답을 폼 오류로 돌려준다.',
[('create가 404','동적 경로가 정적 경로보다 먼저 매칭','인증 resource 생성 경로를 먼저 등록'),('405 Method Not Allowed','URL은 맞지만 HTTP 메서드가 다름','Network의 method와 route:list를 대조'),('API 대신 HTML이 옴','주소 또는 Accept 헤더가 잘못됨','/api 경로와 Accept application/json 확인')],
['q와 page를 함께 바꾸고 화면·응답 meta를 추적한다.','등록 폼 action의 route 이름을 찾아 해당 POST 라우트를 확인한다.'],
['동적 경로와 쿼리 파라미터를 구분했다.','400·404·405의 발생 조건을 재현했다.','웹·API 경로와 프론트 요청 주소를 맞췄다.'],
['demo/routes/web.php','demo/routes/api.php','demo/bootstrap/app.php'],
'''cd demo
php artisan route:list --path=api
curl.exe -i "http://127.0.0.1:8000/api/posts?q=Laravel&limit=1"
curl.exe -i http://127.0.0.1:8000/api/posts/not-a-number''')

lesson(5,'폼·입력·검증','입력·검증·오류 표시·중복 제출 방지를 웹과 JSON 폼에 적용한다.',
'''클라이언트 검증은 빠른 피드백, 서버 검증은 저장을 허용하는 최종 문이다. 브라우저 required만 믿으면 직접 HTTP 요청으로 우회할 수 있다. Blade 폼은 `@csrf`, `old()`, `@error`로 토큰·입력 복원·필드 오류를 연결한다. Vue에서는 vee-validate의 `useForm`, `defineField`, `handleSubmit`이 입력과 오류를 관리한다.

등록은 201, 조회·수정은 200, 삭제는 204다. 이 저장소의 기준 `/api`는 공통 스펙에 따라 검증 실패 400과 `error.fields`를 보낸다. Laravel 기본 JSON 검증과 이전 `/api/v1`은 422다. 같은 실패라도 422를 400으로 바꾸는 위치를 명시해 화면이 두 코드 모두 오류로 처리하게 한다. `busy`는 요청 중 버튼을 막지만 결제 같은 작업의 진짜 중복 방지는 서버의 멱등성 키가 담당한다.''',
'''1. Blade의 글쓰기 폼을 비워 제출하고 오류와 old 값 복원을 확인한다.
2. `/app`에서 회원가입 후 글을 등록한다. Vue submit.prevent가 전체 페이지 이동을 막고 Pinia request가 JSON을 보낸다.
3. App.vue의 run이 busy를 설정하고 finally에서 해제하는지 확인한다. 저장·삭제 실패 후에도 버튼이 다시 활성화되어야 한다.
4. 개발자도구로 200/201/204/400을 확인한다. `/api/v1`의 422도 같은 오류 처리 분기로 들어간다. 로그인은 8자부터 클라이언트 검증하고 가입은 서버가 12자 이상을 요구한다.
5. 수정은 PATCH에 바뀐 필드만 보낼 수 있다. title만 바꿔도 body·tags가 유지되는지 테스트로 확인한다.''',
'폼의 필드 이름 title/body/tags는 다음 단계 API 스키마로 이어진다. 서버 검증 후에만 모델을 만들며 user_id는 클라이언트가 결정하지 못한다. Stripe의 멱등성은 study13에서 서버로 확장한다.',
[('419 Page Expired','웹 POST의 CSRF 토큰·세션 만료','@csrf와 세션 쿠키 확인, 화면 재진입'),('오류가 필드에 안 보임','error.fields와 라이브러리 오류 상태를 연결하지 않음','setErrors(error.fields) 호출 확인'),('두 번 저장됨','busy 설정 전에 요청을 중복 실행함','폼 이벤트와 버튼 클릭을 이중 연결하지 않고 서버 멱등성도 별도 설계')],
['개발자도구에서 required를 지우고 서버 검증 실패를 재현한다.','제목만 PATCH하고 본문이 유지되는지 확인한다.','응답을 지연시켜 저장 버튼 비활성화를 확인한다.'],
['입력·old·필드 오류를 연결했다.','200·400·422의 화면 흐름을 설명했다.','중복 제출 방지와 서버 멱등성을 구분했다.'],
['demo/resources/views/posts/_form.blade.php','demo/app/Http/Controllers/PostController.php','demo/resources/js/App.vue'])

lesson(6,'DB·API 연동','환경변수·마이그레이션·모델·CRUD를 공통 API v1 계약으로 연결한다.',
'''DB 연결은 `.env → config/database.php → Eloquent`를 거친다. 마이그레이션은 테이블 설계의 이력이고 모델은 행의 사용법이다. 창고 설계도와 실제 물품 대장에 비유할 수 있다. 공개 목록과 상세는 조회, 생성·수정·삭제는 인증과 소유권 확인 뒤 실행한다.

공통 API **스펙 이름**이 v1이며 기준 주소는 `/api`다. `/api/v1`은 이전 실습 호환 경로로 남겼다. 새 화면은 `/api`만 부른다. 목록은 `data`와 `meta.page/limit/total/totalPages/q`, 단건은 `data`, 날짜는 UTC ISO 8601, 필드는 camelCase다. 생성은 201과 Location, 삭제는 빈 204를 보낸다. id·createdAt은 클라이언트 입력으로 저장하지 않는다.''',
'''1. SQLite 연결을 준비하고 `migrate`로 posts·comments·tokens·tags JSON 컬럼을 만든다. 기존 DB를 지우는 migrate:fresh는 사용하지 않는다.
2. GET 목록·상세를 먼저 호출한 뒤 회원가입/로그인 토큰으로 POST·PATCH·DELETE를 실행한다.
3. ContractController의 검증 → 트랜잭션 → 관계 저장 → Resource 직렬화 순서를 읽는다. user 관계로 저장하므로 입력 user_id를 무시한다.
4. tags는 JSON 문자열이 아니라 문자열 배열이다. `limit`은 1 이상이며 50 초과는 50으로 제한한다. 검색·정렬 허용값을 고정한다.
5. 공통 게시판 규격의 댓글 주소도 연결한다. `project`의 `/api/posts`는 서재 Note를 같은 계약으로 제공하고 댓글의 내부 FK는 note_id다. Blade의 `/notes` 모델과 같은 DB 행을 읽는다.
6. 연결 실패는 서버 로그의 requestId로 조사한다. 운영 응답에 DB 접속 정보나 예외 스택을 내보내지 않는다.''',
'API는 Vue·Blade가 함께 사용하는 DB의 명시적인 입출력 경계다. 다음 단계에서 Sanctum 토큰과 세션 인증, Policy가 쓰기 권한을 제한한다. 연결 정보는 환경변수로 분리했으며 PostgreSQL·MariaDB 전환은 study11에서 수행한다.',
[('no such table','마이그레이션 전 또는 다른 DB를 가리킴','config:clear 후 migrate:status와 DB_DATABASE 확인'),('MassAssignmentException','fillable과 검증 결과 불일치','허용한 업무 필드만 모델로 전달; user_id 추가로 해결하지 않음'),('422 또는 400','필수값·tags 타입 위반','기준 API는 tags 배열, 기존 v1은 쉼표 문자열이라는 계약 차이 확인')],
['limit=999 요청이 50으로 제한되는지 확인한다.','태그 배열로 생성하고 제목만 PATCH해 태그가 유지되는지 확인한다.','없는 글, 인증 없음, 남의 글 변경을 각각 요청한다.'],
['Eloquent 모델 + 마이그레이션','게시판 CRUD','경로 `/api/v1`을 스펙의 `/api`와 맞출지 결정','연결값을 .env로 분리했다.','Location·204·태그 배열 계약을 확인했다.'],
['demo/app/Http/Controllers/Api/ContractController.php','demo/app/Http/Resources/EntryResource.php','demo/app/Http/Controllers/Api/CommentContractController.php','demo/database/migrations/2026_11_23_135403_add_tags_to_posts.php'],
'''cd demo
php artisan migrate
php artisan migrate:status
curl.exe -i "http://127.0.0.1:8000/api/posts?limit=2&sort=-createdAt"''')

lesson(7,'인증·보안 기초','세션과 Sanctum 토큰을 발급하고 소유권·해시·CSRF·XSS·CORS를 적용한다.',
'''인증은 누구인지, 인가는 이 행을 바꿀 수 있는지 확인한다. 회원증과 출입 가능한 방의 차이다. User의 password hashed cast가 비밀번호를 해시하고 Hash::check가 확인한다. 원문·해시 모두 응답에 포함하지 않는다.

Blade 로그인은 세션 쿠키를 사용하고 로그인 후 세션 id를 재생성한다. Vue는 메모리에 보관한 Sanctum Bearer 토큰을 전송한다. DB에는 토큰 해시만 남으며 새 표준 토큰은 1시간 후 만료된다. 로그아웃은 현재 토큰만 폐기한다. 서로 다른 로그인 수단은 같은 User를 가리켜도 토큰·세션을 자동 복사하지 않는다.

Policy는 작성자만 수정·삭제하도록 한다. Vue·Blade의 텍스트 출력은 기본 이스케이프를 사용한다. 웹 폼에는 CSRF 토큰을 넣는다. Bearer API는 브라우저가 자동 첨부하는 인증 쿠키에 의존하지 않는다. CORS는 브라우저의 읽기 허용 규칙이고 서버 권한 확인을 대체하지 않는다. `CORS_ORIGIN`으로 출처를 지정하며 공개 VITE 변수에 비밀키를 넣지 않는다.''',
'''1. 가입은 nickname/email/password를 받는다. 중복 이메일은 409, 잘못된 로그인은 계정 존재를 구별하지 않는 401이다.
2. 로그인 응답의 accessToken을 Authorization 헤더에 넣고 `/api/auth/me`를 요청한다. API 토큰을 URL 쿼리에 넣거나 콘솔 로그에 남기지 않는다.
3. 두 회원을 만들고 다른 회원의 글을 PATCH/DELETE하면 403인지 확인한다. 비공개 AI 문서는 존재도 숨기기 위해 404를 사용한다.
4. 로그아웃한 토큰·만료 토큰으로 다시 요청하면 401인지 확인한다. 로그인 경로는 분당 10회로 제한한다.
5. Blade 세션 로그아웃의 invalidate/regenerateToken과 Vue 토큰 폐기를 구분한다. 운영은 HTTPS와 SESSION_SECURE_COOKIE=true를 사용한다.''',
'프론트는 토큰을 request 함수 한 곳에서 붙이고 백엔드는 auth:sanctum과 Policy로 매 요청을 검증한다. 다음 단계는 이 공통 처리와 설정을 재사용 단위로 정리한다. 메일 인증·비밀번호 재설정·MFA는 현재 구현 범위에 없으므로 운영 요구가 생기면 별도 설계한다.',
[('401이 반복','토큰 누락·만료 또는 폐기','me 응답과 Authorization 헤더 확인 후 다시 로그인'),('403인데 버튼이 보임','UI 표시만으로 서버 권한이 생기지 않음','author.id로 버튼 표시하고 서버 Policy 유지'),('CORS 오류','요청 출처와 환경변수 불일치','정확한 scheme/host/port를 설정하고 config:clear')],
['로그아웃 후 같은 토큰이 거부되는지 확인한다.','게시글 제목에 스크립트 태그를 저장해 문자로 보이는지 확인한다.','다른 계정으로 소유권 검사를 재현한다.'],
['Blade 템플릿 또는 API (Sanctum)','인증 (Breeze / Jetstream / 직접)','해시·세션 재생성·토큰 만료를 확인했다.','Policy와 CORS의 책임을 구분했다.'],
['demo/app/Http/Controllers/Api/AuthController.php','demo/app/Http/Controllers/Auth/SessionController.php','demo/app/Models/User.php','demo/app/Policies/PostPolicy.php','demo/config/cors.php'])

lesson(8,'구조화·재사용','문자열 규칙·화면 조각·요청 처리를 추출하고 개발·운영 설정을 나눈다.',
'''재사용은 동일한 업무 규칙이 여러 곳에서 다르게 바뀌는 일을 막기 위해 한다. TagNames는 태그 공백·중복·길이·개수를 한 곳에서 정리한다. Blade status 컴포넌트는 같은 알림 HTML을 반복하지 않게 한다. Pinia request는 인증·JSON·오류 해석을 모은다. 자주 쓰는 연장을 공용 공구함에 넣는 것과 같다.

컨트롤러는 HTTP, 서비스는 계산과 외부 작업, 모델은 행과 관계, Resource는 외부 JSON 표현을 맡는다. config 파일에서만 env를 읽으면 config:cache 뒤에도 설정이 일관된다. `APP_ENV`, `APP_DEBUG`, DB·메일·AI 연결은 배포별로 다르고 코드 구조는 같다.''',
'''1. TagNames::normalize 입력에 공백·중복·빈 값·문자열 0을 넣어 정규화 규칙을 확인한다.
2. 컴포넌트의 @props 기본값과 호출부의 :message를 확인한다. 선택하지 않은 추가 화면 프레임워크는 설치하지 않는다.
3. `.env.example`은 변수 이름과 안전한 기본값만 제공한다. 운영 변수는 비밀 저장소나 호스트 환경에서 주입한다.
4. 운영에서 APP_DEBUG=false, HTTPS URL, 안전한 쿠키, stderr 로그를 지정한다. 설정 변경 뒤 config:clear 또는 새 프로세스 재시작이 필요하다.
5. src 간 공유를 위해 다른 앱 폴더를 직접 require하지 않는다. demo와 project는 같은 Laravel 학습 과정의 별도 실행 결과다.''',
'순수 정규화 함수는 다음 단계의 빠른 단위 테스트 대상이다. HTTP·DB가 필요한 테스트는 Laravel Feature 테스트로 분리한다. 환경변수와 요청 공통 처리는 이후 Docker·외부 서비스에서도 그대로 사용한다.',
[('설정값이 예전 그대로','config 캐시에 이전 .env가 남음','개발은 config:clear, 운영은 새 환경에서 캐시 재생성'),('태그 0이 사라짐','기본 array_filter가 문자열 0도 제거','빈 문자열과 명시적으로 비교'),('노트의 태그가 없어짐','PATCH 누락 필드를 빈 배열로 취급','array_key_exists로 실제 전달 여부 검사')],
['TagNames에 한글 40자를 넣어 30자로 제한되는지 확인한다.','동일한 status 컴포넌트를 다른 Blade 뷰에서 호출한다.'],
['공통 유틸·뷰·HTTP 처리를 분리했다.','설정 코드에서만 env를 읽었다.','개발·운영의 APP_DEBUG와 연결값을 구분했다.'],
['demo/app/Support/TagNames.php','demo/resources/views/components/status.blade.php','demo/config/study.php','project/docker/production.env.example'])

lesson(9,'테스트·디버깅','순수 단위 테스트와 DB·HTTP 요청 테스트로 실패 원인을 재현한다.',
'''단위 테스트는 작은 계산을 빠르게 확인하고 Feature 테스트는 요청·인증·검증·DB·응답의 연결을 확인한다. 부품 검사와 조립품 검사에 비유할 수 있다. TagNamesTest는 PHP 순수 함수, ContractTest는 실제 SQLite DB와 HTTP 계약을 검증한다.

테스트 DB는 메모리 SQLite이며 실제 학습 DB를 지우지 않는다. 외부 API는 Http::fake와 preventStrayRequests, 파일은 Storage::fake, 큐는 Queue::fake, 알림은 Notification::fake로 바꾼다. DB 쿼리 빌더 자체를 mock하면 SQL 실수를 놓치므로 실제 테스트 DB를 사용한다. project의 DocumentTest는 AI·파일·큐 가짜를 연결한 심화 예제다.

디버깅 순서는 재현 요청 → 상태 코드 → error.requestId → storage/logs/laravel.log → 좁은 테스트다. 개발자도구 Network는 요청 본문과 응답, Console은 Vue 오류, php artisan route:list는 URL, php artisan pail은 로그를 보여 준다. 운영 로그에 비밀번호·토큰·문서 전문을 남기지 않는다.''',
'''1. TagNamesTest만 실행해 순수 규칙을 확인한다. 테스트가 실제 사용할 문자열 0과 유니코드 경계를 다루는 이유를 읽는다.
2. ContractTest는 가입·로그인·소유권·페이지·부분 수정·로그아웃·댓글·캐시를 검증한다. 요청 결과와 DB 변경을 함께 단언한다.
3. project의 DocumentTest에서 Http::preventStrayRequests가 실제 AI 호출을 막고 NDJSON 스트림만 가짜로 주는 부분을 찾는다.
4. 실패 테스트 하나를 수정한 뒤 그 테스트부터 다시 실행한다. 마지막에 전체 앱 테스트를 한 번 실행해 회귀를 확인한다.
5. 아래 TOP 10을 증상별 시작점으로 사용한다. 토큰을 바꾸는 한 테스트 안에서는 forgetGuards가 이전 사용자를 초기화한다.''',
'테스트는 API 계약과 보안의 변경을 배포 전에 멈추는 기준이다. 다음 단계의 배포 점검은 이 테스트와 빌드 결과를 전제로 한다. 심화에서는 같은 테스트를 PostgreSQL·MariaDB 서비스에서도 실행하는 CI 행렬을 사용한다.',
[('1. php 명령 없음','PATH 설정 누락','새 터미널에서 경로 확인'),('2. No application key','APP_KEY 없음','새 로컬 환경에서만 key:generate'),('3. no such table','DB/마이그레이션 불일치','migrate:status와 연결 설정 확인'),('4. could not find driver','PDO 확장 없음','php --ini와 php -m 확인'),('5. 419','CSRF·세션 만료','@csrf와 쿠키 확인'),('6. 401','토큰 누락·만료','로그인/Authorization 확인'),('7. 403','Policy 소유권 거부','인증 사용자와 user_id 대조'),('8. 404 create','라우트 순서 오류','정적 경로를 먼저 등록'),('9. Vite manifest 없음','빌드 미실행','npm ci 후 npm run build'),('10. 테스트 사용자 혼선','같은 테스트에서 가드 캐시 재사용','토큰 전환 사이 forgetGuards 호출')],
['TagNames의 trim을 지웠을 때 단위 테스트가 실패하는지 실험 후 복원한다.','다른 계정 삭제 테스트가 DB 행을 보존하는지 단언을 찾는다.','AI 실패 가짜 응답을 503으로 지정해 이력이 저장되지 않는지 확인한다.'],
['단위 테스트와 요청 테스트를 각각 실행했다.','DB를 실제로 사용하고 외부 HTTP만 fake로 바꿨다.','오류 TOP 10과 requestId 로그를 확인했다.'],
['demo/tests/Unit/TagNamesTest.php','demo/tests/Feature/ContractTest.php','project/tests/Feature/DocumentTest.php'],
'''cd demo
php artisan test --compact --filter=TagNamesTest
php artisan test --compact --filter=ContractTest
php artisan test --compact
Get-Content storage/logs/laravel.log -Tail 30
# project에서는 php artisan test --compact --filter=DocumentTest''')

lesson(10,'배포·기초 정리','자산 빌드와 Laravel 운영 설정을 연결하고 첫 배포 점검 기준을 세운다.',
'''개발 서버는 학습 도구이며 운영은 Nginx와 PHP-FPM 같은 지속 실행 환경을 사용한다. npm run build가 Vue·CSS를 public/build와 manifest로 만들고 Laravel의 @vite가 파일 이름을 찾는다. 도메인은 서버 주소의 이름표, DNS는 주소록, HTTPS 인증서는 통신 상대와 암호화 연결을 확인하는 증명서다.

PHP 소스 전체를 웹 루트에 놓지 않고 public만 공개한다. DB 비밀번호·APP_KEY는 배포 환경에 주입한다. APP_KEY는 기존 암호화 데이터와 연결되므로 매 배포 재생성하지 않는다. SQLite는 파일 권한·영속 디스크가 필요하고 여러 인스턴스 운영은 서버 DB를 선택한다.''',
'''1. 로컬에서 composer install, npm ci, npm run build, php artisan test를 통과시킨다.
2. Linux 서버에 PHP 8.4와 필요한 확장, Composer, Nginx/PHP-FPM을 준비한다. Node는 빌드 단계에만 필요하다.
3. 운영 환경변수를 넣고 기존 APP_KEY를 보존한다. 운영 DB 계정은 해당 DB에 필요한 권한만 갖는다.
4. composer install --no-dev --optimize-autoloader, migrate --force, php artisan optimize를 실행한다. 캐시는 새 서버 환경에서 만든다.
5. Nginx root를 앱의 public으로 지정하고 storage와 bootstrap/cache만 실행 계정이 쓸 수 있게 한다. 777 권한으로 해결하지 않는다.
6. 도메인 A/AAAA 레코드와 인증서를 설정한다. HTTP에서 HTTPS로 이동하고 보안 쿠키를 켠다.
7. /health와 /up, 로그인·CRUD·권한 거부·로그를 점검한다. study16에서는 이 순서를 Docker와 CI/CD로 옮긴다.''',
'배포 서버의 DB·메일·파일 디스크는 환경변수와 영속 저장소로 잇는다. 다음 midpoint에서는 기초의 CRUD·로그인·댓글을 하나의 서비스로 검수한다. 실제 외부 호스트 배포는 자격증명이 제공되지 않아 실행하지 않았으며 절차와 코드의 준비 상태를 구분한다.',
[('500인데 상세 메시지 없음','운영 APP_DEBUG=false의 정상적인 정보 제한','서버 로그와 requestId로 원인 확인'),('CSS·Vue가 안 보임','public/build 누락 또는 잘못된 document root','빌드 산출물 포함과 public 경로 확인'),('DB 쓰기 실패','권한·DB_HOST·자격증명 불일치','접속 대상과 최소 권한 확인 후 재시도')],
['운영 예시에서 로컬과 다른 환경변수 5개를 적는다.','빌드 manifest에 app.js와 docs.js 진입점이 있는지 확인한다.'],
['빌드·테스트를 통과시켰다.','APP_DEBUG=false와 HTTPS 쿠키를 설정했다.','APP_KEY·DB·파일 저장소를 보존한다.','배포 후 로그인·등록·삭제·403·로그를 점검한다.','복구할 이전 이미지·코드와 DB 백업이 있다.'],
['project/docker/nginx.conf','project/docker/production.env.example'],
'''cd project
npm ci
npm run build
php artisan test --compact
# 아래 명령은 운영 환경변수를 주입한 배포 서버에서 수행
composer install --no-dev --prefer-dist --optimize-autoloader --no-interaction
php artisan migrate --force
php artisan optimize''')

lesson('Midpoint','중간 응용 · 회원 게시판','study0~10의 로그인·글·댓글·검색을 Laravel 안의 한 서비스로 완성한다.',
'''### 기능 목록

- Blade의 가입·로그인·로그아웃과 작성자 전용 글 CRUD
- 같은 DB를 읽는 Vue 게시판, 메모리 토큰 로그인, 댓글 작성·삭제
- 제목·본문 검색, 정렬, 1부터 시작하는 페이지, JSON 태그
- 설정 파일·세션 저장, 검증 오류, Policy, XSS 이스케이프, 테스트

이 구간은 큐·AI·외부 결제·OAuth 없이 기초에서 설명한 도구만 사용한다. 목표는 기능을 많이 붙이는 것보다 입력 한 건이 검증·권한·저장·응답·화면을 통과하는 전체 흐름을 이해하는 것이다.''',
'''### 폴더 구조

```text
demo/
  routes/                 웹·API 주소
  app/Http/Controllers/   요청과 인증
  app/Http/Resources/     공통 JSON 모양
  app/Models/             User, Post, Comment
  app/Policies/           작성자 권한
  app/Support/            TagNames 순수 규칙
  resources/views/        Blade 화면
  resources/js/           Vue 화면과 Pinia 스토어
  database/migrations/    회원·글·댓글·토큰·태그
  tests/                  순수 함수·요청·DB 계약
```

### 단계별 구현 순서

1. study0의 환경과 .env를 준비하고 빈 DB에 migrate한다.
2. study1~4의 MVC와 URL을 확인하고 Post·Comment·User 관계를 만든다.
3. study5의 폼 검증과 오류 복원을 연결하고 Blade CRUD를 수행한다.
4. study6의 /api JSON, 태그 배열, 페이지·검색, Location·204를 맞춘다.
5. study7의 세션·Sanctum·Policy로 쓰기를 제한한다.
6. study3·5·8에서 익힌 ref·Pinia request·폼 처리로 /app을 연결한다.
7. study9 테스트와 study10 빌드·배포 점검표를 통과시킨다.

아래 파일은 조립된 기초 서비스의 전체 핵심 코드다. 나머지 모델·인증·Resource 전체 코드는 해당 study에서 이미 제공했다.''',
'''### DB·API 연동 구성도

```mermaid
flowchart LR
    B[브라우저: Blade 또는 Vue] --> R[Laravel 웹·API 라우트]
    R --> A[인증·검증·Policy]
    A --> M[Eloquent: User/Post/Comment]
    M --> D[(SQLite)]
    M --> J[Resource: data + meta]
    J --> B
```

한 서비스 안의 두 표현 방식이며 별도 프론트 배포가 필요 없다. 다음 심화 서재는 같은 인증·API 계약을 유지하면서 Note·Tag와 문서 기능을 추가한다.''',
[('Blade는 로그인인데 Vue는 손님','세션과 Bearer 토큰이 서로 다른 인증 수단','Vue에서 별도로 로그인하거나 Blade 화면을 사용'),('댓글 개수가 안 변함','이전 목록 상태를 유지함','상세 재조회로 commentCount 확인, 댓글 목록 갱신'),('새 DB에서 샘플 계정 없음','migrate와 seed는 다른 작업','로컬에서만 db:seed 또는 직접 가입')],
['두 계정으로 글과 댓글을 만들고 서로 삭제가 거부되는지 확인한다.','검색 결과 6개를 만들어 limit=5의 두 번째 페이지를 연다.','로그아웃 후 쓰기 요청이 차단되는지 확인한다.'],
['1차 배포: npm build·전체 테스트가 통과한다.','1차 배포: public만 공개하고 HTTPS·환경변수·DB 권한을 점검한다.','1차 배포: 운영에서 학습 시드를 실행하지 않는다.','1차 배포: /health·/api/posts·로그인·CRUD·권한 거부를 점검한다.'],
['demo/app/Http/Controllers/Api/ContractController.php','demo/app/Http/Controllers/Api/CommentContractController.php','demo/resources/js/App.vue'],
'''cd demo
composer install
npm ci
php artisan migrate
php artisan db:seed
npm run build
php artisan test --compact
php artisan serve --host=127.0.0.1 --port=8000
# 브라우저: http://127.0.0.1:8000/app''',
'''### 회고

입력 검증을 프론트에만 둘 수 없는 이유, 세션과 토큰이 공유하는 것과 따로 유지하는 것, DB 관계로 소유자를 결정하는 이유를 각각 본인 말로 적는다. 실패 요청 하나의 requestId와 해결 과정을 남긴다. 기초에서 가장 수정하기 어려웠던 중복은 심화의 서비스·Resource 분리 기준으로 사용한다.''')

lesson(11,'DB 확장','PostgreSQL·MariaDB 연결을 전환하고 MongoDB 모델의 다른 전제를 설명한다.',
'''같은 Eloquent 코드도 DB 드라이버와 스키마 제약에 따라 실제 SQL이 달라진다. 어댑터가 다른 콘센트에 맞춰 주더라도 전압 규칙까지 없애지는 못하는 것과 같다. PostgreSQL과 MariaDB는 기존 정수 PK·외래키·트랜잭션·중간 테이블을 유지할 수 있다. 검색은 whereLike를 사용해 PostgreSQL에서도 대소문자 무시 계약을 유지한다.

| 대상 | 연결 | 모델·스키마 주의점 |
|---|---|---|
| SQLite | pdo_sqlite, 파일 경로 | 파일 영속성, 동시 쓰기, 외래키 활성화 |
| PostgreSQL | pdo_pgsql, pgsql | DB 생성·권한, UTC, JSON·인덱스 검토 |
| MariaDB | pdo_mysql, mariadb | utf8mb4·collation, JSON cast, 외래키 타입 일치 |
| MongoDB | ext-mongodb + mongodb/laravel-mongodb | 전용 Model, ObjectId, 컬렉션·인덱스, 관계·트랜잭션 지원 검토 |

MongoDB는 DB_CONNECTION만 바꿔 SQL 모델·정수 URL·note_tag 마이그레이션을 그대로 실행할 수 없다. 별도 보관 모델 예제를 제공한다. 기본 서재 DB 교체 대상은 PostgreSQL 또는 MariaDB이며 Mongo 예제는 선택 실험이다.''',
'''1. Docker 엔진을 켠 뒤 루트에서 선택한 profile을 실행한다. 로컬 포트는 PostgreSQL 54329, MariaDB 33069, MongoDB 27019다.
2. Windows php.ini에서 PDO 확장을 켠다. use_database.ps1은 필요한 확장을 검사하고 기존 .env를 고유한 이름으로 백업한 뒤 연결값만 바꾼다.
3. PostgreSQL 또는 MariaDB로 migrate하고 새 DB에서 직접 가입해 CRUD를 확인한다. **연결 변경은 데이터 복사가 아니다.** 기존 SQLite는 남으며 데이터 이전은 별도 export/import와 건수 검증이 필요하다.
4. notes-tags-note_tag의 다대다를 확인한다. 배열 태그는 모델에서 중간 테이블 id로 sync한다.
5. Mongo 선택 실습: PHP에 맞는 ext-mongodb를 설치한 뒤 project에서 composer require mongodb/laravel-mongodb를 실행한다. MONGODB_URI와 MONGODB_DATABASE를 .env에 넣고 예제 run.php를 실행한다. SQL 기본 연결은 유지한다.
6. Mongo의 sourceId 인덱스는 명시적으로 만들고 ObjectId는 문자열로 직렬화한다. 기존 /posts/{id}의 숫자 제약을 Mongo id에 재사용하지 않는다.
7. 이 환경은 Docker 엔진 미실행 및 로컬 SQL PDO 확장 미활성화 상태여서 외부 DB 실행 검증은 완료로 표시하지 않는다. CI에 PostgreSQL·MariaDB 테스트 행렬을 준비했다.''',
'SQL DB를 바꿔도 Vue가 읽는 API 필드와 상태 코드는 유지한다. Mongo ObjectId를 공개하려면 별도 API 자원 스키마를 설계한다. 다음 단계에서는 DB 내부 변화와 무관하게 같은 Vue UI를 연동한다.',
[('could not find driver','pdo_pgsql/pdo_mysql 비활성화','php --ini의 확장을 켜고 새 PHP 프로세스로 실행'),('Connection refused','Docker 엔진·profile·포트가 다름','docker compose ps와 공개 로컬 포트 확인'),('새 DB가 비어 있음','연결 전환만 하고 데이터 이전을 안 함','원본 보존 후 export/import와 FK·건수 검증')],
['PostgreSQL 연결 뒤 같은 ContractTest를 실행하고 결과를 기록한다.','MariaDB에서 한글 태그를 저장·검색한다.','Mongo 보관 문서의 id 타입과 SQL id를 출력해 URL 설계 차이를 적는다.'],
['PostgreSQL과 MariaDB의 연결·마이그레이션 절차를 작성했다.','SQL 모델과 Mongo 전용 모델을 구분했다.','실제 DB 실행 결과를 별도로 기록한다.','데이터 이전·백업·원복 절차를 확인한다.'],
['compose.yaml','tools/use_database.ps1','project/app/Models/Note.php','examples/mongodb/ArchiveDocument.php','examples/mongodb/run.php'],
'''# 저장소 루트, Docker 엔진이 실행 중일 때
docker compose --profile postgres up -d postgres
powershell -File tools/use_database.ps1 -App project -Driver pgsql
# MariaDB 선택 시
docker compose --profile mariadb up -d mariadb
powershell -File tools/use_database.ps1 -App project -Driver mariadb
# SQLite로 연결 원복 (다른 DB 데이터는 삭제하지 않음)
powershell -File tools/use_database.ps1 -App project -Driver sqlite
# Mongo 선택 실습: PHP ext-mongodb 설치 후
docker compose --profile mongo up -d mongo
php --ri mongodb
composer --working-dir=project require mongodb/laravel-mongodb
# project/.env.example의 MONGODB_URI/DATABASE를 .env에 반영한 뒤
php examples/mongodb/run.php''')

lesson(12,'프론트·UI 연동','Vue·Bootstrap·Pinia·vee-validate로 서재의 입력·인증·목록을 연결한다.',
'''Vue SFC는 script setup과 template을 한 컴포넌트에 모은다. Bootstrap은 화면 프레임워크를 추가하지 않고 CSS 유틸과 접근 가능한 기본 요소를 제공한다. Pinia는 token/user와 공통 요청 행동, vee-validate는 폼 입력과 오류 상태를 맡는다. 각각 화면의 옷·공용 기억·입력 안내원으로 비유할 수 있다.

이 저장소는 Vue 한 가지를 사용한다. Laravel의 /app HTML이 Vue를 마운트하고 같은 호스트의 /api를 호출한다. Vite 개발 서버는 자산만 제공한다. 운영에서는 PHP-FPM·Nginx가 빌드 파일과 요청을 함께 제공하므로 프론트용 별도 앱 서버가 없다.''',
'''1. npm ci로 잠금 파일의 Vue·Pinia·vee-validate·Bootstrap을 설치한다. 기존 JS/TS 화면별 폴더를 다시 만들지 않는다.
2. app.js의 createApp과 createPinia, App.vue의 props·ref·이벤트를 연결한다.
3. login → accessToken → 공통 Authorization → 목록/저장 → 오류 fields 순서를 Network에서 추적한다. 기준 API의 data/meta와 camelCase 필드를 그대로 읽는다.
4. 제목·본문·태그·댓글을 등록하고 자기 글에만 수정·삭제 버튼이 보이는지 확인한다. 버튼 노출과 서버 Policy를 함께 적용한다.
5. 로그인/가입은 useForm으로, 글쓰기 입력은 v-model과 서버 errors로 관리한다. busy로 중복 요청을 막고 키보드 label·role=status를 유지한다.
6. 개발은 PHP 주소 /app에 접속하고 npm run dev를 병행한다. 운영은 npm run build를 사용한다. project의 실시간 알림 연결은 study17에서 확장한다.''',
'study6·14에서 맞춘 API 계약을 실제 Vue 화면이 소비한다. DB 교체와 무관하게 화면 요청 경로는 /api다. 다음 단계에서는 서버만 외부 서비스 키를 갖고 Vue에는 성공·실패 결과만 전달한다.',
[('401 후 화면이 로그인 상태','인증 실패 때 store를 지우지 않음','request 함수의 token/user 초기화 확인'),('Vue가 마운트되지 않음','진입점·DOM id·Vite manifest 불일치','#app과 @vite, 빌드 입력 확인'),('한글이 중간에 깨짐','스트림 바이트를 매번 독립 디코딩','TextDecoder stream 옵션 사용')],
['화면에서 가입→글→수정→댓글→삭제→로그아웃을 수행한다.','Network를 offline으로 바꾸고 오류와 busy 해제를 확인한다.','키보드만으로 폼 label과 버튼에 접근한다.'],
['Vue / React / Svelte를 프론트로 붙이기 (선택)','선택 목표 "Vue / React / Svelte를 프론트로 붙이기": 위 항목을 맞춘 뒤 기존 프론트 게시판을 그대로 연결해 보기','Vue 1개와 Laravel의 단일 배포 구성을 확인했다.','Pinia·폼 오류·UI CSS를 연결했다.'],
['project/resources/js/app.js','project/resources/js/stores/auth.js','project/resources/js/App.vue','project/resources/views/workspace.blade.php'])

lesson(13,'외부 서비스 연동','테스트 결제·메일·비공개 파일·GitHub OAuth를 서버 경계에서 연결한다.',
'''외부 서비스는 실패·지연·중복 응답이 생기는 별도 시스템이다. 택배 발송처럼 접수와 완료 확인을 분리해야 한다. Stripe Checkout은 서버가 정한 price id로 테스트 세션을 만들고 서명 웹훅으로 수신을 확인한다. 현재 예제는 수신 영수증을 저장하며 결제 금액에 따른 이용 권한 변경은 하지 않는다.

메일은 Laravel Notification을 큐에 넣어 log/SMTP 전송으로 바꾼다. 파일은 외부 공개 public 디스크 대신 private에 저장한다. GitHub OAuth는 redirect→state 검증→callback→User→세션으로 이어진다. 같은 이메일이라는 이유로 기존 계정을 자동 연결하지 않는다.''',
'''1. Stripe 테스트 키·서버 price·웹훅 secret을 .env에 설정한다. 키가 없으면 Checkout은 503을 반환한다. 실결제를 실행하지 않는다.
2. 인증된 POST /api/checkout의 URL로 테스트 Checkout을 연다. 클라이언트가 가격을 보내도 서버 price를 사용하고 분 단위 멱등성 키로 재요청을 묶는다.
3. /api/webhooks/stripe는 raw body와 Stripe-Signature의 t/v1을 검증한다. 5분 시각 허용 범위와 event_id unique로 위조·오래된 요청·중복 수신을 제한한다. 브라우저 success 쿼리로 결제 완료를 판정하지 않는다.
4. MAIL_MAILER=log로 로컬 알림 내용을 확인한다. SMTP로 바꾸려면 host/port/username/password/from과 실제 메일 공급자 설정을 맞춘다.
5. 문서는 UTF-8 TXT/MD, 최대 100KB만 허용한다. 임의 실행 파일·공개 URL을 만들지 않고 본인에게만 다운로드를 허용한다.
6. GitHub OAuth 앱에 callback URL을 정확히 등록하고 services.github 환경값을 채운다. state 오류·거절·이메일 없음·기존 이메일 충돌을 처리한다.
7. OAuth 결과는 Blade 세션이다. Vue의 Bearer 토큰으로 자동 변환하지 않는다. 외부 계정이 필요한 실제 결제·SMTP·GitHub 왕복은 공급자 자격증명 설정 후 별도 검증한다.''',
'브라우저는 Laravel만 호출하고 외부 비밀키는 서버의 services 설정에서만 읽는다. 파일 저장 후 요약 job으로 잇는 흐름은 study15·18에서 완성한다. 외부 HTTP 가짜와 서명 테스트는 실제 과금 없이 이 경계를 검증한다.',
[('503 결제 사용 불가','Stripe 키·price 미설정','테스트 환경변수 구성 후 config:clear'),('웹훅 서명 400','다른 secret·body 변형·시각 만료','서명 대상 raw body와 endpoint secret을 확인'),('OAuth state 오류','세션 쿠키·callback 도메인 불일치','stateless로 우회하지 말고 같은 도메인·세션 설정 확인')],
['테스트 웹훅을 두 번 보내 duplicate=true인지 확인한다.','서명 한 글자를 바꿔 거부되고 DB 영수증이 늘지 않는지 확인한다.','php 확장 파일 업로드를 시도해 검증 거부를 확인한다.'],
['테스트 결제와 실제 과금을 구분했다.','메일·파일·OAuth 환경변수를 분리했다.','웹훅의 서명·시각·중복을 검사했다.','기존 계정을 이메일만으로 자동 연결하지 않는다.'],
['project/app/Http/Controllers/IntegrationController.php','project/config/services.php','project/app/Http/Controllers/Api/DocumentController.php','project/app/Notifications/DocumentReady.php','project/tests/Feature/IntegrationTest.php'])

lesson(14,'API 설계','REST·OpenAPI·버전·페이지·오류 규칙을 구현과 문서에 동일하게 고정한다.',
'''REST는 URL을 자원으로, 메서드를 동작으로 표현한다. API 문서는 사람과 클라이언트가 함께 보는 계약서다. `/api/posts`는 목록/생성, `/api/posts/{id}`는 상세/부분 수정/삭제다. 공통 스펙 v1의 버전 이름을 OpenAPI info.version=1.0.0으로 기록하고 경로 /api를 기준으로 한다.

호환 경로 /api/v1은 예전 Resource·검증 방식 학습용이다. 새 필드 변경으로 기준 API를 깨야 한다면 새 버전과 폐기 일정을 설계한다. 단순히 같은 주소에서 data/meta 키를 바꾸지 않는다. Resource는 DB snake_case를 camelCase로 바꾸는 번역기이고 예외 응답 처리기는 오류를 같은 봉투에 넣는다.''',
'''1. /api-docs를 열어 로컬 Swagger UI와 /openapi.json을 확인한다. 자산은 npm 패키지로 빌드하므로 외부 CDN에 의존하지 않는다.
2. EntryResource·DocumentResource와 실제 응답 필드를 비교한다. 비밀번호·원문 문서·서버 파일 경로는 목록에 노출하지 않는다.
3. 목록 meta는 page/limit/total/totalPages/q다. page는 1부터, limit은 기본10·최대50이다. 정렬은 createdAt, -createdAt, -commentCount만 허용한다.
4. 400 검증 오류는 fields, 401 인증, 403 공개 글 소유권, 404 없는 자원/비공개 문서, 409 중복 이메일, 429 제한, 500/502/503 서비스 오류로 정리한다.
5. X-Request-Id를 응답 헤더와 error.requestId에 맞춘다. 요청 id는 길이와 안전한 문자만 허용하고 없으면 생성한다.
6. OpenAPI에서 Bearer를 넣어 요청할 때 로컬 학습 계정만 사용한다. 문서 UI는 토큰 영속 저장을 끈다.
7. 웹소켓 인증과 MCP는 각각 프로토콜 응답을 따르며 REST 오류 봉투로 MCP JSON-RPC를 덮어쓰지 않는다.''',
'study12의 Vue는 이 계약의 실제 소비자다. 다음 단계의 캐시·큐는 내부 구현을 바꿔도 같은 API 계약을 유지해야 한다. 새 엔드포인트를 추가하면 OpenAPI와 계약 테스트를 함께 바꾼다.',
[('meta.current_page를 읽어 페이지가 안 바뀜','새 화면이 이전 v1 형식을 사용','기준 /api의 meta.page로 맞춤'),('태그가 문자열로 전송됨','이전 입력 형태를 재사용','tags 문자열 배열로 JSON 인코딩'),('500에 SQL이 보임','예외 원문을 API에 포함','APP_DEBUG=false와 공통 오류 봉투 사용')],
['Swagger UI에서 limit=1로 목록을 확인한다.','위조 X-Request-Id에 제어문자를 넣지 못하도록 안전한 값 생성 분기를 확인한다.','OpenAPI와 실제 응답에서 createdAt과 error.fields를 대조한다.'],
['목록 `meta.current_page/last_page/total`을 `page/limit/total/totalPages`로 (API Resource 변환)','필드 이름 camelCase','오류 응답을 `error.code/message/fields`로 (예외 핸들러)','OpenAPI 3와 실제 응답·인증을 대조했다.','버전 이름 v1과 기준 경로 /api를 구분했다.'],
['project/app/Http/Resources/EntryResource.php','project/app/Http/Resources/DocumentResource.php','project/bootstrap/app.php','project/app/Http/Middleware/RequestContext.php','project/resources/js/docs.js'],
'''cd project
php artisan route:list --path=api
php artisan test --compact --filter=ContractTest
curl.exe -i http://127.0.0.1:8001/openapi.json
# 전체 OpenAPI 원문: project/public/openapi.json (Git에 커밋됨)''')

lesson(15,'성능·캐시','캐시 무효화와 큐 작업을 적용하고 전후 지표로 효과를 측정한다.',
'''캐시는 비싼 계산 결과를 잠시 빌려 쓰는 메모장이고 큐는 오래 걸리는 일을 접수 후 처리하는 대기표다. `/api/stats`는 전체 글 수를 30초 기억하고 API 글 생성·삭제 후 무효화한다. Blade나 외부 SQL 변경은 즉시 무효화하지 않으므로 최대30초 지연이 허용되는 통계로만 쓴다. 권한 판정·결제 상태를 이 캐시에 의존시키지 않는다.

업로드는 202로 접수하고 SummarizeDocument job이 상태를 queued→processing→ready로 바꾼다. 실패하면 재시도하고 최종 실패는 failed로 기록한다. ShouldBeUnique와 documentId로 중복 작업을 제한한다. AI timeout90초 < job/worker100초 < retry_after150초 순서를 유지해 같은 작업이 동시에 재할당되지 않게 한다. 알림도 별도 큐 작업으로 전송한다.''',
'''1. /api/stats를 두 번 요청해 count 쿼리가 첫 요청에만 발생하는지 확인한다. 생성·삭제 뒤 total이 바뀌는 테스트를 실행한다.
2. notes·posts 목록이 user/tags/comments를 eager load하고 withCount로 댓글 개수를 가져오는지 확인한다. 반복문 안의 DB 조회는 N+1을 만든다.
3. QUEUE_CONNECTION=database와 DB_QUEUE_RETRY_AFTER=150을 설정하고 별도 터미널에서 queue:work를 실행한다. mock 요약으로 처리 상태와 알림을 확인한다.
4. 실패는 queue:failed, 로그, 문서 status로 확인하고 원인을 고친 뒤 queue:retry로 재시도한다. 성공 상태인 문서는 다시 요약하지 않는다.
5. 같은 데이터·동시성·워밍 조건에서 반복 측정한다. p50/p95 응답 시간, 요청당 SQL 수, 큐 대기 시간, AI 첫 토큰 시간을 비교한다. 숫자를 측정하지 않고 빨라졌다고 기록하지 않는다.
6. 상세 사용자 응답·문서 원문은 공용 캐시에 넣지 않는다. 서버를 늘리면 캐시와 큐 저장소를 공유해야 고유 잠금이 전 인스턴스에서 유효하다.''',
'큐는 문서 저장과 AI 호출의 응답 시간을 분리한다. 다음 운영 단계는 worker·scheduler를 웹 프로세스와 별도로 실행하고 같은 이미지·DB·파일 볼륨에 연결한다.',
[('문서가 queued에 머묾','worker가 실행되지 않음','queue:work와 DB jobs 테이블 확인'),('같은 작업이 중복됨','retry_after가 작업 timeout보다 짧음','90 < 100 < 150 순서를 적용하고 worker 재시작'),('변경 후 통계가 예전 값','캐시 무효화 누락 또는 다른 쓰기 경로','API 무효화·30초 TTL을 확인하고 일관성 요구 재설계')],
['AI 가짜 응답을 실패로 바꿔 재시도·failed 상태를 기록한다.','동일 조건에서 stats 첫 요청과 두 번째 요청 시간을 10회 측정한다.','with를 제거했을 때 SQL 수가 늘어나는지 실험 후 복원한다.'],
['캐시 TTL·키·무효화 범위를 설명했다.','작업·워커·retry_after 타임아웃 순서를 맞췄다.','N+1·SQL 수·응답 시간을 측정한다.','외부 호출 실패와 재시도를 검증했다.'],
['project/app/Services/LibraryStats.php','project/app/Jobs/SummarizeDocument.php','project/app/Notifications/DocumentReady.php'],
'''cd project
php artisan queue:work --tries=3 --timeout=100
# 별도 터미널
php artisan queue:failed
php artisan test --compact --filter=DocumentTest
curl.exe -w "time=%{time_total}" http://127.0.0.1:8001/api/stats''')

lesson(16,'운영·CI/CD','Docker 이미지·DB·워커를 연결하고 자동 검사·배포·백업 절차를 만든다.',
'''Docker 이미지는 실행에 필요한 파일·확장을 고정하는 상자이고 볼륨은 상자를 교체해도 남는 데이터 보관함이다. assets 단계는 Vue를 빌드하고 app 단계는 PHP-FPM과 런타임 의존성을 설치한다. web 단계는 같은 public 산출물을 Nginx에 넣는다. 최종 서재는 app/web/worker/scheduler와 PostgreSQL로 운영하고 Reverb는 realtime profile로 추가한다.

CI는 main push/PR에서 두 앱의 빌드·테스트·감사와 문서 정합성을 검사한다. DB 작업은 PostgreSQL·MariaDB에서도 같은 테스트를 실행한다. Deploy는 CI 성공 또는 수동 실행에서 DEPLOY_ENABLED=true일 때만 정확한 커밋 이미지 두 개를 GHCR에 올리고 서버로 배포한다. 서버 자격증명은 저장소 코드에 넣지 않는다.''',
'''1. Docker 엔진이 실행 중인지 docker info로 확인하고 app/web 대상을 각각 빌드한다. 현재 로컬 환경에서는 엔진이 꺼져 있으므로 컨테이너 실행 검증은 미완료다.
2. 서버의 /srv/laravel-study에 저장소와 compose.production.yaml을 준비한다. .env.production은 production.env.example을 복사해 실제 값으로 채우고 서버에서만 보관한다. APP_KEY·DB 암호는 비밀 저장소에서 주입한다.
3. IMAGE에 정확한 이미지 태그를 지정한다. 비공개 GHCR 패키지라면 서버에 읽기 전용 인증을 먼저 설정한다. DB·private-files 볼륨의 백업·소유권을 확인한다.
4. GitHub production 환경에 DEPLOY_SSH_KEY, DEPLOY_KNOWN_HOSTS, DEPLOY_TARGET을 설정한다. 호스트 키는 신뢰 경로로 확인하고 StrictHostKeyChecking을 끄지 않는다. DEPLOY_ENABLED 저장소 변수와 선택적 Reverb 공개 빌드값을 설정한다.
5. 배포는 image pull→migrate --force→서비스 교체→/health 점검 순서다. 새/구 버전이 공존해도 가능한 확장형 스키마 변경을 사용한다. worker는 새 컨테이너로 교체한다.
6. 로그는 stderr로 모으고 5xx 비율·지연·DB 연결·큐 backlog·디스크 사용량·업로드 실패율을 모니터링한다. requestId로 요청과 오류를 연결한다.
7. backup.ps1은 PostgreSQL dump와 비공개 파일 tar를 복사한다. APP_KEY는 별도로 보관한다. 다른 디렉터리/서버에 암호화해 복제하고 보관 기간을 정한다.
8. 복원은 먼저 격리 DB와 빈 파일 볼륨에서 한다. pg_restore 대신 plain SQL에는 psql을 사용한다. 기록 건수·소유권·파일 해시·로그인·요약을 확인한 뒤 전환한다. 운영 DB를 바로 덮어쓰지 않는다.''',
'배포된 웹·워커는 같은 환경변수·DB·private-files를 사용한다. HTTPS는 호스트의 Caddy/Nginx에서 8088로 역방향 프록시하고 실시간은 8080에 별도 wss 호스트를 연결한다. 다음 단계의 Reverb도 같은 인증·권한 규칙을 사용한다.',
[('Docker daemon 연결 실패','Desktop/엔진이 꺼짐','Docker 실행 후 docker info 확인'),('worker에서 파일 없음','app과 worker의 private-files 볼륨이 다름','동일 named volume 마운트 확인'),('자동 배포가 실행 안 됨','DEPLOY_ENABLED·CI 결과·production 환경 미설정','Actions 조건과 저장소 변수·비밀값을 확인')],
['compose config로 변수·볼륨·서비스 구성을 검증한다.','격리 DB에 백업을 복원해 사용자·문서·파일 수를 대조한다.','실패한 health 점검에서 이전 이미지로 원복할 명령을 적는다.'],
['Docker app/web 이미지 빌드·헬스를 실제 실행해 기록한다.','CI 빌드·SQLite·PostgreSQL·MariaDB 결과를 확인한다.','운영 비밀값과 HTTPS·호스트 키를 설정한다.','로그·큐·디스크 경보 기준을 정한다.','DB·파일·APP_KEY 백업과 격리 복원 시험을 수행한다.','데이터를 지우는 down -v를 운영에서 실행하지 않는다.'],
['project/Dockerfile','compose.production.yaml','.github/workflows/ci.yml','.github/workflows/deploy.yml','tools/backup.ps1'],
'''docker build -f project/Dockerfile --target app -t study-app project
docker build -f project/Dockerfile --target web -t study-web project
# 운영 서버: IMAGE에 -app/-web 접미사 직전까지의 태그 설정
$env:IMAGE="ghcr.io/OWNER/my_laravel_study:COMMIT_SHA"
docker compose -f compose.production.yaml config --quiet
docker compose -f compose.production.yaml pull
docker compose -f compose.production.yaml run --rm app php artisan migrate --force
docker compose -f compose.production.yaml up -d
curl.exe -f http://127.0.0.1:8088/health
powershell -File tools/backup.ps1''')

lesson(17,'실시간·확장','Reverb 비공개 채널로 문서 완료 알림을 보내고 파일 접근을 제한한다.',
'''웹소켓은 연결을 유지하며 서버 사건을 브라우저에 전달한다. SSE는 서버→브라우저의 단방향 스트림이고 웹소켓은 양방향 채널이다. 안내 방송을 계속 듣는 창과 양방향 통화의 차이다. 문서 완료 알림에는 Laravel Notification→broadcast→Reverb→Echo 경로를 사용한다. AI 답변은 study18의 SSE로 별도 처리한다.

공개 채널에 사용자 문서 정보를 보내지 않는다. private-App.Models.User.{id} 채널은 Sanctum 인증 뒤 본인 id만 허용한다. Echo는 /api/broadcasting/auth에 Bearer를 보내 서명받는다. 공개 키는 브라우저에 주입해도 되지만 Reverb secret은 서버에만 둔다. 기본 앱은 log broadcaster이며 실제 소켓은 환경변수 전환 후 실행한다.''',
'''1. project의 .env에 Reverb id/key/secret, host/port/scheme와 허용 origin을 설정한다. BROADCAST_CONNECTION=reverb로 바꾸고 캐시·워커를 다시 시작한다.
2. VITE_REVERB_APP_KEY/HOST/PORT/SCHEME는 브라우저에서 접근 가능한 주소를 지정한다. Docker 내부 reverb 서비스명은 브라우저 주소로 쓰지 않는다.
3. PHP 서버, queue:work, reverb:start를 각각 실행하고 Vue에 로그인한다. Echo가 본인의 private 채널을 구독한다.
4. 문서를 올리고 worker가 요약을 완료하면 DocumentReady가 database/mail/broadcast로 전달된다. 화면은 알림을 받고 본인 문서·알림 목록을 다시 조회한다.
5. 다른 사용자 채널 인증이 403인 테스트를 확인한다. 로그아웃·컴포넌트 해제 시 disconnect한다.
6. 파일 다운로드와 삭제는 owned 검사 뒤 수행한다. 업로드 원본을 public/storage로 링크하지 않는다. 삭제는 질문 이력도 FK cascade로 정리한다.
7. 운영은 wss와 허용 origin, 프록시 Upgrade/Connection 헤더, 연결 수·큐 지연·재연결을 점검한다. 로컬에서는 소켓 서버 실제 연결과 수신을 별도 검증한다.''',
'큐 요약 완료가 실시간 사건이 되고 Vue는 서버의 최신 상태를 다시 읽는다. 다음 AI 단계는 같은 문서 소유권을 유지하며 SSE로 답변 텍스트를 전달하고 MCP 읽기 도구도 연결한다.',
[('웹소켓 연결 거부','reverb 서버·포트·키 불일치','서버 실행과 VITE 빌드값·브라우저 주소 확인'),('채널 인증 403','다른 사용자 id 또는 토큰 누락','본인 private 채널과 Bearer 헤더 확인'),('로컬은 되는데 HTTPS에서 실패','ws 혼합 콘텐츠 또는 프록시 업그레이드 누락','wss·공개 호스트·Upgrade 헤더 설정')],
['두 사용자로 로그인해 상대 채널 인증이 거부되는지 확인한다.','Reverb를 끊고 수동 새로고침으로 문서 상태가 여전히 보이는지 확인한다.','문서 삭제 뒤 원본 파일·질문 이력이 정리되는지 확인한다.'],
['웹소켓과 SSE의 역할을 구분했다.','private 채널에 Sanctum과 본인 id 검사를 적용했다.','본인 파일만 다운로드·삭제할 수 있다.','실제 Reverb 수신·재연결 결과를 기록한다.'],
['project/resources/js/realtime.js','project/routes/channels.php','project/app/Notifications/DocumentReady.php','project/config/reverb.php'],
'''cd project
php artisan config:clear
php artisan reverb:start --host=127.0.0.1 --port=8080
# 다른 터미널: php artisan queue:work --tries=3 --timeout=100
# VITE_ 값을 바꿨으면 npm run build 또는 dev 서버 재시작
php artisan test --compact --filter=private_broadcast_channel''')

lesson(18,'AI 연동·MCP','문서 근거 질문·진짜 토큰 스트리밍·인증된 MCP 읽기 도구를 연결한다.',
'''이 단계는 노션 DocuForge의 문서 업로드→요약→근거 질문→히스토리라는 학습 목적을 Laravel 안에서 구현한다. 기존 프로젝트의 다른 서버를 연결하지 않는다. 이 예제는 UTF-8 TXT/MD와 어휘 기반 청크 검색으로 범위를 정했으며 PDF/DOCX/PPTX 추출·OCR·임베딩 인덱스는 구현하지 않았다.

문서를 600자 청크로 나누고 100자 겹침을 유지하며 질문 단어 점수로 최대3개 발췌를 고른다. 프롬프트는 system 규칙과 JSON 자료를 분리하고 문서 속 명령을 따르지 않도록 한다. 근거가 없으면 모델을 호출하지 않고 찾을 수 없다고 응답한다. 이는 사전식 검색 기반 RAG 미니 예제이며 의미 검색 품질을 보장하지 않는다.

AI_DRIVER=mock은 외부 모델 없이 [mock 실습] 발췌를 보여 준다. 실제 모델은 ollama 드라이버가 /api/chat의 NDJSON을 읽어 SSE delta로 전달한다. provider 응답을 다 받은 뒤 글자를 잘라 스트리밍인 것처럼 보이지 않도록 실제 스트림을 중계한다. 출력은 최대20KB, 모델 예측은512토큰, 연결5초·전체90초로 제한한다.

MCP는 모델·호스트가 사용할 도구 이름·입력 스키마·호출 결과를 주고받는 규약이다. REST 게시판 API와 별개 프로토콜이다. LibraryServer는 read-document 도구를 노출하고 소유한 문서만 최대4000자 읽는다. 클라이언트는 initialize(연결 협상)→tools/list→tools/call 흐름으로 서버를 사용한다. 이 예제의 MCP 클라이언트는 Laravel MCP Client이며 외부 호스트 제품을 설정하지 않아도 명령으로 검증할 수 있다.''',
'''1. 기본 mock으로 가입→TXT/MD 업로드→worker 요약→문서 선택→질문→이력 저장을 실행한다. 본인 문서만 목록과 도구에 나타나야 한다.
2. 실제 Ollama를 로컬에서 실행하고 gemma4:12b를 준비한다. 장비에 맞는 모델을 AI_MODEL로 바꿔도 된다. AI_DRIVER=ollama, AI_URL을 설정하고 PHP·worker를 다시 시작한다. 키가 필요한 다른 공급자를 임의로 호출하지 않는다.
3. DocumentAi의 system 규칙·근거 발췌·질문 JSON을 읽는다. 근거 번호는 검색 순위가 아니라 원래 청크 번호다. 모델 출력은 신뢰할 수 없는 텍스트로 표시하며 v-html을 쓰지 않는다.
4. DocumentController의 SSE는 delta 이벤트, done/sources/driver 또는 error 이벤트를 보낸다. 스트림 시작 뒤 실패는 HTTP 상태를 바꿀 수 없으므로 error 이벤트로 표시하고 불완전한 답변은 이력에 저장하지 않는다.
5. Vue의 TextDecoder는 chunk 경계의 한글 바이트를 보존한다. Nginx fastcgi_buffering off와 X-Accel-Buffering:no를 맞춰야 첫 토큰부터 보인다.
6. /mcp/library는 auth:sanctum과 분당 제한을 적용한다. MCP_TOOL의 사용자 입력 id를 검증하고 user_id 조건을 쿼리에 함께 넣는다. 임의 파일 경로·셸·SQL 도구를 노출하지 않는다.
7. 별도 HTTP 서버를 켜고 MCP_TOKEN을 셸 환경에만 넣어 study:mcp-read id를 실행한다. 토큰을 명령 인수·Git·문서에 기록하지 않는다. Laravel Client가 협상을 처리한다. 단일 스레드 개발 서버에서 웹 요청이 자기 자신을 다시 부르는 구조는 피한다.
8. DocumentTest는 NDJSON 분할·연결 실패·소유권·MCP 호출을 fake/실제 테스트 DB로 검증한다. 실제 Ollama 생성과 검색 품질은 모델이 준비된 환경에서 별도로 기록한다.''',
'노션 DocuForge에서 가져온 것은 요약·근거·히스토리라는 학습 요구다. 최종 문서는 이 기능을 기존 서재·DB 교체·큐·보안·Docker·배포에 함께 연결한다. 다른 백엔드나 AI 서버 프레임워크를 추가하지 않는다.',
[('mock만 나옴','AI_DRIVER 기본값이 mock','실제 Ollama 실행 후 .env 전환과 프로세스 재시작'),('답변이 마지막에 한꺼번에 보임','프록시·FastCGI 버퍼링','스트리밍 헤더와 Nginx 버퍼 설정 확인'),('HTTP 200인데 AI 실패','SSE 시작 뒤 provider 연결 실패','error 이벤트를 표시하고 이력 미저장을 확인'),('MCP Document not found','소유하지 않은 id 또는 없는 문서','본인 문서 id로 재요청; 권한 검사 우회 금지')],
['문서에 없는 질문을 보내 근거 없음 응답을 확인한다.','문서 안에 이전 명령 무시 문장을 넣어 근거 자료로만 취급되는지 평가한다.','본인·다른 회원 토큰으로 같은 MCP id를 호출해 결과를 비교한다.'],
['DocuForge 문서 요약·근거 질문·히스토리를 Laravel에 연결했다.','mock과 실제 모델 검증을 구분했다.','NDJSON→SSE→Vue 스트리밍과 실패를 처리했다.','MCP 서버·스키마·클라이언트·소유권을 확인했다.','모델 출력과 문서 입력을 신뢰하지 않는다.'],
['project/app/Services/DocumentAi.php','project/app/Http/Controllers/Api/DocumentController.php','project/app/Mcp/Servers/LibraryServer.php','project/app/Mcp/Tools/ReadDocument.php','project/routes/ai.php','project/app/Console/Commands/McpRead.php'],
'''# 실제 모델 실험 (설치된 Ollama가 있을 때)
ollama pull gemma4:12b
# project/.env: AI_DRIVER=ollama, AI_URL=http://127.0.0.1:11434
cd project
php artisan config:clear
php artisan serve --host=127.0.0.1 --port=8001
# 별도 터미널에서 MCP_TOKEN 환경변수를 안전하게 설정한 뒤
php artisan study:mcp-read 1
php artisan test --compact --filter=DocumentTest''')

lesson('Final','심화 응용 · AI 학습 서재','중간 게시판의 인증·CRUD에 DB 교체·외부 서비스·AI·운영을 결합한 서재를 완성한다.',
'''### 기능 목록

- User·Note·Tag·note_tag와 댓글, Blade와 Vue CRUD, 검색·페이지·작성자 권한
- 공통 /api 계약·camelCase·오류 봉투·OpenAPI·요청 추적 id
- SQLite 기본 실행, PostgreSQL/MariaDB 전환 절차와 CI, Mongo 보관 모델 선택 예제
- 비공개 TXT/MD 업로드·다운로드·삭제, 큐 요약·질문 이력·메일·알림
- Ollama API·근거 발췌·SSE·인증된 MCP 읽기 서버와 클라이언트
- Stripe 테스트 Checkout·서명 수신 영수증, GitHub OAuth Blade 세션
- Docker app/web/worker/scheduler, GitHub Actions, 볼륨·DB·키 백업과 격리 복원 절차

### 연동 구성도

```mermaid
flowchart TD
    U[브라우저 Vue 또는 Blade] --> N[Nginx HTTPS 프록시]
    N --> L[Laravel: API / Policy / Resource]
    L --> D[(PostgreSQL 또는 MariaDB)]
    L --> F[비공개 파일 볼륨]
    L --> Q[DB 큐]
    Q --> W[Laravel worker]
    W --> A[Ollama 모델 API]
    W --> M[메일 / DB 알림 / Reverb]
    L --> S[Stripe 테스트 API / GitHub OAuth]
    L --> E[SSE 답변]
    E --> U
    M --> U
    C[MCP Client] --> T[인증된 Laravel MCP]
    T --> D
```

Laravel이 인증·데이터·외부 호출·AI 중계를 담당하고 Vue는 같은 앱의 화면이다. DB와 모델 공급자는 연결 대상이며 별도 백엔드 프레임워크를 두지 않는다.''',
'''### 구현 순서

1. midpoint의 요청·검증·소유권·테스트 흐름을 확인한다. project의 Note·Tag와 다대다 관계로 주제를 서재로 확장한다.
2. study11의 DB 연결을 선택한다. 원본 DB를 보존하고 마이그레이션·데이터 이전·건수·FK·원복을 검증한다. Mongo는 선택 보관 실험으로 분리한다.
3. study12·14의 Vue와 공통 API를 맞추고 OpenAPI에서 요청·응답을 대조한다.
4. study13의 파일·메일·OAuth·테스트 결제를 설정한다. 결제 영수증 수신과 실제 유료 권한 부여를 구분한다.
5. study15의 큐·고유 job·타임아웃·캐시 무효화를 적용한다. study17에서 private 알림과 파일 소유권을 검증한다.
6. study18의 mock 흐름부터 완주한 뒤 실제 Ollama로 전환하고 근거 없는 질문·주입 문서·연결 중단을 평가한다. MCP도 같은 소유권을 적용한다.
7. study16의 Docker 이미지·환경변수·DB·파일 볼륨을 연결한다. CI 성공 후 배포 비밀값을 설정한 환경에서 자동 배포한다.
8. 전체 테스트·빌드·의존성 감사를 실행하고 배포 후 기능·보안·로그·백업 복원을 검수한다.

전체 소스는 project에 있으며 아래에는 최종 조립의 핵심 파일을 전문으로 수록한다. AI·외부 연동·배포 코드 전문은 study13·16·17·18에서 연결해 읽는다.''',
'DB 연결을 바꿔도 브라우저 계약은 유지하고, 워커는 웹과 같은 DB·파일 볼륨을 사용한다. AI·MCP는 문서 소유권 경계 안에서만 데이터를 읽는다. 기능별 실측·외부 연결 결과는 docs/verification.md에 추가하고 실제 확인 전에는 완료로 표시하지 않는다.',
[('웹은 되는데 요약이 안 됨','worker·AI_URL·공유 파일 볼륨 문제','각 프로세스 로그와 동일 환경변수·볼륨 확인'),('배포 후 세션이 풀림','APP_KEY 변경 또는 다른 DB/세션 저장소','키·세션 저장소의 영속성과 일치 확인'),('DB 교체 후 일부 기능 실패','미이전 데이터·드라이버별 SQL·FK 차이','동일 계약 테스트·건수·관계·문자열 검색 검증')],
['새 회원으로 글·태그·댓글·문서·질문·삭제까지 한 번의 사용자 시나리오를 실행한다.','AI와 메일을 실패시킨 뒤 UI·큐·로그·재시도 결과를 기록한다.','격리 복원 환경에서 DB·원본 파일·APP_KEY를 복원하고 소유권을 검수한다.'],
['배포: PHP·Vue 빌드·전체 테스트·보안 감사를 통과했다.','배포: 실제 SQL DB 전환·데이터 이전·원복을 검증한다.','배포: 외부 결제 테스트·SMTP·OAuth 공급자 왕복을 검증한다.','배포: 실제 AI·Reverb·MCP 클라이언트 연결 결과를 기록한다.','배포: Docker·CI 결과·HTTPS·비밀값·볼륨을 검증한다.','배포: 401/403/404·CSRF·XSS·소유권·제한·웹훅 검사를 수행한다.','배포: 백업 격리 복원·이전 이미지 원복·로그 경보를 확인한다.'],
['project/routes/api.php','project/app/Models/Note.php','project/app/Http/Controllers/Api/ContractController.php','project/app/Jobs/SummarizeDocument.php','compose.production.yaml'],
'''cd project
composer install
npm ci
php artisan migrate
# 로컬 연습에서만: php artisan db:seed
npm run build
php artisan test --compact
composer audit
npm audit --omit=dev
php artisan serve --host=127.0.0.1 --port=8001
# 별도 터미널: php artisan queue:work --tries=3 --timeout=100
# 최종 화면: http://127.0.0.1:8001/app''',
'''### 최종 회고

1. **해결한 문제:** 분리된 화면 실습을 Laravel 안의 Vue 화면으로 모으고, 노션에 남아 있던 API 계약의 차이를 Resource·예외 처리·테스트로 고정했다.
2. **설계 근거:** 공개 학습 노트와 비공개 업로드 문서를 구분하고, 긴 AI 작업은 큐로 분리했다. MCP도 소유권 쿼리를 통과한다.
3. **검증의 범위:** 로컬 SQLite 요청·단위·보안 테스트, 빌드·패키지 감사·구성 검사를 수행한다. Docker/DB 서버·외부 계정·실모델·원격 배포는 준비된 환경의 실행 기록이 필요하다.
4. **다음 개선:** 실제 모델의 한국어 검색 품질 평가, 선택적 문서 형식 추출, 결제 권한 상태 머신, 비밀번호 재설정·이메일 인증·MFA, 복원 훈련을 요구에 따라 확장한다. 미구현 항목을 완료로 기록하지 않는다.

### 노션 추가 체크 항목 반영에서 빠진 것

없음. Laravel 원문의 추가 체크 5개와 선택 프론트 목표는 study6·12·14에 원문 그대로 배치했다. 원문의 타 프레임워크 비교·조합 방향은 사용자의 이번 지시에 따라 학습 범위에서 제외했다. 실행 환경이 없어 미검증인 항목은 체크리스트에 남겼으며 누락과 구분한다.''')
