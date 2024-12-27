CREATE TABLE IF NOT EXISTS Experiments (
    experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_family TEXT NOT NULL,
    model_name TEXT NOT NULL,
    puzzle_year INTEGER NOT NULL,
    puzzle_day INTEGER NOT NULL,
    puzzle_part INTEGER NOT NULL,
    prompt TEXT,
    program TEXT,
    run_status TEXT CHECK( run_status IN ('error', 'timeout', 'answer') ),
    run_error_message TEXT,
    run_timeout_seconds INTEGER,
    answer TEXT,
    answer_is_correct BOOLEAN,
    experiment_started_at TIMESTAMP,
    experiment_finished_at TIMESTAMP,
    UNIQUE(model_family, model_name, puzzle_year, puzzle_day, puzzle_part)
);

CREATE TABLE IF NOT EXISTS QuotaTimeouts (
    model_family TEXT PRIMARY KEY,
    timeout_until TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ModelRank (
    model_family TEXT NOT NULL,
    model_name TEXT NOT NULL,
    solved_count INTEGER NOT NULL,
    total_attempted INTEGER NOT NULL,
    success_rate REAL NOT NULL,
    PRIMARY KEY (model_family, model_name)
);

CREATE TABLE IF NOT EXISTS ModelFamilyRank (
    model_family TEXT PRIMARY KEY,
    solved_count INTEGER NOT NULL,
    total_attempted INTEGER NOT NULL,
    success_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS YearRank (
    puzzle_year INTEGER PRIMARY KEY,
    solved_count INTEGER NOT NULL,
    total_attempted INTEGER NOT NULL,
    success_rate REAL NOT NULL
);
