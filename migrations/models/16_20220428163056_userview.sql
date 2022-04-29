-- upgrade --
ALTER TABLE "userview" ALTER COLUMN "count_view" SET DEFAULT 0;
-- downgrade --
ALTER TABLE "userview" ALTER COLUMN "count_view" DROP DEFAULT;
