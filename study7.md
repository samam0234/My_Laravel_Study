# study7 · 인증·보안 기초

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

세션과 Sanctum 토큰을 발급하고 소유권·해시·CSRF·XSS·CORS를 적용한다.

## ② 📖 이론

인증은 누구인지, 인가는 이 행을 바꿀 수 있는지 확인한다. 회원증과 출입 가능한 방의 차이다. User의 password hashed cast가 비밀번호를 해시하고 Hash::check가 확인한다. 원문·해시 모두 응답에 포함하지 않는다.

Blade 로그인은 세션 쿠키를 사용하고 로그인 후 세션 id를 재생성한다. Vue는 메모리에 보관한 Sanctum Bearer 토큰을 전송한다. DB에는 토큰 해시만 남으며 새 표준 토큰은 1시간 후 만료된다. 로그아웃은 현재 토큰만 폐기한다. 서로 다른 로그인 수단은 같은 User를 가리켜도 토큰·세션을 자동 복사하지 않는다.

Policy는 작성자만 수정·삭제하도록 한다. Vue·Blade의 텍스트 출력은 기본 이스케이프를 사용한다. 웹 폼에는 CSRF 토큰을 넣는다. Bearer API는 브라우저가 자동 첨부하는 인증 쿠키에 의존하지 않는다. CORS는 브라우저의 읽기 허용 규칙이고 서버 권한 확인을 대체하지 않는다. `CORS_ORIGIN`으로 출처를 지정하며 공개 VITE 변수에 비밀키를 넣지 않는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. 가입은 nickname/email/password를 받는다. 중복 이메일은 409, 잘못된 로그인은 계정 존재를 구별하지 않는 401이다.
2. 로그인 응답의 accessToken을 Authorization 헤더에 넣고 `/api/auth/me`를 요청한다. API 토큰을 URL 쿼리에 넣거나 콘솔 로그에 남기지 않는다.
3. 두 회원을 만들고 다른 회원의 글을 PATCH/DELETE하면 403인지 확인한다. 비공개 AI 문서는 존재도 숨기기 위해 404를 사용한다.
4. 로그아웃한 토큰·만료 토큰으로 다시 요청하면 401인지 확인한다. 로그인 경로는 분당 10회로 제한한다.
5. Blade 세션 로그아웃의 invalidate/regenerateToken과 Vue 토큰 폐기를 구분한다. 운영은 HTTPS와 SESSION_SECURE_COOKIE=true를 사용한다.

### `demo/app/Http/Controllers/Api/AuthController.php` 전체 코드

[demo/app/Http/Controllers/Api/AuthController.php](demo/app/Http/Controllers/Api/AuthController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Symfony\Component\HttpFoundation\Response;

class AuthController extends Controller
{
    public function signup(Request $request): JsonResponse
    {
        $data = $request->validate([
            'nickname' => ['required', 'string', 'max:80'],
            'email' => ['required', 'email', 'max:255'],
            'password' => ['required', 'string', 'min:12', 'max:128'],
        ]);
        abort_if(User::query()->where('email', $data['email'])->exists(), 409, 'EMAIL_TAKEN');
        $user = User::query()->create(['name' => $data['nickname'], 'email' => $data['email'], 'password' => $data['password']]);

        return $this->token($user, 201);
    }

    public function login(Request $request): JsonResponse
    {
        $data = $request->validate(['email' => ['required', 'email'], 'password' => ['required', 'string']]);
        $user = User::query()->where('email', $data['email'])->first();
        abort_unless($user && Hash::check($data['password'], $user->password), 401, 'INVALID_CREDENTIALS');

        return $this->token($user);
    }

    public function me(Request $request): JsonResponse
    {
        $user = $request->user();

        return response()->json(['data' => ['id' => $user->id, 'email' => $user->email, 'nickname' => $user->name]]);
    }

    public function logout(Request $request): Response
    {
        $request->user()->currentAccessToken()?->delete();

        return response()->noContent();
    }

    private function token(User $user, int $status = 200): JsonResponse
    {
        return response()->json(['data' => [
            'user' => ['id' => $user->id, 'email' => $user->email, 'nickname' => $user->name],
            'accessToken' => $user->createToken('vue', ['*'], now()->addHour())->plainTextToken,
        ]], $status);
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
| 11 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 12 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 13 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 14 | `signup` 메서드를 선언한다. 신규 회원을 검증·생성한다. |
| 15 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 16 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 17 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 조건이 참이면 지정한 오류 상태로 요청을 중단한다. |
| 22 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 23 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 24 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 27 | `login` 메서드를 선언한다. 입력 자격증명을 확인하고 로그인 상태를 만든다. |
| 28 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 29 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 30 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 31 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 34 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 35 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 36 | `me` 메서드를 선언한다. 현재 인증 사용자 공개 정보를 응답한다. |
| 37 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 38 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 39 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 40 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 41 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 42 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 43 | `logout` 메서드를 선언한다. 현재 인증 정보를 폐기한다. |
| 44 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 45 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 46 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 47 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 48 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 49 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 50 | `token` 메서드를 선언한다. 제한된 사용자 정보와 만료가 있는 토큰을 응답한다. |
| 51 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 52 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 53 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 54 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 55 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 56 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 57 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Http/Controllers/Auth/SessionController.php` 전체 코드

[demo/app/Http/Controllers/Auth/SessionController.php](demo/app/Http/Controllers/Auth/SessionController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\ValidationException;

class SessionController extends Controller
{
    public function create()
    {
        return view('auth.login');
    }

    public function store(Request $request)
    {
        $credentials = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ], [
            'email.required' => '이메일을 입력해 주세요.',
            'password.required' => '비밀번호를 입력해 주세요.',
        ]);

        if (! Auth::attempt($credentials, $request->boolean('remember'))) {
            throw ValidationException::withMessages([
                'email' => '이메일 또는 비밀번호가 올바르지 않습니다.',
            ]);
        }

        $request->session()->regenerate();

        return redirect()->intended(route('posts.index'))->with('status', '로그인했습니다.');
    }

    public function destroy(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('home')->with('status', '로그아웃했습니다.');
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
| 12 | `create` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 13 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 14 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 15 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 16 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 17 | `store` 메서드를 선언한다. 검증한 입력으로 자원을 생성하는 진입점이다. |
| 18 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 19 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 20 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 21 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 22 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 27 | 서버의 세션 인증 상태를 확인·설정·종료한다. |
| 28 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 29 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 30 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | 현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | `destroy` 메서드를 선언한다. 권한 확인 뒤 자원을 삭제하는 진입점이다. |
| 39 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 40 | 서버의 세션 인증 상태를 확인·설정·종료한다. |
| 41 | 현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다. |
| 42 | 현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다. |
| 43 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 44 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 45 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 46 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Models/User.php` 전체 코드

[demo/app/Models/User.php](demo/app/Models/User.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Database\Factories\UserFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

#[Fillable(['name', 'email', 'password'])]
#[Hidden(['password', 'remember_token'])]
class User extends Authenticatable
{
    /** @use HasFactory<UserFactory> */
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
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
| 5 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 8 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 11 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 14 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 15 | PHP 속성으로 클래스의 허용 필드·이름·버전·설명을 선언한다. |
| 16 | PHP 속성으로 클래스의 허용 필드·이름·버전·설명을 선언한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 19 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 20 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 21 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 22 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 23 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 24 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 25 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 26 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 27 | `casts` 메서드를 선언한다. 저장 값과 PHP 값의 타입 변환을 정의한다. |
| 28 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 29 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 30 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 31 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 32 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 33 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | `posts` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 36 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 37 | 현재 모델의 자식 여러 건을 찾는 관계를 정의한다. |
| 38 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 39 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 40 | `comments` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 41 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 42 | 현재 모델의 자식 여러 건을 찾는 관계를 정의한다. |
| 43 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 44 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Policies/PostPolicy.php` 전체 코드

[demo/app/Policies/PostPolicy.php](demo/app/Policies/PostPolicy.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    public function viewAny(?User $user): bool
    {
        return true;
    }

    public function view(?User $user, Post $post): bool
    {
        return true;
    }

    public function update(User $user, Post $post): bool
    {
        return $post->user_id === $user->id;
    }

    public function delete(User $user, Post $post): bool
    {
        return $this->update($user, $post);
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
| 7 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 10 | `viewAny` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 13 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 14 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 15 | `view` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 16 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 17 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 20 | `update` 메서드를 선언한다. 소유권 확인 뒤 전달된 필드만 수정하는 진입점이다. |
| 21 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 22 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 25 | `delete` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 26 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 27 | 이미 확인한 행에 전달된 변경값을 저장한다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/config/cors.php` 전체 코드

[demo/config/cors.php](demo/config/cors.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

return [
    'paths' => ['api/*'], 'allowed_methods' => ['*'],
    'allowed_origins' => array_filter(explode(',', env('CORS_ORIGIN', 'http://127.0.0.1:5173'))),
    'allowed_origins_patterns' => [], 'allowed_headers' => ['*'],
    'exposed_headers' => ['X-Request-Id', 'Location'], 'max_age' => 600, 'supports_credentials' => false,
];
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 4 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 5 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 6 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 8 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

프론트는 토큰을 request 함수 한 곳에서 붙이고 백엔드는 auth:sanctum과 Policy로 매 요청을 검증한다. 다음 단계는 이 공통 처리와 설정을 재사용 단위로 정리한다. 메일 인증·비밀번호 재설정·MFA는 현재 구현 범위에 없으므로 운영 요구가 생기면 별도 설계한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 401이 반복 | 토큰 누락·만료 또는 폐기 | me 응답과 Authorization 헤더 확인 후 다시 로그인 |
| 403인데 버튼이 보임 | UI 표시만으로 서버 권한이 생기지 않음 | author.id로 버튼 표시하고 서버 Policy 유지 |
| CORS 오류 | 요청 출처와 환경변수 불일치 | 정확한 scheme/host/port를 설정하고 config:clear |

## ⑥ 직접 해보기

1. 로그아웃 후 같은 토큰이 거부되는지 확인한다.
2. 게시글 제목에 스크립트 태그를 저장해 문자로 보이는지 확인한다.
3. 다른 계정으로 소유권 검사를 재현한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] Blade 템플릿 또는 API (Sanctum)
- [ ] 인증 (Breeze / Jetstream / 직접)
- [ ] 해시·세션 재생성·토큰 만료를 확인했다.
- [ ] Policy와 CORS의 책임을 구분했다.

## ⑧ 다음 단계 연결

세션과 Sanctum 토큰을 발급하고 소유권·해시·CSRF·XSS·CORS를 적용한다. 이 결과를 [study8.md](study8.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/sanctum)
- [공식 문서 2](https://laravel.com/docs/13.x/csrf)
