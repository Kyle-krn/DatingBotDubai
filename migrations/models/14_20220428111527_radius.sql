-- upgrade --
ALTER TABLE "usermodel" ADD "search_radius" INT NOT NULL  DEFAULT 200;
-- downgrade --
ALTER TABLE "usermodel" DROP COLUMN "search_radius";
