USE mazerun;
-- Stored procedures to manage the table 'simulation'

-- Procedure to create a new game/simulation
DELIMITER //

CREATE PROCEDURE sp_create_game(
    IN p_descricao TEXT,
    IN p_equipa INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        @p_message = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @p_message;
    END;

    INSERT INTO simulation (description, team, startDate)
    VALUES (p_descricao, p_equipa, NOW());

    SELECT LAST_INSERT_ID() AS game_id, 'Game created successfully' AS message;
END //

-- Procedure to update an existing game/simulation
CREATE PROCEDURE sp_update_game(
    IN p_descricao TEXT,
    IN p_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        @p_message = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @p_message;
    END;

    IF EXISTS (SELECT 1 FROM simulation WHERE id = p_id) THEN
        UPDATE simulation
        SET description = p_descricao
        WHERE id = p_id;

        SELECT 'Game updated successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Game not found';
    END IF;
END //

-- Procedure to get games for logged user or specific user if admin
CREATE PROCEDURE sp_get_user_games(
    IN p_email VARCHAR(50)
)
BEGIN
    DECLARE user_type VARCHAR(3);

    -- Get user type to determine if admin
    SELECT type INTO user_type
    FROM user
    WHERE email = p_email;

    -- If user is admin (assuming 'ADM' or similar), return all games
    -- Otherwise return only games for that user
    IF user_type = 'ADM' THEN
        SELECT s.id, s.description, s.team, s.user_email, s.startDate
        FROM simulation s
        ORDER BY s.startDate DESC;
    ELSE
        SELECT s.id, s.description, s.team, s.user_email, s.startDate
        FROM simulation s
        WHERE s.user_email = p_email
        ORDER BY s.startDate DESC;
    END IF;
END //

-- Procedure to get all games (admin only)
CREATE PROCEDURE sp_get_all_games()
BEGIN
    SELECT s.id, s.description, s.team, s.user_email, s.startDate
    FROM simulation s
    ORDER BY s.startDate DESC;
END //

DELIMITER ;


