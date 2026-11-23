# study3 · 데이터 다루기

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

요청 변수·세션·파일·모델·Vue 상태의 수명을 구분하고 저장한다.

## ② 📖 이론

PHP 지역 변수는 한 요청 동안 살고, 세션은 같은 방문자의 여러 요청을 잇고, DB·파일은 서버 재시작 뒤에도 남는다. Vue의 `ref`는 브라우저 메모리의 관찰 가능한 상자다. Pinia의 ref는 여러 화면 함수에서 같은 상자를 사용하게 한다. 메모지·개인 서랍·서고의 차이로 기억한다.

Post 모델은 posts 테이블과 연결되고 user/comments 관계를 제공한다. `fillable`은 대량 할당 가능한 속성의 명단이며 `user_id`를 제외한다. `casts`의 array는 JSON 태그를 PHP 배열로 읽고 쓴다. Vue의 `v-model`은 입력값과 상태를 묶지만 서버 저장을 자동으로 하지 않는다. 저장 버튼의 HTTP 요청이 있어야 영속화된다. 토큰은 Pinia 메모리에만 두므로 새로고침하면 다시 로그인한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. 테마 화면에서 dark를 선택해 POST한다. 세션의 theme과 비공개 JSON 파일에 같은 값이 들어간다.
2. 새 요청에서 컨트롤러가 파일을 읽어 선택 상태를 복원하는지 확인한다. 파일은 `storage/app/private/preferences/{본인 id}.json`이다.
3. Post의 tags JSON cast와 scopeSearch를 읽는다. 검색 값은 바인딩되어 SQL 문자열에 직접 붙지 않는다.
4. Pinia 스토어의 token/user ref를 읽고 응답 후 값이 바뀌는 위치를 찾는다. 비밀번호·토큰을 localStorage에 쓰는 코드는 추가하지 않는다.

### `demo/app/Models/Post.php` 전체 코드

[demo/app/Models/Post.php](demo/app/Models/Post.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Models;

use Database\Factories\PostFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['title', 'body', 'tags'])]
class Post extends Model
{
    /** @use HasFactory<PostFactory> */
    use HasFactory;

    public function scopeSearch(Builder $query, ?string $term): Builder
    {
        $term = trim((string) $term);
        if ($term === '') {
            return $query;
        }

        $like = '%'.$term.'%';

        return $query->where(function (Builder $inner) use ($like) {
            $inner->whereLike('title', $like)->orWhereLike('body', $like);
        });
    }

    protected function casts(): array
    {
        return ['tags' => 'array'];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
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
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 11 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 12 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 13 | PHP 속성으로 클래스의 허용 필드·이름·버전·설명을 선언한다. |
| 14 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 15 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 16 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 17 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 18 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 19 | `scopeSearch` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 20 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 21 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 22 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 23 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 24 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 25 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 26 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 27 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 28 | 사용자 입력을 바인딩한 조회 조건을 추가한다. |
| 29 | DB 드라이버에 맞는 부분 일치 검색 조건을 만든다. |
| 30 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | `casts` 메서드를 선언한다. 저장 값과 PHP 값의 타입 변환을 정의한다. |
| 34 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 35 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | `user` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 39 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 40 | 현재 모델에서 소유자나 부모 한 건을 찾는 관계를 정의한다. |
| 41 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 42 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 43 | `comments` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 44 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 45 | 현재 모델의 자식 여러 건을 찾는 관계를 정의한다. |
| 46 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 47 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


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


### `demo/resources/js/stores/auth.js` 전체 코드

[demo/resources/js/stores/auth.js](demo/resources/js/stores/auth.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useAuth = defineStore('auth', () => {
    const token = ref('');
    const user = ref(null);
    async function request(path, options = {}) {
        const headers = { Accept: 'application/json', ...options.headers };
        if (token.value) headers.Authorization = `Bearer ${token.value}`;
        if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
        const response = await fetch(path, { ...options, headers });
        const body = response.status === 204 ? null : await response.json();
        if (!response.ok) {
            if (response.status === 401) { token.value = ''; user.value = null; }
            const error = new Error(body?.error?.message || '요청 실패');
            error.fields = body?.error?.fields || {};
            error.status = response.status;
            throw error;
        }
        return body;
    }
    async function login(values, signup = false) {
        const result = await request(`/api/auth/${signup ? 'signup' : 'login'}`, { method: 'POST', body: JSON.stringify(values) });
        token.value = result.data.accessToken;
        user.value = result.data.user;
    }
    async function logout() {
        try { await request('/api/auth/logout', { method: 'POST' }); }
        finally { token.value = ''; user.value = null; }
    }
    return { token, user, request, login, logout };
});
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 여러 화면 함수가 공유할 Pinia 상태와 행동을 정의한다. |
| 4 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 5 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 6 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 8 | 현재 메모리 토큰을 Bearer 인증 헤더에 연결한다. |
| 9 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 10 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 11 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 12 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 13 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 14 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 15 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 16 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 22 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 23 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 24 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 27 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 28 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 30 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

파일 저장은 DB 이전의 작은 영속화 실습이다. 다음 단계는 어떤 URL이 조회·변경을 호출하는지 정의한다. DB로 옮길 때도 화면 입력 이름과 서버 검증 규칙의 계약을 유지한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 새로고침하면 로그아웃됨 | Vue 토큰이 메모리 저장 방식임 | 설계된 동작; 다시 로그인하거나 세션 방식의 Blade 화면 사용 |
| 파일 permission denied | storage 쓰기 권한 없음 | 애플리케이션 실행 계정에 storage 권한 부여 |
| 다른 사용자의 설정이 바뀜 | 파일 이름을 입력 user_id로 구성함 | 인증 객체의 id로만 경로 작성 |

## ⑥ 직접 해보기

1. 두 회원으로 각각 설정을 저장해 서로 다른 파일인지 확인한다.
2. tags의 JSON DB 값과 API 배열 값을 대조한다.
3. Vue 입력만 바꾸고 저장하지 않으면 DB가 변하지 않는 것을 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 세션과 파일 저장을 재요청으로 확인했다.
- [ ] v-model과 서버 저장의 차이를 설명했다.
- [ ] fillable에 소유자 id를 넣지 않았다.

## ⑧ 다음 단계 연결

요청 변수·세션·파일·모델·Vue 상태의 수명을 구분하고 저장한다. 이 결과를 [study4.md](study4.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/session)
- [공식 문서 2](https://laravel.com/docs/13.x/filesystem)
- [공식 문서 3](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
