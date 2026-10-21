# study0. Laravel 기초이론

Notion 페이지 [Laravel](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf)의 방향은 이렇습니다. PHP 기반 풀스택이고, Blade 템플릿과 Eloquent ORM, 인증이 한 세트로 있습니다. 같은 게시판을 Django, Rails와 다시 만들어 비교합니다.

이 문서는 명령을 치기 전에 지도를 그리는 단계입니다. 코드는 다음 문서부터 `demo/`에 쌓입니다.

## 1. Laravel란?

Laravel은 PHP로 웹 애플리케이션을 만드는 풀스택 프레임워크입니다. 라우팅, ORM, 템플릿, 마이그레이션, 큐, 테스트, 보안 기본값이 한 프로젝트에 들어 있습니다.

두 문장이 이 과정의 중심입니다.

- **Eloquent는 테이블 한 줄을 PHP 객체로 다룬다.** `Post::create(...)`는 INSERT이고, `Post::find(1)`은 SELECT입니다. Rails의 Active Record, Django ORM과 같은 자리입니다.
- **Blade는 서버가 HTML을 만들어 보낸다.** 브라우저가 먼저 빈 껍데기를 받고 JavaScript로 화면을 그리지 않습니다. 로그인한 작성 화면까지 서버 템플릿으로 갈 수 있습니다.

요청 하나는 이렇게 흐릅니다.

```
브라우저
  → public/index.php
  → HTTP 커널과 미들웨어 (세션, CSRF, 인증)
  → routes/web.php 또는 routes/api.php
  → 컨트롤러
  → Eloquent 모델 (필요하면 SQLite)
  → Blade 뷰 또는 JSON
  → HTTP 응답
```

`routes/web.php`의 `GET /posts/{post}`는 `PostController@show`로 가고, 그 액션이 `resources/views/posts/show.blade.php`를 고릅니다. URL과 파일을 약속으로 묶는 점은 Rails의 `resources :posts`, Django의 URLconf와 같습니다. 문법이 PHP인 점이 다릅니다.

## 2. MVC와 Django, Rails

| 관심사 | Laravel | Django | Rails |
|---|---|---|---|
| 언어 | PHP | Python | Ruby |
| 구조 | MVC | MTV | MVC |
| 화면 | Blade | Django 템플릿 | ERB |
| ORM | Eloquent | Django ORM | Active Record |
| 스키마 변경 | 마이그레이션 | 마이그레이션 | 마이그레이션 |
| CRUD 시작 | `make:model -mcr` 또는 리소스 컨트롤러 | 제네릭 뷰 + 폼 | `rails generate scaffold` |
| 관리 화면 | 없음. 필요하면 Filament 등을 추가 | Admin이 기본 포함 | 없음 |
| 인증 꾸러미 | Breeze, Jetstream, Fortify, 또는 직접 | `django.contrib.auth` | Devise 또는 직접 |
| API 토큰 | Sanctum | DRF + 토큰/세션 | JWT 젬 또는 직접 |

이름이 겹치는 지점이 하나 있습니다. Django의 View는 Laravel의 Controller에 가깝습니다. Django의 Template이 Laravel의 View(Blade)입니다.

이 저장소의 `demo/`는 게시판입니다. 글, 댓글, 세션 로그인, JSON API까지 가서 Django 게시판, Rails 게시판과 같은 기능을 나란히 볼 수 있게 합니다. `project/`는 그 재료로 다시 만든 작은 웹사이트이고, 주소와 모델 이름이 게시판과 다릅니다.

## 3. 라우팅, 컨트롤러, 뷰

Laravel 11부터 라우트 등록은 `bootstrap/app.php`의 `withRouting()`에 있습니다. 웹 화면은 `routes/web.php`, 콘솔은 `routes/console.php`, 헬스 체크는 기본으로 `/up`입니다. API 파일을 쓰면 `routes/api.php`를 같은 곳에 연결합니다. API 주소에는 `/api` 접두사가 붙습니다.

웹 라우트 그룹은 `web` 미들웨어를 탑니다. 여기에는 쿠키 세션, CSRF 검증, 에러 공유가 들어 있습니다. Blade 폼은 `@csrf` 한 줄로 토큰을 넣습니다. API 라우트 그룹은 세션과 CSRF를 기본으로 타지 않습니다. 상태를 실으려면 토큰을 헤더로 보냅니다. 이 과정에서는 Sanctum의 Bearer 토큰을 씁니다.

컨트롤러는 `app/Http/Controllers`에 둡니다. 리소스 컨트롤러의 액션 이름은 REST를 따릅니다.

| 액션 | HTTP | 경로 예 | 하는 일 |
|---|---|---|---|
| index | GET | /posts | 목록 |
| show | GET | /posts/{post} | 한 건 |
| create | GET | /posts/create | 작성 폼 |
| store | POST | /posts | 저장 |
| edit | GET | /posts/{post}/edit | 수정 폼 |
| update | PUT/PATCH | /posts/{post} | 수정 반영 |
| destroy | DELETE | /posts/{post} | 삭제 |

`Route::resource('posts', PostController::class)`가 이 일곱 줄을 만듭니다. `{post}`는 숫자 id로 `Post` 모델을 찾아 액션 인자에 넣습니다. 이 주입을 라우트 모델 바인딩이라고 부릅니다. Rails의 `params[:id]`로 `Post.find`를 직접 하는 자리와 같습니다.

## 4. Eloquent와 마이그레이션

스키마는 모델 클래스에 적지 않습니다. `database/migrations`의 마이그레이션이 테이블을 만들고, `php artisan migrate`가 적용합니다. 파일 이름 앞의 시각이 순서입니다. 이미 적용한 파일을 고치는 대신 새 마이그레이션을 추가하는 것이 약속입니다. 적용 결과는 SQLite 파일에 남고, `database/migrations` 테이블이 어디까지 돌았는지 기억합니다.

관계는 메서드로 선언합니다.

```php
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}

public function comments(): HasMany
{
    return $this->hasMany(Comment::class);
}
```

`belongsTo(User::class)`는 `posts.user_id`가 있다는 약속입니다. 외래 키 이름은 모델의 단수형에 `_id`를 붙입니다. Rails의 `belongs_to :user`와 같고, Django의 `ForeignKey`와 같은 일을 합니다.

대량 할당을 허용할 컬럼은 모델의 `#[Fillable([...])]`에 적습니다. 요청에 `is_admin` 같은 키가 섞여도 fillable 밖이면 버려집니다. Rails의 Strong Parameters와 같은 방어입니다. 이 저장소는 그에 더해 컨트롤러에서 `$request->validate()`로 형식을 먼저 검사합니다.

## 5. Blade와 JSON API

Blade 파일은 `resources/views`에 있고 확장자는 `.blade.php`입니다. `{{ $post->title }}`는 HTML을 이스케이프합니다. `{!! $html !!}`는 이스케이프하지 않으므로 학습 중에는 쓰지 않습니다. 레이아웃은 `@extends`와 `@section`, 또는 컴포넌트로 나눕니다. 이 과정은 `@extends('layouts.app')` 한 가지로 통일합니다.

같은 `Post` 모델을 두 출구로 내보냅니다.

- 웹: `PostController`가 Blade를 렌더합니다. 인증은 세션 쿠키입니다.
- API: `Api\V1\PostController`가 `PostResource`로 JSON을 만듭니다. 인증은 Sanctum 토큰입니다.

Notion의 "Blade 템플릿 또는 API (Sanctum)"는 둘 중 하나를 고르라는 뜻이 아니라, 한 데이터를 화면과 API로 나눌 수 있다는 뜻으로 실습합니다. 목록의 검색과 페이지는 두 출구가 같은 쿼리를 씁니다.

Vue, React, Svelte를 Laravel 안에 섞는 방법(Inertia, Breeze의 React/Vue 스택)도 있습니다. 그 선택은 이 저장소에서 하지 않습니다. 대신 `js/`, `ts/`가 Laravel 코드를 수정하지 않고 JSON API만 부릅니다. 프레임워크 화면을 붙이고 싶으면 그 API를 그대로 호출하면 됩니다.

## 6. 인증 세 갈래

Notion 학습 목표는 "Breeze / Jetstream / 직접"입니다.

| 이름 | 정체 | 이 과정에서 |
|---|---|---|
| 직접 | `Auth::attempt`, 세션, `Hash` | study5에서 구현 |
| Breeze | 로그인 화면과 라우트를 얇게 생성. Blade, React, Vue 중 선택 | 직접 구현과 1:1로 대응만 설명 |
| Jetstream | 팀, 2단계 인증, 프로필까지 포함한 스타터 | 범위 밖. 이름과 차이만 적음 |
| Fortify | 화면 없이 인증 백엔드만 제공 | Breeze가 내부에서 쓰는 층 |
| Sanctum | SPA 쿠키 또는 API 토큰 | study9에서 토큰만 사용 |

직접 구현으로 보는 이유는 Breeze가 숨기는 `session()->regenerate()`, 비밀번호 `hashed` 캐스트, `auth` 미들웨어를 먼저 읽기 위해서입니다. 세션 로그인과 Sanctum 토큰은 공존합니다. Blade는 쿠키를 쓰고, `js/`와 `ts/`는 `Authorization: Bearer`를 씁니다.

## 7. 디렉터리 지도

`composer create-project laravel/laravel`이 만드는 트리에서 이 과정이 자주 여는 곳입니다.

```
demo/
├── app/
│   ├── Http/Controllers/     # 웹, API 컨트롤러
│   ├── Http/Requests/        # 검증
│   ├── Models/               # Eloquent
│   └── Policies/             # 작성자 권한
├── bootstrap/app.php         # 라우트, 미들웨어, 예외
├── database/migrations/      # 스키마 변경
├── resources/views/          # Blade
├── routes/web.php            # 화면 URL
├── routes/api.php            # /api URL (study6에서 연결)
├── tests/Feature/            # HTTP 테스트
└── artisan                   # 서버, 생성기, 마이그레이션 진입점
```

저장소 루트는 이렇게 나뉩니다.

| 폴더 | 하는 일 |
|---|---|
| `demo/` | study1~10이 쌓인 Laravel 앱 |
| `project/` | studyFinal 작은 웹사이트. 모델과 URL이 demo와 다름 |
| `js/demo`, `ts/demo` | demo API를 각자 호출 |
| `js/project`, `ts/project` | project API를 각자 호출 |

JS와 TS는 의존성을 공유하지 않습니다. 한쪽에서 `npm install`을 해도 다른 쪽은 그대로입니다.

## 8. 로드맵

| 문서 | 내용 | Notion 학습 목표 |
|---|---|---|
| study0 | 기초이론 | 선행 지도 |
| study1 | 설치, `composer create-project`, 명령어, 첫 화면 | Laravel 프로젝트 |
| study2 | Post 모델과 마이그레이션 | Eloquent 모델 + 마이그레이션 |
| study3 | 리소스 라우트, 컨트롤러, Blade CRUD | 라우팅 / 컨트롤러 / 뷰, 게시판 CRUD |
| study4 | 댓글 `hasMany` / `belongsTo` | 모델 관계 |
| study5 | 세션 로그인, 작성자만 수정 | 인증 (직접, Breeze와 비교) |
| study6 | 게시글 JSON API | Blade와 API |
| study7 | 중첩 댓글 API | API |
| study8 | 검색, 페이지, Policy | API를 목록 화면에서 쓸 준비 |
| study9 | Sanctum 토큰 | Sanctum |
| study10 | CORS, JS/TS 화면 | 프론트를 따로 붙이기 |
| studyFinal | 학습 서재 | 지금까지의 응용 |

## 9. 실습 전에 기억할 것

- `.env`의 `APP_KEY`는 쿠키와 암호 값을 암호화합니다. Git에 올리지 않습니다. 클론한 뒤에는 `php artisan key:generate`를 합니다.
- SQLite 파일(`database/database.sqlite`)도 커밋하지 않습니다. `php artisan migrate`가 다시 만듭니다.
- `vendor/`는 `composer install`로 다시 받습니다.
- 확인은 Feature 테스트와 브라우저 주소로 합니다. 각 문서의 검증 절은 그 실행 결과만 적습니다.

다음 문서는 [study1.md](study1.md)입니다. PHP와 Composer로 `demo/`를 만들고 첫 화면을 띄웁니다.
