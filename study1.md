# study1 · Hello World와 기본 문법

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

라우트에서 Blade로 데이터를 전달하고 첫 화면을 렌더링한다.

## ② 📖 이론

요청은 `public/index.php → bootstrap/app.php → 라우트 → 컨트롤러 → 뷰 → 응답`을 지난다. 식당에 비유하면 라우트는 메뉴 번호, 컨트롤러는 주문 담당자, Blade는 완성된 접시다. PHP 변수는 `$greeting`, 배열은 `['라우트', 'Blade']`, 객체 접근은 `->`를 쓴다. `return`은 결과를 호출자에게 돌려준다.

Blade의 `{{ $greeting }}`은 HTML을 이스케이프한다. `@foreach`는 반복, `$loop->iteration`은 1부터 시작하는 순서, `@if`는 조건이다. `@extends`는 공통 레이아웃을 선택하고 `@section`은 채울 부분을 지정한다. Vue의 `{{ value }}`는 브라우저 반응형 상태를 출력한다. Blade와 Vue 템플릿은 각각 `.blade.php`, `.vue`로 분리해 같은 중괄호를 서로 해석하지 않게 한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. `demo`에서 서버를 실행하고 `/`를 연다. `Hello Laravel`과 기본 단위 목록이 보이는지 확인한다.
2. `HomeController`의 greeting 문자열을 바꾸고 저장한다. Blade를 감시하는 Vite 개발 서버가 실행 중이면 브라우저가 새로고침된다. PHP 클래스의 동작 자체는 다음 요청에서 반영된다.
3. 아래 전체 컨트롤러와 뷰를 짝으로 읽는다. 값의 이름을 바꾸면 전달 배열의 키와 뷰의 변수도 함께 바꿔야 한다.
4. 개발자도구 Network에서 문서 응답 200과 HTML 본문을 확인하고 Console에서 Vite 연결 오류를 확인한다. Elements의 HTML은 서버가 만든 결과다.

### 실행 명령

```powershell
cd demo
php artisan serve --host=127.0.0.1 --port=8000
# 별도 터미널에서 cd demo 후 npm run dev
curl.exe -i http://127.0.0.1:8000/
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `demo/app/Http/Controllers/HomeController.php` 전체 코드

[demo/app/Http/Controllers/HomeController.php](demo/app/Http/Controllers/HomeController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers;

class HomeController extends Controller
{
    public function index()
    {
        return view('home', ['greeting' => 'Hello Laravel', 'topics' => ['라우트', '컨트롤러', 'Blade']]);
    }
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 6 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 7 | `index` 메서드를 선언한다. 목록을 조회해 응답으로 반환하는 진입점이다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 10 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 11 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/resources/views/home.blade.php` 전체 코드

[demo/resources/views/home.blade.php](demo/resources/views/home.blade.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```blade
@extends('layouts.app')

@section('title', '첫 화면')

@section('content')
    <section class="hero">
        <p class="eyebrow">study1 · Blade</p>
        <p>{{ $greeting }}</p>
        <ul>@foreach ($topics as $topic)<li>{{ $loop->iteration }}. {{ $topic }}</li>@endforeach</ul>
        <p><a href="{{ route('workspace') }}">Vue 게시판 열기</a></p>
        <h1>Laravel 게시판을 이 폴더에서 만듭니다.</h1>
        <p>라우트 <code>home</code>이 <code>HomeController</code>의 <code>index</code>를 고르고, 액션은 이 Blade를 반환합니다. 시간대는 <code>Asia/Seoul</code>, 로캘은 <code>ko</code>입니다.</p>
        <p>프레임워크 헬스 체크는 <a href="{{ url('/up') }}">/up</a> 입니다.</p>
    </section>
@endsection
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 공통 Blade 레이아웃을 부모로 선택한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 레이아웃의 지정 영역에 이 뷰 내용을 채운다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 레이아웃의 지정 영역에 이 뷰 내용을 채운다. |
| 6 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 7 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 8 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 9 | 서버에서 전달받은 목록을 반복해 이스케이프한 HTML을 만든다. |
| 10 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 11 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 12 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 13 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 14 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 15 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |


## ④ 🔗 연동 포인트

컨트롤러가 전달하는 배열은 다음 단계 MVC의 데이터 계약이다. `/app` 링크는 같은 Laravel이 제공하는 Vue 화면으로 이동한다. Vite의 자산 주소와 API 주소는 다르며 API 상대 경로 `/api/posts`는 PHP 서버를 가리킨다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| Undefined variable | 뷰에 전달한 키와 변수명이 다름 | 컨트롤러 배열의 greeting/topics 키 확인 |
| 변경해도 화면 유지 | 개발 서버 미실행 또는 오래된 빌드 | npm run dev 실행; 배포에서는 npm run build |
| View not found | 뷰 경로와 점 표기 불일치 | home은 resources/views/home.blade.php인지 확인 |

## ⑥ 직접 해보기

1. topics에 새로운 핵심 용어를 하나 추가한다.
2. greeting에 <b>안녕</b>를 넣어 태그가 실행되지 않는 것을 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 첫 화면에서 Hello Laravel을 확인했다.
- [ ] Blade 변수·반복·레이아웃을 설명할 수 있다.
- [ ] Network의 200과 Console을 확인했다.

## ⑧ 다음 단계 연결

라우트에서 Blade로 데이터를 전달하고 첫 화면을 렌더링한다. 이 결과를 [study2.md](study2.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/blade)
