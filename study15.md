# study15 · 성능·캐시

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

캐시 무효화와 큐 작업을 적용하고 전후 지표로 효과를 측정한다.

## ② 📖 이론

캐시는 비싼 계산 결과를 잠시 빌려 쓰는 메모장이고 큐는 오래 걸리는 일을 접수 후 처리하는 대기표다. `/api/stats`는 전체 글 수를 30초 기억하고 API 글 생성·삭제 후 무효화한다. Blade나 외부 SQL 변경은 즉시 무효화하지 않으므로 최대30초 지연이 허용되는 통계로만 쓴다. 권한 판정·결제 상태를 이 캐시에 의존시키지 않는다.

업로드는 202로 접수하고 SummarizeDocument job이 상태를 queued→processing→ready로 바꾼다. 실패하면 재시도하고 최종 실패는 failed로 기록한다. ShouldBeUnique와 documentId로 중복 작업을 제한한다. AI timeout90초 < job/worker100초 < retry_after150초 순서를 유지해 같은 작업이 동시에 재할당되지 않게 한다. 알림도 별도 큐 작업으로 전송한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. /api/stats를 두 번 요청해 count 쿼리가 첫 요청에만 발생하는지 확인한다. 생성·삭제 뒤 total이 바뀌는 테스트를 실행한다.
2. notes·posts 목록이 user/tags/comments를 eager load하고 withCount로 댓글 개수를 가져오는지 확인한다. 반복문 안의 DB 조회는 N+1을 만든다.
3. QUEUE_CONNECTION=database와 DB_QUEUE_RETRY_AFTER=150을 설정하고 별도 터미널에서 queue:work를 실행한다. mock 요약으로 처리 상태와 알림을 확인한다.
4. 실패는 queue:failed, 로그, 문서 status로 확인하고 원인을 고친 뒤 queue:retry로 재시도한다. 성공 상태인 문서는 다시 요약하지 않는다.
5. 같은 데이터·동시성·워밍 조건에서 반복 측정한다. p50/p95 응답 시간, 요청당 SQL 수, 큐 대기 시간, AI 첫 토큰 시간을 비교한다. 숫자를 측정하지 않고 빨라졌다고 기록하지 않는다.
6. 상세 사용자 응답·문서 원문은 공용 캐시에 넣지 않는다. 서버를 늘리면 캐시와 큐 저장소를 공유해야 고유 잠금이 전 인스턴스에서 유효하다.

### 실행 명령

```powershell
cd project
php artisan queue:work --tries=3 --timeout=100
# 별도 터미널
php artisan queue:failed
php artisan test --compact --filter=DocumentTest
curl.exe -w "time=%{time_total}" http://127.0.0.1:8001/api/stats
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `project/app/Services/LibraryStats.php` 전체 코드

[project/app/Services/LibraryStats.php](project/app/Services/LibraryStats.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Cache;

class LibraryStats
{
    public function total(): int
    {
        return Cache::remember('study.total', 30, fn () => config('study.model')::query()->count());
    }

    public function invalidate(): void
    {
        Cache::forget('study.total');
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
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | `total` 메서드를 선언한다. 캐시에 저장한 글 수 또는 새 count 결과를 반환한다. |
| 10 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 11 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 12 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | `invalidate` 메서드를 선언한다. 변경 뒤 오래된 통계 캐시를 제거한다. |
| 15 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 16 | 키에 연결된 오래된 결과를 무효화한다. |
| 17 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/app/Jobs/SummarizeDocument.php` 전체 코드

[project/app/Jobs/SummarizeDocument.php](project/app/Jobs/SummarizeDocument.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Jobs;

use App\Models\Document;
use App\Notifications\DocumentReady;
use App\Services\DocumentAi;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Throwable;

class SummarizeDocument implements ShouldBeUnique, ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public int $timeout = 100;

    public int $uniqueFor = 180;

    public function uniqueId(): string
    {
        return (string) $this->documentId;
    }

    public function __construct(public int $documentId) {}

    public function backoff(): array
    {
        return [10, 30, 60];
    }

    public function handle(DocumentAi $ai): void
    {
        $document = Document::query()->find($this->documentId);
        if (! $document || $document->status === 'ready') {
            return;
        }
        $document->update(['status' => 'processing']);
        $summary = $ai->summarize($document->content);
        $document->update(['summary' => $summary, 'status' => 'ready']);
        $document->user->notify(new DocumentReady($document->id));
    }

    public function failed(?Throwable $exception): void
    {
        Document::query()->whereKey($this->documentId)->update(['status' => 'failed']);
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
| 17 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 18 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 19 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 20 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 21 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | `uniqueId` 메서드를 선언한다. 같은 문서의 중복 job을 막을 식별자를 반환한다. |
| 24 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 25 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 26 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 27 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 28 | `__construct` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 29 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 30 | `backoff` 메서드를 선언한다. 재시도 간격을 초 단위로 돌려준다. |
| 31 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 32 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 33 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | `handle` 메서드를 선언한다. 큐·미들웨어·MCP가 호출할 작업 진입점이다. |
| 36 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 37 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 38 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 39 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 40 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 41 | 이미 확인한 행에 전달된 변경값을 저장한다. |
| 42 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 43 | 이미 확인한 행에 전달된 변경값을 저장한다. |
| 44 | 사용자에게 정의한 알림 채널 전송을 예약한다. |
| 45 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 46 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 47 | `failed` 메서드를 선언한다. 재시도까지 끝난 실패 상태를 기록한다. |
| 48 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 49 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 50 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 51 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


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


## ④ 🔗 연동 포인트

큐는 문서 저장과 AI 호출의 응답 시간을 분리한다. 다음 운영 단계는 worker·scheduler를 웹 프로세스와 별도로 실행하고 같은 이미지·DB·파일 볼륨에 연결한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 문서가 queued에 머묾 | worker가 실행되지 않음 | queue:work와 DB jobs 테이블 확인 |
| 같은 작업이 중복됨 | retry_after가 작업 timeout보다 짧음 | 90 < 100 < 150 순서를 적용하고 worker 재시작 |
| 변경 후 통계가 예전 값 | 캐시 무효화 누락 또는 다른 쓰기 경로 | API 무효화·30초 TTL을 확인하고 일관성 요구 재설계 |

## ⑥ 직접 해보기

1. AI 가짜 응답을 실패로 바꿔 재시도·failed 상태를 기록한다.
2. 동일 조건에서 stats 첫 요청과 두 번째 요청 시간을 10회 측정한다.
3. with를 제거했을 때 SQL 수가 늘어나는지 실험 후 복원한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 캐시 TTL·키·무효화 범위를 설명했다.
- [ ] 작업·워커·retry_after 타임아웃 순서를 맞췄다.
- [ ] N+1·SQL 수·응답 시간을 측정한다.
- [ ] 외부 호출 실패와 재시도를 검증했다.

## ⑧ 다음 단계 연결

캐시 무효화와 큐 작업을 적용하고 전후 지표로 효과를 측정한다. 이 결과를 [study16.md](study16.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/cache)
- [공식 문서 2](https://laravel.com/docs/13.x/queues)
