-- upgrade --
CREATE UNIQUE INDEX "uid_hobbies_title_h_ee57a1" ON "hobbies" ("title_hobbie");
-- downgrade --
DROP INDEX "idx_hobbies_title_h_ee57a1";
