-- upgrade --
ALTER TABLE "usermodel" ADD "free_likes" INT NOT NULL  DEFAULT 3;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "free_likes";
