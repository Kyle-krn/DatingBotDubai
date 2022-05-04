-- upgrade --
ALTER TABLE "mutuallike" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
-- downgrade --
ALTER TABLE "mutuallike" DROP COLUMN "created_at";
