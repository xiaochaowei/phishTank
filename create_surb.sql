use PhishTank
CREATE TABLE phishTank(
	phish_id integer primary key,
	url varchar(255) not null,
	submission_time varchar(255),
	valid varchar(255),
	online varchar(255),
	ip varchar(255)
)
