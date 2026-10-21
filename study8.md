# study8. 고급 기술 구현 3 — 검색, 페이지, 읽기 인가

웹 목록과 API 목록이 같은 검색을 쓰게 합니다. 읽기 권한은 Policy에 명시합니다. 쓰기는 여전히 웹은 세션, API는 아직 없습니다.

## 1. 검색은 모델 스코프다

조건문을 컨트롤러 두 곳에 복사하지 않으려고 `Post::scopeSearch`에 모았습니다.

```php
public function scopeSearch(Builder $query, ?string $term): Builder
{
    $term = trim((string) $term);
    if ($term === '') {
        return $query;
    }

    $like = '%'.$term.'%';

    return $query->where(function (Builder $inner) use ($like) {
        $inner->where('title', 'like', $like)->orWhere('body', 'like', $like);
    });
}
```

호출은 `->search($request->query('q'))`입니다. 빈 문자열이면 쿼리를 그대로 돌려줍니다. `%`를 양쪽에 붙이므로 "쿠키"가 제목 중간의 "쿠키"와 맞습니다. SQLite의 `like`는 기본적으로 대소문자를 가리지 않습니다.

## 2. 페이지

API는 `paginate($perPage)`입니다. `per`은 1에서 50 사이로 자릅니다. 기본은 10입니다. `withQueryString()`은 다음 페이지 주소에 `q`를 유지합니다.

Resource 컬렉션은 페이지 결과를 받으면 `data` 옆에 `links`와 `meta`를 붙입니다. `meta.total`, `meta.per_page`, `meta.current_page`를 테스트에서 확인합니다.

웹 목록은 한 페이지에 5건입니다. Blade는 `previousPageUrl()`과 `hasMorePages()`로 이전/다음만 그립니다. Tailwind 페이지네이션 뷰를 쓰지 않아서 CSS가 `public/css/app.css` 안에 남습니다. 검색 폼은 `GET /posts?q=`입니다.

## 3. 읽기 Policy

study5의 `update`와 `delete`는 작성자만 통과합니다. 읽기는 손님도 가능하지만, "누구나 된다"를 코드에 적습니다.

```php
public function viewAny(?User $user): bool
{
    return true;
}

public function view(?User $user, Post $post): bool
{
    return true;
}
```

`?User`는 손님이면 null입니다. 웹 `index`/`show`와 API `index`/`show`가 `$this->authorize`를 부릅니다. 나중에 비공개 글을 만들면 이 메서드만 고치면 두 출구가 같이 바뀝니다.

## 4. 검증

`php artisan test`는 18개, 80개 단언이 통과했습니다. 검색 테스트는 `q=라라벨&per=2`일 때 `data`가 2건, `meta.total`이 4, "다른 주제"는 빠집니다.

실행 중인 서버:

| 요청 | 결과 |
|---|---|
| `GET /api/v1/posts?q=쿠키&per=1` | `meta.total` 1. 제목은 시드의 세션 글 |
| `GET /posts?q=Eloquent` | 200. Eloquent 글만 보이고 "세션 로그인은"은 없음. 페이지 표시가 있음 |

다음 문서는 [study9.md](study9.md)입니다. Sanctum 토큰으로 API 쓰기를 엽니다.
