<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\View\View;

class LearningController extends Controller
{
    public function preferences(Request $request): View
    {
        $path = 'preferences/'.$request->user()->id.'.json';
        $saved = Storage::disk('local')->exists($path) ? json_decode(Storage::disk('local')->get($path), true) : [];

        return view('study.preferences', ['theme' => $saved['theme'] ?? 'light']);
    }

    public function save(Request $request): RedirectResponse
    {
        $data = $request->validate(['theme' => ['required', 'in:light,dark']]);
        $request->session()->put('theme', $data['theme']);
        Storage::disk('local')->put('preferences/'.$request->user()->id.'.json', json_encode($data, JSON_THROW_ON_ERROR));

        return redirect()->route('study.preferences')->with('status', '화면 설정을 저장했습니다.');
    }
}
