-- upgrade --
ALTER TABLE "usersrelations" ADD "percent_children" INT NOT NULL;
ALTER TABLE "usersrelations" ADD "percent_age" INT NOT NULL;
ALTER TABLE "usersrelations" ADD "percent_hobbies" INT NOT NULL;
-- downgrade --
ALTER TABLE "usersrelations" DROP COLUMN "percent_children";
ALTER TABLE "usersrelations" DROP COLUMN "percent_age";
ALTER TABLE "usersrelations" DROP COLUMN "percent_hobbies";
