# Estrutura das Coleções MongoDB

Aqui tens a estrutura esperada (*schema*) de cada coleção, baseada na lógica de inserção do código.

## 1. `active_sessions`

Gere o estado atual do *handshake*.

```json
{
  "_id": 1,                     // ID do jogador (player_id)
  "simulation_id": 50,
  "registered_at": "ISODate"
}
```

---

## 2. Coleções de Sensores

Coleções: `temperature`, `sound`, `actions`

Os campos em maiúsculas vêm diretamente do *payload* do sensor via MQTT.

```json
{
  "_id": "ObjectId",
  "Sensor": "T1",
  "Value": 25.4,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending"
}
```

---

## 3. `simulation_configs`

Guarda a configuração lida diretamente do MySQL de consulta no início de cada
simulação. O `_id` é o ID da simulação, garantindo uma única configuração por
simulação.

```json
{
  "_id": 50,                     // ID da simulação
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

---

## 4. `moves`

Especializada para o rastreio de jogadores no labirinto.

```json
{
  "_id": "ObjectId",
  "Marsami": 123,
  "RoomOrigin": 1,
  "RoomDestiny": 2,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending"
}
```

---

## 5. `rooms`

Mantém o estado agregado das salas em tempo real, isolado por simulação.

```json
{
  "_id": "ObjectId",           // Gerado automaticamente
  "room_id": 5,                // Número da sala
  "simulation_id": 50,         // ID da simulação (Isolamento)
  "player_id": 1,              // ID do jogador associado
  "marsami_count": 3,
  "current_marsamis": [
    123,
    124,
    125
  ],
  "last_update": "ISODate",
  "process_status": "pending"
}
```

---

## Nota

Como o MongoDB é *schemaless*, se um sensor novo enviar um campo extra, por exemplo:

```json
{
  "BatteryLevel": 87
}
```

esse campo será guardado automaticamente no documento da respetiva coleção, sem ser necessário alterar o código.
