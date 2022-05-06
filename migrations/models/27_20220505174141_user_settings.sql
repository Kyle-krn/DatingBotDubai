-- upgrade --
CREATE TABLE IF NOT EXISTS "usersearchsettings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "male" BOOL,
    "min_age" INT,
    "max_age" INT,
    "children" BOOL,
    "children_min_age" INT,
    "children_max_age" INT,
    "user_id" INT NOT NULL UNIQUE REFERENCES "usermodel" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "usersearchsettings";
