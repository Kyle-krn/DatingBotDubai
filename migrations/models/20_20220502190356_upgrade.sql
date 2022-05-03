-- upgrade --
ALTER TABLE "userview" ADD "dislike" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "userview" DROP COLUMN "dislike";
