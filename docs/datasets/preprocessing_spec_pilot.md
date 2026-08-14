# Pilot AOI Preprocessing Specification

Generated: M2 validation

## AOI
- Path: `data/external/bengaluru_pilot_aoi.geojson`
- CRS: `EPSG:32643`
- Resolution: 30 m

## Temporal
- Start: 2023-01-01
- End: 2024-06-30
- Composite: monthly

## Cloud masking
- SCL classes masked: [3, 8, 9, 10, 11]
- Max scene cloud fraction: 0.6

## Compositing
- Method: median
- Nodata: -9999

## Output grid
- Shape: (120, 120)
- Alignment OK: True

## QC summary
- Months: 18
- Overall valid fraction: 0.704
- Monsoon valid fraction: 0.422
- Synthetic: True
- Go to M3: True
