drop database if exists test;
create database test default character set utf8 collate utf8_general_ci;
use test;
create table `Cards`(
    `id` int primary key not null,
    `name` varchar(255) not null,
    `type` varchar(255) not null,
    constraint CARDTYPE check (`type` in ("怪兽", "魔法", "陷阱")),
    `isOcg` tinyint not null default 1,
    `isTcg` tinyint not null default 1
);
create table `MonsterCards`(
    `Cardid` int primary key,
    `type` varchar(255) not null,
    `isNormal` bool not null default 0,
    `isEffect` bool not null default 0,
    `isTuner` bool not null default 0,
    `isReversal` bool not null default 0,
    `isSoul` bool not null default 0,
    `isDouble` bool not null default 0,
    `isAlliance` bool not null default 0,
    `isCartoon` bool not null default 0,
    `isToken` bool not null default 0,
    `isSpecial` bool not null default 0,
    `starNumber` int not null,
    `race` varchar(255) not null,
    `attrib` varchar(255) not null,
    constraint SNUM check (`starNumber` >= 0),
    `PendulumNumber` int,
    constraint PNUM check (
        `PendulumNumber` >= 0
        and `PendulumNumber` <= 13
    ),
    `linkMark` int,
    constraint LNUM	check(`linkMark`>=0),
    `atk` int not null ,
    constraint ANUM check(`atk` >= -1),
    `def` int,
    constraint DNUM check(`def` >= -1),
    `monsterEffect` varchar(1024),
    `pendulumEffect` varchar(1024),
    constraint MONSTER foreign key(`Cardid`) references `Cards`(`id`)
);
create table `MagicCards`
(
    `Cardid` int not null primary key,
    constraint MAGIC foreign key(`Cardid`) references `Cards`(`id`),
	`type` varchar(255) not null,
    `effect` varchar(1024) not null,
    constraint MTYPE check(`type` in ("通常","速攻","仪式","永续","装备","场地"))
);
create table `TrapCards`
(
    `Cardid` int not null primary key,
    constraint TRAP foreign key(`Cardid`) references `Cards`(`id`),
	`type` varchar(255) not null,
    `effect` varchar(1024) not null,
    constraint TTYPE check(`type` in ("通常","永续","反击"))
);
create table `CardBag`(
    `id` int primary key,
    `short_name` varchar(255) ,
    `name` varchar(1024) ,
    `Time` date
);
create table `User`(
`name` varchar(255) not null primary key ,
`password` varchar(255) not null,
`email` varchar(255)not null,
`isAdmin` bool not null default 0
)
;
create table `CardSet`(
    `user` varchar(255) not null,
    constraint SetUser foreign key(`user`) references `User`(`name`),
    `name` varchar(255) not null,
    primary key(`user`, `name`),
    `createTime` date,
    `LastAlterTime` date
);

create table `BagContent`(
	`CardBagId` int,
	constraint BAGID foreign key (`CardBagId`) references `CardBag`(`id`),
    `Cardid` int,
    constraint BAGCARD foreign key(`Cardid`) references `Cards`(`id`),
	primary key(`CardBagId`,`Cardid`)
);
create table `SetContent`(
	`SetUser` varchar(255),
    `SetName` varchar(255),
    constraint USERDATA foreign key(`SetUser`,`SetName`) references `CardSet`(`user`, `name`),
	`Cardid` int,
    constraint USERCARD foreign key(`Cardid`) references `Cards`(`id`),
	`number` int not null,
	constraint SETNUM check(`number`>0),
    `position` int not null default 0 ,
    constraint `AREA` check(`position`>=0 and `position` <=2),
    primary key(`SetUser`,`SetName`,`Cardid`,`position`)
);
create table `ForbiddenCard`(
	`Cardid` int,
    constraint FORBIDDEN foreign key(`Cardid`) references `Cards`(`id`),
    `env` varchar(255),
    `time` date,
    primary key(`Cardid`,`time`,`env`),
    `Number` int not null,
    constraint `LIMIT` check (`Number`>=0 and `Number` < 3)
);


