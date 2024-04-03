create database  migration;

create schema stage;

use migration;
create Table stage.hired_employees(
    id INTEGER,
    name VARCHAR(100),
    DATETIME VARCHAR(30),
    department_id INTEGER,
    job_id INTEGER 
);

create table stage.departments(
    id INTEGER,
    department VARCHAR(100)
);

create Table stage.jobs(
    id INTEGER,
    job VARCHAR(30)
);