<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
header("Access-Control-Allow-Methods: GET, POST, DELETE, PUT, OPTIONS");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;

// Enable exception reporting for mysqli
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

try {
    $conn = new mysqli('mysql-db', 'root', 'root', 'mazerun');

    $input = file_get_contents("php://input");
    $data = json_decode($input, true) ?? [];

    $action = $_GET['action'] ?? $data['action'] ?? '';
    $requester_email = $_GET['requester_email'] ?? $data['requester_email'] ?? '';

    $response = ["success" => false, "message" => "Action not found: " . $action];

    function handle_sp_result($stmt) {
        $stmt->execute();
        $message = "Operation successful";
        $resultData = null;

        do {
            if ($res = $stmt->get_result()) {
                $row = $res->fetch_assoc();
                if (isset($row['message'])) $message = $row['message'];
                if (isset($row['game_id'])) $resultData = $row;
                $res->free();
            }
        } while ($stmt->next_result());

        return ["success" => true, "message" => $message, "data" => $resultData];
    }

    switch ($action) {
        case 'login':
            $email = $data['email'] ?? '';
            $stmt = $conn->prepare("SELECT * FROM user WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $res = $stmt->get_result();
            $user = $res->fetch_assoc();
            $response = $user ? ["success" => true, "data" => $user] : ["success" => false, "message" => "User not found"];
            break;

        case 'register':
            $team = !empty($data['team']) ? (int)$data['team'] : null;
            $stmt = $conn->prepare("CALL sp_create_user(?, ?, 'usr', ?, ?, ?)");
            $stmt->bind_param("ssssi", $data['name'], $data['phone'], $data['email'], $data['birth'], $team);
            $response = handle_sp_result($stmt);
            break;

        case 'create_user':
            $team = !empty($data['team']) ? (int)$data['team'] : null;
            $stmt = $conn->prepare("CALL sp_create_user(?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("sssssi", $data['name'], $data['phone'], $data['type'], $data['email'], $data['birth'], $team);
            $response = handle_sp_result($stmt);
            break;

        case 'get_users':
            $res = $conn->query("CALL sp_get_all_users()");
            $users = $res->fetch_all(MYSQLI_ASSOC);
            $response = ["success" => true, "data" => $users];
            break;

        case 'update_user':
            $team = !empty($data['team']) ? (int)$data['team'] : null;
            $stmt = $conn->prepare("CALL sp_update_user(?, ?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("ssssssi", $requester_email, $data['email'], $data['name'], $data['phone'], $data['type'], $data['birth'], $team);
            $response = handle_sp_result($stmt);
            break;

        case 'delete_user':
            $stmt = $conn->prepare("CALL sp_delete_user(?, ?)");
            $stmt->bind_param("ss", $requester_email, $data['email']);
            $response = handle_sp_result($stmt);
            break;

        case 'create_simulation':
            $team = (int)($data['team'] ?? 0);
            $player_id = (int)($data['player_id'] ?? 0);
            $stmt = $conn->prepare("CALL sp_create_game(?, ?, ?, ?)");
            $stmt->bind_param("ssii", $requester_email, $data['description'], $team, $player_id);
            $response = handle_sp_result($stmt);
            break;

        case 'update_simulation':
            $team = (int)($data['team'] ?? 0);
            $stmt = $conn->prepare("CALL sp_update_game(?, ?, ?, ?)");
            $stmt->bind_param("sisi", $requester_email, $data['id'], $data['description'], $team);
            $response = handle_sp_result($stmt);
            break;

        case 'get_simulations':
            $teamFilter = $_GET['team'] ?? $data['team'] ?? null;
            $where = !empty($teamFilter) ? "WHERE team = " . (int)$teamFilter : "";
            $res = $conn->query("SELECT s.*, (SELECT COUNT(*) FROM measure WHERE simulation_id = s.id) as measures FROM simulation s $where ORDER BY startDate DESC");
            $response = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        case 'get_analytics':
            $teamFilter = $_GET['team'] ?? $data['team'] ?? null;
            $where = !empty($teamFilter) ? "WHERE team = " . (int)$teamFilter : "";
            $stats = [
                "total_sims" => $conn->query("SELECT COUNT(*) FROM simulation $where")->fetch_row()[0],
                "total_measures" => $conn->query("SELECT COUNT(*) FROM measure m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "total_alerts" => $conn->query("SELECT COUNT(*) FROM message m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "avg_temp" => round($conn->query("SELECT AVG(temperature) FROM temperature t JOIN simulation s ON t.simulation_id = s.id $where")->fetch_row()[0], 2),
                "avg_sound" => round($conn->query("SELECT AVG(sound) FROM sound t JOIN simulation s ON t.simulation_id = s.id $where")->fetch_row()[0], 2),
                "total_marsamis" => $conn->query("SELECT SUM(oddMarsamis + evenMarsamis) FROM ocupation o JOIN simulation s ON o.id = s.id $where")->fetch_row()[0] ?? 0
            ];
            $response = ["success" => true, "data" => $stats];
            break;

        case 'get_sensor_data':
            $sim_id_param = (int)($_GET['simulation_id'] ?? $data['simulation_id'] ?? 0);
            $temps = $conn->query("SELECT time, temperature as value FROM temperature WHERE simulation_id = $sim_id_param ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $sounds = $conn->query("SELECT time, sound as value FROM sound WHERE simulation_id = $sim_id_param ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $occupations = $conn->query("SELECT Room as room, oddMarsamis as odd, evenMarsamis as even, (oddMarsamis + evenMarsamis) as total FROM ocupation WHERE id = $sim_id_param ORDER BY Room ASC")->fetch_all(MYSQLI_ASSOC);
            $response = ["success" => true, "data" => ["temperature" => $temps, "sound" => $sounds, "occupation" => $occupations]];
            break;

        case 'get_unified_logs':
            $sim_id_param = (int)($_GET['simulation_id'] ?? $data['simulation_id'] ?? 0);
            $limit = (int)($_GET['limit'] ?? $data['limit'] ?? 100);
            $where = $sim_id_param ? "WHERE simulation_id = $sim_id_param" : "";
            $sql = "(SELECT time, 'ALERT' as type, msg as detail FROM message $where) UNION ALL (SELECT time, 'ACTION' as type, CONCAT(action_type, ' -> ', target) as detail FROM action $where) UNION ALL (SELECT time, 'INVALID' as type, reason as detail FROM invalid_measure $where) UNION ALL (SELECT time, 'OUTLIER' as type, reason as detail FROM sound_outlier $where) ORDER BY time DESC LIMIT $limit";
            $res = $conn->query($sql);
            $response = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        case 'get_status':
            $status = [
                ["name" => "MySQL Database", "status" => "ONLINE"],
                ["name" => "MQTT Broker", "status" => "OFFLINE"]
            ];
            $fp = @fsockopen("broker.hivemq.com", 1883, $errno, $errstr, 1);
            if ($fp) {
                $status[1]["status"] = "ONLINE";
                fclose($fp);
            }
            $response = ["success" => true, "data" => $status];
            break;
    }
} catch (mysqli_sql_exception $e) {
    $response = ["success" => false, "message" => "Database Error: " . $e->getMessage()];
} catch (Exception $e) {
    $response = ["success" => false, "message" => "General Error: " . $e->getMessage()];
}

echo json_encode($response);
if (isset($conn) && $conn) $conn->close();
?>
