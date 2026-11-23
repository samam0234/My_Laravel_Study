<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EntryResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id, 'title' => $this->title, 'body' => $this->body,
            'tags' => ($this->tags ?? []),
            'author' => $this->user ? ['id' => $this->user->id, 'nickname' => $this->user->name] : null,
            'commentCount' => (int) ($this->comments_count ?? 0),
            'createdAt' => $this->created_at?->utc()->toISOString(),
            'updatedAt' => $this->updated_at?->utc()->toISOString(),
        ];
    }
}
