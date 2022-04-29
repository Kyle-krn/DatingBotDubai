-- upgrade --
ALTER TABLE "usermodel" ADD "avatar_id" INT  UNIQUE;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "avatar_id";
