<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

require_once __DIR__ . '/auth_check.php';
$auth = require_android_auth();

// Estrutura de resposta idêntica ao login.php
$response = array('success' => false, 'message' => '', 'data' => array());

$database = $auth['db'] ?? $_REQUEST['database'] ?? '';

if (empty($database)) {
    $response['message'] = 'Base de dados não especificada no token ou pedido.';
    echo json_encode($response);
    exit;
}

$host = 'mysql-db';
$db_user = 'root';
$db_pass = 'root';

$conn = new mysqli($host, $db_user, $db_pass, $database);

// 2. Verificar conexão
if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// 3. Consulta
$sql = "SELECT id, alertType, time, msg, reading, sensor FROM message ORDER BY id DESC";
$result = $conn->query($sql);

if ($result) {
    $messages = array();
    while ($row = $result->fetch_assoc()) {
        $messages[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $messages; // As mensagens vão aqui dentro
    $response['message'] = 'Mensagens carregadas com sucesso.';
} else {
    $response['message'] = 'Erro ao executar consulta: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>
