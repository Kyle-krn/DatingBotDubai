-- upgrade --
CREATE TABLE "users_purp" ("purposeofdating_id" INT NOT NULL REFERENCES "purposeofdating" ("id") ON DELETE CASCADE,"usermodel_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "users_purp";
