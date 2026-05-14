<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
header("Access-Control-Allow-Methods: GET, POST, DELETE, PUT, OPTIONS");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS')
    exit;

$conn = new mysqli('mysql-db', 'root', 'root', 'mazerun');
if ($conn->connect_error) {
    echo json_encode(["success" => false, "message" => "DB Connection failed"]);
    exit;
}

$data = json_decode(file_get_contents("php://input"), true);
$action = $_GET['action'] ?? $data['action'] ?? '';
$team = $_GET['team'] ?? $data['team'] ?? null;
$sim_id = $_GET['simulation_id'] ?? $data['simulation_id'] ?? null;

$response = ["success" => false, "message" => "Action not found"];

try {
    switch ($action) {
        case 'login':
            $email = $data['email'] ?? '';
            $res = $conn->query("SELECT * FROM user WHERE email = '$email'");
            $user = $res->fetch_assoc();
            $response = $user ? ["success" => true, "data" => $user] : ["success" => false, "message" => "User not found"];
            break;

        case 'get_users':
            $res = $conn->query("SELECT name, email, phone, type, birth, team FROM user ORDER BY name");
            $users = $res->fetch_all(MYSQLI_ASSOC);
            $response = ["success" => true, "data" => $users];
            break;

        case 'get_simulations':
            $where = $team ? "WHERE team = $team" : "";
            $res = $conn->query("SELECT s.*, (SELECT COUNT(*) FROM measure WHERE simulation_id = s.id) as measures FROM simulation s $where ORDER BY startDate DESC");
            $response = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        case 'get_analytics':
            $where = $team ? "WHERE team = $team" : "";
            $stats = [
                "total_sims" => $conn->query("SELECT COUNT(*) FROM simulation $where")->fetch_row()[0],
                "total_measures" => $conn->query("SELECT COUNT(*) FROM measure m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "total_alerts" => $conn->query("SELECT COUNT(*) FROM message m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "avg_temp" => round($conn->query("SELECT AVG(temperature) FROM temperature t JOIN simulation s ON t.simulation_id = s.id $where")->fetch_row()[0], 2)
            ];
            $response = ["success" => true, "data" => $stats];
            break;

        case 'get_sensor_data':
            if (!$sim_id)
                throw new Exception("Simulation ID required");
            $temps = $conn->query("SELECT time, temperature as value FROM temperature WHERE simulation_id = $sim_id ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $sounds = $conn->query("SELECT time, sound as value FROM sound WHERE simulation_id = $sim_id ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $response = ["success" => true, "data" => ["temperature" => $temps, "sound" => $sounds]];
            break;

        case 'get_unified_logs':
            $where = $sim_id ? "WHERE simulation_id = $sim_id" : "";
            $sql = "
                (SELECT time, 'ALERT' as type, msg as detail FROM message $where)
                UNION ALL
                (SELECT time, 'ACTION' as type, CONCAT(action_type, ' -> ', target) as detail FROM action $where)
                UNION ALL
                (SELECT time, 'INVALID' as type, reason as detail FROM invalid_measure $where)
                UNION ALL
                (SELECT time, 'OUTLIER' as type, reason as detail FROM sound_outlier $where)
                ORDER BY time DESC LIMIT 100
            ";
            $res = $conn->query($sql);
            $response = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        case 'create_user':
            $stmt = $conn->prepare("INSERT INTO user (name, phone, type, email, password, birth, team) VALUES (?, ?, ?, ?, '', ?, ?)");
            $stmt->bind_param("sssssi", $data['name'], $data['phone'], $data['type'], $data['email'], $data['birth'], $data['team']);
            $response = $stmt->execute() ? ["success" => true] : ["success" => false, "message" => $stmt->error];
            break;

        case 'delete_user':
            $email = $data['email'];
            $response = $conn->query("DELETE FROM user WHERE email = '$email'") ? ["success" => true] : ["success" => false];
            break;

        case 'create_simulation':
            $stmt = $conn->prepare("INSERT INTO simulation (description, team, user_email, startDate) VALUES (?, ?, ?, NOW())");
            $stmt->bind_param("sis", $data['description'], $data['team'], $data['email']);
            $response = $stmt->execute() ? ["success" => true] : ["success" => false, "message" => $stmt->error];
            break;
    }
} catch (Exception $e) {
    $response = ["success" => false, "message" => $e->getMessage()];
}

echo json_encode($response);
$conn->close();
?>
