-- upgrade --
CREATE TABLE IF NOT EXISTS "avatarmodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "file_id" VARCHAR(255) NOT NULL,
    "file_path" VARCHAR(255) NOT NULL,
    "type_file" VARCHAR(40) NOT NULL
);;
ALTER TABLE "usermodel" DROP COLUMN "avatar_path";
-- downgrade --
ALTER TABLE "usermodel" ADD "avatar_path" TEXT;
DROP TABLE IF EXISTS "avatarmodel";
