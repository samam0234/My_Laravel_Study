# study2 · 핵심 구조

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

라우트·컨트롤러·모델·뷰의 책임을 나누고 호출 관계를 만든다.

## ② 📖 이론

Laravel의 기본 업무 단위는 컨트롤러 액션과 Eloquent 모델이다. 컨트롤러에 HTML·SQL·파일 처리를 한꺼번에 넣으면 수정 범위가 커진다. 요청 검증은 컨트롤러 경계, 행과 관계는 모델, 공통 계산은 서비스, 표현은 Blade/Vue에 둔다. 서류를 창구·담당자·보관함으로 나누는 것과 같다.

`Request $request`는 컨테이너가 넣어 주는 객체다. `view('study.preferences', ['theme' => $value])`로 서버에서 뷰로 값을 보낸다. Blade 컴포넌트는 `:message="session('status')"`로 속성을 받는다. Vue의 props는 부모가 자식에게 보내는 읽기 전용 입력이고 이벤트는 자식이 변경 의도를 부모에게 알리는 방식이다. 이 과정은 같은 PHP 메모리의 함수 호출과 브라우저 HTTP 요청을 구분해야 이해된다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. `LearningController`의 preferences와 save를 읽고 조회·저장 액션을 나눈 이유를 확인한다.
2. 로그인한 상태로 `/study/preferences`를 연다. 컨트롤러가 파일에서 읽은 theme을 뷰에 넘긴다. 저장 구현은 다음 단계에서 자세히 다룬다.
3. 경로를 다루는 코드에서 사용자가 보낸 user_id를 쓰지 않고 인증 객체의 id를 쓴다. 단위 간 전달도 신뢰 경계를 넘어오면 검증한다.
4. `Controller`의 AuthorizesRequests 트레이트가 하위 컨트롤러에서 authorize를 제공하는지 확인한다.

### `demo/app/Http/Controllers/Controller.php` 전체 코드

[demo/app/Http/Controllers/Controller.php](demo/app/Http/Controllers/Controller.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

abstract class Controller
{
    use AuthorizesRequests;
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Http/Controllers/LearningController.php` 전체 코드

[demo/app/Http/Controllers/LearningController.php](demo/app/Http/Controllers/LearningController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\View\View;

class LearningController extends Controller
{
    public function preferences(Request $request): View
    {
        $path = 'preferences/'.$request->user()->id.'.json';
        $saved = Storage::disk('local')->exists($path) ? json_decode(Storage::disk('local')->get($path), true) : [];

        return view('study.preferences', ['theme' => $saved['theme'] ?? 'light']);
    }

    public function save(Request $request): RedirectResponse
    {
        $data = $request->validate(['theme' => ['required', 'in:light,dark']]);
        $request->session()->put('theme', $data['theme']);
        Storage::disk('local')->put('preferences/'.$request->user()->id.'.json', json_encode($data, JSON_THROW_ON_ERROR));

        return redirect()->route('study.preferences')->with('status', '화면 설정을 저장했습니다.');
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
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 8 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 9 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 10 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | `preferences` 메서드를 선언한다. 본인 비공개 설정 파일을 읽어 뷰에 전달한다. |
| 13 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 14 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 15 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 16 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 17 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 20 | `save` 메서드를 선언한다. 검증된 값을 저장하고 화면을 다시 조회하게 한다. |
| 21 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 22 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 23 | 현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다. |
| 24 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 25 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 26 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 27 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/resources/views/study/preferences.blade.php` 전체 코드

[demo/resources/views/study/preferences.blade.php](demo/resources/views/study/preferences.blade.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```blade
@extends('layouts.app')
@section('content')
    <h1>화면 설정</h1>
    <form method="POST" action="{{ route('study.preferences.save') }}">
        @csrf
        <label for="theme">테마</label>
        <select id="theme" name="theme">
            <option value="light" @selected($theme === 'light')>밝게</option>
            <option value="dark" @selected($theme === 'dark')>어둡게</option>
        </select>
        @error('theme')<p role="alert">{{ $message }}</p>@enderror
        <button type="submit">저장</button>
    </form>
    <x-status :message="session('status')" />
@endsection
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 공통 Blade 레이아웃을 부모로 선택한다. |
| 2 | 레이아웃의 지정 영역에 이 뷰 내용을 채운다. |
| 3 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 4 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 5 | 웹 POST의 위조 요청을 막는 세션 CSRF 토큰을 숨김 필드로 출력한다. |
| 6 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 7 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 8 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 9 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 10 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 11 | 서버 검증에서 해당 필드에 발생한 오류를 출력한다. |
| 12 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 13 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 14 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 15 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |


## ④ 🔗 연동 포인트

요청 객체 → 컨트롤러의 지역 변수 → 뷰의 입력값 → 폼 POST로 데이터가 왕복한다. 다음 단계에서는 이 값이 요청이 끝난 뒤에도 남도록 세션·파일·모델 저장을 연결한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| authorize 메서드 없음 | 기본 Controller에 권한 트레이트가 없음 | AuthorizesRequests 사용 여부 확인 |
| 컴포넌트 속성이 문자열로 출력 | PHP 표현식에 :가 빠짐 | :message="session(...)"처럼 전달 |
| 로그인 없이 설정을 열면 이동함 | auth 미들웨어가 보호함 | 먼저 회원가입·로그인하고 재시도 |

## ⑥ 직접 해보기

1. 컨트롤러가 넘기는 theme을 뷰에서 문장으로도 출력한다.
2. 조회 액션과 저장 액션이 각각 언제 호출되는지 Network에서 찾는다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 라우팅 / 컨트롤러 / 뷰
- [ ] MVC 각 단위의 책임과 전달값을 설명했다.
- [ ] 컨트롤러의 의존성 주입과 일반 함수 호출을 구분했다.

## ⑧ 다음 단계 연결

라우트·컨트롤러·모델·뷰의 책임을 나누고 호출 관계를 만든다. 이 결과를 [study3.md](study3.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/controllers)
