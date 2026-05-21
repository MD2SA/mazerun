<?php
if (php_sapi_name() !== 'cli') {
    exit(1);
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

function mqtt_write_packet($socket, int $packetType, string $body, int $flags = 0): void {
    fwrite($socket, chr(($packetType << 4) | $flags) . mqtt_encode_remaining_length(strlen($body)) . $body);
}

function mqtt_string(string $value): string {
    return pack('n', strlen($value)) . $value;
}

function mqtt_connect($broker, $port, $clientId) {
    $socket = @fsockopen($broker, $port, $errno, $errstr, 5);
    if (!$socket) {
        return null;
    }
    stream_set_timeout($socket, 3);
    $connectBody = mqtt_string('MQTT') . chr(4) . chr(2) . pack('n', 30) . mqtt_string($clientId);
    mqtt_write_packet($socket, 1, $connectBody);
    $header = fread($socket, 4);
    if ($header === false || strlen($header) < 4 || ord($header[0]) !== 0x20 || ord($header[3]) !== 0x00) {
        fclose($socket);
        return null;
    }
    return $socket;
}

function publish_simulation_finished(int $team, int $playerId, int $simulationId): bool {
    $broker = getenv('MQTT_BROKER') ?: 'broker.hivemq.com';
    $port = (int)(getenv('MQTT_PORT') ?: 1883);
    $socket = mqtt_connect($broker, $port, 'mazerun-finish-' . bin2hex(random_bytes(4)));
    if (!$socket) {
        return false;
    }

    $topic = "pisid/$team/simulation/finished";
    $payload = json_encode([
        'simulation_id' => $simulationId,
        'player_id' => $playerId,
        'timestamp' => gmdate('c')
    ]);
    mqtt_write_packet($socket, 3, mqtt_string($topic) . $payload);
    mqtt_write_packet($socket, 14, '');
    fclose($socket);
    return true;
}

function sync_final_score(int $simulationId, int $playerId): void {
    try {
        $remote = new mysqli('194.210.86.10', 'aluno', 'aluno', 'maze');
        $remote->set_charset('utf8mb4');

        $stmt = $remote->prepare("SELECT COALESCE(SUM(score), 0) AS total_score FROM roomsscore WHERE playerId = ?");
        $stmt->bind_param("i", $playerId);
        $stmt->execute();
        $row = $stmt->get_result()->fetch_assoc();
        $totalScore = (int)($row['total_score'] ?? 0);
        $stmt->close();
        $remote->close();

        $local = new mysqli('mysql-db', 'root', 'root', 'mazerun');
        $local->set_charset('utf8mb4');
        $local->query("ALTER TABLE simulation ADD COLUMN IF NOT EXISTS total_score BIGINT NULL");
        $update = $local->prepare("UPDATE simulation SET total_score = ? WHERE id = ? AND player_id = ?");
        $update->bind_param("iii", $totalScore, $simulationId, $playerId);
        $update->execute();
        $update->close();
        $local->close();
    } catch (Throwable $e) {
        error_log("[simulation_finish_watcher] Failed to sync final score: " . $e->getMessage());
    }
}

if ($argc < 5) {
    exit(1);
}

$team = (int)$argv[1];
$playerId = (int)$argv[2];
$simulationId = (int)$argv[3];
$pid = (int)$argv[4];

while (true) {
    if ($pid <= 0) {
        break;
    }
    $alive = false;
    @exec('kill -0 ' . $pid . ' 2>/dev/null', $o, $code);
    if ((int)$code === 0) {
        $alive = true;
    }
    if (!$alive) {
        break;
    }
    sleep(2);
}

sync_final_score($simulationId, $playerId);
publish_simulation_finished($team, $playerId, $simulationId);

