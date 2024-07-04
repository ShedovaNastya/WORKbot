DROP DATABASE IF EXISTS work;

CREATE DATABASE work
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

DROP TABLE IF EXISTS salary_tab CASCADE;
DROP TABLE IF EXISTS vacancies CASCADE;
CREATE TABLE salary_tab
(
    id_salary Serial PRIMARY KEY, 
    salary_from int,
    salary_to int,
    currency text,
	unique (salary_from,salary_to,currency)
);

-- Создаем таблицу vacancies
CREATE TABLE vacancies
(
    id_vac serial PRIMARY KEY,
    title_vacancy text NOT NULL,
    region text NOT NULL,
	salary int NOT NULL REFERENCES salary_tab(id_salary),
    experience text,
    employment text,
    url varchar(255) NOT NULL,
	unique (title_vacancy, region, salary, experience, employment, url)
);

INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (80000, 100000, 'RUR');
INSERT INTO vacancies (title_vacancy, region, salary, experience, employment, url)VALUES ('t','New York', 1, '3 years', 'Full-time', 'https://example.com/vacancies/1');
-- Assuming the tables 'salary_tab' and 'vacancies' already exist with appropriate schemas.

-- Inserting into salary_tab
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (75000, 95000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (82000, 102000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (78000, 98000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (81000, 101000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (79000, 99000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (83000, 103000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (77000, 97000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (84000, 104000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (76000, 96000, 'RUR');
INSERT INTO salary_tab(salary_from, salary_to, currency) VALUES (85000, 105000, 'RUR');
INSERT INTO salary_tab (salary_from, salary_to, currency)VALUES (74000, 94000, 'RUR');
INSERT INTO salary_tab (salary_from, salary_to, currency)VALUES (86000, 106000, 'RUR');

-- Inserting into vacancies with the same name in the second column
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Los Angeles', 2, '2 years', 'Part-time', 'https://example.com/vacancies/2');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Chicago', 3, '4 years', 'Full-time', 'https://example.com/vacancies/3');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Houston', 4, '3 years', 'Contract', 'https://example.com/vacancies/4');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Phoenix', 5, '2 years', 'Full-time', 'https://example.com/vacancies/5');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Philadelphia', 6, '3 years', 'Part-time', 'https://example.com/vacancies/6');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'San Antonio', 7, '4 years', 'Full-time', 'https://example.com/vacancies/7');
INSERT INTO vacancies (title_vacancy, region, salary, experience, employment, url)VALUES ('t', 'San Diego', 8, '2 years', 'Contract', 'https://example.com/vacancies/8');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Dallas', 9, '3 years', 'Full-time', 'https://example.com/vacancies/9');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'San Jose', 10, '2 years', 'Part-time', 'https://example.com/vacancies/10');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Austin', 11, '4 years', 'Full-time', 'https://example.com/vacancies/11');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Jacksonville', 12, '3 years', 'Contract', 'https://example.com/vacancies/12');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Fort Worth', 13, '2 years', 'Full-time', 'https://example.com/vacancies/13');
INSERT INTO vacancies(title_vacancy, region, salary, experience, employment, url) VALUES ('t', 'Los Angeles', 2, '2 years', 'Part-time', 'https://example.com/vacancies/2') on conflict (title_vacancy, region, salary, experience, employment, url) do nothing;