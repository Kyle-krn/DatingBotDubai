-- upgrade --
ALTER TABLE "avatarmodel" RENAME COLUMN "photo" TO "photo_bool";
-- downgrade --
ALTER TABLE "avatarmodel" RENAME COLUMN "photo_bool" TO "photo";
