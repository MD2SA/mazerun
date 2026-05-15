<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

require_once __DIR__ . '/auth_check.php';
$auth = require_android_auth();

$response = array('success' => false, 'message' => '', 'data' => array());

$database = $auth['db'] ?? $_REQUEST['database'] ?? '';

if (empty($database)) {
    $response['message'] = 'Base de dados não especificada.';
    echo json_encode($response);
    exit;
}

$host = 'mysql-db'; 
$db_user = 'root';
$db_pass = 'root';

$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Adjusted to match dump.sql table 'sound' and columns 'sound', 'id'
$sql = "SELECT sound as som, id as idsom FROM sound ORDER BY id ASC";
$result = $conn->query($sql);

if ($result) {
    $soundData = array();
    while ($row = $result->fetch_assoc()) {
        $soundData[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $soundData;
    $response['message'] = 'Dados de som carregados com sucesso.';
} else {
    $response['message'] = "Erro na query: " . $conn->error;
}

$conn->close();
echo json_encode($response);
?>
