-- upgrade --
ALTER TABLE "usermodel" DROP COLUMN "avatar_id";
ALTER TABLE "usermodel" ALTER COLUMN "search_radius" SET DEFAULT 7000;
-- downgrade --
ALTER TABLE "usermodel" ADD "avatar_id" INT  UNIQUE;
ALTER TABLE "usermodel" ALTER COLUMN "search_radius" SET DEFAULT 200;
