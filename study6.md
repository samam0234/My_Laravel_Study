# study6 · DB·API 연동

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

환경변수·마이그레이션·모델·CRUD를 공통 API v1 계약으로 연결한다.

## ② 📖 이론

DB 연결은 `.env → config/database.php → Eloquent`를 거친다. 마이그레이션은 테이블 설계의 이력이고 모델은 행의 사용법이다. 창고 설계도와 실제 물품 대장에 비유할 수 있다. 공개 목록과 상세는 조회, 생성·수정·삭제는 인증과 소유권 확인 뒤 실행한다.

공통 API **스펙 이름**이 v1이며 기준 주소는 `/api`다. `/api/v1`은 이전 실습 호환 경로로 남겼다. 새 화면은 `/api`만 부른다. 목록은 `data`와 `meta.page/limit/total/totalPages/q`, 단건은 `data`, 날짜는 UTC ISO 8601, 필드는 camelCase다. 생성은 201과 Location, 삭제는 빈 204를 보낸다. id·createdAt은 클라이언트 입력으로 저장하지 않는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. SQLite 연결을 준비하고 `migrate`로 posts·comments·tokens·tags JSON 컬럼을 만든다. 기존 DB를 지우는 migrate:fresh는 사용하지 않는다.
2. GET 목록·상세를 먼저 호출한 뒤 회원가입/로그인 토큰으로 POST·PATCH·DELETE를 실행한다.
3. ContractController의 검증 → 트랜잭션 → 관계 저장 → Resource 직렬화 순서를 읽는다. user 관계로 저장하므로 입력 user_id를 무시한다.
4. tags는 JSON 문자열이 아니라 문자열 배열이다. `limit`은 1 이상이며 50 초과는 50으로 제한한다. 검색·정렬 허용값을 고정한다.
5. 공통 게시판 규격의 댓글 주소도 연결한다. `project`의 `/api/posts`는 서재 Note를 같은 계약으로 제공하고 댓글의 내부 FK는 note_id다. Blade의 `/notes` 모델과 같은 DB 행을 읽는다.
6. 연결 실패는 서버 로그의 requestId로 조사한다. 운영 응답에 DB 접속 정보나 예외 스택을 내보내지 않는다.

### 실행 명령

```powershell
cd demo
php artisan migrate
php artisan migrate:status
curl.exe -i "http://127.0.0.1:8000/api/posts?limit=2&sort=-createdAt"
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `demo/app/Http/Controllers/Api/ContractController.php` 전체 코드

[demo/app/Http/Controllers/Api/ContractController.php](demo/app/Http/Controllers/Api/ContractController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\EntryResource;
use App\Services\LibraryStats;
use App\Support\TagNames;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Gate;
use Symfony\Component\HttpFoundation\Response;

class ContractController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $request->validate(['q' => ['nullable', 'string', 'max:200'], 'page' => ['sometimes', 'integer', 'min:1'],
            'limit' => ['sometimes', 'integer', 'min:1'], 'sort' => ['sometimes', 'in:createdAt,-createdAt,-commentCount']]);
        $query = config('study.model')::query()->with(['user'])->search($request->query('q'));
        $query->withCount('comments');
        $sort = $request->query('sort', '-createdAt');
        if ($sort === '-commentCount') {
            $query->orderByDesc('comments_count');
        } else {
            $query->orderBy('created_at', $sort === 'createdAt' ? 'asc' : 'desc');
        }
        $items = $query->orderBy('id', $sort === 'createdAt' ? 'asc' : 'desc')
            ->paginate(min($request->integer('limit', 10), 50));

        return response()->json(['data' => EntryResource::collection($items)->resolve($request), 'meta' => [
            'page' => $items->currentPage(), 'limit' => $items->perPage(), 'total' => $items->total(),
            'totalPages' => $items->lastPage(), 'q' => $request->query('q', ''),
        ]]);
    }

    public function show(int $id): EntryResource
    {
        return new EntryResource(config('study.model')::query()->with(['user'])->withCount('comments')->findOrFail($id));
    }

    public function store(Request $request): JsonResponse
    {
        $data = $this->validated($request);
        if (isset($data['tags'])) {
            $data['tags'] = TagNames::normalize($data['tags']);
        }
        $entry = DB::transaction(function () use ($request, $data) {
            $relation = config('study.relation');
            $entry = $request->user()->{$relation}()->create($data);

            return $entry;
        });
        app(LibraryStats::class)->invalidate();

        return (new EntryResource($entry->load(['user'])))->response()->setStatusCode(201)
            ->header('Location', '/api/posts/'.$entry->id);
    }

    public function update(Request $request, int $id): EntryResource
    {
        $entry = config('study.model')::query()->findOrFail($id);
        Gate::authorize('update', $entry);
        $data = $this->validated($request, true);
        if (isset($data['tags'])) {
            $data['tags'] = TagNames::normalize($data['tags']);
        }
        DB::transaction(function () use ($entry, $data): void {
            $entry->update($data);

        });

        return new EntryResource($entry->load(['user'])->loadCount('comments'));
    }

    public function destroy(int $id): Response
    {
        $entry = config('study.model')::query()->findOrFail($id);
        Gate::authorize('delete', $entry);
        $entry->delete();
        app(LibraryStats::class)->invalidate();

        return response()->noContent();
    }

    private function validated(Request $request, bool $partial = false): array
    {
        return $request->validate([
            'title' => [$partial ? 'sometimes' : 'required', 'required', 'string', 'max:200'],
            'body' => [$partial ? 'sometimes' : 'required', 'required', 'string', 'max:20000'],
            'tags' => ['sometimes', 'array', 'max:8'], 'tags.*' => ['required', 'string', 'max:30', 'distinct'],
        ]);
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
| 14 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 15 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 16 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 17 | `index` 메서드를 선언한다. 목록을 조회해 응답으로 반환하는 진입점이다. |
| 18 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 19 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 20 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 21 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 22 | 관계 행 수를 추가 쿼리 반복 없이 count 필드로 읽는다. |
| 23 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 24 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 25 | 허용한 정렬 기준을 DB 쿼리에 적용한다. |
| 26 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 27 | 허용한 정렬 기준을 DB 쿼리에 적용한다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 허용한 정렬 기준을 DB 쿼리에 적용한다. |
| 30 | 전체 건수와 현재 페이지를 계산하고 페이지 크기를 제한한다. |
| 31 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 32 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 33 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 34 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 35 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | `show` 메서드를 선언한다. 지정한 자원 한 건을 조회하는 진입점이다. |
| 39 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 40 | 관계 행 수를 추가 쿼리 반복 없이 count 필드로 읽는다. |
| 41 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 42 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 43 | `store` 메서드를 선언한다. 검증한 입력으로 자원을 생성하는 진입점이다. |
| 44 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 45 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 46 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 47 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 48 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 49 | 묶인 DB 변경이 함께 성공하거나 함께 취소되도록 트랜잭션을 연다. |
| 50 | 환경에 맞게 로드한 설정값을 읽는다. |
| 51 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 52 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 53 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 54 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 55 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 56 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 57 | 응답에 필요한 관계 데이터를 모델에 추가로 불러온다. |
| 58 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 61 | `update` 메서드를 선언한다. 소유권 확인 뒤 전달된 필드만 수정하는 진입점이다. |
| 62 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 63 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 64 | 현재 사용자가 지정한 모델 동작을 수행할 수 있는지 Policy에 묻는다. |
| 65 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 66 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 67 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 68 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 69 | 묶인 DB 변경이 함께 성공하거나 함께 취소되도록 트랜잭션을 연다. |
| 70 | 이미 확인한 행에 전달된 변경값을 저장한다. |
| 71 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 72 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 73 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 74 | 응답에 필요한 관계 데이터를 모델에 추가로 불러온다. |
| 75 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 76 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 77 | `destroy` 메서드를 선언한다. 권한 확인 뒤 자원을 삭제하는 진입점이다. |
| 78 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 79 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 80 | 현재 사용자가 지정한 모델 동작을 수행할 수 있는지 Policy에 묻는다. |
| 81 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 82 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 83 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 84 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 85 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 86 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 87 | `validated` 메서드를 선언한다. 저장할 입력의 타입·길이·필수 여부를 확정한다. |
| 88 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 89 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 90 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 91 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 92 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 93 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 94 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 95 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Http/Resources/EntryResource.php` 전체 코드

[demo/app/Http/Resources/EntryResource.php](demo/app/Http/Resources/EntryResource.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EntryResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id, 'title' => $this->title, 'body' => $this->body,
            'tags' => ($this->tags ?? []),
            'author' => $this->user ? ['id' => $this->user->id, 'nickname' => $this->user->name] : null,
            'commentCount' => (int) ($this->comments_count ?? 0),
            'createdAt' => $this->created_at?->utc()->toISOString(),
            'updatedAt' => $this->updated_at?->utc()->toISOString(),
        ];
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
| 10 | `toArray` 메서드를 선언한다. 모델 내부 속성을 외부 JSON 계약으로 변환한다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 13 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/app/Http/Controllers/Api/CommentContractController.php` 전체 코드

[demo/app/Http/Controllers/Api/CommentContractController.php](demo/app/Http/Controllers/Api/CommentContractController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Symfony\Component\HttpFoundation\Response;

class CommentContractController extends Controller
{
    public function index(Post $post): JsonResponse
    {
        return response()->json(['data' => $post->comments()->with('user')->oldest('id')->get()->map($this->serialize(...))]);
    }

    public function store(Request $request, Post $post): JsonResponse
    {
        $data = $request->validate(['body' => ['required', 'string', 'max:1000']]);
        $comment = $post->comments()->make($data);
        $comment->user()->associate($request->user());
        $comment->save();

        return response()->json(['data' => $this->serialize($comment->load('user'))], 201);
    }

    public function destroy(Comment $comment): Response
    {
        Gate::authorize('delete', $comment);
        $comment->delete();

        return response()->noContent();
    }

    private function serialize(Comment $comment): array
    {
        return ['id' => $comment->id, 'postId' => $comment->post_id, 'body' => $comment->body,
            'author' => $comment->user ? ['id' => $comment->user->id, 'nickname' => $comment->user->name] : null,
            'createdAt' => $comment->created_at?->utc()->toISOString()];
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
| 15 | `index` 메서드를 선언한다. 목록을 조회해 응답으로 반환하는 진입점이다. |
| 16 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 17 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 20 | `store` 메서드를 선언한다. 검증한 입력으로 자원을 생성하는 진입점이다. |
| 21 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 22 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 23 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 24 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 25 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 26 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 27 | 응답에 필요한 관계 데이터를 모델에 추가로 불러온다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 30 | `destroy` 메서드를 선언한다. 권한 확인 뒤 자원을 삭제하는 진입점이다. |
| 31 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 32 | 현재 사용자가 지정한 모델 동작을 수행할 수 있는지 Policy에 묻는다. |
| 33 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | 계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | `serialize` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 39 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 40 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 41 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 42 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 43 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 44 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/database/migrations/2026_11_23_135403_add_tags_to_posts.php` 전체 코드

[demo/database/migrations/2026_11_23_135403_add_tags_to_posts.php](demo/database/migrations/2026_11_23_135403_add_tags_to_posts.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('posts', fn (Blueprint $table) => $table->json('tags')->nullable());
    }

    public function down(): void
    {
        Schema::table('posts', fn (Blueprint $table) => $table->dropColumn('tags'));
    }
};
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | `up` 메서드를 선언한다. 이번 DB 스키마 변경을 적용한다. |
| 10 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 11 | 기존 테이블의 스키마를 변경한다. |
| 12 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | `down` 메서드를 선언한다. 이번 변경을 되돌리는 마이그레이션을 정의한다. |
| 15 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 16 | 기존 테이블의 스키마를 변경한다. |
| 17 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

API는 Vue·Blade가 함께 사용하는 DB의 명시적인 입출력 경계다. 다음 단계에서 Sanctum 토큰과 세션 인증, Policy가 쓰기 권한을 제한한다. 연결 정보는 환경변수로 분리했으며 PostgreSQL·MariaDB 전환은 study11에서 수행한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| no such table | 마이그레이션 전 또는 다른 DB를 가리킴 | config:clear 후 migrate:status와 DB_DATABASE 확인 |
| MassAssignmentException | fillable과 검증 결과 불일치 | 허용한 업무 필드만 모델로 전달; user_id 추가로 해결하지 않음 |
| 422 또는 400 | 필수값·tags 타입 위반 | 기준 API는 tags 배열, 기존 v1은 쉼표 문자열이라는 계약 차이 확인 |

## ⑥ 직접 해보기

1. limit=999 요청이 50으로 제한되는지 확인한다.
2. 태그 배열로 생성하고 제목만 PATCH해 태그가 유지되는지 확인한다.
3. 없는 글, 인증 없음, 남의 글 변경을 각각 요청한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] Eloquent 모델 + 마이그레이션
- [ ] 게시판 CRUD
- [ ] 경로 `/api/v1`을 스펙의 `/api`와 맞출지 결정
- [ ] 연결값을 .env로 분리했다.
- [ ] Location·204·태그 배열 계약을 확인했다.

## ⑧ 다음 단계 연결

환경변수·마이그레이션·모델·CRUD를 공통 API v1 계약으로 연결한다. 이 결과를 [study7.md](study7.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/eloquent-resources)
- [공식 문서 2](https://laravel.com/docs/13.x/migrations)
