CREATE DATABASE migration;
GO

USE migration;
GO

CREATE SCHEMA stage;
GO

CREATE TABLE stage.departments (
    id          INTEGER      NOT NULL,
    department  VARCHAR(100) NOT NULL,
    CONSTRAINT pk_departments PRIMARY KEY (id)
);

CREATE TABLE stage.jobs (
    id   INTEGER     NOT NULL,
    job  VARCHAR(30) NOT NULL,
    CONSTRAINT pk_jobs PRIMARY KEY (id)
);

CREATE TABLE stage.hired_employees (
    id            INTEGER      NOT NULL,
    name          VARCHAR(100) NOT NULL,
    DATETIME      VARCHAR(30)  NOT NULL,
    department_id INTEGER      NOT NULL,
    job_id        INTEGER      NOT NULL,
    CONSTRAINT pk_hired_employees  PRIMARY KEY (id),
    CONSTRAINT fk_hired_department FOREIGN KEY (department_id) REFERENCES stage.departments (id),
    CONSTRAINT fk_hired_job        FOREIGN KEY (job_id)        REFERENCES stage.jobs (id)
);
