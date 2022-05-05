-- upgrade --
ALTER TABLE "usermodel" DROP COLUMN "search_radius";
-- downgrade --
ALTER TABLE "usermodel" ADD "search_radius" INT NOT NULL  DEFAULT 7000;
