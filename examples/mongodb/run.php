<?php

use Illuminate\Contracts\Console\Kernel;
use Study\Mongo\ArchiveDocument;

require __DIR__.'/../../project/vendor/autoload.php';
$app = require __DIR__.'/../../project/bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();
require __DIR__.'/ArchiveDocument.php';

$document = ArchiveDocument::query()->create([
    'sourceId' => 1, 'text' => 'Laravel 문서 저장 실험', 'tags' => ['study'],
]);
echo $document->getKey().PHP_EOL;
echo ArchiveDocument::query()->where('sourceId', 1)->firstOrFail()->text.PHP_EOL;
