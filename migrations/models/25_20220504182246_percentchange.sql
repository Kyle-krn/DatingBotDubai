-- upgrade --
ALTER TABLE "usersrelations" ADD "result_distance_check" BOOL NOT NULL;
ALTER TABLE "usersrelations" ADD "result_purp_check" BOOL NOT NULL;
-- downgrade --
ALTER TABLE "usersrelations" DROP COLUMN "result_distance_check";
ALTER TABLE "usersrelations" DROP COLUMN "result_purp_check";
