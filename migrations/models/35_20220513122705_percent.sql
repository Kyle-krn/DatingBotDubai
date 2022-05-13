-- upgrade --
CREATE TABLE IF NOT EXISTS "datingpercent" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "discription" VARCHAR(255) NOT NULL,
    "percent" INT NOT NULL
);
-- downgrade --
DROP TABLE IF EXISTS "datingpercent";
