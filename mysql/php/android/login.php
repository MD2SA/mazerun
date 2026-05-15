<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

require_once __DIR__ . '/jwt.php';

$response = array('success' => false, 'message' => '', 'token' => '');

// Usamos $_REQUEST para aceitar tanto GET (browser) quanto POST (Android)
$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos (username, password, database).';
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

// 3. Consulta - Agora verificando a password
$sql = "SELECT password, team, type FROM user WHERE email = ?";
$stmt = $conn->prepare($sql);

if ($stmt) {
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();

    if ($user) {
        if (!empty($user['password']) && password_verify($password, $user['password'])) {
            $token = jwt_encode([
                'sub' => $username,
                'type' => $user['type'],
                'team' => $user['team'],
                'db' => $database
            ]);

            $response['success'] = true;
            $response['token'] = $token;
            $response['IDGrupo'] = $user['team'];
            $response['message'] = 'Login bem-sucedido.';
        } else {
            $response['message'] = 'Credenciais inválidas.';
        }
    } else {
        $response['message'] = 'Utilizador não encontrado.';
    }
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>