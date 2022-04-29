-- upgrade --
ALTER TABLE "avatarmodel" RENAME COLUMN "type_file" TO "file_type";
-- downgrade --
ALTER TABLE "avatarmodel" RENAME COLUMN "file_type" TO "type_file";
