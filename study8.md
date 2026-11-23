# study8 · 구조화·재사용

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

문자열 규칙·화면 조각·요청 처리를 추출하고 개발·운영 설정을 나눈다.

## ② 📖 이론

재사용은 동일한 업무 규칙이 여러 곳에서 다르게 바뀌는 일을 막기 위해 한다. TagNames는 태그 공백·중복·길이·개수를 한 곳에서 정리한다. Blade status 컴포넌트는 같은 알림 HTML을 반복하지 않게 한다. Pinia request는 인증·JSON·오류 해석을 모은다. 자주 쓰는 연장을 공용 공구함에 넣는 것과 같다.

컨트롤러는 HTTP, 서비스는 계산과 외부 작업, 모델은 행과 관계, Resource는 외부 JSON 표현을 맡는다. config 파일에서만 env를 읽으면 config:cache 뒤에도 설정이 일관된다. `APP_ENV`, `APP_DEBUG`, DB·메일·AI 연결은 배포별로 다르고 코드 구조는 같다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. TagNames::normalize 입력에 공백·중복·빈 값·문자열 0을 넣어 정규화 규칙을 확인한다.
2. 컴포넌트의 @props 기본값과 호출부의 :message를 확인한다. 선택하지 않은 추가 화면 프레임워크는 설치하지 않는다.
3. `.env.example`은 변수 이름과 안전한 기본값만 제공한다. 운영 변수는 비밀 저장소나 호스트 환경에서 주입한다.
4. 운영에서 APP_DEBUG=false, HTTPS URL, 안전한 쿠키, stderr 로그를 지정한다. 설정 변경 뒤 config:clear 또는 새 프로세스 재시작이 필요하다.
5. src 간 공유를 위해 다른 앱 폴더를 직접 require하지 않는다. demo와 project는 같은 Laravel 학습 과정의 별도 실행 결과다.

### `demo/app/Support/TagNames.php` 전체 코드

[demo/app/Support/TagNames.php](demo/app/Support/TagNames.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Support;

class TagNames
{
    public static function normalize(array $names): array
    {
        $names = array_map(fn (string $name): string => mb_substr(trim($name), 0, 30), $names);

        return array_slice(array_values(array_unique(array_filter($names, fn ($name) => $name !== ''))), 0, 8);
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
| 7 | `normalize` 메서드를 선언한다. 태그 공백·중복·개수·유니코드 길이를 정규화한다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | UTF-8 문자 기준으로 텍스트 길이를 제한한다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 정의한 조건에 맞지 않는 원소를 제거한다. |
| 12 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 13 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/resources/views/components/status.blade.php` 전체 코드

[demo/resources/views/components/status.blade.php](demo/resources/views/components/status.blade.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```blade
@props(['message' => null])
@if ($message)
    <p role="status">{{ $message }}</p>
@endif
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | Blade 컴포넌트가 받는 속성과 기본값을 선언한다. |
| 2 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 3 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 4 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |


### `demo/config/study.php` 전체 코드

[demo/config/study.php](demo/config/study.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use App\Models\Post;

return [
    'model' => Post::class,
    'relation' => 'posts',
    'ai_driver' => env('AI_DRIVER', 'mock'),
    'ai_url' => env('AI_URL', 'http://127.0.0.1:11434'),
    'ai_model' => env('AI_Post', 'gemma4:12b'),
];
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 6 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 8 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 9 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 10 | 설정 경계에서 환경변수와 기본값을 읽는다. |
| 11 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/docker/production.env.example` 전체 코드

[project/docker/production.env.example](project/docker/production.env.example)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```dotenv
APP_NAME=StudyShelf
APP_ENV=production
APP_KEY=base64:replace-with-php-artisan-key-generate-show
APP_DEBUG=false
APP_URL=https://study.example.com
LOG_CHANNEL=stderr
LOG_LEVEL=warning
DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE=study
DB_USERNAME=study
DB_PASSWORD=replace-with-random-password
POSTGRES_DB=study
POSTGRES_USER=study
POSTGRES_PASSWORD=replace-with-same-db-password
SESSION_DRIVER=database
SESSION_SECURE_COOKIE=true
CACHE_STORE=database
QUEUE_CONNECTION=database
DB_QUEUE_RETRY_AFTER=150
FILESYSTEM_DISK=local
MAIL_MAILER=log
MAIL_FROM_ADDRESS=study@example.com
MAIL_FROM_NAME=StudyShelf
AI_DRIVER=mock
AI_URL=http://host.docker.internal:11434
AI_MODEL=gemma4:12b
BROADCAST_CONNECTION=log
REVERB_APP_ID=study
REVERB_APP_KEY=replace-public-key
REVERB_APP_SECRET=replace-secret
REVERB_HOST=reverb
REVERB_PORT=8080
REVERB_SCHEME=http
REVERB_ALLOWED_ORIGINS=study.example.com
CORS_ORIGIN=https://study.example.com
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 2 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 3 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 4 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 5 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 6 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 7 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 8 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 9 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 10 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 11 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 12 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 13 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 14 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 15 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 16 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 17 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 18 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 19 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 20 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 21 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 22 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 23 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 24 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 25 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 26 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 27 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 28 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 29 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 30 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 31 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 32 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 33 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 34 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 35 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 36 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 37 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |


## ④ 🔗 연동 포인트

순수 정규화 함수는 다음 단계의 빠른 단위 테스트 대상이다. HTTP·DB가 필요한 테스트는 Laravel Feature 테스트로 분리한다. 환경변수와 요청 공통 처리는 이후 Docker·외부 서비스에서도 그대로 사용한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 설정값이 예전 그대로 | config 캐시에 이전 .env가 남음 | 개발은 config:clear, 운영은 새 환경에서 캐시 재생성 |
| 태그 0이 사라짐 | 기본 array_filter가 문자열 0도 제거 | 빈 문자열과 명시적으로 비교 |
| 노트의 태그가 없어짐 | PATCH 누락 필드를 빈 배열로 취급 | array_key_exists로 실제 전달 여부 검사 |

## ⑥ 직접 해보기

1. TagNames에 한글 40자를 넣어 30자로 제한되는지 확인한다.
2. 동일한 status 컴포넌트를 다른 Blade 뷰에서 호출한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 공통 유틸·뷰·HTTP 처리를 분리했다.
- [ ] 설정 코드에서만 env를 읽었다.
- [ ] 개발·운영의 APP_DEBUG와 연결값을 구분했다.

## ⑧ 다음 단계 연결

문자열 규칙·화면 조각·요청 처리를 추출하고 개발·운영 설정을 나눈다. 이 결과를 [study9.md](study9.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/configuration)
