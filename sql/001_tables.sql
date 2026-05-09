-- AetherPin Connector: Remote Telescopes
-- Phase 1, Aufgabe 1

CREATE TABLE IF NOT EXISTS remote_telescopes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    observatory VARCHAR(100) DEFAULT NULL,
    software VARCHAR(100) DEFAULT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_api_key_hash (api_key_hash),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS remote_telescope_live_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telescope_id INT NOT NULL,
    target_name VARCHAR(100) DEFAULT NULL,
    ra VARCHAR(20) DEFAULT NULL,
    dec_coord VARCHAR(20) DEFAULT NULL,
    status ENUM('live', 'idle', 'offline') NOT NULL DEFAULT 'idle',
    last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (telescope_id) REFERENCES remote_telescopes(id) ON DELETE CASCADE,
    INDEX idx_telescope_id (telescope_id),
    INDEX idx_last_seen (last_seen),
    INDEX idx_status (status),
    UNIQUE KEY unique_telescope (telescope_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
