use PhishTank;
drop table  if exists phishTank;
CREATE TABLE phishTank2(
	phish_id integer primary key,
	url varchar(1028) charset utf8 not null,
	submission_time varchar(255),
	valid varchar(255),
	online varchar(255),
	ip varchar(255),
	flag integer(1)
);

CREATE TRIGGER insertphishTank
BEFORE INSERT on phishTank2 FOR EACH ROW SET NEW.flag = 0;