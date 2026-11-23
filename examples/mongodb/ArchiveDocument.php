<?php

namespace Study\Mongo;

use MongoDB\Laravel\Eloquent\Model;

class ArchiveDocument extends Model
{
    protected $connection = 'mongodb';

    protected $table = 'archive_documents';

    protected $fillable = ['sourceId', 'text', 'tags'];
}
