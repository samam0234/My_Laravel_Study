"""실제 코드 전문·줄별 설명과 한국어 수업 내용을 study 문서에 반영한다."""
from pathlib import Path
import hashlib
import json
import re
from course_content import LESSONS

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
    'notion':'https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf',
    'api':'https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e',
    'docuforge':'https://app.notion.com/p/40bd7dec5e2e818d9c91c6fb26dccc4c',
}
OFFICIAL={
    '0':['https://laravel.com/docs/13.x/installation','https://vuejs.org/guide/quick-start.html'],
    '1':['https://laravel.com/docs/13.x/blade'],
    '2':['https://laravel.com/docs/13.x/controllers'],
    '3':['https://laravel.com/docs/13.x/session','https://laravel.com/docs/13.x/filesystem','https://vuejs.org/guide/essentials/reactivity-fundamentals.html'],
    '4':['https://laravel.com/docs/13.x/routing'],
    '5':['https://laravel.com/docs/13.x/validation'],
    '6':['https://laravel.com/docs/13.x/eloquent-resources','https://laravel.com/docs/13.x/migrations'],
    '7':['https://laravel.com/docs/13.x/sanctum','https://laravel.com/docs/13.x/csrf'],
    '8':['https://laravel.com/docs/13.x/configuration'],
    '9':['https://laravel.com/docs/13.x/http-tests','https://docs.phpunit.de/en/12.5/'],
    '10':['https://laravel.com/docs/13.x/deployment'],
    'Midpoint':['https://laravel.com/docs/13.x/eloquent-relationships'],
    '11':['https://laravel.com/docs/13.x/database','https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/'],
    '12':['https://vuejs.org/guide/introduction.html','https://v3--pinia-official.netlify.app/core-concepts/','https://vee-validate.logaretm.com/v4/guide/composition-api/getting-started/','https://getbootstrap.com/docs/5.3/getting-started/introduction/'],
    '13':['https://laravel.com/docs/13.x/socialite','https://laravel.com/docs/13.x/notifications','https://docs.stripe.com/api/checkout/sessions/create','https://docs.stripe.com/webhooks'],
    '14':['https://spec.openapis.org/oas/v3.0.3','https://laravel.com/docs/13.x/errors'],
    '15':['https://laravel.com/docs/13.x/cache','https://laravel.com/docs/13.x/queues'],
    '16':['https://docs.docker.com/build/building/multi-stage/','https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/using-secrets-in-github-actions'],
    '17':['https://laravel.com/docs/13.x/reverb','https://laravel.com/docs/13.x/broadcasting'],
    '18':['https://docs.ollama.com/api/chat','https://laravel.com/docs/13.x/mcp','https://modelcontextprotocol.io/specification/2025-11-25'],
    'Final':['https://laravel.com/docs/13.x/deployment','https://laravel.com/docs/13.x/queues'],
}
METHODS={
    'index':'목록을 조회해 응답으로 반환하는 진입점이다.', 'store':'검증한 입력으로 자원을 생성하는 진입점이다.',
    'show':'지정한 자원 한 건을 조회하는 진입점이다.', 'update':'소유권 확인 뒤 전달된 필드만 수정하는 진입점이다.',
    'destroy':'권한 확인 뒤 자원을 삭제하는 진입점이다.', 'validated':'저장할 입력의 타입·길이·필수 여부를 확정한다.',
    'login':'입력 자격증명을 확인하고 로그인 상태를 만든다.', 'logout':'현재 인증 정보를 폐기한다.',
    'signup':'신규 회원을 검증·생성한다.', 'token':'제한된 사용자 정보와 만료가 있는 토큰을 응답한다.',
    'toArray':'모델 내부 속성을 외부 JSON 계약으로 변환한다.', 'casts':'저장 값과 PHP 값의 타입 변환을 정의한다.',
    'handle':'큐·미들웨어·MCP가 호출할 작업 진입점이다.', 'schema':'MCP 도구의 허용 입력 JSON 스키마를 선언한다.',
    'stream':'실제 모델 또는 명시적인 mock의 출력 조각을 생성한다.', 'summarize':'문서 앞부분을 근거로 요약 스트림을 수집한다.',
    'excerpts':'질문과 겹치는 문서 청크를 점수순으로 고른다.', 'owned':'인증된 사용자와 문서 소유자를 비교한다.',
    'preferences':'본인 비공개 설정 파일을 읽어 뷰에 전달한다.', 'save':'검증된 값을 저장하고 화면을 다시 조회하게 한다.',
    'normalize':'태그 공백·중복·개수·유니코드 길이를 정규화한다.', 'failed':'재시도까지 끝난 실패 상태를 기록한다.',
    'backoff':'재시도 간격을 초 단위로 돌려준다.', 'uniqueId':'같은 문서의 중복 job을 막을 식별자를 반환한다.',
    'via':'알림이 전달될 채널을 설정에 따라 선택한다.', 'toMail':'메일 제목·본문·링크를 구성한다.',
    'up':'이번 DB 스키마 변경을 적용한다.', 'down':'이번 변경을 되돌리는 마이그레이션을 정의한다.',
    'webhook':'원문 서명을 검증하고 중복 수신 영수증을 저장한다.', 'checkout':'서버 가격으로 결제 테스트 세션을 요청한다.',
    'callback':'OAuth 결과를 검증하고 별도 사용자 세션을 만든다.', 'redirect':'등록된 OAuth 공급자 주소로 이동한다.',
    'history':'본인 문서 질문 이력을 조회한다.', 'download':'본인 파일을 다운로드 응답으로 보낸다.',
    'ask':'검색 근거를 사용해 답변을 SSE 이벤트로 전달한다.', 'total':'캐시에 저장한 글 수 또는 새 count 결과를 반환한다.',
    'invalidate':'변경 뒤 오래된 통계 캐시를 제거한다.', 'me':'현재 인증 사용자 공개 정보를 응답한다.',
}

def explain(line, suffix):
    s=line.strip()
    if not s: return '가독성을 위한 빈 줄이며 실행 동작은 없다.'
    if s == '<?php': return 'PHP 코드 시작을 선언한다.'
    if s.startswith('namespace '): return '이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다.'
    if s.startswith('use '): return '다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다.'
    if s.startswith(('//','# ','/*','*','<!--')): return '다음 동작·형식·설정의 의미를 설명하는 주석이다.'
    if s in ['{','[','(']: return '현재 선언·조건·설정의 내부 블록을 연다.'
    if s in ['}', '};', '});', ']);', '];', ');', '},', '],', '})']: return '현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다.'
    if s.startswith('#['): return 'PHP 속성으로 클래스의 허용 필드·이름·버전·설명을 선언한다.'
    match=re.search(r'(?:public|private|protected) (?:static )?function\s+(\w+)',s)
    if match:
        name=match.group(1)
        if name.startswith('test_'): return f'`{name}` 시나리오를 독립된 회귀 테스트로 선언한다.'
        return f'`{name}` 메서드를 선언한다. '+METHODS.get(name,'호출자에게 제공할 입력·출력 경계를 정한다.')
    if 'Route::' in s:
        route=re.search(r"Route::(\w+)\('([^']*)'",s)
        if route: return f'HTTP `{route.group(1).upper()}`의 `{route.group(2)}` 주소에 동작·제약을 등록한다.'
        return '라우트 그룹·인증 미들웨어·자원 경로를 묶어서 등록한다.'
    rules=[
        ('Gate::authorize','현재 사용자가 지정한 모델 동작을 수행할 수 있는지 Policy에 묻는다.'),
        ('->authorize(','컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다.'),
        ('->validate(','서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다.'),
        ('abort_unless','조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다.'),
        ('abort_if','조건이 참이면 지정한 오류 상태로 요청을 중단한다.'),
        ('abort(','처리할 수 없는 요청을 명시적인 HTTP 오류로 중단한다.'),
        ('DB::transaction','묶인 DB 변경이 함께 성공하거나 함께 취소되도록 트랜잭션을 연다.'),
        ('->withCount(','관계 행 수를 추가 쿼리 반복 없이 count 필드로 읽는다.'),
        ('->with(','관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다.'),
        ('->paginate(','전체 건수와 현재 페이지를 계산하고 페이지 크기를 제한한다.'),
        ('->orderBy','허용한 정렬 기준을 DB 쿼리에 적용한다.'),
        ('->latest(','지정한 열의 내림차순으로 최근 항목을 먼저 가져온다.'),
        ('->load(','응답에 필요한 관계 데이터를 모델에 추가로 불러온다.'),
        ('::query()','모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다.'),
        ('->where(','사용자 입력을 바인딩한 조회 조건을 추가한다.'),
        ('->whereLike(','DB 드라이버에 맞는 부분 일치 검색 조건을 만든다.'),
        ('->findOrFail(','id로 자원을 찾고 없으면 404 흐름으로 보낸다.'),
        ('->create(','검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다.'),
        ('->update(','이미 확인한 행에 전달된 변경값을 저장한다.'),
        ('->delete(','대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다.'),
        ('createToken','원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다.'),
        ('Hash::check','입력 비밀번호와 저장한 해시가 일치하는지 안전하게 확인한다.'),
        ('Storage::','비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다.'),
        ('Cache::remember','만료 전 캐시값을 쓰고 없으면 콜백 결과를 저장한다.'),
        ('Cache::forget','키에 연결된 오래된 결과를 무효화한다.'),
        ('Http::fake','지정한 외부 HTTP 응답을 테스트 가짜로 바꾼다.'),
        ('preventStrayRequests','가짜로 지정하지 않은 외부 HTTP가 나가지 못하게 막는다.'),
        ('::fake(','테스트에 필요한 외부 부작용을 프레임워크 가짜로 대체한다.'),
        ('assert','응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다.'),
        ('Http::','서버에서 외부 API 요청을 구성한다. 연결·전체 시간 제한을 함께 적용한다.'),
        ('->post(','정해진 주소로 요청 본문을 POST한다.'),
        ('->throw()','외부의 실패 응답을 성공 데이터로 사용하지 않고 예외로 전달한다.'),
        ('json_decode','JSON 문자열을 구조화한 값으로 바꾸고 잘못된 입력을 처리한다.'),
        ('json_encode','값을 JSON으로 직렬화한다. 민감한 필드가 포함되지 않는지 확인한다.'),
        ('yield','모든 결과를 모으기 전에 현재 텍스트 조각을 호출자에게 전달한다.'),
        ('->read(','외부 응답 스트림에서 다음 바이트 조각을 읽는다.'),
        ('->eof()','외부 스트림이 끝났는지 확인한다.'),
        ('$emit(','SSE 이벤트 한 건을 JSON data 프레임으로 브라우저에 보낸다.'),
        ('->dispatch','비동기 처리를 큐에 예약한다.'),
        ('::dispatch','문서 id를 전달해 백그라운드 작업을 큐에 예약한다.'),
        ('->notify(','사용자에게 정의한 알림 채널 전송을 예약한다.'),
        ('->session()->','현재 방문자의 세션 값을 읽거나 바꾸고 인증 경계를 갱신한다.'),
        ('Auth::','서버의 세션 인증 상태를 확인·설정·종료한다.'),
        ('Socialite::','OAuth 공급자 설정을 사용하며 세션 기반 state 검증을 유지한다.'),
        ('hash_hmac','원문과 비밀키로 서명값을 계산한다.'),
        ('hash_equals','서명 비교에서 타이밍 차이를 줄인다.'),
        ('return response()','계약에 맞는 HTTP 응답 본문·상태·헤더를 만들어 반환한다.'),
        ('return view(','명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다.'),
        ('return redirect()','처리 후 브라우저를 조회 화면으로 이동시킨다.'),
        ('Response::text','MCP 텍스트 결과를 프로토콜 응답으로 반환한다.'),
        ('Response::error','MCP 도구 실패를 오류 결과로 반환한다.'),
        ('->belongsTo','현재 모델에서 소유자나 부모 한 건을 찾는 관계를 정의한다.'),
        ('->hasMany','현재 모델의 자식 여러 건을 찾는 관계를 정의한다.'),
        ('->belongsToMany','중간 테이블을 통한 다대다 관계를 정의한다.'),
        ('Schema::create','마이그레이션에서 테이블과 제약을 생성한다.'),
        ('Schema::table','기존 테이블의 스키마를 변경한다.'),
        ('$table->','열·타입·외래키·인덱스 또는 삭제 규칙을 정의한다.'),
        ('env(','설정 경계에서 환경변수와 기본값을 읽는다.'),
        ('config(','환경에 맞게 로드한 설정값을 읽는다.'),
        ('mb_substr','UTF-8 문자 기준으로 텍스트 길이를 제한한다.'),
        ('mb_str_split','UTF-8 문자를 깨뜨리지 않고 mock 텍스트를 나눈다.'),
        ('array_key_exists','PATCH에서 누락한 필드와 명시적으로 보낸 필드를 구분한다.'),
        ('array_map','각 원소에 같은 변환을 적용한다.'),
        ('array_filter','정의한 조건에 맞지 않는 원소를 제거한다.'),
        ('array_slice','처리할 개수나 구간을 제한한다.'),
    ]
    if suffix in ['.php','.blade.php']:
        for needle, description in rules:
            if needle in s: return description
    if s.startswith('import '): return '번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다.'
    if 'defineProps' in s: return '부모 또는 마운트 진입점에서 전달받는 읽기 전용 입력을 선언한다.'
    if 'defineStore' in s: return '여러 화면 함수가 공유할 Pinia 상태와 행동을 정의한다.'
    if 'ref(' in s: return '화면이 변경을 관찰할 반응형 상태를 초기화한다.'
    if 'useForm' in s or 'defineField' in s: return '폼 입력·오류 상태를 필드와 연결한다.'
    if 'fetch(' in s or 'auth.request(' in s: return '같은 Laravel 서버에 비동기 HTTP 요청을 보낸다.'
    if 'Authorization' in s: return '현재 메모리 토큰을 Bearer 인증 헤더에 연결한다.'
    if 'TextDecoder' in s or 'decoder.decode' in s: return '스트림 조각 사이에 걸친 한글 UTF-8 바이트를 보존하며 디코딩한다.'
    if 'reader.read' in s: return '서버 스트림의 다음 데이터 조각이 도착할 때까지 읽는다.'
    if 'JSON.parse' in s or 'response.json' in s: return '응답 JSON을 화면에서 다룰 객체로 변환한다.'
    if 'JSON.stringify' in s: return '브라우저 상태를 API 요청 JSON 본문으로 변환한다.'
    if 'callback(' in s: return '채널 인증 요청의 성공 또는 실패를 Echo에 전달한다.'
    if 'echo.private' in s: return '현재 회원 전용 비공개 알림 채널을 구독한다.'
    if s.startswith('async function') or s.startswith('function '): return '재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다.'
    if s.startswith('@csrf'): return '웹 POST의 위조 요청을 막는 세션 CSRF 토큰을 숨김 필드로 출력한다.'
    if s.startswith('@props'): return 'Blade 컴포넌트가 받는 속성과 기본값을 선언한다.'
    if '@extends' in s: return '공통 Blade 레이아웃을 부모로 선택한다.'
    if '@section' in s: return '레이아웃의 지정 영역에 이 뷰 내용을 채운다.'
    if '@foreach' in s: return '서버에서 전달받은 목록을 반복해 이스케이프한 HTML을 만든다.'
    if '@error' in s: return '서버 검증에서 해당 필드에 발생한 오류를 출력한다.'
    if 'v-model' in s: return '입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다.'
    if 'v-for' in s: return '목록 상태를 key로 구분해 반복 렌더링한다.'
    if 'v-if' in s or '@if' in s or '@auth' in s: return '인증·상태·오류 조건에 맞는 UI만 렌더링한다.'
    if '@submit' in s: return '폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다.'
    if '@click' in s: return '클릭 이벤트를 화면 동작에 연결한다.'
    if '<' in s and '>' in s: return '화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다.'
    if s.startswith('FROM '): return 'Docker 빌드 단계와 기반 이미지를 선택한다.'
    if s.startswith('COPY '): return '소스 또는 이전 단계 산출물을 이미지 안으로 복사한다.'
    if s.startswith('RUN '): return '이미지 빌드 중 필요한 설치·컴파일 명령을 실행한다.'
    if s.startswith('USER '): return '런타임을 권한이 제한된 사용자로 전환한다.'
    if s.startswith('CMD ') or 'command:' in s: return '컨테이너가 시작할 프로세스와 실행 인수를 정의한다.'
    if s.startswith('ARG '): return '브라우저 공개값 등 빌드 인수를 선언한다. 비밀값은 넣지 않는다.'
    if s.startswith('WORKDIR '): return '다음 명령의 컨테이너 작업 디렉터리를 지정한다.'
    if 'secret' in s.lower() or 'password' in s.lower() or 'APP_KEY=' in s: return '민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다.'
    if re.match(r'^[A-Z_]+=.*',s): return '설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다.'
    if suffix == '.ps1':
        if s.startswith('$'): return '이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다.'
        return '명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다.'
    if suffix in ['.yaml','.yml']:
        if 'uses:' in s: return '워크플로에서 재사용할 GitHub Action을 선택한다.'
        if 'run:' in s: return 'CI 또는 배포 단계에서 실행할 명령을 선언한다.'
        if 'volumes:' in s: return '컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다.'
        if 'ports:' in s: return '허용할 호스트 주소·포트와 컨테이너 포트를 연결한다.'
        if 'env' in s: return '프로세스가 사용할 환경 설정 경계를 지정한다.'
        return '현재 서비스·작업·단계의 구성 키와 값을 선언한다.'
    if s.startswith('if ') or s.startswith('if ('): return '조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다.'
    if s.startswith(('foreach','for ','for (','while')): return '목록·청크·응답 스트림의 각 항목을 순서대로 처리한다.'
    if s.startswith(('try','catch','finally')): return '실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다.'
    if s.startswith('return '): return '구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다.'
    if '=>' in s or ':' in s: return '배열·객체·설정의 키에 값 또는 처리 함수를 연결한다.'
    if '=' in s: return '이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다.'
    if s.startswith(('const ','let ','export ')): return '현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다.'
    return '앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다.'

def code_section(path):
    text=(ROOT/path).read_text(encoding='utf-8').rstrip()
    suffix='.blade.php' if path.endswith('.blade.php') else Path(path).suffix
    language={'.php':'php','.blade.php':'blade','.js':'javascript','.vue':'vue','.ps1':'powershell','.json':'json','.yml':'yaml','.yaml':'yaml'}.get(suffix,'dockerfile' if path.endswith('Dockerfile') else 'dotenv' if '.env' in path else 'text')
    rows=[]
    for n,line in enumerate(text.splitlines(),1):
        explanation=explain(line,suffix).replace('|','\\|')
        rows.append(f'| {n} | {explanation} |')
    return f'### `{path}` 전체 코드\n\n[{path}]({path})를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.\n\n```{language}\n{text}\n```\n\n#### 줄별 설명\n\n| 줄 | 설명 |\n|---:|---|\n'+'\n'.join(rows)+'\n',hashlib.sha256((text+'\n').encode()).hexdigest()

manifest={}
for i,item in enumerate(LESSONS):
    number=item['number']; name=f'study{number}.md'
    next_name=f"study{LESSONS[i+1]['number']}.md" if i+1<len(LESSONS) else 'README.md'
    lines=[f"# study{number} · {item['title']}",
        f"학습 기준: [Laravel 노션]({SOURCES['notion']}) · 단일 구성: Laravel + Vue · [전체 순서](README.md)\n\n이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.",
        '## ① 목표 한 줄',item['goal'],'## ② 📖 이론',item['theory'],
        '## ③ 🛠️ 실기 · 전체 코드와 줄별 설명',item['steps']]
    if item['commands']:
        lines+=['### 실행 명령',f"```powershell\n{item['commands']}\n```"]
        lines+=['명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.']
    manifest[name]={}
    for path in item['files']:
        section,digest=code_section(path); lines.append(section); manifest[name][path]=digest
    lines+=['## ④ 🔗 연동 포인트',item['links'],'## ⑤ 오류 노트',
        '| 증상 | 원인 | 해결 |\n|---|---|---|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in item['errors']),
        '## ⑥ 직접 해보기','\n'.join(f'{n}. {task}' for n,task in enumerate(item['exercises'],1)),
        '## ⑦ ☐ 체크리스트','학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.\n\n'+'\n'.join('- [ ] '+task for task in item['checks'])]
    if item['extra']: lines.append(item['extra'])
    lines+=['## ⑧ 다음 단계 연결',f"{item['goal']} 이 결과를 [{next_name}]({next_name})에서 다음 실습과 연결한다." if number!='Final' else '완성한 서재를 [README](README.md)의 검증 순서로 재현하고, 외부 환경 확인 결과와 회고를 추가한다.',
        '### 근거·참고',f"[공통 API 스펙 v1]({SOURCES['api']}) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)",
        '\n'.join(f'- [공식 문서 {n}]({url})' for n,url in enumerate(OFFICIAL[number],1))]
    if number in ['18','Final']: lines.append(f"- [노션 DocuForge 학습 요구]({SOURCES['docuforge']})")
    (ROOT/name).write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'docs/code-index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/curriculum.json').write_text(json.dumps(LESSONS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(LESSONS)} study documents rendered with full sources and per-line explanations.')
