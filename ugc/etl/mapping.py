# маппинг событий для загрузки в кликхаус

event_mappings = {
    "movie_events": [
        [
            "user_id",
            "user_fio",
            "movie_id",
            "movie_name",
            "date_event",
            "fully_viewed",
        ],  # name
        ["String", "String", "String", "String", "DateTime", "Bool"],  # type
        ["date_event", "user_id", "movie_id"],
    ]  # order by
}
