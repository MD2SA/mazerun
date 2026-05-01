USE mazerun;
-- 1. Creates the users
CREATE USER IF NOT EXISTS 'adm_user'@'%' IDENTIFIED BY 'pass_adm';
CREATE USER IF NOT EXISTS 'migrator_user'@'%' IDENTIFIED BY 'pass_migrator';
CREATE USER IF NOT EXISTS 'operational_user'@'%' IDENTIFIED BY 'pass_operational';
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'pass_user';

-- 2. Admin privileges
GRANT SELECT, UPDATE, DELETE ON mazerun.user TO 'adm_user'@'%';
GRANT SELECT, UPDATE, DELETE ON mazerun.simulation TO 'adm_user'@'%';
GRANT SELECT, UPDATE, DELETE ON mazerun.message TO 'adm_user'@'%';
GRANT SELECT, UPDATE, DELETE ON mazerun.sound_outlier TO 'adm_user'@'%';
GRANT SELECT, UPDATE, DELETE ON mazerun.invalid_measure TO 'adm_user'@'%';
GRANT SELECT, UPDATE, DELETE ON mazerun.processed_event TO 'adm_user'@'%';
GRANT SELECT ON mazerun.ocupation TO 'adm_user'@'%';
GRANT SELECT ON mazerun.temperature TO 'adm_user'@'%';
GRANT SELECT ON mazerun.sound TO 'adm_user'@'%';
GRANT SELECT ON mazerun.measure TO 'adm_user'@'%';
GRANT SELECT ON mazerun.action TO 'adm_user'@'%';

-- 3. Migrator privileges
GRANT INSERT ON mazerun.simulation TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.ocupation TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.temperature TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.sound TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.message TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.sound_outlier TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.invalid_measure TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.processed_event TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.measure TO 'migrator_user'@'%';
GRANT INSERT ON mazerun.action TO 'migrator_user'@'%';

-- 4. Operational privileges
GRANT SELECT, UPDATE ON mazerun.user TO 'operational_user'@'%';
GRANT SELECT, UPDATE ON mazerun.simulation TO 'operational_user'@'%';
GRANT SELECT, INSERT ON mazerun.message TO 'operational_user'@'%';
GRANT SELECT, INSERT ON mazerun.sound_outlier TO 'operational_user'@'%';
GRANT SELECT, INSERT ON mazerun.invalid_measure TO 'operational_user'@'%';
GRANT SELECT, INSERT ON mazerun.processed_event TO 'operational_user'@'%';
GRANT SELECT ON mazerun.ocupation TO 'operational_user'@'%';
GRANT SELECT ON mazerun.temperature TO 'operational_user'@'%';
GRANT SELECT ON mazerun.sound TO 'operational_user'@'%';
GRANT SELECT ON mazerun.measure TO 'operational_user'@'%';
GRANT SELECT ON mazerun.action TO 'operational_user'@'%';

-- 5. User privileges
GRANT SELECT ON mazerun.* TO 'app_user'@'%';

-- 6. Apply changes
FLUSH PRIVILEGES;
