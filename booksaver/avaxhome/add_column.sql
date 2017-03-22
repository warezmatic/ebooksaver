ALTER TABLE avaxhome_link ADD COLUMN filename VARCHAR(100) AFTER info;
CREATE INDEX `avaxhome_link_31ab5940` ON `avaxhome_link` (`filename`);
