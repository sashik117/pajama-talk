from sqlalchemy import Engine


def ensure_dev_schema(engine: Engine) -> None:
    if not engine.url.drivername.startswith("sqlite"):
        return

    with engine.begin() as connection:
        word_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(words)").all()
        }
        if "language_code" not in word_columns:
            connection.exec_driver_sql(
                "ALTER TABLE words ADD COLUMN language_code VARCHAR(12) NOT NULL DEFAULT 'en'",
            )
