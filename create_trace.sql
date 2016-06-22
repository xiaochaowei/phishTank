use PhishTank;
drop table  if exists traceips;
CREATE TABLE traceips(
	id integer primary key auto_increment, 
	date varchar(255),
	ip varchar(255),
	server varchar(255),
	phish_id integer
);
