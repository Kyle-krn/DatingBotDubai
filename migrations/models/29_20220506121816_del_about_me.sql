-- upgrade --
ALTER TABLE "usermodel" DROP COLUMN "about_me";
-- downgrade --
ALTER TABLE "usermodel" ADD "about_me" TEXT;
