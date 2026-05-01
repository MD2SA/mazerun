USE mazerun;
DELIMITER //

DROP PROCEDURE IF EXISTS sp_insert_measure //
CREATE PROCEDURE sp_insert_measure(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT, 
    IN p_marsami INT, IN p_status INT, IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO measure (time, originRoom, destinyRoom, Marsami, Status, simulation_id)
        VALUES (p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_invalid_measure //
CREATE PROCEDURE sp_insert_invalid_measure(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT, IN p_marsami INT, 
    IN p_status INT, IN p_reason VARCHAR(100), IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO invalid_measure (time, originRoom, destinyRoom, marsami, status, reason, simulation_id)
        VALUES (p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_reason, p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_temperature //
CREATE PROCEDURE sp_insert_temperature(
    IN p_time TIMESTAMP, IN p_temperature DECIMAL(5,2), IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO temperature (time, temperature, room, simulation_id) 
        VALUES (p_time, p_temperature, 0, p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_sound //
CREATE PROCEDURE sp_insert_sound(
    IN p_time TIMESTAMP, IN p_sound DECIMAL(5,2), IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO sound (time, sound, room, simulation_id) 
        VALUES (p_time, p_sound, 0, p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_sound_outlier //
CREATE PROCEDURE sp_insert_sound_outlier(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2), 
    IN p_reason VARCHAR(100), IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO sound_outlier (time, sensor, value, reason, simulation_id) 
        VALUES (p_time, p_sensor, p_value, p_reason, p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_message //
CREATE PROCEDURE sp_insert_message(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2), 
    IN p_alertType VARCHAR(50), IN p_description VARCHAR(100), IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    -- Messages are often derived events, but we still use mongo_id for idempotency if provided
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id) 
        VALUES (p_time, 0, p_sensor, p_value, p_alertType, p_description, NOW(), p_simulation_id);
        
        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_update_ocupation //
CREATE PROCEDURE sp_update_ocupation(
    IN p_room INT, IN p_odd INT, IN p_even INT, IN p_simulation_id INT,
    IN p_mongo_id VARCHAR(50)
)
BEGIN
    -- Idempotency check
    IF p_mongo_id IS NOT NULL AND EXISTS (SELECT 1 FROM processed_event WHERE mongo_id = p_mongo_id) THEN
        BEGIN END;
    ELSE
        IF EXISTS (SELECT 1 FROM ocupation WHERE Room = p_room AND id = p_simulation_id) THEN
            UPDATE ocupation SET oddMarsamis = p_odd, evenMarsamis = p_even WHERE Room = p_room AND id = p_simulation_id;
        ELSE
            INSERT INTO ocupation (oddMarsamis, evenMarsamis, Room, id) 
            VALUES (p_odd, p_even, p_room, p_simulation_id);
        END IF;

        IF p_mongo_id IS NOT NULL THEN
            INSERT IGNORE INTO processed_event (mongo_id) VALUES (p_mongo_id);
        END IF;
    END IF;
    SELECT 1;
END //

DROP PROCEDURE IF EXISTS sp_insert_simulation //
CREATE PROCEDURE sp_insert_simulation(
    IN p_sim_id INT, IN p_team INT, IN p_start_date TIMESTAMP
)
BEGIN
    INSERT IGNORE INTO simulation (id, description, team, startDate, user_email)
    VALUES (p_sim_id, CONCAT('Simulation ', p_sim_id), p_team, p_start_date, 'aluno@iscte-iul.pt');
END //

DELIMITER ;
