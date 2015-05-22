drop table if exists texts;

/*
 * TODO: Add timestamp field.
 * TODO: Add foreign key to published version.
 * TODO: Make identifier and published field unique together.
 */
create table texts (
    id integer primary key autoincrement,
    identifier text not null,
    content text not null,
    published integer not null
);


drop table if exists images;

create table images (
    id integer primary key autoincrement,
    identifier text not null,
    filename text not null,
    published integer not null
);


drop table if exists containers;

create table containers (
    id integer primary key autoincrement,
    identifier text not null,
    size integer not null,
    published integer not null
);


drop table if exists mapbox;

create table mapbox (
    id integer primary key autoincrement,
    geojson text not null
);
