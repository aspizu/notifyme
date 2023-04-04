create table user (
  id            integer primary key,
  username      text not null unique,
  password_hash text not null,
  display_name  text not null,
  avatar_url    text default null,
  tags          text not null default "[]",
  permission    integer not null default 0,
  created_time  integer not null default (unixepoch())
);

create table post (
  id           integer primary key,
  author_id    integer not null,
  content      text not null,
  tags         text not null,
  recipients   text not null,
  created_time integer not null default (unixepoch()),
  foreign key(author_id) references user(id)
);

create table reaction (
  id           integer primary key,
  emoji        integer not null,
  post_id      integer not null,
  user_id      integer not null,
  created_time integer not null default (unixepoch()),
  foreign key(post_id) references post(id),
  foreign key(user_id) references user(id),
  unique (emoji, post_id, user_id)
);
