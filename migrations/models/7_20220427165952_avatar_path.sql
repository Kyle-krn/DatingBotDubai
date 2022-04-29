-- upgrade --
ALTER TABLE "usermodel" RENAME COLUMN "photo_path" TO "avatar_path";
-- downgrade --
ALTER TABLE "usermodel" RENAME COLUMN "avatar_path" TO "photo_path";
