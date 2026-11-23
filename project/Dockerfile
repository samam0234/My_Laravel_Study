FROM node:24-alpine AS assets
WORKDIR /src
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY vite.config.js ./
COPY resources ./resources
ARG VITE_REVERB_APP_KEY
ARG VITE_REVERB_HOST
ARG VITE_REVERB_PORT=443
ARG VITE_REVERB_SCHEME=https
RUN npm run build

FROM php:8.4-fpm-alpine AS app
RUN apk add --no-cache icu-dev libzip-dev oniguruma-dev postgresql-dev sqlite-dev \
    && docker-php-ext-install pdo_pgsql pdo_mysql pdo_sqlite intl zip mbstring pcntl opcache
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /var/www/html
COPY composer.* ./
RUN composer install --no-dev --prefer-dist --no-interaction --no-scripts --no-autoloader
COPY . .
COPY --from=assets /src/public/build ./public/build
RUN composer dump-autoload --no-dev --optimize --no-scripts && php artisan package:discover \
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data
EXPOSE 9000
CMD ["php-fpm"]

FROM nginx:1.28-alpine AS web
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=app /var/www/html/public /var/www/html/public
EXPOSE 80
