<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
header("Access-Control-Allow-Methods: GET, POST, DELETE, PUT, OPTIONS");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;

require_once __DIR__ . '/jwt.php';

// Enable exception reporting for mysqli
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

// ─── Public actions (no JWT required) ────────────────────────────────────────
const PUBLIC_ACTIONS = ['login', 'register', 'get_status', 'get_teams'];

// ─── Helper: require a valid JWT and return its payload ──────────────────────
function require_auth(): array {
    $payload = get_auth_payload();
    if (!$payload) {
        http_response_code(401);
        echo json_encode(['success' => false, 'message' => 'Unauthorized: missing or invalid token']);
        exit;
    }
    return $payload;
}

try {
    $conn = new mysqli('mysql-db', 'root', 'root', 'mazerun');
    $conn->set_charset("utf8mb4");

    $input = file_get_contents("php://input");
    $data  = json_decode($input, true) ?? [];

    $action          = $_GET['action'] ?? $data['action'] ?? '';
    $requester_email = $_GET['requester_email'] ?? $data['requester_email'] ?? '';

    $response = ["success" => false, "message" => "Action not found: " . $action];

    // ─── Auth guard ───────────────────────────────────────────────────────────
    $authPayload = null;
    if (!in_array($action, PUBLIC_ACTIONS, true)) {
        $authPayload = require_auth();
        // Override requester_email with the JWT subject (prevents spoofing)
        $requester_email = $authPayload['sub'];
    }

    // ─── SP result helper ─────────────────────────────────────────────────────
    function handle_sp_result($stmt) {
        $stmt->execute();
        $message    = "Operation successful";
        $resultData = null;

        do {
            if ($res = $stmt->get_result()) {
                $row = $res->fetch_assoc();
                if (isset($row['message']))  $message    = $row['message'];
                if (isset($row['game_id']))  $resultData = $row;
                $res->free();
            }
        } while ($stmt->next_result());

        return ["success" => true, "message" => $message, "data" => $resultData];
    }

    switch ($action) {

        // ── LOGIN ─────────────────────────────────────────────────────────────
        case 'login':
            $email    = trim($data['email']    ?? '');
            $password = $data['password'] ?? '';

            if (empty($email) || empty($password)) {
                $response = ["success" => false, "message" => "Email and password are required"];
                break;
            }

            $stmt = $conn->prepare("SELECT * FROM user WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $res  = $stmt->get_result();
            $user = $res->fetch_assoc();

            if (!$user) {
                $response = ["success" => false, "message" => "Invalid credentials"];
                break;
            }

            // Legacy accounts (empty password hash) — deny login gracefully
            if (empty($user['password'])) {
                $response = ["success" => false, "message" => "Account has no password set. Contact an administrator."];
                break;
            }

            if (!password_verify($password, $user['password'])) {
                $response = ["success" => false, "message" => "Invalid credentials"];
                break;
            }

            // Strip password before returning user object
            unset($user['password']);

            $token    = jwt_encode(['sub' => $user['email'], 'type' => $user['type'], 'team' => $user['team']]);
            $response = ["success" => true, "data" => $user, "token" => $token];
            break;

        // ── REGISTER ─────────────────────────────────────────────────────────
        case 'register':
            $password = $data['password'] ?? '';
            if (strlen($password) < 6) {
                $response = ["success" => false, "message" => "Password must be at least 6 characters"];
                break;
            }
            $hashed = password_hash($password, PASSWORD_BCRYPT);
            $team   = !empty($data['team']) ? (int)$data['team'] : null;

            $stmt = $conn->prepare("CALL sp_create_user(?, ?, 'usr', ?, ?, ?, ?)");
            $stmt->bind_param("ssssss", $data['name'], $data['phone'], $data['email'], $data['birth'], $team, $hashed);
            $response = handle_sp_result($stmt);
            break;

        // ── CREATE USER (admin) ───────────────────────────────────────────────
        case 'create_user':
            // Check admin role from JWT
            if ($authPayload['type'] !== 'adm') {
                http_response_code(403);
                $response = ["success" => false, "message" => "Forbidden: Admins only"];
                break;
            }
            $password = $data['password'] ?? '';
            if (strlen($password) < 6) {
                $response = ["success" => false, "message" => "Password must be at least 6 characters"];
                break;
            }
            $hashed = password_hash($password, PASSWORD_BCRYPT);
            $team   = !empty($data['team']) ? (int)$data['team'] : null;

            $stmt = $conn->prepare("CALL sp_create_user(?, ?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("sssssss", $data['name'], $data['phone'], $data['type'], $data['email'], $data['birth'], $team, $hashed);
            $response = handle_sp_result($stmt);
            break;

        // ── GET USERS ─────────────────────────────────────────────────────────
        case 'get_users':
            $stmt = $conn->prepare("CALL sp_get_all_users()");
            $stmt->execute();
            $result = $stmt->get_result();
            $users = $result->fetch_all(MYSQLI_ASSOC);
            $stmt->close();
            // Clear remaining results from the connection
            while($conn->more_results()) $conn->next_result();

            $response = ["success" => true, "data" => $users];
            break;

        // ── UPDATE USER ───────────────────────────────────────────────────────
        case 'update_user':
            $team = !empty($data['team']) ? (int)$data['team'] : null;
            $stmt = $conn->prepare("CALL sp_update_user(?, ?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("ssssssi", $requester_email, $data['email'], $data['name'], $data['phone'], $data['type'], $data['birth'], $team);
            $response = handle_sp_result($stmt);
            break;

        // ── DELETE USER ───────────────────────────────────────────────────────
        case 'delete_user':
            $stmt = $conn->prepare("CALL sp_delete_user(?, ?)");
            $stmt->bind_param("ss", $requester_email, $data['email']);
            $response = handle_sp_result($stmt);
            break;

        // ── CHANGE PASSWORD ───────────────────────────────────────────────────
        case 'change_password':
            $target_email    = $data['email']        ?? $requester_email;
            $current_password = $data['current_password'] ?? '';
            $new_password     = $data['new_password']     ?? '';

            // Only admins can change another user's password
            if ($target_email !== $requester_email && $authPayload['type'] !== 'adm') {
                http_response_code(403);
                $response = ["success" => false, "message" => "Forbidden"];
                break;
            }

            if (strlen($new_password) < 6) {
                $response = ["success" => false, "message" => "New password must be at least 6 characters"];
                break;
            }

            // If changing own password, verify current password first
            if ($target_email === $requester_email) {
                $stmt = $conn->prepare("SELECT password FROM user WHERE email = ?");
                $stmt->bind_param("s", $requester_email);
                $stmt->execute();
                $row = $stmt->get_result()->fetch_assoc();
                if (!$row || !password_verify($current_password, $row['password'])) {
                    $response = ["success" => false, "message" => "Current password is incorrect"];
                    break;
                }
            }

            $hashed = password_hash($new_password, PASSWORD_BCRYPT);
            $stmt   = $conn->prepare("UPDATE user SET password = ? WHERE email = ?");
            $stmt->bind_param("ss", $hashed, $target_email);
            $stmt->execute();
            $response = ["success" => true, "message" => "Password updated successfully"];
            break;

        // ── SIMULATIONS ───────────────────────────────────────────────────────
        case 'create_simulation':
            $team      = (int)($data['team']      ?? 0);
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
            $where      = !empty($teamFilter) ? "WHERE team = " . (int)$teamFilter : "";
            $res        = $conn->query("SELECT s.*, (SELECT COUNT(*) FROM measure WHERE simulation_id = s.id) as measures FROM simulation s $where ORDER BY startDate DESC");
            $response   = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        // ── ANALYTICS ─────────────────────────────────────────────────────────
        case 'get_analytics':
            $teamFilter = $_GET['team'] ?? $data['team'] ?? null;
            $where = !empty($teamFilter) ? "WHERE s.team = " . (int)$teamFilter : "";
            $sim_where = !empty($teamFilter) ? "WHERE team = " . (int)$teamFilter : "";

            $stats = [
                "total_sims"     => $conn->query("SELECT COUNT(*) FROM simulation $sim_where")->fetch_row()[0],
                "total_measures" => $conn->query("SELECT COUNT(*) FROM measure m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "total_alerts"   => $conn->query("SELECT COUNT(*) FROM alert a JOIN simulation s ON a.simulation_id = s.id $where")->fetch_row()[0],
                "avg_temp"       => round($conn->query("SELECT AVG(temperature) FROM temperature t JOIN simulation s ON t.simulation_id = s.id $where")->fetch_row()[0], 2),
                "avg_sound"      => round($conn->query("SELECT AVG(sound) FROM sound t JOIN simulation s ON t.simulation_id = s.id $where")->fetch_row()[0], 2),
                "total_marsamis" => $conn->query("SELECT SUM(oddMarsamis + evenMarsamis) FROM ocupation o JOIN simulation s ON o.id = s.id $where")->fetch_row()[0] ?? 0
            ];
            $response = ["success" => true, "data" => $stats];
            break;

        // ── SENSOR DATA ───────────────────────────────────────────────────────
        case 'get_sensor_data':
            $sim_id_param = (int)($_GET['simulation_id'] ?? $data['simulation_id'] ?? 0);
            $temps        = $conn->query("SELECT time, temperature as value FROM temperature WHERE simulation_id = $sim_id_param ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $sounds       = $conn->query("SELECT time, sound as value FROM sound WHERE simulation_id = $sim_id_param ORDER BY time ASC LIMIT 100")->fetch_all(MYSQLI_ASSOC);
            $occupations  = $conn->query("SELECT Room as room, oddMarsamis as odd, evenMarsamis as even, (oddMarsamis + evenMarsamis) as total FROM ocupation WHERE id = $sim_id_param ORDER BY Room ASC")->fetch_all(MYSQLI_ASSOC);
            $response = ["success" => true, "data" => ["temperature" => $temps, "sound" => $sounds, "occupation" => $occupations]];
            break;

        // ── UNIFIED LOGS ──────────────────────────────────────────────────────
        case 'get_unified_logs':
            $sim_id_param = (int)($_GET['simulation_id'] ?? $data['simulation_id'] ?? 0);
            $team_param   = (int)($_GET['team'] ?? $data['team'] ?? 0);
            $limit        = (int)($_GET['limit'] ?? $data['limit'] ?? 100);

            $where = "1=1";
            if ($sim_id_param > 0) {
                $where = "simulation_id = $sim_id_param";
            } else if ($team_param > 0) {
                // To filter global logs by team, we join with the simulation table
                $where = "simulation_id IN (SELECT id FROM simulation WHERE team = $team_param)";
            }

            $sql = "(SELECT time, 'ALERT' as type, msg as detail FROM alert WHERE $where)
                    UNION ALL
                    (SELECT time, 'ACTION' as type, CONCAT(action_type, ' -> ', target) as detail FROM action WHERE $where)
                    UNION ALL
                    (SELECT time, 'INVALID' as type, reason as detail FROM invalid_measure WHERE $where)
                    UNION ALL
                    (SELECT time, 'OUTLIER' as type, reason as detail FROM sound_outlier WHERE simulation_id IN (SELECT id FROM simulation WHERE team = $team_param OR $team_param=0))
                    ORDER BY time DESC LIMIT $limit";

            $res          = $conn->query($sql);
            $response     = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
            break;

        case 'get_teams':
            $sql = "SELECT team FROM user WHERE team IS NOT NULL UNION SELECT team FROM simulation ORDER BY team ASC";
            $res = $conn->query($sql);
            $teams = array_map(fn($row) => (int)$row[0], $res->fetch_all());
            $response = ["success" => true, "data" => $teams];
            break;

        // ── SYSTEM STATUS ─────────────────────────────────────────────────────
        case 'get_status':
            $status = [
                ["name" => "MySQL Database", "status" => "ONLINE"],
                ["name" => "MQTT Broker",    "status" => "OFFLINE"]
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
