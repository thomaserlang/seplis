from typing import Any


async def update_series(ctx: dict[str, Any], series_id: int) -> None:
    import seplis.importer

    await seplis.importer.series.update_series_by_id(series_id)
