
async def update_series(ctx, series_id) -> None:
    import seplis.importer
    await seplis.importer.series.update_series_by_id(series_id)