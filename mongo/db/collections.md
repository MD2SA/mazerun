# Estrutura das Coleções MongoDB

No total existem **8 coleções físicas** gravadas no MongoDB (incluindo a nova coleção `alerts`).
Abaixo encontras todos os *schemas* isolados e limpos. No final do documento está a explicação do objetivo de cada uma.

Nota: Como o MongoDB é *schemaless*, campos extra enviados pelos sensores são guardados automaticamente sem necessidade de alterar o código.

---

## 1. Schemas

### `active_sessions`
```json
{
  "_id": 1,
  "simulation_id": 50,
  "registered_at": "ISODate"
}
```

### `simulation_configs`
```json
{
  "_id": 50,
  "numbermarsamis": 30,
  "numberrooms": 10,
  "numberplayers": 40,
  "normalnoise": 10.0,
  "noisevartoleration": 17.0,
  "normaltemperature": 15,
  "temperaturevarhightoleration": 20,
  "temperaturevarlowtoleration": 1,
  "loaded_at": "ISODate"
}
```

### `actions`
```json
{
  "_id": "ObjectId",
  "Action": "OPEN_DOOR",
  "Value": 1,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `temperature` e `sound` (Sensores)
```json
{
  "_id": "ObjectId",
  "Sensor": "T1",
  "Value": 25.4,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `moves`
```json
{
  "_id": "ObjectId",
  "Marsami": 123,
  "RoomOrigin": 1,
  "RoomDestiny": 2,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `rooms`
```json
{
  "_id": "ObjectId",
  "room_id": 5,
  "simulation_id": 50,
  "player_id": 1,
  "marsami_count": 3,
  "current_marsamis": [123, 124, 125],
  "last_update": "ISODate",
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `alerts`
```json
{
  "_id": "ObjectId",
  "collection": "sound",
  "player": 1,
  "game": 1,
  "simulation_id": 50,
  "sensor": "sound",
  "value": 35.0,
  "alertType": "HIGH_SOUND",
  "alert": "High sound level detected (35.0 dB)",
  "timestamp": "ISODate",
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

---

## 2. Explicação de cada Entidade

* **`active_sessions`**: Gere o estado atual do *handshake* dos jogadores em jogo. Guarda a sessão ativa (ID de simulação) associada a cada jogador. O ID do jogador funciona como `_id` na coleção.
* **`simulation_configs`**: Guarda em cache a configuração lida diretamente do MySQL no início de cada simulação. O `_id` é o ID da simulação para garantir unicidade e não estar sempre a fazer consultas ao MySQL.
* **`actions`**: Regista as ações disparadas e recebidas no sistema e os respetivos *payloads* (ex: "OPEN_DOOR").
* **`temperature` e `sound`**: Guardam os *payloads* em bruto recebidos diretamente dos sensores via MQTT. Os campos em maiúsculas vêm exatamente do payload original.
* **`moves`**: Especializada para o rastreio histórico das movimentações de jogadores e marsamis através do labirinto (sala de origem para sala de destino).
* **`rooms`**: Coleção especial que mantém o **estado agregado** (quantidade total e lista individual de marsamis) das salas em tempo real, sempre isolado por simulação. Atualizado automaticamente em *upsert* cada vez que um documento novo de `moves` é processado pelo MongoDB (soma ou retira do total).
* **`alerts`**: Os alertas agora **formam uma coleção dedicada**. O sistema analisa as anomalias dos sensores (como temperatura ou som demasiado altos) e insere um documento na coleção `alerts` com `process_status: "pending"`. O `AlertWorker` processa-os e envia via MQTT para o MySQL com **garantia de entrega** (retries automáticos se o MySQL falhar a gravação).

### O fluxo `process_status`

A maior parte das coleções sujeitas a migração para o MySQL sofre um ciclo de estados que altera os documentos:
1. Começa como `"pending"`.
2. Um *worker* de processamento apanha o documento, altera-o para `"processing"`, e regista o `sent_at`.
3. Quando o *script* de MySQL sinaliza sucesso (via MQTT ACK), o documento passa a `"processed"` e recebe a flag cronológica de `processed_at`.
