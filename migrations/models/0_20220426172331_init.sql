-- upgrade --
CREATE TABLE IF NOT EXISTS "hobbies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_hobbie" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "purposeofdating" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_purp" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "usermodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL,
    "tg_username" VARCHAR(255),
    "male" BOOL,
    "name" VARCHAR(255),
    "about_me" TEXT,
    "lat" DECIMAL(10,6),
    "long" DECIMAL(10,6),
    "address" TEXT,
    "moving_to_dubai" BOOL,
    "birthday" DATE,
    "interest_place_companion" VARCHAR(255),
    "children_age" JSONB NOT NULL,
    "photo_path" TEXT
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users_hobbies" (
    "usermodel_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE,
    "hobbies_id" INT NOT NULL REFERENCES "hobbies" ("id") ON DELETE CASCADE
);
