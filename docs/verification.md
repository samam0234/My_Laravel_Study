# 검증 기록

검증일: 2026-11-23 (Asia/Seoul). 코드·문서 준비, 로컬 실행, 실제 외부 서비스 연결을 구분한다.

## 수행 결과

| 검사 | 실제 결과 |
|---|---|
| demo 전체 테스트 | 37 passed, 190 assertions |
| project 전체 테스트 | 39 passed, 194 assertions |
| PHP Pint | 두 앱 통과, Mongo 선택 예제도 형식 적용 |
| Vue 운영 빌드 | 두 앱 통과; 앱과 Swagger 문서 진입점 별도 생성 |
| composer audit | 두 앱 취약점 경고 0 |
| npm audit --omit=dev | 두 앱 취약점 0 |
| 문서 자동 검사 | 21개·8절·직접 해보기·원문 체크·로컬 링크·전체 코드 해시·API 경로 검사 통과 |
| Docker Compose | 로컬 DB profiles와 운영 구성의 변수·구문 검증 통과 |
| 실제 HTTP | /health, /app, /api-docs, /openapi.json 모두 200 |
| 실제 API 연결 | 가입·토큰·글 생성/부분 수정/삭제·태그·댓글 통과 |
| 실제 큐·AI mock | 비공개 업로드→DB job→실제 queue:work→ready 요약→SSE delta/done→질문 이력 통과 |
| 실제 MCP Client | 별도 CLI의 connect→tools/list→tools/call로 HTTP 서버의 본인 문서 읽기 통과 |
| 브라우저 UI | 연결 호스트가 unavailable이고 사용 가능한 browser 목록이 없어 클릭·시각 검증 미수행 |
| 노션 갱신 | 기존 Laravel 페이지의 단일 구성·API 체크·학습 이력을 갱신하고 21개 과정·근거·미검증 항목을 추가 |

실제 연결 시험은 `python -X utf8 tools/smoke_local.py http://127.0.0.1:8111`로 재현한다. 시작 전에 project 개발 서버가 필요하다. 시험 글·댓글·파일·문서·질문·토큰은 API로 정리하며 로컬 시험 회원 한 명은 남긴다. 이 스크립트는 루프백 개발 서버만 허용한다. 이전 노션의 21+9 결과는 과거 이력이며 현재 결과로 재사용하지 않았다.

Swagger UI 번들은 약1.55MB로 Vite의 큰 청크 안내가 나온다. `/api-docs`의 별도 진입점이므로 일반 앱 화면이 이 문서 번들을 내려받지는 않는다. 일반 앱 JavaScript는 demo 약106KB, project 약199KB다(압축 전). 성능 개선 수치로 주장하지 않는다.

## 외부 환경 확인 항목

| 항목 | 현재 조건·확인 방법 |
|---|---|
| Docker 이미지 실행 | Docker CLI는 있지만 Linux 엔진 소켓이 없다. compose 구문 검증과 실제 빌드를 구분한다. |
| PostgreSQL·MariaDB | 로컬 PHP는 pdo_sqlite만 활성화. profile·전환 도구·CI DB 행렬을 제공하며 실제 DB 테스트 결과를 추가한다. |
| MongoDB | ext-mongodb와 선택 패키지는 기본 의존성에 설치하지 않았다. 선택 보관 예제·연결 설정·절차를 제공한다. |
| Ollama 실제 생성 | 기본 mock과 HTTP fake로 파이프라인·스트림·실패·이력을 확인한다. 실제 모델 설치·추론 품질은 별도 기록한다. |
| Stripe·GitHub OAuth·SMTP | 테스트 HTTP·서명·provider mock·로컬 메일 방식으로 경계를 검증한다. 공급자 계정으로 왕복·메일 수신·실결제를 수행하지 않는다. |
| Reverb 실제 소켓 | private 채널 인증/거부 테스트와 클라이언트·서버 설정을 제공한다. 실제 수신·재연결을 별도로 기록한다. |
| 원격 배포·HTTPS·복원 | 호스트·SSH·도메인·운영 비밀값이 제공되지 않았다. Docker·배포 workflow·백업과 격리 복원 절차를 제공한다. |

## 추적

[노션 요구사항 매핑](notion-coverage.md), [최종 배포 점검](../studyFinal.md), [운영 문서](../study16.md)를 함께 확인한다. 추가 체크 항목 누락은 없으며 이 표의 미검증 상태와 구분한다.
