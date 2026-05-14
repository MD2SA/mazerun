USE mazerun;
-- Stored procedures to manage the table 'user' with RBAC enforcement

-- Procedure to create a new user (Sign-up)
DELIMITER //

DROP PROCEDURE IF EXISTS sp_create_user //
CREATE PROCEDURE sp_create_user(
    IN p_name VARCHAR(100),
    IN p_phone VARCHAR(12),
    IN p_type ENUM('usr', 'adm'),
    IN p_email VARCHAR(50),
    IN p_birth DATE,
    IN p_team INT
)
BEGIN
    -- Admins should not have a team
    IF p_type = 'adm' THEN
        SET p_team = NULL;
    END IF;

    INSERT INTO user (name, phone, type, email, birth, team)
    VALUES (p_name, p_phone, p_type, p_email, p_birth, p_team);
    SELECT 'User created successfully' AS message;
END //

-- Procedure to update a user (RBAC)
DROP PROCEDURE IF EXISTS sp_update_user //
CREATE PROCEDURE sp_update_user(
    IN p_current_user_email VARCHAR(50),
    IN p_target_email VARCHAR(50),
    IN p_name VARCHAR(100),
    IN p_phone VARCHAR(12),
    IN p_type ENUM('usr', 'adm'),
    IN p_birth DATE,
    IN p_team INT
)
BEGIN
    DECLARE v_current_type ENUM('usr', 'adm');
    DECLARE v_new_type ENUM('usr', 'adm');

    SELECT type INTO v_current_type FROM user WHERE email = p_current_user_email;
    
    -- Admins can update anyone, users can only update themselves
    IF v_current_type = 'adm' OR p_current_user_email = p_target_email THEN
        SET v_new_type = CASE WHEN v_current_type = 'adm' THEN p_type ELSE (SELECT type FROM user WHERE email = p_target_email) END;

        -- Admins should not have a team
        IF v_new_type = 'adm' THEN
            SET p_team = NULL;
        END IF;

        UPDATE user
        SET name = p_name,
            phone = p_phone,
            type = v_new_type,
            birth = p_birth,
            team = p_team
        WHERE email = p_target_email;
        SELECT 'User updated successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Permission denied: Cannot update other users';
    END IF;
END //

-- Procedure to delete a user (RBAC)
DROP PROCEDURE IF EXISTS sp_delete_user //
CREATE PROCEDURE sp_delete_user(
    IN p_current_user_email VARCHAR(50),
    IN p_target_email VARCHAR(50)
)
BEGIN
    DECLARE v_current_type ENUM('usr', 'adm');
    
    SELECT type INTO v_current_type FROM user WHERE email = p_current_user_email;
    
    -- Admins can delete anyone, users can only delete themselves
    IF v_current_type = 'adm' OR p_current_user_email = p_target_email THEN
        DELETE FROM user WHERE email = p_target_email;
        SELECT 'User deleted successfully' AS message;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Permission denied: Cannot delete other users';
    END IF;
END //

-- Get all users (Admin only logic should be in API, but this procedure exists)
DROP PROCEDURE IF EXISTS sp_get_all_users //
CREATE PROCEDURE sp_get_all_users()
BEGIN
    SELECT name, phone, type, email, birth, team FROM user ORDER BY name;
END //

DELIMITER ;
