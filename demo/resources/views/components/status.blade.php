@props(['message' => null])
@if ($message)
    <p role="status">{{ $message }}</p>
@endif
