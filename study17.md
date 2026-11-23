# study17 · 실시간·확장

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

Reverb 비공개 채널로 문서 완료 알림을 보내고 파일 접근을 제한한다.

## ② 📖 이론

웹소켓은 연결을 유지하며 서버 사건을 브라우저에 전달한다. SSE는 서버→브라우저의 단방향 스트림이고 웹소켓은 양방향 채널이다. 안내 방송을 계속 듣는 창과 양방향 통화의 차이다. 문서 완료 알림에는 Laravel Notification→broadcast→Reverb→Echo 경로를 사용한다. AI 답변은 study18의 SSE로 별도 처리한다.

공개 채널에 사용자 문서 정보를 보내지 않는다. private-App.Models.User.{id} 채널은 Sanctum 인증 뒤 본인 id만 허용한다. Echo는 /api/broadcasting/auth에 Bearer를 보내 서명받는다. 공개 키는 브라우저에 주입해도 되지만 Reverb secret은 서버에만 둔다. 기본 앱은 log broadcaster이며 실제 소켓은 환경변수 전환 후 실행한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. project의 .env에 Reverb id/key/secret, host/port/scheme와 허용 origin을 설정한다. BROADCAST_CONNECTION=reverb로 바꾸고 캐시·워커를 다시 시작한다.
2. VITE_REVERB_APP_KEY/HOST/PORT/SCHEME는 브라우저에서 접근 가능한 주소를 지정한다. Docker 내부 reverb 서비스명은 브라우저 주소로 쓰지 않는다.
3. PHP 서버, queue:work, reverb:start를 각각 실행하고 Vue에 로그인한다. Echo가 본인의 private 채널을 구독한다.
4. 문서를 올리고 worker가 요약을 완료하면 DocumentReady가 database/mail/broadcast로 전달된다. 화면은 알림을 받고 본인 문서·알림 목록을 다시 조회한다.
5. 다른 사용자 채널 인증이 403인 테스트를 확인한다. 로그아웃·컴포넌트 해제 시 disconnect한다.
6. 파일 다운로드와 삭제는 owned 검사 뒤 수행한다. 업로드 원본을 public/storage로 링크하지 않는다. 삭제는 질문 이력도 FK cascade로 정리한다.
7. 운영은 wss와 허용 origin, 프록시 Upgrade/Connection 헤더, 연결 수·큐 지연·재연결을 점검한다. 로컬에서는 소켓 서버 실제 연결과 수신을 별도 검증한다.

### 실행 명령

```powershell
cd project
php artisan config:clear
php artisan reverb:start --host=127.0.0.1 --port=8080
# 다른 터미널: php artisan queue:work --tries=3 --timeout=100
# VITE_ 값을 바꿨으면 npm run build 또는 dev 서버 재시작
php artisan test --compact --filter=private_broadcast_channel
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `project/resources/js/realtime.js` 전체 코드

[project/resources/js/realtime.js](project/resources/js/realtime.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import Echo from 'laravel-echo';
import Pusher from 'pusher-js';
let echo;
export function disconnect() { echo?.disconnect(); echo = undefined; }
export function connect(auth, onNotification) {
    disconnect();
    if (!import.meta.env.VITE_REVERB_APP_KEY) return;
    echo = new Echo({
        broadcaster: 'reverb', client: undefined, Pusher,
        key: import.meta.env.VITE_REVERB_APP_KEY,
        wsHost: import.meta.env.VITE_REVERB_HOST || window.location.hostname,
        wsPort: Number(import.meta.env.VITE_REVERB_PORT || 8080),
        wssPort: Number(import.meta.env.VITE_REVERB_PORT || 443),
        forceTLS: (import.meta.env.VITE_REVERB_SCHEME || 'http') === 'https',
        enabledTransports: ['ws', 'wss'],
        authorizer: channel => ({
            authorize(socketId, callback) {
                auth.request('/api/broadcasting/auth', { method: 'POST', body: JSON.stringify({ socket_id: socketId, channel_name: channel.name }) })
                    .then(data => callback(null, data)).catch(error => callback(error, null));
            },
        }),
    });
    echo.private(`App.Models.User.${auth.user.id}`).notification(onNotification);
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다. |
| 4 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 5 | 현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 8 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 9 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 10 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 11 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 12 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 13 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 19 | 채널 인증 요청의 성공 또는 실패를 Echo에 전달한다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 22 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 23 | 현재 회원 전용 비공개 알림 채널을 구독한다. |
| 24 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/routes/channels.php` 전체 코드

[project/routes/channels.php](project/routes/channels.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use Illuminate\Support\Facades\Broadcast;

Broadcast::channel('App.Models.User.{id}', function ($user, $id) {
    return (int) $user->id === (int) $id;
}, ['guards' => ['sanctum']]);
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 6 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |


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


### `project/config/reverb.php` 전체 코드

[project/config/reverb.php](project/config/reverb.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default Reverb Server
    |--------------------------------------------------------------------------
    |
    | This option controls the default server used by Reverb to handle
    | incoming messages as well as broadcasting message to all your
    | connected clients. At this time only "reverb" is supported.
    |
    */

    'default' => env('REVERB_SERVER', 'reverb'),

    /*
    |--------------------------------------------------------------------------
    | Reverb Servers
    |--------------------------------------------------------------------------
    |
    | Here you may define details for each of the supported Reverb servers.
    | Each server has its own configuration options that are defined in
    | the array below. You should ensure all the options are present.
    |
    */

    'servers' => [

        'reverb' => [
            'host' => env('REVERB_SERVER_HOST', '0.0.0.0'),
            'port' => env('REVERB_SERVER_PORT', 8080),
            'path' => env('REVERB_SERVER_PATH', ''),
            'hostname' => env('REVERB_HOST'),
            'options' => [
                'tls' => [],
            ],
            'max_request_size' => env('REVERB_MAX_REQUEST_SIZE', 10_000),
            'scaling' => [
                'enabled' => env('REVERB_SCALING_ENABLED', false),
                'channel' => env('REVERB_SCALING_CHANNEL', 'reverb'),
                'server' => [
                    'url' => env('REDIS_URL'),
                    'host' => env('REDIS_HOST', '127.0.0.1'),
                    'port' => env('REDIS_PORT', '6379'),
                    'username' => env('REDIS_USERNAME'),
                    'password' => env('REDIS_PASSWORD'),
                    'database' => env('REDIS_DB', '0'),
                    'timeout' => env('REDIS_TIMEOUT', 60),
                ],
            ],
            'pulse_ingest_interval' => env('REVERB_PULSE_INGEST_INTERVAL', 15),
            'telescope_ingest_interval' => env('REVERB_TELESCOPE_INGEST_INTERVAL', 15),
        ],

    ],

    /*
    |--------------------------------------------------------------------------
    | Reverb Applications
    |--------------------------------------------------------------------------
    |
    | Here you may define how Reverb applications are managed. If you choose
    | to use the "config" provider, you may define an array of apps which
    | your server will support, including their connection credentials.
    |
    */

    'apps' => [

        'provider' => 'config',

        'apps' => [
            [
                'key' => env('REVERB_APP_KEY'),
                'secret' => env('REVERB_APP_SECRET'),
                'app_id' => env('REVERB_APP_ID'),
                'options' => [
                    'host' => env('REVERB_HOST'),
                    'port' => env('REVERB_PORT', 443),
                    'scheme' => env('REVERB_SCHEME', 'https'),
                    'useTLS' => env('REVERB_SCHEME', 'https') === 'https',
                ],
                'allowed_origins' => explode(',', env('REVERB_ALLOWED_ORIGINS', 'localhost,127.0.0.1')),
                'ping_interval' => env('REVERB_APP_PING_INTERVAL', 60),
                'activity_timeout' => env('REVERB_APP_ACTIVITY_TIMEOUT', 30),
                'max_connections' => env('REVERB_APP_MAX_CONNECTIONS'),
                'max_message_size' => env('REVERB_APP_MAX_MESSAGE_SIZE', 10_000),
                'max_channels_per_connection' => env('REVERB_APP_MAX_CHANNELS_PER_CONNECTION', 1000),
                'accept_client_events_from' => env('REVERB_APP_ACCEPT_CLIENT_EVENTS_FROM', 'members'),
                'rate_limiting' => [
                    'enabled' => env('REVERB_APP_RATE_LIMITING_ENABLED', false),
                    'max_attempts' => env('REVERB_APP_RATE_LIMIT_MAX_ATTEMPTS', 60),
                    'decay_seconds' => env('REVERB_APP_RATE_LIMIT_DECAY_SECONDS', 60),
                    'terminate_on_limit' => env('REVERB_APP_RATE_LIMIT_TERMINATE', false),
                ],
            ],
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
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 10 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 11 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 12 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 13 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 14 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 15 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 16 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 17 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 18 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 19 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 20 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 21 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 22 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 23 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 24 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 25 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 26 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 27 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 28 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 29 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 30 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 31 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 32 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 33 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 34 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 35 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 36 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 37 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 38 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 39 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 40 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 41 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 42 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 43 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 44 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 45 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 46 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 47 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 48 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 49 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 50 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 51 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 52 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 53 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 54 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 55 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 56 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 57 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 58 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 59 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 60 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 61 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 62 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 63 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 64 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 65 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 66 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 67 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 68 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 69 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 70 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 71 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 72 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 73 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 74 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 75 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 76 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 77 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 78 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 79 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 80 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 81 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 82 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 83 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 84 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 85 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 86 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 87 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 88 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 89 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 90 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 91 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 92 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 93 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 94 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 95 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 96 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 97 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 98 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 99 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 100 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 101 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 102 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 103 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

큐 요약 완료가 실시간 사건이 되고 Vue는 서버의 최신 상태를 다시 읽는다. 다음 AI 단계는 같은 문서 소유권을 유지하며 SSE로 답변 텍스트를 전달하고 MCP 읽기 도구도 연결한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 웹소켓 연결 거부 | reverb 서버·포트·키 불일치 | 서버 실행과 VITE 빌드값·브라우저 주소 확인 |
| 채널 인증 403 | 다른 사용자 id 또는 토큰 누락 | 본인 private 채널과 Bearer 헤더 확인 |
| 로컬은 되는데 HTTPS에서 실패 | ws 혼합 콘텐츠 또는 프록시 업그레이드 누락 | wss·공개 호스트·Upgrade 헤더 설정 |

## ⑥ 직접 해보기

1. 두 사용자로 로그인해 상대 채널 인증이 거부되는지 확인한다.
2. Reverb를 끊고 수동 새로고침으로 문서 상태가 여전히 보이는지 확인한다.
3. 문서 삭제 뒤 원본 파일·질문 이력이 정리되는지 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 웹소켓과 SSE의 역할을 구분했다.
- [ ] private 채널에 Sanctum과 본인 id 검사를 적용했다.
- [ ] 본인 파일만 다운로드·삭제할 수 있다.
- [ ] 실제 Reverb 수신·재연결 결과를 기록한다.

## ⑧ 다음 단계 연결

Reverb 비공개 채널로 문서 완료 알림을 보내고 파일 접근을 제한한다. 이 결과를 [study18.md](study18.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/reverb)
- [공식 문서 2](https://laravel.com/docs/13.x/broadcasting)
