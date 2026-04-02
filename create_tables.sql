/*
 * Create tables for the Rebrickable dataset in Azure SQL Database.
 * We add all of the tables from here: https://rebrickable.com/downloads/
 *  - Even though we don't need all of the tables, we've added them just in case. 
*/ 

CREATE TABLE themes (
    id        INT           NOT NULL,
    name      VARCHAR(256)  NOT NULL,
    parent_id INT               NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id) REFERENCES themes(id)
);

CREATE TABLE colors (
    id        INT           NOT NULL,
    name      VARCHAR(200)  NOT NULL,
    rgb       VARCHAR(6)    NOT NULL,
    is_trans  BIT           NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE sets (
    set_num   VARCHAR(20)   NOT NULL,
    name      VARCHAR(256)  NOT NULL,
    year      INT           NOT NULL,
    theme_id  INT           NOT NULL,
    num_parts INT           NOT NULL,
    PRIMARY KEY (set_num),
    FOREIGN KEY (theme_id) REFERENCES themes(id)
);

CREATE TABLE inventories (
    id        INT           NOT NULL,
    version   INT           NOT NULL,
    set_num   VARCHAR(20)   NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (set_num) REFERENCES sets(set_num)
);

CREATE TABLE inventory_sets (
    inventory_id INT          NOT NULL,
    set_num      VARCHAR(20)  NOT NULL,
    quantity     INT          NOT NULL,
    FOREIGN KEY (inventory_id) REFERENCES inventories(id),
    FOREIGN KEY (set_num)      REFERENCES sets(set_num)
);

CREATE TABLE part_categories (
    id   INT          NOT NULL,
    name VARCHAR(200) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE parts (
    part_num    VARCHAR(20)  NOT NULL,
    name        VARCHAR(250) NOT NULL,
    part_cat_id INT          NOT NULL,
    PRIMARY KEY (part_num),
    FOREIGN KEY (part_cat_id) REFERENCES part_categories(id)
);

CREATE TABLE inventory_parts (
    inventory_id INT          NOT NULL,
    part_num     VARCHAR(20)  NOT NULL,
    color_id     INT          NOT NULL,
    quantity     INT          NOT NULL,
    is_spare     BIT          NOT NULL,
    FOREIGN KEY (inventory_id) REFERENCES inventories(id),
    FOREIGN KEY (part_num)     REFERENCES parts(part_num),
    FOREIGN KEY (color_id)     REFERENCES colors(id)
);

CREATE TABLE minifigs (
    fig_num   VARCHAR(20)  NOT NULL,
    name      VARCHAR(256) NOT NULL,
    num_parts INT          NOT NULL,
    PRIMARY KEY (fig_num)
);

CREATE TABLE inventory_minifigs (
    inventory_id INT         NOT NULL,
    fig_num      VARCHAR(20) NOT NULL,
    quantity     INT         NOT NULL,
    FOREIGN KEY (inventory_id) REFERENCES inventories(id),
    FOREIGN KEY (fig_num)      REFERENCES minifigs(fig_num)
);

CREATE TABLE elements (
    element_id VARCHAR(10) NOT NULL,
    part_num   VARCHAR(20) NOT NULL,
    color_id   INT         NOT NULL,
    PRIMARY KEY (element_id),
    FOREIGN KEY (part_num)  REFERENCES parts(part_num),
    FOREIGN KEY (color_id)  REFERENCES colors(id)
);

CREATE TABLE part_relationships (
    rel_type        VARCHAR(1)  NOT NULL,
    child_part_num  VARCHAR(20) NOT NULL,
    parent_part_num VARCHAR(20) NOT NULL
);
