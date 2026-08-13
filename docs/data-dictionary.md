# FMCG data dictionary

Weekly input grain is uniquely `week_start_date + sku_id + channel + region`.
Required measures include sell-out units, sell-in units, promotion flag,
discount depth, net/gross sales value, gross margin, stock on hand, out-of-stock
flag, and returns. Identifiers include SKU, brand, category, channel, and region.

Dates use ISO dates and weekly alignment. Money uses declared ISO currency and
fixed precision. Discount is normalized to a 0–1 fraction. Stock is explicitly
declared as units or cases. Gross margin is declared as amount or percentage.
Critical schema errors invalidate the dataset; warnings and transformations are
persisted. Exact definitions and validation outputs are exposed in OpenAPI.
