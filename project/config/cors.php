<?php

return [
    'paths' => ['api/*'], 'allowed_methods' => ['*'],
    'allowed_origins' => array_filter(explode(',', env('CORS_ORIGIN', 'http://127.0.0.1:5173'))),
    'allowed_origins_patterns' => [], 'allowed_headers' => ['*'],
    'exposed_headers' => ['X-Request-Id', 'Location'], 'max_age' => 600, 'supports_credentials' => false,
];
