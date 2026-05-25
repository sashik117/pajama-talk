from sqlalchemy import Engine


def ensure_dev_schema(engine: Engine) -> None:
    if engine.url.drivername.startswith("postgresql"):
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_level VARCHAR(24) NOT NULL DEFAULT 'Starter'",
            )
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS target_level VARCHAR(24) NOT NULL DEFAULT 'B1'",
            )
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS effort_level VARCHAR(24) NOT NULL DEFAULT 'Steady'",
            )
            connection.exec_driver_sql(
                "ALTER TABLE words ADD COLUMN IF NOT EXISTS status VARCHAR(24) NOT NULL DEFAULT 'learning'",
            )
        return

    if not engine.url.drivername.startswith("sqlite"):
        return

    with engine.begin() as connection:
        user_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(users)").all()
        }
        if "active_language_code" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN active_language_code VARCHAR(12) NOT NULL DEFAULT 'en'",
            )
        if "native_language_code" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN native_language_code VARCHAR(12) NOT NULL DEFAULT 'uk'",
            )
        if "daily_vibe_minutes" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN daily_vibe_minutes INTEGER NOT NULL DEFAULT 5",
            )
        if "current_level" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN current_level VARCHAR(24) NOT NULL DEFAULT 'Starter'",
            )
        if "target_level" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN target_level VARCHAR(24) NOT NULL DEFAULT 'B1'",
            )
        if "effort_level" not in user_columns:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN effort_level VARCHAR(24) NOT NULL DEFAULT 'Steady'",
            )

        word_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(words)").all()
        }
        if "language_code" not in word_columns:
            connection.exec_driver_sql(
                "ALTER TABLE words ADD COLUMN language_code VARCHAR(12) NOT NULL DEFAULT 'en'",
            )
        if "status" not in word_columns:
            connection.exec_driver_sql(
                "ALTER TABLE words ADD COLUMN status VARCHAR(24) NOT NULL DEFAULT 'learning'",
            )
