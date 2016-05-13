use PhishTank;
DROP TABLE IF EXISTS solved;
CREATE TABLE solved(
	url varchar(100)  primary key,
	ips varchar(1024) ,
	sub_time varchar(2014) 
);
