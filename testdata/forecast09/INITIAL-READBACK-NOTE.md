# Initial consumer expectation corrected

The first Python example readback assumed Product.forecast_time was always a
JSON key and raised KeyError for the missing forecast. Existing derived Product
ToJson omits None-valued metadata; exact0 and6 are ordinary JSON numbers.
The actual example output is preserved in the first js-forecast-example log.
The consumer now uses product.get('forecast_time') and verifies the missing key
explicitly. Typed None and the station Sample.value=null checks remain separate.
No Product/Sample serializer, source fixture or accepted schema was changed.
