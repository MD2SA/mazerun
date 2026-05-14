<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => null);

// These come from Android (APP LEVEL)
$username = $_REQUEST['username'] ?? '';
$database = $_REQUEST['database'] ?? '';

// Validate only what you actually need
if (empty($username) || empty($database)) {
    $response['message'] = 'Missing username or database.';
    echo json_encode($response);
    exit;
}

// DB credentials (SERVER LEVEL — FIXED)
$host = 'mysql-db';
$db_user = 'root';
$db_pass = 'root';

// Connect to DB
$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de ligação: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// Check if table exists
$table_check = $conn->query("SHOW TABLES LIKE 'configtemp'");
$table_exists = ($table_check && $table_check->num_rows > 0);

if ($table_exists) {

    $sql = "SELECT minimo, maximo FROM configtemp LIMIT 1";
    $result = $conn->query($sql);

    if ($result && $row = $result->fetch_assoc()) {

        $response['success'] = true;
        $response['data'] = array(
            "minimo" => (float)$row['minimo'],
            "maximo" => (float)$row['maximo']
        );

    } else {

        // fallback if empty
        $response['success'] = true;
        $response['data'] = array("minimo" => 15, "maximo" => 35);
        $response['message'] = "Tabela vazia. Defaults usados.";
    }

} else {

    // fallback if table missing
    $response['success'] = true;
    $response['data'] = array("minimo" => 15, "maximo" => 35);
    $response['message'] = "Tabela inexistente. Defaults usados.";
}

$conn->close();
echo json_encode($response);
?>