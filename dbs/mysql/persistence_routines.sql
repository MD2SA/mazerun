DELIMITER //

DROP PROCEDURE IF EXISTS sp_insert_move //
CREATE PROCEDURE sp_insert_move(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT, 
    IN p_marsami INT, IN p_status INT, IN p_simulation_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM measures WHERE time = p_time AND Marsami = p_marsami) THEN
        INSERT INTO measures (time, originRoom, destinyRoom, Marsami, Status, simulation_id)
        VALUES (p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_simulation_id);
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_insert_temperature //
CREATE PROCEDURE sp_insert_temperature(
    IN p_time TIMESTAMP, IN p_temperature DECIMAL(5,2), IN p_room INT, IN p_simulation_id INT
)
BEGIN
    INSERT INTO temperature (time, temperature, room, simulation_id) 
    VALUES (p_time, CAST(p_temperature AS CHAR), p_room, p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_sound //
CREATE PROCEDURE sp_insert_sound(
    IN p_time TIMESTAMP, IN p_sound DECIMAL(5,2), IN p_room INT, IN p_simulation_id INT
)
BEGIN
    INSERT INTO sound (time, sound, room, simulation_id) 
    VALUES (p_time, CAST(p_sound AS CHAR), p_room, p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_invalid_data //
CREATE PROCEDURE sp_insert_invalid_data(
    IN p_time TIMESTAMP, IN p_originRoom INT, IN p_destinyRoom INT, IN p_marsami INT, 
    IN p_status INT, IN p_reason VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id) 
    VALUES (p_time, p_originRoom, 'SYSTEM', 0.0, 'INVALID_DATA', p_reason, NOW(), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_outlier //
CREATE PROCEDURE sp_insert_outlier(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2), 
    IN p_reason VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id) 
    VALUES (p_time, 0, p_sensor, p_value, 'OUTLIER', p_reason, NOW(), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_insert_alert //
CREATE PROCEDURE sp_insert_alert(
    IN p_time TIMESTAMP, IN p_sensor VARCHAR(10), IN p_value DECIMAL(10,2), 
    IN p_alertType VARCHAR(50), IN p_description VARCHAR(100), IN p_simulation_id INT
)
BEGIN
    INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id) 
    VALUES (p_time, 0, p_sensor, p_value, p_alertType, p_description, NOW(), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_register_score_event //
CREATE PROCEDURE sp_register_score_event(
    IN p_time TIMESTAMP, IN p_action_type VARCHAR(50), IN p_target VARCHAR(50), 
    IN p_value INT, IN p_simulation_id INT
)
BEGIN
    INSERT INTO message (time, room, sensor, reading, alertType, msg, insertTime, simulation_id) 
    VALUES (p_time, CAST(p_target AS UNSIGNED), 'SCORE', p_value, p_action_type, 'SCORE EQUILIBRIUM', NOW(), p_simulation_id);
END //

DROP PROCEDURE IF EXISTS sp_update_ocupation //
CREATE PROCEDURE sp_update_ocupation(
    IN p_room INT, IN p_odd INT, IN p_even INT, IN p_simulation_id INT
)
BEGIN
    INSERT INTO ocupation (oddMarsamis, evenMarsamis, Room, simulation_id) 
    VALUES (p_odd, p_even, p_room, p_simulation_id)
    ON DUPLICATE KEY UPDATE 
    oddMarsamis = p_odd,
    evenMarsamis = p_even;
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
