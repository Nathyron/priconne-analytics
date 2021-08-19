CREATE TABLE account (
    id SERIAL not null primary key,
    email varchar(255) not null,
    nickname varchar(255) not null,
    auth_key varchar(255) not null,
    password_hash varchar(255) not null,
    password_reset_token varchar(255) not null,
    type varchar(100) not null,
    region varchar(100) not null,
	is_activated bool not null default false,
	is_admi bool not null default false,
	first_login timestamp,
	last_login timestamp,
    create_date timestamp not null default now(),
    update_date timestamp default now(),
    constraint unique_email unique(email)
);


CREATE TABLE character (
    id SERIAL not null primary key,
    nickname varchar(255) not null,
    rol varchar(25) not null,
    category varchar(25) not null,
    placement smallint not null,
    create_date timestamp not null default now()
);


CREATE TABLE game_version (
    id SERIAL not null primary key,
    nickname varchar(255) not null,
    start_date timestamp not null,
    end_date timestamp not null,
    create_date timestamp not null default now()
);


CREATE TABLE boss (
    id SERIAL not null primary key,
    nickname varchar(255) not null,
	health int not null,
	p_attack int,
	p_defense smallint not null,
	p_crit smallint,
	m_attack int,
	m_defense smallint not null,
	m_crit smallint,
	dodge smallint,
	hp_drain smallint,
	hp_boost smallint,
	tp_boost smallint,
	tp_retain smallint,
	accuracy smallint,
	eff_physical_hp int,
	eff_magical_hp int,
	last_seen_game_version_id int not null,
    create_date timestamp not null default now(),
    constraint fk_game_version_id
    	foreign key (last_seen_game_version_id) 
    	references game_version(id)
    	on delete set null
);


CREATE TABLE team (
	id SERIAL not null primary key,
    character1_id smallint not null,
    star1 smallint not null,
    equipment1 boolean not null default false,
    character2_id smallint not null,
    star2 smallint not null,
    equipment2 boolean not null default false,
    character3_id smallint not null,
    star3 smallint not null,
    equipment3 boolean not null default false,
    character4_id smallint not null,
    star4 smallint not null,
    equipment4 boolean not null default false,
    character5_id smallint not null,
    star5 smallint not null,
    equipment5 boolean default false,
    first_seen timestamp,
    last_seen timestamp,
    create_date timestamp not null default now(),
    constraint fk_character1_id
    	foreign key(character1_id)
    	references character(id)
    	on delete set null,
    constraint fk_character2_id 
     	foreign key(character2_id) 
     	references character(id)
     	on delete set null,
	constraint fk_character3_id 
		foreign key(character3_id) 
		references character(id)
		on delete set null,
	constraint fk_character4_id 
		foreign key(character4_id) 
		references character(id)
		on delete set null,
	constraint fk_character5_id 
		foreign key(character5_id) 
		references character(id)
		on delete set null,
	constraint unique_team
		unique(
			character1_id,star1,equipment1,
			character2_id,star2,equipment2,
			character3_id,star3,equipment3,
			character4_id,star4,equipment4,
			character5_id,star5,equipment5
		)
);


CREATE TABLE pvp_battle(
	id SERIAL not null primary key,
    team1_id int not null,
    team2_id int not null,
    pvp_result smallint,
    rating int not null default 0,
    category varchar(10) not null, -- is battle arena (ba) or princess arena (pa)
    region varchar(25) not null, -- in which region the battle took place
    incomplete boolean not null default false,
    test boolean not null default false,
    account_id int not null,
    game_version_id int,
    sourced varchar(50), -- from what datasource this was pull from
    create_date timestamp not null default now(),
    update_date timestamp default now(),
    constraint fk_team1_id 
    	foreign key(team1_id) 
    	references team(id)
    	on delete set null,
    constraint fk_team2_id 
    	foreign key(team2_id) 
    	references team(id)
    	on delete set null,
    constraint valid_winner_value 
    	check (pvp_result between 1 and 2),
    constraint fk_account_id 
    	foreign key(account_id) 
    	references account(id)
    	on delete set null,
    constraint fk_game_version_id 
    	foreign key(game_version_id) 
    	references game_version(id)
    	on delete set null
);

CREATE TABLE pve_battle(
	id SERIAL not null primary key,
    team_id int not null,
    boss_id int,
    pve_dmg int,
    pve_fail boolean not null,
    pve_fail_reason varchar(255),
    rating int not null default 0,
    category varchar(10) not null, -- clan boss, event boss, regular map
    region varchar(25) not null,
    incomplete boolean not null default false,
    test boolean not null default false,
    account_id int not null,
    game_version_id int,
    sourced varchar(50),
    create_date timestamp not null default now(),
    update_date timestamp default now(),
    constraint fk_team_id 
    	foreign key(team_id) 
    	references team(id)
    	on delete set null,
    constraint fk_boss_id 
    	foreign key(boss_id) 
    	references boss(id)
    	on delete set null,
    constraint valid_dmg_value 
    	check (pve_dmg >= 0),
    constraint fk_account_id 
    	foreign key(account_id) 
    	references account(id)
    	on delete set null,
    constraint fk_game_version_id 
    	foreign key(game_version_id) 
    	references game_version(id)
    	on delete set null
);

