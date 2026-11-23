"""누락·깨진 로컬 링크·원문 추가 체크·문서와 실제 코드의 차이를 검사한다."""
from pathlib import Path
import hashlib
import json
import re

root=Path(__file__).resolve().parents[1]
expected={f'study{i}.md' for i in range(19)} | {'studyMidpoint.md','studyFinal.md'}
actual={p.name for p in root.glob('study*.md')}
assert expected==actual, f'Study files differ: {expected ^ actual}'
headings=['① 목표','② 📖 이론','③ 🛠️ 실기','④ 🔗 연동','⑤ 오류','⑥ 직접','⑦ ☐ 체크','⑧ 다음']
index=json.loads((root/'docs/code-index.json').read_text(encoding='utf-8'))
for name in sorted(expected):
    text=(root/name).read_text(encoding='utf-8')
    positions=[text.index(heading) for heading in headings]
    assert positions==sorted(positions), f'{name}: section order'
    exercises=text.split('## ⑥ 직접 해보기')[1].split('## ⑦')[0]
    assert 2<=len(re.findall(r'^\d+\. ',exercises,re.M))<=3, f'{name}: 2-3 exercises required'
    assert '- [ ] ' in text, f'{name}: missing checklist'
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in target and not target.startswith('#'):
            assert (root/target.split('#')[0]).exists(), f'{name}: broken link {target}'
    for path,digest in index[name].items():
        source=(root/path).read_text(encoding='utf-8').rstrip()+'\n'
        assert hashlib.sha256(source.encode()).hexdigest()==digest, f'{name}: outdated source {path}; run render_course.py'
        assert source.rstrip() in text, f'{name}: incomplete source {path}'
        assert '#### 줄별 설명' in text

requirements={
    'study6.md':['경로 `/api/v1`을 스펙의 `/api`와 맞출지 결정'],
    'study12.md':['Vue / React / Svelte를 프론트로 붙이기 (선택)', '선택 목표 "Vue / React / Svelte를 프론트로 붙이기": 위 항목을 맞춘 뒤 기존 프론트 게시판을 그대로 연결해 보기'],
    'study14.md':['목록 `meta.current_page/last_page/total`을 `page/limit/total/totalPages`로 (API Resource 변환)','필드 이름 camelCase','오류 응답을 `error.code/message/fields`로 (예외 핸들러)'],
}
for name,checks in requirements.items():
    text=(root/name).read_text(encoding='utf-8').split('## ⑦ ☐ 체크리스트')[1]
    for check in checks: assert '- [ ] '+check in text, f'Missing exact Notion item: {check}'
for app in ['demo','project']:
    spec=json.loads((root/app/'public/openapi.json').read_text(encoding='utf-8'))
    assert spec['openapi']=='3.0.3'
    for path in ['/health','/api/auth/signup','/api/auth/login','/api/auth/me','/api/posts','/api/posts/{id}','/api/posts/{id}/comments','/api/comments/{id}']:
        assert path in spec['paths'], f'{app}: missing OpenAPI path {path}'
    for file in ['composer.lock','package-lock.json']: assert (root/app/file).exists()
print('PASS: 21 documents, 8 sections, exercises, exact Notion items, local links, full-code hashes, API path coverage.')
