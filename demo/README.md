# Laravel 기초 회원 게시판

실행·학습 순서·환경변수·검증 결과는 [루트 README](../README.md)를 따른다.

- PHP 8.4 + Laravel 13, 앱 내부 Vue + Pinia + vee-validate + Bootstrap
- 화면 `/app`, Blade `/`, 기준 API `/api`, Swagger `/api-docs`
- 포트 8000, 로컬 SQLite, 메모리 DB 테스트
- `composer install`, `.env` 준비와 키 보존, `php artisan migrate`, `npm ci`, `npm run build`, `php artisan serve`
- `php artisan test --compact`, `composer audit`, `npm audit --omit=dev`
- `.env`·DB·업로드·토큰은 Git에 넣지 않는다.

[요구사항 매핑](../docs/notion-coverage.md) · [검증 기록](../docs/verification.md)
