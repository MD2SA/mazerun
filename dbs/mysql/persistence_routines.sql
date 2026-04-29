DELIMITER //

DROP PROCEDURE IF EXISTS sp_insert_measure //
CREATE PROCEDURE sp_insert_measure(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT,
    IN p_marsami INT, IN p_status INT, IN p_simulation_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM measure WHERE time = p_time AND Marsami = p_marsami) THEN
        INSERT INTO measure (time, originRoom, destinyRoom, Marsami, Status, simulation_id)
        VALUES (p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_simulation_id);
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_insert_invalid_measure //
CREATE PROCEDURE sp_insert_invalid_measure(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT, IN p_marsami INT,
    IN p_status INT, IN p_reason VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO invalid_measure (time, originRoom, destinyRoom, Marsami, Status, reason, simulation_id)
    VALUES (p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_reason, p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_temperature //
CREATE PROCEDURE sp_insert_temperature(
    IN p_time TIMESTAMP, IN p_temperature DECIMAL(5,2), IN p_simulation_id INT
)
BEGIN
    INSERT INTO temperature (time, temperature, simulation_id)
    VALUES (p_time, CAST(p_temperature AS CHAR), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_sound //
CREATE PROCEDURE sp_insert_sound(
    IN p_time TIMESTAMP, IN p_sound DECIMAL(5,2), IN p_simulation_id INT
)
BEGIN
    INSERT INTO sound (time, sound, simulation_id)
    VALUES (p_time, CAST(p_sound AS CHAR), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_sound_outlier //
CREATE PROCEDURE sp_insert_sound_outlier(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2),
    IN p_reason VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO sound_outlier (time, sensor, value, reason, simulation_id)
    VALUES (p_time, p_sensor, p_value, p_reason, p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_message //
CREATE PROCEDURE sp_insert_message(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2),
    IN p_alertType VARCHAR(50), IN p_description VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id)
    VALUES (p_time, 0, p_sensor, p_value, p_alertType, p_description, NOW(), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_initialize_ocupation //
CREATE PROCEDURE sp_initialize_ocupation(IN p_simulation_id INT)
BEGIN
    IF EXISTS (SELECT 1 FROM ocupation WHERE Room = 1 AND simulation_id = p_simulation_id) THEN
        UPDATE ocupation SET oddMarsamis = 0, evenMarsamis = 0 WHERE Room = 1 AND simulation_id = p_simulation_id;
    ELSE
        INSERT INTO ocupation (oddMarsamis, evenMarsamis, Room, simulation_id)
        VALUES (0, 0, 1, p_simulation_id);
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_update_ocupation //
CREATE PROCEDURE sp_update_ocupation(
    IN p_room INT, IN p_odd INT, IN p_even INT, IN p_simulation_id INT
)
BEGIN
    IF EXISTS (SELECT 1 FROM ocupation WHERE Room = p_room AND simulation_id = p_simulation_id) THEN
        UPDATE ocupation SET oddMarsamis = p_odd, evenMarsamis = p_even WHERE Room = p_room AND simulation_id = p_simulation_id;
    ELSE
        INSERT INTO ocupation (oddMarsamis, evenMarsamis, Room, simulation_id)
        VALUES (p_odd, p_even, p_room, p_simulation_id);
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_insert_simulation //
CREATE PROCEDURE sp_insert_simulation(
    IN p_sim_id INT, IN p_team INT, IN p_start_date TIMESTAMP
)
BEGIN
    INSERT IGNORE INTO simulation (id, description, team, startDate)
    VALUES (p_sim_id, CONCAT('Simulation ', p_sim_id, ' for Team ', p_team), p_team, p_start_date);
END //

DELIMITER ;
