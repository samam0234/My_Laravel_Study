# study10. 고급 기술 구현 5 — CORS와 브라우저 클라이언트

`js/demo`와 `ts/demo`는 Laravel과 다른 포트에서 열립니다. 브라우저는 `http://127.0.0.1:5173`에서 `http://127.0.0.1:8000`으로의 요청을 막습니다. `config/cors.php`가 `api/*`만 엽니다.

허용 origin:

| 폴더 | 주소 |
|---|---|
| js/demo | http://127.0.0.1:5173 |
| ts/demo | http://127.0.0.1:5174 |
| js/project | http://127.0.0.1:5180 |
| ts/project | http://127.0.0.1:5181 |

그 외 origin은 `Access-Control-Allow-Origin`에 그대로 실리지 않습니다. `supports_credentials`는 false입니다. 쿠키 세션은 Blade가 쓰고, 이 화면들은 `Authorization: Bearer`만 보냅니다.

두 클라이언트는 Laravel 코드를 수정하지 않습니다. `js/demo`는 의존성 없는 `node server.mjs`입니다. `ts/demo`는 Vite와 TypeScript입니다. 토큰은 각자 `sessionStorage`에 둡니다. JS 키는 `laravel.demo.token`, TS 키는 `laravel.demo.ts.token`입니다.

목록 JSON은 `data` 배열과 `meta.current_page`, `meta.last_page`, `meta.per_page`, `meta.total`입니다. 글 하나와 댓글 목록도 `data`로 감쌉니다. 화면은 목록, 검색, 페이지, 로그인, 로그아웃, 글 작성, 상세, 댓글 작성을 합니다.

## 검증

`php artisan test`

```
Tests:    21 passed (96 assertions)
Duration: 1.43s
```

`CorsTest`만 보면 2 passed (5 assertions)입니다. `Origin: http://127.0.0.1:5173` 목록은 200이고 같은 origin을 돌려줍니다. `http://evil.example`은 그 값을 헤더에 실지 않습니다.

실행 중인 서버에서 확인한 preflight:

| Origin | GET /api/v1/posts | OPTIONS |
|---|---|---|
| http://127.0.0.1:5173 | 200, Allow-Origin 동일 | 204, Allow-Methods POST, Allow-Headers authorization,content-type |
| http://127.0.0.1:5174 | 200, Allow-Origin 동일 | 204, Allow-Methods POST |

`js/demo`의 `node --test`는 3개 통과입니다. 그 클라이언트로 검색 `q=Eloquent`를 호출하면 total 1, 제목은 “Eloquent는 한 줄이 객체다”, 작성자는 미나입니다. `POST /api/v1/login`은 `token_type` Bearer, 이름 미나, 토큰 길이 50입니다. 이어서 로그아웃은 204입니다.

`ts/demo`의 `npm test`는 4개 통과입니다. `tsc --noEmit`과 `vite build`도 통과했습니다. `http://127.0.0.1:5173/`과 `http://127.0.0.1:5174/`는 둘 다 200이고 제목 영역에 “게시판 API”가 있습니다.

이 환경에는 브라우저 자동화 도구가 없어서, 클릭 대신 테스트와 HTTP로 확인했습니다.

`node_modules/`와 `dist/`는 커밋하지 않습니다.

다음 문서는 [studyFinal.md](studyFinal.md)입니다. 같은 기술을 게시판이 아닌 학습 서재로 다시 조립합니다.
