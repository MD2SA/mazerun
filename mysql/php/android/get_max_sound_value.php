<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => null);

// App-level inputs
$username = $_REQUEST['username'] ?? '';
$database = $_REQUEST['database'] ?? '';

// Validate only what matters
if (empty($username) || empty($database)) {
    $response['message'] = 'Missing username or database.';
    echo json_encode($response);
    exit;
}

// DB credentials (fixed)
$host = 'mysql-db';
$db_user = 'root';
$db_pass = 'root';

// Connect
$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Check table
$table_check = $conn->query("SHOW TABLES LIKE 'configsound'");
$table_exists = ($table_check && $table_check->num_rows > 0);

if ($table_exists) {

    $sql = "SELECT maximo FROM configsound LIMIT 1";
    $result = $conn->query($sql);

    if ($result && $row = $result->fetch_assoc()) {

        $response['success'] = true;
        $response['data'] = array(
            "maximo" => (int)$row['maximo']
        );
        $response['message'] = 'Configuração de som carregada.';

    } else {

        $response['success'] = true;
        $response['data'] = array("maximo" => 80);
        $response['message'] = 'Tabela vazia. Default usado.';
    }

} else {

    $response['success'] = true;
    $response['data'] = array("maximo" => 80);
    $response['message'] = 'Tabela inexistente. Default usado.';
}

$conn->close();
echo json_encode($response);
?>