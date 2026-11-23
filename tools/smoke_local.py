"""로컬 실제 HTTP → DB 큐 워커 → AI mock → MCP Client의 연결 시험.

실행 중인 로컬 project 서버와 설치된 PHP가 필요하다. 별도 학습 회원 한 명을
생성하며 글·댓글·업로드는 종료 시 API로 정리한다. 운영 서버에는 실행하지 않는다.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import uuid
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

root=Path(__file__).resolve().parents[1]
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8111'
parsed=urlparse(base)
if parsed.scheme!='http' or parsed.hostname not in ['localhost','127.0.0.1']:
    raise SystemExit('Only a local development HTTP server is allowed.')
token=''
def request(path, method='GET', body=None, raw=None, content_type=None):
    headers={'Accept':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    if body is not None: raw=json.dumps(body).encode(); content_type='application/json'
    if content_type: headers['Content-Type']=content_type
    req=Request(base+path,data=raw,headers=headers,method=method)
    try:
        with urlopen(req,timeout=30) as response:
            payload=response.read().decode('utf-8')
            return response.status,payload,response.headers
    except HTTPError as error:
        return error.code,error.read().decode('utf-8'),error.headers

results=[]
for path in ['/health','/app','/api-docs','/openapi.json']:
    status,payload,_=request(path); assert status==200,(path,status)
    results.append(path+': 200')
unique=uuid.uuid4().hex[:12]
status,payload,_=request('/api/auth/signup','POST',{'nickname':'HTTP 학습검증','email':f'study-{unique}@example.test','password':'Local-Study-'+unique})
assert status==201,(status,payload)
token=json.loads(payload)['data']['accessToken']
entry_id=None; document_id=None
try:
    status,payload,headers=request('/api/posts','POST',{'title':'HTTP 흐름 검증','body':'Laravel 실제 서버 검증','tags':['study','HTTP']})
    assert status==201,(status,payload)
    entry_id=json.loads(payload)['data']['id']; assert headers['Location']==f'/api/posts/{entry_id}'
    status,payload,_=request(f'/api/posts/{entry_id}','PATCH',{'title':'수정한 HTTP 글'})
    assert status==200 and json.loads(payload)['data']['body']=='Laravel 실제 서버 검증'
    status,payload,_=request(f'/api/posts/{entry_id}/comments','POST',{'body':'실제 댓글'})
    assert status==201,(status,payload)
    comment_id=json.loads(payload)['data']['id']
    assert request(f'/api/comments/{comment_id}','DELETE')[0]==204
    results.append('실제 가입·인증·글 CRUD·태그·댓글: 통과')
    boundary='StudyBoundary'+unique
    upload=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="study.txt"\r\nContent-Type: text/plain\r\n\r\nLaravel 학습은 문서 소유권을 확인합니다.\n비공개 문서는 본인만 읽을 수 있습니다.\r\n--{boundary}--\r\n').encode('utf-8')
    status,payload,_=request('/api/documents','POST',raw=upload,content_type='multipart/form-data; boundary='+boundary)
    assert status==202,(status,payload)
    document_id=json.loads(payload)['data']['id']
    env=os.environ.copy(); env.update({'AI_DRIVER':'mock','MAIL_MAILER':'log','BROADCAST_CONNECTION':'log'})
    worker=subprocess.run(['php','artisan','queue:work','--stop-when-empty','--tries=1','--timeout=100'],cwd=root/'project',env=env,capture_output=True,text=True,encoding='utf-8',timeout=45)
    assert worker.returncode==0,worker.stderr
    status,payload,_=request('/api/documents')
    document=next(item for item in json.loads(payload)['data'] if item['id']==document_id)
    assert document['status']=='ready' and '[mock 실습]' in document['summary'],document
    status,payload,_=request(f'/api/documents/{document_id}/ask','POST',{'question':'Laravel 문서 소유권'})
    assert status==200 and '"done":true' in payload and '"delta":' in payload,(status,payload)
    status,payload,_=request(f'/api/documents/{document_id}/questions')
    assert status==200 and len(json.loads(payload)['data'])==1
    results.append('실제 파일 업로드→DB 큐→worker→mock 요약→SSE→질문 이력: 통과')
    env.update({'MCP_TOKEN':token,'APP_URL':base})
    client=subprocess.run(['php','artisan','study:mcp-read',str(document_id)],cwd=root/'project',env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
    assert client.returncode==0,client.stdout+client.stderr
    assert 'read-document' in client.stdout and '소유권' in client.stdout,client.stdout
    results.append('실제 Laravel MCP Client connect→tools/list→tools/call: 통과')
finally:
    if document_id: assert request(f'/api/documents/{document_id}','DELETE')[0]==204
    if entry_id: assert request(f'/api/posts/{entry_id}','DELETE')[0]==204
    assert request('/api/auth/logout','POST')[0]==204
print(json.dumps({'passed':results,'cleanup':'글·댓글·파일·문서·질문·토큰 정리. 로컬 시험 회원 한 명은 남음.'},ensure_ascii=False,indent=2))
