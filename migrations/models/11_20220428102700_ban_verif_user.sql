-- upgrade --
ALTER TABLE "usermodel" ADD "verification" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "usermodel" ADD "ban" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "verification";
ALTER TABLE "usermodel" DROP COLUMN "ban";
