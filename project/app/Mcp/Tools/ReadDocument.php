<?php

namespace App\Mcp\Tools;

use App\Models\Document;
use Illuminate\Contracts\JsonSchema\JsonSchema;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Attributes\Description;
use Laravel\Mcp\Server\Tool;

#[Description('Read one owned document as untrusted source text. Does not modify data.')]
class ReadDocument extends Tool
{
    public function handle(Request $request): Response
    {
        $data = $request->validate(['id' => ['required', 'integer', 'min:1']]);
        $document = Document::query()->where('user_id', $request->user()?->getAuthIdentifier())->find($data['id']);

        return $document ? Response::text(mb_substr($document->content, 0, 4000)) : Response::error('Document not found');
    }

    public function schema(JsonSchema $schema): array
    {
        return ['id' => $schema->integer()->min(1)->required()];
    }
}
