# study13 · 외부 서비스 연동

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

테스트 결제·메일·비공개 파일·GitHub OAuth를 서버 경계에서 연결한다.

## ② 📖 이론

외부 서비스는 실패·지연·중복 응답이 생기는 별도 시스템이다. 택배 발송처럼 접수와 완료 확인을 분리해야 한다. Stripe Checkout은 서버가 정한 price id로 테스트 세션을 만들고 서명 웹훅으로 수신을 확인한다. 현재 예제는 수신 영수증을 저장하며 결제 금액에 따른 이용 권한 변경은 하지 않는다.

메일은 Laravel Notification을 큐에 넣어 log/SMTP 전송으로 바꾼다. 파일은 외부 공개 public 디스크 대신 private에 저장한다. GitHub OAuth는 redirect→state 검증→callback→User→세션으로 이어진다. 같은 이메일이라는 이유로 기존 계정을 자동 연결하지 않는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. Stripe 테스트 키·서버 price·웹훅 secret을 .env에 설정한다. 키가 없으면 Checkout은 503을 반환한다. 실결제를 실행하지 않는다.
2. 인증된 POST /api/checkout의 URL로 테스트 Checkout을 연다. 클라이언트가 가격을 보내도 서버 price를 사용하고 분 단위 멱등성 키로 재요청을 묶는다.
3. /api/webhooks/stripe는 raw body와 Stripe-Signature의 t/v1을 검증한다. 5분 시각 허용 범위와 event_id unique로 위조·오래된 요청·중복 수신을 제한한다. 브라우저 success 쿼리로 결제 완료를 판정하지 않는다.
4. MAIL_MAILER=log로 로컬 알림 내용을 확인한다. SMTP로 바꾸려면 host/port/username/password/from과 실제 메일 공급자 설정을 맞춘다.
5. 문서는 UTF-8 TXT/MD, 최대 100KB만 허용한다. 임의 실행 파일·공개 URL을 만들지 않고 본인에게만 다운로드를 허용한다.
6. GitHub OAuth 앱에 callback URL을 정확히 등록하고 services.github 환경값을 채운다. state 오류·거절·이메일 없음·기존 이메일 충돌을 처리한다.
7. OAuth 결과는 Blade 세션이다. Vue의 Bearer 토큰으로 자동 변환하지 않는다. 외부 계정이 필요한 실제 결제·SMTP·GitHub 왕복은 공급자 자격증명 설정 후 별도 검증한다.

### `project/app/Http/Controllers/IntegrationController.php` 전체 코드

[project/app/Http/Controllers/IntegrationController.php](project/app/Http/Controllers/IntegrationController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;
use Laravel\Socialite\Facades\Socialite;
use Symfony\Component\HttpFoundation\RedirectResponse as OAuthRedirect;
use Throwable;

class IntegrationController extends Controller
{
    public function redirect(): OAuthRedirect
    {
        abort_unless(config('services.github.client_id'), 503);

        return Socialite::driver('github')->scopes(['user:email'])->redirect();
    }

    public function callback(Request $request): RedirectResponse
    {
        abort_if($request->has('error'), 400, 'OAuth denied');
        try {
            $identity = Socialite::driver('github')->user();
        } catch (Throwable $exception) {
            report($exception);
            abort(400, 'OAuth state or provider failed');
        }
        abort_unless($identity->getEmail(), 422, '공개 이메일을 설정하세요.');
        $user = User::query()->where('github_id', $identity->getId())->first();
        if (! $user) {
            abort_if(User::query()->where('email', $identity->getEmail())->exists(), 409, '기존 계정은 자동 연결하지 않습니다.');
            $user = new User(['name' => $identity->getName() ?: $identity->getNickname(), 'email' => $identity->getEmail(), 'password' => Str::random(64)]);
            $user->github_id = $identity->getId();
            $user->save();
        }
        Auth::login($user);
        $request->session()->regenerate();

        return redirect()->route('notes.index');
    }

    public function checkout(Request $request): JsonResponse
    {
        abort_unless(config('services.stripe.secret') && config('services.stripe.price'), 503);
        $session = Http::asForm()->withToken(config('services.stripe.secret'))->connectTimeout(5)->timeout(20)
            ->withHeaders(['Idempotency-Key' => $request->user()->id.'-'.now()->format('YmdHi')])
            ->post('https://api.stripe.com/v1/checkout/sessions', [
                'mode' => 'payment', 'line_items[0][price]' => config('services.stripe.price'), 'line_items[0][quantity]' => 1,
                'client_reference_id' => (string) $request->user()->id,
                'success_url' => rtrim(config('app.url'), '/').'/app?checkout=success',
                'cancel_url' => rtrim(config('app.url'), '/').'/app?checkout=cancel',
            ]);
        abort_unless($session->successful(), 502);

        return response()->json(['data' => ['url' => $session->json('url')]]);
    }

    public function webhook(Request $request): JsonResponse
    {
        $secret = config('services.stripe.webhook_secret');
        abort_unless($secret, 503);
        $parts = [];
        foreach (explode(',', $request->header('Stripe-Signature', '')) as $piece) {
            $pair = explode('=', $piece, 2);
            if (count($pair) === 2) {
                $parts[$pair[0]][] = $pair[1];
            }
        }
        $timestamp = $parts['t'][0] ?? '';
        abort_unless(ctype_digit($timestamp) && abs(time() - (int) $timestamp) <= 300, 400);
        $expected = hash_hmac('sha256', $timestamp.'.'.$request->getContent(), $secret);
        $valid = false;
        foreach ($parts['v1'] ?? [] as $signature) {
            $valid = hash_equals($expected, $signature) || $valid;
        }
        abort_unless($valid, 400);
        $data = $request->validate(['id' => ['required', 'string', 'max:255'], 'type' => ['required', 'string', 'max:255']]);
        $inserted = DB::table('integration_receipts')->insertOrIgnore(['event_id' => $data['id'], 'type' => $data['type'], 'created_at' => now(), 'updated_at' => now()]);

        return response()->json(['data' => ['received' => true, 'duplicate' => $inserted === 0]]);
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
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 14 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 15 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 16 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 19 | `redirect` 메서드를 선언한다. 등록된 OAuth 공급자 주소로 이동한다. |
| 20 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 21 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | OAuth 공급자 설정을 사용하며 세션 기반 state 검증을 유지한다. |
| 24 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 25 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 26 | `callback` 메서드를 선언한다. OAuth 결과를 검증하고 별도 사용자 세션을 만든다. |
| 27 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 28 | 조건이 참이면 지정한 오류 상태로 요청을 중단한다. |
| 29 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 30 | OAuth 공급자 설정을 사용하며 세션 기반 state 검증을 유지한다. |
| 31 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 32 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 33 | 처리할 수 없는 요청을 명시적인 HTTP 오류로 중단한다. |
| 34 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 35 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 36 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 37 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 38 | 조건이 참이면 지정한 오류 상태로 요청을 중단한다. |
| 39 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 40 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 41 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 42 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 43 | 서버의 세션 인증 상태를 확인·설정·종료한다. |
| 44 | 현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다. |
| 45 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 46 | 처리 후 브라우저를 조회 화면으로 이동시킨다. |
| 47 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 48 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 49 | `checkout` 메서드를 선언한다. 서버 가격으로 결제 테스트 세션을 요청한다. |
| 50 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 51 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 52 | 서버에서 외부 API 요청을 구성한다. 연결·전체 시간 제한을 함께 적용한다. |
| 53 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 54 | 정해진 주소로 요청 본문을 POST한다. |
| 55 | 환경에 맞게 로드한 설정값을 읽는다. |
| 56 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 57 | 환경에 맞게 로드한 설정값을 읽는다. |
| 58 | 환경에 맞게 로드한 설정값을 읽는다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 61 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 62 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 63 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 64 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 65 | `webhook` 메서드를 선언한다. 원문 서명을 검증하고 중복 수신 영수증을 저장한다. |
| 66 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 67 | 환경에 맞게 로드한 설정값을 읽는다. |
| 68 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 69 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 70 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 71 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 72 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 73 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 74 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 75 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 76 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 77 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 78 | 원문과 비밀키로 서명값을 계산한다. |
| 79 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 80 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 81 | 서명 비교에서 타이밍 차이를 줄인다. |
| 82 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 83 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 84 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 85 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 86 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 87 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 88 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 89 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/config/services.php` 전체 코드

[project/config/services.php](project/config/services.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

return [
    'github' => ['client_id' => env('GITHUB_CLIENT_ID'), 'client_secret' => env('GITHUB_CLIENT_SECRET'), 'redirect' => env('GITHUB_REDIRECT_URI')],
    'stripe' => ['secret' => env('STRIPE_SECRET'), 'price' => env('STRIPE_PRICE_ID'), 'webhook_secret' => env('STRIPE_WEBHOOK_SECRET')],

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Resend, Postmark, AWS, and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

];
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 4 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 5 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 10 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 11 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 12 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 13 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 14 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 15 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 16 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 17 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 18 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 19 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 20 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 27 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 28 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 29 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 30 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 34 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 35 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 36 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 37 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 38 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 39 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 40 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/app/Http/Controllers/Api/DocumentController.php` 전체 코드

[project/app/Http/Controllers/Api/DocumentController.php](project/app/Http/Controllers/Api/DocumentController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\DocumentResource;
use App\Jobs\SummarizeDocument;
use App\Models\Document;
use App\Services\DocumentAi;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Throwable;

class DocumentController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        return response()->json(['data' => DocumentResource::collection(Document::query()->where('user_id', $request->user()->id)->latest('id')->limit(50)->get())->resolve($request)]);
    }

    public function store(Request $request): JsonResponse
    {
        $request->validate(['file' => ['required', 'file', 'max:100', 'extensions:txt,md', 'mimetypes:text/plain,text/markdown,text/x-markdown']]);
        $file = $request->file('file');
        $content = $file->getContent();
        abort_unless(mb_check_encoding($content, 'UTF-8') && ! str_contains($content, "\0"), 422);
        $path = $file->store('documents', 'local');
        try {
            $document = Document::query()->create(['user_id' => $request->user()->id,
                'filename' => basename($file->getClientOriginalName()), 'path' => $path, 'content' => $content]);
        } catch (Throwable $exception) {
            Storage::disk('local')->delete($path);
            throw $exception;
        }
        SummarizeDocument::dispatch($document->id);

        return response()->json(['data' => (new DocumentResource($document->fresh()))->resolve($request)], 202);
    }

    public function download(Request $request, Document $document): StreamedResponse
    {
        $this->owned($request, $document);

        return Storage::disk('local')->download($document->path, $document->filename, ['Content-Type' => 'text/plain; charset=utf-8', 'X-Content-Type-Options' => 'nosniff']);
    }

    public function destroy(Request $request, Document $document): Response
    {
        $this->owned($request, $document);
        Storage::disk('local')->delete($document->path);
        $document->delete();

        return response()->noContent();
    }

    public function history(Request $request, Document $document): JsonResponse
    {
        $this->owned($request, $document);

        $questions = DB::table('document_questions')->where('document_id', $document->id)->latest('id')->limit(20)->get();

        return response()->json(['data' => $questions->map(fn ($row) => ['id' => $row->id, 'documentId' => $row->document_id,
            'question' => $row->question, 'answer' => $row->answer, 'sources' => json_decode($row->sources, true),
            'createdAt' => Carbon::parse($row->created_at)->utc()->toISOString()])]);
    }

    public function ask(Request $request, Document $document, DocumentAi $ai): StreamedResponse
    {
        $this->owned($request, $document);
        $data = $request->validate(['question' => ['required', 'string', 'max:1000']]);
        $sources = $ai->excerpts($document->content, $data['question']);
        $context = implode("\n", array_map(fn ($source) => '(발췌 '.$source['index'].') '.$source['text'], $sources));

        return response()->stream(function () use ($ai, $context, $data, $sources, $document): void {
            $emit = function (array $event): void {
                echo 'data: '.json_encode($event, JSON_UNESCAPED_UNICODE)."\n\n";
                if (ob_get_level() > 0) {
                    ob_flush();
                } flush();
            };
            $answer = '';
            try {
                foreach ($ai->stream($context, $data['question']) as $delta) {
                    $answer .= $delta;
                    $emit(['delta' => $delta]);
                    if (connection_aborted()) {
                        return;
                    }
                }
                DB::table('document_questions')->insert(['document_id' => $document->id, 'question' => $data['question'],
                    'answer' => $answer, 'sources' => json_encode($sources, JSON_UNESCAPED_UNICODE), 'created_at' => now(), 'updated_at' => now()]);
                $emit(['done' => true, 'sources' => $sources, 'driver' => config('study.ai_driver')]);
            } catch (Throwable $exception) {
                report($exception);
                $emit(['error' => 'AI 서비스 연결을 확인하세요.']);
            }
        }, 200, ['Content-Type' => 'text/event-stream', 'Cache-Control' => 'no-cache', 'X-Accel-Buffering' => 'no']);
    }

    private function owned(Request $request, Document $document): void
    {
        abort_unless($document->user_id === $request->user()->id, 404);
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
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 14 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 15 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 16 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 17 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 18 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 19 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 20 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 21 | `index` 메서드를 선언한다. 목록을 조회해 응답으로 반환하는 진입점이다. |
| 22 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 23 | 지정한 열의 내림차순으로 최근 항목을 먼저 가져온다. |
| 24 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 25 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 26 | `store` 메서드를 선언한다. 검증한 입력으로 자원을 생성하는 진입점이다. |
| 27 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 28 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 29 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 30 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 31 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 32 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 33 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 34 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 35 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 36 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 37 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 38 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 39 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 40 | 문서 id를 전달해 백그라운드 작업을 큐에 예약한다. |
| 41 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 42 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 43 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 44 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 45 | `download` 메서드를 선언한다. 본인 파일을 다운로드 응답으로 보낸다. |
| 46 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 47 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 48 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 49 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 50 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 51 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 52 | `destroy` 메서드를 선언한다. 권한 확인 뒤 자원을 삭제하는 진입점이다. |
| 53 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 54 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 55 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 56 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 57 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 58 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 61 | `history` 메서드를 선언한다. 본인 문서 질문 이력을 조회한다. |
| 62 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 63 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 64 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 65 | 지정한 열의 내림차순으로 최근 항목을 먼저 가져온다. |
| 66 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 67 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 68 | JSON 문자열을 구조화한 값으로 바꾸고 잘못된 입력을 처리한다. |
| 69 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 70 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 71 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 72 | `ask` 메서드를 선언한다. 검색 근거를 사용해 답변을 SSE 이벤트로 전달한다. |
| 73 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 74 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 75 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 76 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 77 | 각 원소에 같은 변환을 적용한다. |
| 78 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 79 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 80 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 81 | 값을 JSON으로 직렬화한다. 민감한 필드가 포함되지 않는지 확인한다. |
| 82 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 83 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 84 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 85 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 86 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 87 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 88 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 89 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 90 | SSE 이벤트 한 건을 JSON data 프레임으로 브라우저에 보낸다. |
| 91 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 92 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 93 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 94 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 95 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 96 | 값을 JSON으로 직렬화한다. 민감한 필드가 포함되지 않는지 확인한다. |
| 97 | SSE 이벤트 한 건을 JSON data 프레임으로 브라우저에 보낸다. |
| 98 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 99 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 100 | SSE 이벤트 한 건을 JSON data 프레임으로 브라우저에 보낸다. |
| 101 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 102 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 103 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 104 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 105 | `owned` 메서드를 선언한다. 인증된 사용자와 문서 소유자를 비교한다. |
| 106 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 107 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 108 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 109 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/app/Notifications/DocumentReady.php` 전체 코드

[project/app/Notifications/DocumentReady.php](project/app/Notifications/DocumentReady.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class DocumentReady extends Notification implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public function __construct(public int $documentId) {}

    public function via(object $notifiable): array
    {
        return config('broadcasting.default') === 'reverb' ? ['database', 'mail', 'broadcast'] : ['database', 'mail'];
    }

    public function toMail(object $notifiable): MailMessage
    {
        return (new MailMessage)->subject('문서 요약 완료')->line('문서 요약을 확인할 수 있습니다.')
            ->action('학습 서재', url('/app'));
    }

    public function toArray(object $notifiable): array
    {
        return ['documentId' => $this->documentId, 'message' => '문서 요약이 완료되었습니다.'];
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
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 15 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 16 | `__construct` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 17 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 18 | `via` 메서드를 선언한다. 알림이 전달될 채널을 설정에 따라 선택한다. |
| 19 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 20 | 환경에 맞게 로드한 설정값을 읽는다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | `toMail` 메서드를 선언한다. 메일 제목·본문·링크를 구성한다. |
| 24 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 25 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 26 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 27 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 28 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 29 | `toArray` 메서드를 선언한다. 모델 내부 속성을 외부 JSON 계약으로 변환한다. |
| 30 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 31 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 32 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 33 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/tests/Feature/IntegrationTest.php` 전체 코드

[project/tests/Feature/IntegrationTest.php](project/tests/Feature/IntegrationTest.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace Tests\Feature;

use App\Models\User;
use App\Notifications\DocumentReady;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\User as SocialUser;
use Tests\TestCase;

class IntegrationTest extends TestCase
{
    use RefreshDatabase;

    public function test_signed_webhook_is_idempotent_and_bad_signature_returns_400(): void
    {
        config(['services.stripe.webhook_secret' => 'test-secret']);
        $body = json_encode(['id' => 'evt_test', 'type' => 'checkout.session.completed']);
        $timestamp = (string) time();
        $signature = hash_hmac('sha256', $timestamp.'.'.$body, 'test-secret');
        $headers = ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json', 'HTTP_STRIPE_SIGNATURE' => 't='.$timestamp.',v1='.$signature];
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertOk()->assertJsonPath('data.duplicate', false);
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertOk()->assertJsonPath('data.duplicate', true);
        $headers['HTTP_STRIPE_SIGNATURE'] = 't='.$timestamp.',v1=invalid';
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertBadRequest();
        $this->assertDatabaseCount('integration_receipts', 1);
    }

    public function test_checkout_uses_server_price_instead_of_client_price(): void
    {
        $user = User::factory()->create();
        config(['services.stripe.secret' => 'sk_test', 'services.stripe.price' => 'price_server']);
        Http::preventStrayRequests();
        Http::fake(['https://api.stripe.com/v1/checkout/sessions' => Http::response(['url' => 'https://checkout.stripe.com/test'], 200)]);
        $this->withToken($user->createToken('test')->plainTextToken)->postJson('/api/checkout', ['price' => 'price_attacker'])->assertOk()->assertJsonPath('data.url', 'https://checkout.stripe.com/test');
        Http::assertSent(fn ($request) => $request['line_items[0][price]'] === 'price_server'
            && $request['success_url'] === rtrim(config('app.url'), '/').'/app?checkout=success');
    }

    public function test_oauth_creates_provider_account_and_regenerates_session(): void
    {
        $identity = (new SocialUser)->map(['id' => 'github-123', 'name' => '학습자', 'email' => 'oauth@example.com']);
        Socialite::shouldReceive('driver')->with('github')->andReturnSelf();
        Socialite::shouldReceive('user')->once()->andReturn($identity);
        $this->get('/auth/github/callback')->assertRedirect('/notes');
        $this->assertAuthenticated();
        $this->assertDatabaseHas('users', ['github_id' => 'github-123', 'email' => 'oauth@example.com']);
    }

    public function test_oauth_never_links_an_existing_email_automatically(): void
    {
        User::factory()->create(['email' => 'existing@example.com']);
        $identity = (new SocialUser)->map(['id' => 'attacker', 'email' => 'existing@example.com']);
        Socialite::shouldReceive('driver')->with('github')->andReturnSelf();
        Socialite::shouldReceive('user')->once()->andReturn($identity);
        $this->get('/auth/github/callback')->assertConflict();
        $this->assertGuest();
        $this->assertDatabaseCount('users', 1);
    }

    public function test_notification_is_persisted_and_mail_renders_without_document_content(): void
    {
        $user = User::factory()->create();
        config(['broadcasting.default' => 'null']);
        $user->notify(new DocumentReady(123));
        $this->assertDatabaseCount('notifications', 1);
        $mail = (new DocumentReady(123))->toMail($user)->render();
        $this->assertStringContainsString('/app', (string) $mail);
    }

    public function test_private_broadcast_channel_auth_rejects_another_users_channel(): void
    {
        $user = User::factory()->create();
        config(['broadcasting.default' => 'reverb', 'broadcasting.connections.reverb.key' => 'study', 'broadcasting.connections.reverb.secret' => 'study-secret', 'broadcasting.connections.reverb.app_id' => 'study']);
        require base_path('routes/channels.php');
        $this->withToken($user->createToken('websocket')->plainTextToken)->postJson('/api/broadcasting/auth', ['socket_id' => '123.456', 'channel_name' => 'private-App.Models.User.'.$user->id])->assertOk()->assertJsonStructure(['auth']);
        $this->postJson('/api/broadcasting/auth', ['socket_id' => '123.456', 'channel_name' => 'private-App.Models.User.999'])->assertForbidden();
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
| 13 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 14 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 15 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 16 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 17 | `test_signed_webhook_is_idempotent_and_bad_signature_returns_400` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 18 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 19 | 환경에 맞게 로드한 설정값을 읽는다. |
| 20 | 값을 JSON으로 직렬화한다. 민감한 필드가 포함되지 않는지 확인한다. |
| 21 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 22 | 원문과 비밀키로 서명값을 계산한다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 25 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 26 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 27 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 28 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 30 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 31 | `test_checkout_uses_server_price_instead_of_client_price` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 32 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 33 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 34 | 환경에 맞게 로드한 설정값을 읽는다. |
| 35 | 가짜로 지정하지 않은 외부 HTTP가 나가지 못하게 막는다. |
| 36 | 지정한 외부 HTTP 응답을 테스트 가짜로 바꾼다. |
| 37 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 38 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 39 | 환경에 맞게 로드한 설정값을 읽는다. |
| 40 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 41 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 42 | `test_oauth_creates_provider_account_and_regenerates_session` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 43 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 44 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 45 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 46 | OAuth 공급자 설정을 사용하며 세션 기반 state 검증을 유지한다. |
| 47 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 48 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 49 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 50 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 51 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 52 | `test_oauth_never_links_an_existing_email_automatically` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 53 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 54 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 55 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 56 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 57 | OAuth 공급자 설정을 사용하며 세션 기반 state 검증을 유지한다. |
| 58 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 59 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 60 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 61 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 62 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 63 | `test_notification_is_persisted_and_mail_renders_without_document_content` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 64 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 65 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 66 | 환경에 맞게 로드한 설정값을 읽는다. |
| 67 | 사용자에게 정의한 알림 채널 전송을 예약한다. |
| 68 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 69 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 70 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 71 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 72 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 73 | `test_private_broadcast_channel_auth_rejects_another_users_channel` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 74 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 75 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 76 | 환경에 맞게 로드한 설정값을 읽는다. |
| 77 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 78 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 79 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 80 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 81 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

브라우저는 Laravel만 호출하고 외부 비밀키는 서버의 services 설정에서만 읽는다. 파일 저장 후 요약 job으로 잇는 흐름은 study15·18에서 완성한다. 외부 HTTP 가짜와 서명 테스트는 실제 과금 없이 이 경계를 검증한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 503 결제 사용 불가 | Stripe 키·price 미설정 | 테스트 환경변수 구성 후 config:clear |
| 웹훅 서명 400 | 다른 secret·body 변형·시각 만료 | 서명 대상 raw body와 endpoint secret을 확인 |
| OAuth state 오류 | 세션 쿠키·callback 도메인 불일치 | stateless로 우회하지 말고 같은 도메인·세션 설정 확인 |

## ⑥ 직접 해보기

1. 테스트 웹훅을 두 번 보내 duplicate=true인지 확인한다.
2. 서명 한 글자를 바꿔 거부되고 DB 영수증이 늘지 않는지 확인한다.
3. php 확장 파일 업로드를 시도해 검증 거부를 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 테스트 결제와 실제 과금을 구분했다.
- [ ] 메일·파일·OAuth 환경변수를 분리했다.
- [ ] 웹훅의 서명·시각·중복을 검사했다.
- [ ] 기존 계정을 이메일만으로 자동 연결하지 않는다.

## ⑧ 다음 단계 연결

테스트 결제·메일·비공개 파일·GitHub OAuth를 서버 경계에서 연결한다. 이 결과를 [study14.md](study14.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/socialite)
- [공식 문서 2](https://laravel.com/docs/13.x/notifications)
- [공식 문서 3](https://docs.stripe.com/api/checkout/sessions/create)
- [공식 문서 4](https://docs.stripe.com/webhooks)
