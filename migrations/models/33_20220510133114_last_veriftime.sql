-- upgrade --
ALTER TABLE "usermodel" ADD "last_verification_time" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "last_verification_time";
