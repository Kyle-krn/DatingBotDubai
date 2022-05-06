-- upgrade --
ALTER TABLE "usermodel" ADD "end_registration" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "end_registration";
