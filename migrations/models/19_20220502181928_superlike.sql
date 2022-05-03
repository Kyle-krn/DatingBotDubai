-- upgrade --
ALTER TABLE "usermodel" ADD "superlike_count" INT NOT NULL  DEFAULT 1;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "superlike_count";
