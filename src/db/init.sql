CREATE DATABASE auth_database;

CREATE SCHEMA IF NOT EXISTS auth;

ALTER ROLE app SET search_path TO "auth";