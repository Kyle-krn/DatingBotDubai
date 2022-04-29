-- upgrade --
ALTER TABLE "avatarmodel" ADD "photo" BOOL NOT NULL;
CREATE TABLE IF NOT EXISTS "usersrelations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "percent_compatibility" INT NOT NULL,
    "target_user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "usersrelations" IS 'Процент совместимости междую юзерами';-- downgrade --
ALTER TABLE "avatarmodel" DROP COLUMN "photo";
DROP TABLE IF EXISTS "usersrelations";
