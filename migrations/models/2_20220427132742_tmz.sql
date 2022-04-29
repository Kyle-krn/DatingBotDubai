-- upgrade --
ALTER TABLE "usermodel" ADD "tmz" INT;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "tmz";
