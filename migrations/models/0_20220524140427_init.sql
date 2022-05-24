-- upgrade --
CREATE TABLE IF NOT EXISTS "city" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "place_name" VARCHAR(255) NOT NULL,
    "tmz" INT
);
CREATE TABLE IF NOT EXISTS "dating_interest_place" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_interest" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "dating_percent" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(255) NOT NULL,
    "percent" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "hobbies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_hobbie" VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "marital_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_status" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "dating_purpose" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_purp" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL,
    "tg_username" VARCHAR(255),
    "male" BOOL,
    "name" VARCHAR(255),
    "dubai" BOOL NOT NULL  DEFAULT False,
    "moving_to_dubai" BOOL,
    "birthday" DATE,
    "children" BOOL,
    "children_age" JSONB NOT NULL,
    "end_premium" TIMESTAMPTZ,
    "superlike_count" INT NOT NULL  DEFAULT 1,
    "verification" BOOL NOT NULL  DEFAULT False,
    "ban" BOOL NOT NULL  DEFAULT False,
    "end_registration" BOOL NOT NULL  DEFAULT False,
    "free_likes" INT NOT NULL  DEFAULT 3,
    "spam_ad_ids" JSONB,
    "last_verification_time" TIMESTAMPTZ,
    "marital_status_id" INT REFERENCES "marital_status" ("id") ON DELETE CASCADE,
    "place_id" INT REFERENCES "city" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_avatar" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "file_id" VARCHAR(255),
    "file_path" VARCHAR(255),
    "file_type" VARCHAR(40),
    "photo_bool" BOOL,
    "user_id" INT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "users_avatar" IS 'Аватар';
CREATE TABLE IF NOT EXISTS "mutal_likes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "target_user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "male" BOOL,
    "min_age" INT NOT NULL  DEFAULT 18,
    "max_age" INT NOT NULL  DEFAULT 99,
    "children" BOOL,
    "children_min_age" INT NOT NULL  DEFAULT 0,
    "children_max_age" INT NOT NULL  DEFAULT 18,
    "user_id" INT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_success_payments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "createad_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "amount" DECIMAL(10,2) NOT NULL,
    "product" VARCHAR(200) NOT NULL,
    "count_mount_prem" INT,
    "superlike_count" INT,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_views" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "count_view" INT NOT NULL  DEFAULT 0,
    "like" BOOL NOT NULL  DEFAULT False,
    "superlike" BOOL NOT NULL  DEFAULT False,
    "dislike" BOOL NOT NULL  DEFAULT False,
    "target_user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users_places" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "datinginterestplace_id" INT NOT NULL REFERENCES "dating_interest_place" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_hobbies" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "hobbies_id" INT NOT NULL REFERENCES "hobbies" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_purps" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "purposeofdating_id" INT NOT NULL REFERENCES "dating_purpose" ("id") ON DELETE CASCADE
);
