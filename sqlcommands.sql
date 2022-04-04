CREATE DATABASE tutorial; 

CREATE EXTENSION timescaledb;

CREATE TABLE conditions (   
  time        TIMESTAMPTZ       NOT NULL,   
  location    TEXT              NOT NULL,   
  temperature DOUBLE PRECISION  NULL,   
  humidity    DOUBLE PRECISION  NULL 
);

SELECT create_hypertable('conditions', 'time');

INSERT INTO conditions(time, location, temperature, humidity) 
  VALUES (NOW(), 'office', 70.0, 50.0);

SELECT * FROM conditions ORDER BY time DESC LIMIT 100;