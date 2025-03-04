DROP VIEW IF EXISTS "al_quran";

CREATE VIEW "al_quran" AS 
SELECT 
  "verses"."id", 
  "number", 
  "content", 
  "chapter_id" AS "chapter", 
  "name", 
  "order", 
  CASE WHEN "type" = 1 THEN "Meccan" ELSE "Medinan" END AS "type", 
  "verse_count", 
  "page_count", 
  "part_id" AS "part", 
  "group_id" AS "group", 
  "quarter_id" AS "quarter", 
  "page_id" AS "page" 
FROM 
  "verses" 
  JOIN "chapters" ON "verses"."chapter_id" = "chapters"."id";
