-- upgrade --
ALTER TABLE "avatarmodel" ALTER COLUMN "photo_bool" DROP NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_path" DROP NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_type" DROP NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "avatarmodel" ALTER COLUMN "photo_bool" SET NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_path" SET NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_type" SET NOT NULL;
ALTER TABLE "avatarmodel" ALTER COLUMN "file_id" SET NOT NULL;
