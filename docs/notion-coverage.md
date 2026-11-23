# 노션 요구사항 매핑

기준일: 2026-11-23 (Asia/Seoul). [Laravel 원문](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf), [공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e), [미니 프로젝트 목록](https://app.notion.com/p/40bd7dec5e2e81dab88fda4b558aa498), [DocuForge 상세](https://app.notion.com/p/40bd7dec5e2e818d9c91c6fb26dccc4c)를 읽어 반영했다. Laravel 원문에는 별도 하위 페이지·생략된 블록이 없었다.

사용자 지시에 따라 단일 Laravel + Vue로 구성하고 원문에 있던 타 프레임워크 비교·조합 방향은 학습 범위에서 제외했다. DocuForge의 요구인 요약·문서 근거 답변·질문 이력을 Laravel 안에서 구현한다. 기존 DocuForge 서버나 저장소를 수정·호출하지 않는다.

## 원문 학습 목표

| 원문 항목 | 문서 | 구현·검증 |
|---|---|---|
| Laravel 프로젝트 (composer create-project) | study0 | Composer 잠금 파일·Artisan·설치 과정 |
| 라우팅 / 컨트롤러 / 뷰 | study2·4 | web/api 라우트·Home·Learning·Blade |
| Eloquent 모델 + 마이그레이션 | study6·11 | Post/Comment, Note/Tag/note_tag |
| Blade 템플릿 또는 API (Sanctum) | study7 | 웹 세션·토큰·로그아웃·소유권 |
| 인증 (Breeze / Jetstream / 직접) | study7 | 직접 구현 유지, 스타터는 설치하지 않음 |
| 게시판 CRUD | study6·Midpoint | 웹·표준 API·Vue·댓글 |
| Vue / React / Svelte를 프론트로 붙이기 (선택) | study12 | Vue를 실제 설치·빌드·연결 |

## 원문 추가 체크 5개 · 문구 보존

| 원문 그대로 | 배치 | 실제 결정·코드 |
|---|---|---|
| 경로 `/api/v1`을 스펙의 `/api`와 맞출지 결정 | study6 ⑦ | 기준 /api, 기존 v1 호환 유지, 새 Vue는 /api만 사용 |
| 목록 `meta.current_page/last_page/total`을 `page/limit/total/totalPages`로 (API Resource 변환) | study14 ⑦ | ContractController + EntryResource, ContractTest |
| 필드 이름 camelCase | study14 ⑦ | EntryResource·DocumentResource·이력·알림 |
| 오류 응답을 `error.code/message/fields`로 (예외 핸들러) | study14 ⑦ | bootstrap/app.php의 예외 응답 처리, requestId |
| 선택 목표 "Vue / React / Svelte를 프론트로 붙이기": 위 항목을 맞춘 뒤 기존 프론트 게시판을 그대로 연결해 보기 | study12 ⑦ | 언어별 화면을 제거하고 같은 API 계약의 Vue 게시판으로 통일 |

체크리스트는 직접 해보기용으로 `- [ ]` 상태를 유지한다. 노션의 완료 표시는 실제 구현·검증 근거가 있는 항목에만 적용한다. 다섯 항목은 자동 문서 검사에서 문자열을 비교한다.

## 원문 정리 내용의 보존·갱신

| 내용 | 반영 위치·처리 |
|---|---|
| posts/comments, user_id fillable 제외, nullable/nullOnDelete·cascade | study3·6·7, 기존 migration·Policy 유지 |
| 같은 초의 정렬 안정성 | study4·6, created_at 다음 id로 정렬 |
| notes/tags/note_tag 다대다 | study11·Final, 기존 모델·시드 유지 |
| SQLite와 메모리 테스트 DB | study0·9, SQL 서버 CI 확장 |
| 직접 세션 인증·Sanctum·Policy | study7·13, 만료·표준 인증 응답 추가 |
| 기존 CORS 포트 4개·js/ts 화면 | 사용자 마지막 지시에 따라 제거; CORS_ORIGIN과 단일 Vue로 교체 |
| API vs Blade의 동일 DB | study6·7·12, 세션과 Bearer 차이 명시 |
| authorize·create 순서·PowerShell 캐럿·가드 캐시 오류 | study0·2·4·9, 기존 호환 테스트 유지 |
| 예전 21+9 테스트와 학습 기록 | 노션 이력으로 보존; 새 결과는 docs/verification.md에 분리 |
| GitHub 저장소·실습 위치 | README와 노션 업데이트 |
| AI 프로젝트 미사용 상태 | study18·Final의 Laravel 문서 도우미로 갱신, 실제 모델은 별도 확인 |

## 전체 요청 매핑

study0~18, studyMidpoint, studyFinal의 21개 파일에 8개 공통 절과 직접 해보기 2~3개, 전체 소스·줄별 설명을 제공한다. 기초·심화 항목은 README 진도표에 1:1로 배치했다. midpoint와 final에 목표·기능·구성도·구현 순서·배포 점검·회고가 있다.

## 못 넣은 추가 체크 항목

없음. 외부 계정·Docker 엔진·실제 DB/모델/배포 환경에서 아직 실행하지 못한 검증은 누락이 아니라 미검증 상태이며 docs/verification.md와 studyFinal의 배포 체크리스트에 남긴다.
