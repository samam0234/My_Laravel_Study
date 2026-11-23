<?php

namespace App\Http\Controllers;

class HomeController extends Controller
{
    public function index()
    {
        return view('home', ['greeting' => 'Hello Laravel', 'topics' => ['라우트', '컨트롤러', 'Blade']]);
    }
}
