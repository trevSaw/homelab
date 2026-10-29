ATTACH DATABASE 'file:/hive/backups/media-reorg-20261025-065941/jellyfin/jellyfin-pre-migration.db?mode=ro' AS bak;

PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;

DROP TABLE IF EXISTS _mapped;
CREATE TEMP TABLE _mapped AS
SELECT
  b.Id AS old_id,
  b.Path AS old_path,
  CASE
    WHEN b.Path LIKE '/data/tvshows/Cartoons/The 100 Girlfriends Who Really, Really, Really, Really, REALLY Love You%'
      THEN replace(b.Path,'/data/tvshows/Cartoons/','/data/tvshows/Anime_Series/')
    WHEN b.Path LIKE '/data/tvshows/Anime_Series/Castlevania%'
      OR b.Path LIKE '/data/tvshows/Anime_Series/My Adventures with Superman%'
      THEN replace(b.Path,'/data/tvshows/Anime_Series/','/data/tvshows/TV/')
    WHEN b.Path LIKE '/data/tvshows/Cartoons/%'
      OR b.Path LIKE '/data/tvshows/Drama_Series/%'
      OR b.Path LIKE '/data/tvshows/Fantasy_Series/%'
      OR b.Path LIKE '/data/tvshows/Kdrama_Series/%'
      OR b.Path LIKE '/data/tvshows/Reality/%'
      THEN replace(replace(replace(replace(replace(b.Path,
        '/data/tvshows/Cartoons/','/data/tvshows/TV/'),
        '/data/tvshows/Drama_Series/','/data/tvshows/TV/'),
        '/data/tvshows/Fantasy_Series/','/data/tvshows/TV/'),
        '/data/tvshows/Kdrama_Series/','/data/tvshows/TV/'),
        '/data/tvshows/Reality/','/data/tvshows/TV/')
    ELSE b.Path
  END AS new_path
FROM bak.BaseItems b
WHERE b.Path IS NOT NULL;

DROP TABLE IF EXISTS _restore_userdata;
CREATE TEMP TABLE _restore_userdata AS
SELECT
  nb.Id AS ItemId,
  u.UserId,
  CASE WHEN lower(u.CustomDataKey) = lower(u.ItemId) THEN lower(nb.Id) ELSE u.CustomDataKey END AS CustomDataKey,
  u.AudioStreamIndex,
  u.IsFavorite,
  u.LastPlayedDate,
  u.Likes,
  u.PlayCount,
  u.PlaybackPositionTicks,
  u.Played,
  u.Rating,
  u.SubtitleStreamIndex,
  u.RetentionDate
FROM bak.UserData u
JOIN _mapped m ON m.old_id = u.ItemId
JOIN main.BaseItems nb ON nb.Path = m.new_path
WHERE NOT EXISTS (
  SELECT 1
  FROM main.UserData nu
  WHERE nu.ItemId = nb.Id
    AND nu.UserId = u.UserId
    AND nu.CustomDataKey = CASE WHEN lower(u.CustomDataKey) = lower(u.ItemId) THEN lower(nb.Id) ELSE u.CustomDataKey END
);

SELECT 'to_insert', COUNT(*) FROM _restore_userdata;

INSERT INTO main.UserData (
  ItemId, UserId, CustomDataKey, AudioStreamIndex, IsFavorite, LastPlayedDate,
  Likes, PlayCount, PlaybackPositionTicks, Played, Rating, SubtitleStreamIndex, RetentionDate
)
SELECT
  ItemId, UserId, CustomDataKey, AudioStreamIndex, IsFavorite, LastPlayedDate,
  Likes, PlayCount, PlaybackPositionTicks, Played, Rating, SubtitleStreamIndex, RetentionDate
FROM _restore_userdata;

SELECT 'inserted', changes();
SELECT 'played_inserted', COUNT(*) FROM _restore_userdata WHERE Played = 1;
SELECT 'distinct_played_items_inserted', COUNT(DISTINCT ItemId) FROM _restore_userdata WHERE Played = 1;

COMMIT;
