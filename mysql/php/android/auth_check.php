<?php
require_once __DIR__ . '/jwt.php';

function require_android_auth() {
    $payload = get_auth_payload();
    if (!$payload) {
        http_response_code(401);
        echo json_encode(['success' => false, 'message' => 'Unauthorized: Missing or invalid token']);
        exit;
    }
    return $payload;
}
