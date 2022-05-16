-- upgrade --
ALTER TABLE "usermodel" ADD "spam_ad_ids" JSONB;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "spam_ad_ids";
