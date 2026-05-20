USE mazerun;
-- Stored procedures to manage 'simulation'

DELIMITER //

-- Procedure to create a new game/simulation
DROP PROCEDURE IF EXISTS sp_create_game //
CREATE PROCEDURE sp_create_game(
    IN p_current_user_email VARCHAR(50),
    IN p_descricao TEXT,
    IN p_equipa INT,
    IN p_player_id INT
)
BEGIN
    DECLARE v_current_type ENUM('usr', 'adm');
    DECLARE v_current_team INT;

    SELECT type, team INTO v_current_type, v_current_team
    FROM user
    WHERE email = p_current_user_email;

    IF v_current_type IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Permission denied: Unknown user';
    END IF;

    IF v_current_type <> 'adm' THEN
        SET p_equipa = v_current_team;
    END IF;

    INSERT INTO simulation (description, team, startDate, player_id, user_email)
    VALUES (p_descricao, p_equipa, NOW(), p_player_id, p_current_user_email);
    SELECT LAST_INSERT_ID() AS game_id, 'Game created successfully' AS message;
END //

-- Procedure to update an existing game/simulation (Admin only)
DROP PROCEDURE IF EXISTS sp_update_game //
CREATE PROCEDURE sp_update_game(
    IN p_current_user_email VARCHAR(50),
    IN p_id INT,
    IN p_descricao TEXT,
    IN p_equipa INT
)
BEGIN
    DECLARE v_current_type ENUM('usr', 'adm');
    SELECT type INTO v_current_type FROM user WHERE email = p_current_user_email;

    IF v_current_type = 'adm' THEN
        UPDATE simulation SET description = p_descricao, team = p_equipa WHERE id = p_id;
        SELECT 'Game updated successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Permission denied: Only admins can update simulations';
    END IF;
END //

DELIMITER ;
