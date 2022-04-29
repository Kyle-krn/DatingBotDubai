-- upgrade --
ALTER TABLE "usermodel" ADD "marital_status" VARCHAR(255);
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "marital_status";
