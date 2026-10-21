<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

#[Fillable(['title', 'body'])]
class Note extends Model
{
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class);
    }

    public function scopeSearch(Builder $query, ?string $term): Builder
    {
        $term = trim((string) $term);
        if ($term === '') {
            return $query;
        }

        $like = '%'.$term.'%';

        return $query->where(function (Builder $inner) use ($like) {
            $inner->where('title', 'like', $like)->orWhere('body', 'like', $like);
        });
    }

    public function scopeTagged(Builder $query, ?string $tag): Builder
    {
        $tag = trim((string) $tag);
        if ($tag === '') {
            return $query;
        }

        return $query->whereHas('tags', fn (Builder $inner) => $inner->where('name', $tag));
    }

    public function syncTagString(?string $raw): void
    {
        $names = collect(preg_split('/[,，]/u', (string) $raw) ?: [])
            ->map(fn ($name) => trim((string) $name))
            ->filter(fn ($name) => $name !== '')
            ->unique()
            ->take(8)
            ->map(fn ($name) => mb_substr($name, 0, 30));

        $ids = $names->map(fn (string $name) => Tag::query()->firstOrCreate(['name' => $name])->id);

        $this->tags()->sync($ids->all());
    }
}
