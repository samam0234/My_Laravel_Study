<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Laravel\Mcp\Client;

#[Signature('study:mcp-read {id : Document ID}')]
#[Description('MCP 클라이언트로 본인 문서 읽기. MCP_TOKEN 환경변수와 별도 HTTP 서버가 필요합니다.')]
class McpRead extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(): int
    {
        $token = getenv('MCP_TOKEN');
        if (! $token) {
            $this->error('MCP_TOKEN 환경변수를 설정하세요.');

            return self::FAILURE;
        }
        $client = Client::web(url('/mcp/library'))->withToken($token)->withTimeout(15);
        try {
            $client->connect();
            $this->line('Available tools: '.$client->tools()->pluck('name')->implode(', '));
            $result = $client->callTool('read-document', ['id' => (int) $this->argument('id')]);
            $this->line($result->text());

            return $result->isError ? self::FAILURE : self::SUCCESS;
        } finally {
            $client->disconnect();
        }
    }
}
