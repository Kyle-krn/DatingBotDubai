-- upgrade --
ALTER TABLE "usersrelations" ADD "result_gender_check" BOOL NOT NULL;
-- downgrade --
ALTER TABLE "usersrelations" DROP COLUMN "result_gender_check";
