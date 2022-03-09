DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS ip_blacklist;
DROP TABLE IF EXISTS ua_blacklist;
DROP TABLE IF EXISTS hourly_stats;


CREATE TABLE customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE ip_blacklist (
  ip INTEGER PRIMARY KEY NOT NULL
);

CREATE TABLE ua_blacklist (
  ua TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE hourly_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  time TIMESTAMP NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 0,
  invalid_count INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT unique_customer_time UNIQUE (customer_id, time),
  CONSTRAINT hourly_stats_customer_id FOREIGN KEY (customer_id) REFERENCES customer (id) ON DELETE CASCADE ON UPDATE NO ACTION
);



INSERT INTO customer VALUES (1, 'Big News Media Corp', 1), (2, 'Online Mega Store', 1), (3, 'Nachoroo Delivery', 0), (4, 'Euro Telecom Group', 1);

INSERT INTO ip_blacklist VALUES (0), (2130706433), (4294967295);

INSERT INTO ua_blacklist VALUES ('A6-Indexer'), ('Googlebot-News'), ('Googlebot');




