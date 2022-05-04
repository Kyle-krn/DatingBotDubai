-- upgrade --
ALTER TABLE "avatarmodel" ADD "user_id" INT NOT NULL UNIQUE;
-- downgrade --
ALTER TABLE "avatarmodel" DROP COLUMN "user_id";
