create table user (
  id            integer primary key,
  username      text not null unique,
  displayname   text not null,
  password_hash text not null,
  tags          text not null default "{}", -- JSON Array of tags
  time          integer not null
);

create table notification (
  id         integer primary key,
  author     integer not null,
  content    text not null,
  time       integer not null,
  recipients text not null, -- JSON Array of usernames or tags
  foreign key(author) references user(id)
);
