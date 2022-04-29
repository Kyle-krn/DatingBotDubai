-- upgrade --
CREATE TABLE IF NOT EXISTS "mutuallike" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "target_user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);;
ALTER TABLE "usermodel" ALTER COLUMN "dubai" SET DEFAULT False;
ALTER TABLE "usermodel" ALTER COLUMN "dubai" SET NOT NULL;
ALTER TABLE "userview" ADD "superlike" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "userview" ADD "like" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "userview" DROP COLUMN "superlike";
ALTER TABLE "userview" DROP COLUMN "like";
ALTER TABLE "usermodel" ALTER COLUMN "dubai" DROP NOT NULL;
ALTER TABLE "usermodel" ALTER COLUMN "dubai" DROP DEFAULT;
DROP TABLE IF EXISTS "mutuallike";
