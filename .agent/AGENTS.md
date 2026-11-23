# Laravel 학습 저장소 공통 지침

기준은 Laravel 노션과 사용자의 이번 요청이다. Laravel + Vue 한 구성으로 진행하며 다른 프레임워크 비교·조합이나 독립 JS/TS 화면을 추가하지 않는다.

- study0~10 → studyMidpoint → study11~18 → studyFinal 순서다. 루트 학습 파일에는 study 접두사를 쓴다.
- demo는 기초 게시판(8000), project는 심화 AI 학습 서재(8001)다. 운영은 project 하나를 배포한다.
- Vue는 앱 내부 resources/js의 SFC이며 Laravel /app에서 같은 호스트 /api를 호출한다. Node는 자산 빌드 도구다.
- 표준 API는 공통 스펙 v1의 /api다. /api/v1은 이전 학습 호환 경로다. 표준 검증 오류는 400, 이전 경로는 422다.
- API 변경은 Resource·컨트롤러·OpenAPI·테스트·관련 study를 함께 수정한다. user_id는 요청 입력으로 저장하지 않는다.
- 업로드 문서·질문·다운로드·MCP는 본인만 접근한다. 문서·모델 출력을 HTML로 실행하지 않는다.
- 문서·커밋 설명은 한글, 식별자·파일명·커밋 타입은 영어로 쓴다. COMMIT_GUIDE.md를 따른다.
- 각 앱 AGENTS.md와 설치된 패키지 버전을 확인한다. 동작 변경에 맞는 테스트를 실행한다.
- PHP 변경 후 Pint, 앱 테스트·Vue 빌드·감사를 수행한다. 소스 변경 뒤 python tools/render_course.py와 python tools/check_course.py로 문서를 갱신·검사한다.
- 원문 추가 체크 항목은 해당 study ⑦ 체크리스트에서 문구를 보존한다. docs/notion-coverage.md에 추적한다.
- .env 실값·SQLite·vendor·node_modules·백업·생성 빌드는 커밋하지 않는다. .env.example과 잠금 파일은 커밋한다.
- 외부 DB·모델·메일·OAuth·결제·Docker·원격 배포 실행 여부는 docs/verification.md에 사실대로 기록한다.
- 문서·코드 검증 후 요청받은 Laravel 노션을 갱신한다. 이전 학습 기록은 이력으로 보존하고 새 구성·근거·미검증 범위를 구분한다.

현재 인수인계: 전체 과정과 단일 Vue 구성으로 개편했다. 다음 작업은 실제 외부 환경 검증과 사용자가 선택한 기능 개선이며 구체적 결과는 검증 기록을 따른다.
