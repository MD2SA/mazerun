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
const PUBLIC_ACTIONS = ['login', 'register', 'get_status', 'check_mazerun'];

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

function mqtt_encode_remaining_length(int $length): string {
    $encoded = '';
    do {
        $byte = $length % 128;
        $length = intdiv($length, 128);
        if ($length > 0) {
            $byte |= 128;
        }
        $encoded .= chr($byte);
    } while ($length > 0);
    return $encoded;
}

function mqtt_read_remaining_length($socket): ?int {
    $multiplier = 1;
    $value = 0;

    do {
        $encodedByte = fread($socket, 1);
        if ($encodedByte === false || $encodedByte === '') {
            return null;
        }

        $byte = ord($encodedByte);
        $value += ($byte & 127) * $multiplier;
        $multiplier *= 128;

        if ($multiplier > 128 * 128 * 128) {
            return null;
        }
    } while (($byte & 128) !== 0);

    return $value;
}

function mqtt_read_packet($socket): ?array {
    $header = fread($socket, 1);
    if ($header === false || $header === '') {
        return null;
    }

    $remainingLength = mqtt_read_remaining_length($socket);
    if ($remainingLength === null) {
        return null;
    }

    $body = '';
    while (strlen($body) < $remainingLength) {
        $chunk = fread($socket, $remainingLength - strlen($body));
        if ($chunk === false || $chunk === '') {
            return null;
        }
        $body .= $chunk;
    }

    return ['type' => ord($header) >> 4, 'body' => $body];
}

function mqtt_write_packet($socket, int $packetType, string $body, int $flags = 0): void {
    fwrite($socket, chr(($packetType << 4) | $flags) . mqtt_encode_remaining_length(strlen($body)) . $body);
}

function mqtt_string(string $value): string {
    return pack('n', strlen($value)) . $value;
}

function mqtt_start_simulation(int $team, int $playerId, int $simulationId): array {
    $broker = getenv('MQTT_BROKER') ?: 'broker.hivemq.com';
    $port = (int)(getenv('MQTT_PORT') ?: 1883);
    $timeout = (int)(getenv('MQTT_HANDSHAKE_TIMEOUT') ?: 12);
    $handshakeId = bin2hex(random_bytes(16));
    $clientId = 'mazerun-web-' . bin2hex(random_bytes(4));
    $topicStart = "pisid/$team/game/start";
    $topicAck = "pisid/$team/game/start/ack";

    $socket = @fsockopen($broker, $port, $errno, $errstr, 5);
    if (!$socket) {
        return [
            'success' => false,
            'message' => "MQTT connection failed: $errstr",
            'topic_start' => $topicStart,
            'topic_ack' => $topicAck
        ];
    }

    stream_set_timeout($socket, 2);

    $connectBody = mqtt_string('MQTT') . chr(4) . chr(2) . pack('n', 30) . mqtt_string($clientId);
    mqtt_write_packet($socket, 1, $connectBody);

    $packet = mqtt_read_packet($socket);
    if (!$packet) {
        fclose($socket);
        return [
            'success' => false,
            'message' => 'MQTT broker connection timed out before CONNACK',
            'topic_start' => $topicStart,
            'topic_ack' => $topicAck
        ];
    }

    if ($packet['type'] !== 2 || strlen($packet['body']) < 2) {
        fclose($socket);
        return [
            'success' => false,
            'message' => 'MQTT broker returned an invalid CONNACK packet',
            'topic_start' => $topicStart,
            'topic_ack' => $topicAck
        ];
    }

    $connackCode = ord($packet['body'][1]);
    if ($connackCode !== 0) {
        fclose($socket);
        return [
            'success' => false,
            'message' => "MQTT broker rejected the connection with code $connackCode",
            'topic_start' => $topicStart,
            'topic_ack' => $topicAck
        ];
    }

    $packetId = random_int(1, 65535);
    $subscribeBody = pack('n', $packetId) . mqtt_string($topicAck) . chr(0);
    mqtt_write_packet($socket, 8, $subscribeBody, 2);

    $packet = mqtt_read_packet($socket);
    if (!$packet || $packet['type'] !== 9) {
        fclose($socket);
        return [
            'success' => false,
            'message' => "MQTT subscribe failed for $topicAck",
            'topic_start' => $topicStart,
            'topic_ack' => $topicAck
        ];
    }

    $payload = json_encode([
        'player_id' => $playerId,
        'simulation_id' => $simulationId,
        'handshake_id' => $handshakeId
    ]);
    mqtt_write_packet($socket, 3, mqtt_string($topicStart) . $payload);

    $deadline = time() + $timeout;
    while (time() < $deadline) {
        $packet = mqtt_read_packet($socket);
        if (!$packet || $packet['type'] !== 3) {
            continue;
        }

        $body = $packet['body'];
        if (strlen($body) < 2) {
            continue;
        }

        $topicLength = unpack('n', substr($body, 0, 2))[1];
        $topic = substr($body, 2, $topicLength);
        $message = substr($body, 2 + $topicLength);
        $ack = json_decode($message, true);

        if (
            $topic === $topicAck &&
            is_array($ack) &&
            (int)($ack['player_id'] ?? 0) === $playerId &&
            (int)($ack['simulation_id'] ?? 0) === $simulationId &&
            ($ack['handshake_id'] ?? '') === $handshakeId
        ) {
            mqtt_write_packet($socket, 14, '');
            fclose($socket);
            return [
                'success' => true,
                'message' => 'MongoDB acknowledged the simulation start',
                'handshake_id' => $handshakeId,
                'topic_start' => $topicStart,
                'topic_ack' => $topicAck
            ];
        }
    }

    mqtt_write_packet($socket, 14, '');
    fclose($socket);

    return [
        'success' => false,
        'message' => 'Timeout waiting for MongoDB simulation ACK',
        'handshake_id' => $handshakeId,
        'topic_start' => $topicStart,
        'topic_ack' => $topicAck
    ];
}

function start_mazerun_process(int $team, int $simulationId): array {
    $exePath = getenv('MAZERUN_EXE_PATH') ?: '/game/server/mazerun.exe';
    $broker = getenv('MQTT_BROKER') ?: 'broker.hivemq.com';
    $port = (int)(getenv('MQTT_PORT') ?: 1883);
    $delay = (int)(getenv('MAZERUN_DELAY') ?: 2);
    $logFile = "/tmp/mazerun-$simulationId.log";
    $winePrefix = "/tmp/wine-mazerun";

    if (!file_exists($exePath)) {
        return [
            'success' => false,
            'message' => "mazerun.exe not found at $exePath",
            'log_file' => $logFile
        ];
    }

    $command = sprintf(
        'mkdir -p %s && HOME=/tmp XDG_RUNTIME_DIR=/tmp WINEPREFIX=%s WINEDEBUG=-all nohup wine %s %d --flagMessage 1 --delay %d --broker %s --portbroker %d > %s 2>&1 & echo $!',
        escapeshellarg($winePrefix),
        escapeshellarg($winePrefix),
        escapeshellarg($exePath),
        $team,
        $delay,
        escapeshellarg($broker),
        $port,
        escapeshellarg($logFile)
    );

    $output = [];
    $exitCode = 0;
    exec($command, $output, $exitCode);
    $pid = isset($output[0]) ? (int)$output[0] : 0;

    if ($exitCode !== 0 || $pid <= 0) {
        return [
            'success' => false,
            'message' => 'Failed to start mazerun.exe',
            'log_file' => $logFile
        ];
    }

    usleep(500000);
    $checkOutput = [];
    $checkExitCode = 0;
    exec('kill -0 ' . $pid . ' 2>/dev/null', $checkOutput, $checkExitCode);

    if ($checkExitCode !== 0) {
        $logPreview = file_exists($logFile) ? trim(substr(file_get_contents($logFile), 0, 1000)) : '';
        return [
            'success' => false,
            'message' => 'mazerun.exe exited immediately',
            'pid' => $pid,
            'log_file' => $logFile,
            'log_preview' => $logPreview
        ];
    }

    return [
        'success' => true,
        'message' => 'mazerun.exe started',
        'pid' => $pid,
        'log_file' => $logFile
    ];
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
            $res   = $conn->query("CALL sp_get_all_users()");
            $users = $res->fetch_all(MYSQLI_ASSOC);
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
            $team = (int)($authPayload['team'] ?? 0);
            $owner_email = $requester_email;

            if ($authPayload['type'] === 'adm') {
                $team = (int)($data['team'] ?? $team);
                $owner_email = trim($data['owner_email'] ?? $requester_email);

                $ownerStmt = $conn->prepare("SELECT email FROM user WHERE email = ?");
                $ownerStmt->bind_param("s", $owner_email);
                $ownerStmt->execute();
                if (!$ownerStmt->get_result()->fetch_assoc()) {
                    $response = ["success" => false, "message" => "Owner user email does not exist"];
                    break;
                }
            }

            $player_id = $team;

            if ($team <= 0) {
                $response = ["success" => false, "message" => "User team is required to start a simulation"];
                break;
            }

            $stmt = $conn->prepare("CALL sp_create_game(?, ?, ?, ?)");
            $stmt->bind_param("ssii", $requester_email, $data['description'], $team, $player_id);
            $response = handle_sp_result($stmt);

            $simulation_id = (int)($response['data']['game_id'] ?? 0);
            if (!$simulation_id) {
                $response = ["success" => false, "message" => "Simulation was created but no game_id was returned"];
                break;
            }

            if ($owner_email !== $requester_email) {
                $ownerUpdateStmt = $conn->prepare("UPDATE simulation SET user_email = ? WHERE id = ?");
                $ownerUpdateStmt->bind_param("si", $owner_email, $simulation_id);
                $ownerUpdateStmt->execute();
            }

            $startResult = mqtt_start_simulation($team, $player_id, $simulation_id);
            $response['data']['player_id'] = $player_id;
            $response['data']['team'] = $team;
            $response['data']['owner_email'] = $owner_email;
            $response['data']['mqtt'] = $startResult;
            $response['data']['started'] = $startResult['success'];

            if (!$startResult['success']) {
                $cleanupStmt = $conn->prepare("DELETE FROM simulation WHERE id = ? AND user_email = ?");
                $cleanupStmt->bind_param("is", $simulation_id, $owner_email);
                $cleanupStmt->execute();

                $response['success'] = false;
                $response['message'] = "Simulation start failed and was rolled back: " . $startResult['message'];
                $response['data']['rolled_back'] = $cleanupStmt->affected_rows > 0;
            } else {
                $gameResult = start_mazerun_process($team, $simulation_id);
                $response['data']['game'] = $gameResult;

                if (!$gameResult['success']) {
                    $cleanupStmt = $conn->prepare("DELETE FROM simulation WHERE id = ? AND user_email = ?");
                    $cleanupStmt->bind_param("is", $simulation_id, $owner_email);
                    $cleanupStmt->execute();

                    $response['success'] = false;
                    $response['message'] = "Simulation handshake succeeded, but game start failed and was rolled back: " . $gameResult['message'];
                    $response['data']['rolled_back'] = $cleanupStmt->affected_rows > 0;
                    break;
                }

                $response['message'] = "Simulation created and game started successfully";
            }
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
            $where = !empty($teamFilter) ? "WHERE team = " . (int)$teamFilter : "";
            $stats = [
                "total_sims"     => $conn->query("SELECT COUNT(*) FROM simulation $where")->fetch_row()[0],
                "total_measures" => $conn->query("SELECT COUNT(*) FROM measure m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
                "total_alerts"   => $conn->query("SELECT COUNT(*) FROM alert m JOIN simulation s ON m.simulation_id = s.id $where")->fetch_row()[0],
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
            $limit        = (int)($_GET['limit'] ?? $data['limit'] ?? 100);
            $where        = $sim_id_param ? "WHERE simulation_id = $sim_id_param" : "";
            $sql          = "(SELECT time, 'ALERT' as type, msg as detail FROM alert $where) UNION ALL (SELECT time, 'ACTION' as type, CONCAT(action_type, ' -> ', target) as detail FROM action $where) UNION ALL (SELECT time, 'INVALID' as type, reason as detail FROM invalid_measure $where) UNION ALL (SELECT time, 'OUTLIER' as type, reason as detail FROM sound_outlier $where) ORDER BY time DESC LIMIT $limit";
            $res          = $conn->query($sql);
            $response     = ["success" => true, "data" => $res->fetch_all(MYSQLI_ASSOC)];
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

        case 'check_mazerun':
            $isRunning = false;
            $output = [];
            $exitCode = 0;
            if (strncasecmp(PHP_OS, 'WIN', 3) === 0) {
                @exec("tasklist /FI \"IMAGENAME eq mazerun.exe\"", $output, $exitCode);
                foreach ($output as $line) {
                    if (stripos($line, 'mazerun.exe') !== false) {
                        $isRunning = true;
                        break;
                    }
                }
            } else {
                @exec("pgrep -f mazerun.exe", $output, $exitCode);
                if ($exitCode === 0 && !empty($output)) {
                    $isRunning = true;
                }
            }
            $response = ["success" => true, "running" => $isRunning];
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
