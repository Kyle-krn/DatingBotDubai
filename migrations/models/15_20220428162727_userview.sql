-- upgrade --
CREATE TABLE IF NOT EXISTS "userview" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "count_view" INT NOT NULL,
    "relation_id" INT NOT NULL REFERENCES "usersrelations" ("id") ON DELETE CASCADE,
    "target_user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "userview";
