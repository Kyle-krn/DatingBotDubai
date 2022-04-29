-- upgrade --
ALTER TABLE "usermodel" ADD "dubai" BOOL;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "dubai";
