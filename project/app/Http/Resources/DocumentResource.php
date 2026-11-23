<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class DocumentResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return ['id' => $this->id, 'userId' => $this->user_id, 'filename' => $this->filename,
            'status' => $this->status, 'summary' => $this->summary,
            'createdAt' => $this->created_at?->utc()->toISOString(),
            'updatedAt' => $this->updated_at?->utc()->toISOString()];
    }
}
