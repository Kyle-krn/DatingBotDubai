-- upgrade --
ALTER TABLE "usermodel" ADD "end_premium" TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS "usersuccespayments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "createad_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "amount" DECIMAL(10,2) NOT NULL,
    "product" VARCHAR(200) NOT NULL,
    "count_mount_prem" INT,
    "superlike_count" INT,
    "user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "end_premium";
DROP TABLE IF EXISTS "usersuccespayments";
