<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['user_id', 'filename', 'path', 'content', 'status', 'summary'])]
class Document extends Model
{
    use HasFactory;

    protected $hidden = ['content', 'path'];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
