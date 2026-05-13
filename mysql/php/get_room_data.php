<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => array());

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos.';
    echo json_encode($response);
    exit;
}

$host = 'mysql-db';
$db_user = 'root';
$db_pass = 'root';

$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Adjusted to match dump.sql table 'ocupation' and columns 'room', 'evenMarsamis', 'oddMarsamis'
$sql = "SELECT Room as Sala, evenMarsamis as NumeroMarsamisEven, oddMarsamis as NumeroMarsamisOdd FROM ocupation";
$result = $conn->query($sql);

if ($result) {
    $rooms = array();
    while ($row = $result->fetch_assoc()) {
        $rooms[] = $row;
    }
    
    $response['success'] = true;
    $response['data'] = $rooms;
    $response['message'] = 'Dados dos corredores carregados com sucesso.';
} else {
    $response['message'] = 'Erro ao executar consulta: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>
