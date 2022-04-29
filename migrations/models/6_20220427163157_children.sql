-- upgrade --
ALTER TABLE "usermodel" ADD "children" BOOL;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "children";
