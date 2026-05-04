USE mazerun;
-- Stored procedures to manage the table 'user'

-- Procedure to create a new user
DELIMITER //

CREATE PROCEDURE sp_create_user(
    IN p_name VARCHAR(100),
    IN p_phone VARCHAR(12),
    IN p_type VARCHAR(3),
    IN p_email VARCHAR(50),
    IN p_password VARCHAR(255),
    IN p_birth DATE,
    IN p_team INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        @p_message = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @p_message;
    END;

    INSERT INTO user (name, phone, type, email, password, birth, team)
    VALUES (p_name, p_phone, p_type, p_email, p_password, p_birth, p_team);

    SELECT 'User created successfully' AS message;
END //

-- Procedure to update an existing user
CREATE PROCEDURE sp_update_user(
    IN p_email VARCHAR(50),
    IN p_name VARCHAR(100),
    IN p_phone VARCHAR(12),
    IN p_type VARCHAR(3),
    IN p_password VARCHAR(255),
    IN p_birth DATE,
    IN p_team INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        @p_message = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @p_message;
    END;

    IF EXISTS (SELECT 1 FROM user WHERE email = p_email) THEN
        UPDATE user
        SET name = p_name,
            phone = p_phone,
            type = p_type,
            password = p_password,
            birth = p_birth,
            team = p_team
        WHERE email = p_email;

        SELECT 'User updated successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;
END //

-- Procedure to delete a user
CREATE PROCEDURE sp_delete_user(
    IN p_email VARCHAR(50)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
        @p_message = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @p_message;
    END;

    IF EXISTS (SELECT 1 FROM user WHERE email = p_email) THEN
        DELETE FROM user WHERE email = p_email;
        SELECT 'User deleted successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;
END //

-- Procedure to get a user by email
CREATE PROCEDURE sp_get_user(
    IN p_email VARCHAR(50)
)
BEGIN
    SELECT name, phone, type, email, birth, team
    FROM user
    WHERE email = p_email;
END //

-- Procedure to get all users (admin only)
CREATE PROCEDURE sp_get_all_users()
BEGIN
    SELECT name, phone, type, email, birth, team
    FROM user
    ORDER BY email;
END //

DELIMITER ;
