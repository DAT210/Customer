CREATE DATABASE IF NOT EXISTS customer;

USE customer;

CREATE TABLE IF NOT EXISTS customer_table (
  customer_id int(16) NOT NULL,
  customer_email varchar(128) NOT NULL,
  first_name varchar(128) DEFAULT NULL,
  last_name varchar(128) DEFAULT NULL,
  customer_password varchar(93) DEFAULT NULL,
  customer_birthday date DEFAULT NULL,
  customer_phone int(11) DEFAULT NULL,
  address_id int(11) DEFAULT NULL,
  address varchar(128) DEFAULT NULL,
  PRIMARY KEY (customer_id),
  UNIQUE KEY Cemail_UNIQUE (customer_email),
  UNIQUE KEY Address_UNIQUE (address_id)
);

CREATE TABLE IF NOT EXISTS revoked_tokens (
  id int(11) NOT NULL AUTO_INCREMENT,
  jti varchar(128) DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS customer_address (
  address_id int(11) NOT NULL,
  city varchar(128) DEFAULT NULL,
  postcode smallint(4) ZEROFILL DEFAULT NULL,
  street_name varchar(128) DEFAULT NULL,
  street_number varchar(128) DEFAULT NULL,
  apartment_number varchar(128) DEFAULT NULL,
  PRIMARY KEY (address_id),
  FOREIGN KEY (address_id) REFERENCES customer_table(address_id)
  ON UPDATE RESTRICT ON DELETE RESTRICT
);