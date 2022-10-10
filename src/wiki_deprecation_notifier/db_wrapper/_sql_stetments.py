CREATE_TABLES_STATEMENT = """
    CREATE TABLE IF NOT EXISTS conflicts(
        hash VARCHAR(255) PRIMARY KEY,
        signature SMALLTEXT NOT NULL,
        action_required BOOLEAN,
        action_done BOOLEAN
    );
    """
