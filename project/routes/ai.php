<?php

use App\Mcp\Servers\LibraryServer;
use Laravel\Mcp\Facades\Mcp;

Mcp::web('/mcp/library', LibraryServer::class)->middleware(['auth:sanctum', 'throttle:30,1']);
