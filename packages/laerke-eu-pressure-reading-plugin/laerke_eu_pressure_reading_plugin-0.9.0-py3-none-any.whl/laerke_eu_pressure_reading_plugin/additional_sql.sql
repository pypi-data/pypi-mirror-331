CREATE TABLE IF NOT EXISTS laerke_eu_pressure_readings (
    experiment               TEXT NOT NULL,
    pioreactor_unit          TEXT NOT NULL,
    timestamp                TEXT NOT NULL,
    pressure                 REAL
);
