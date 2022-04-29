-- upgrade --
ALTER TABLE "usermodel" RENAME COLUMN "address" TO "place";
-- downgrade --
ALTER TABLE "usermodel" RENAME COLUMN "place" TO "address";
