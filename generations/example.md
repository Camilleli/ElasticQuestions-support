# Elastic Certification Questions

**Index:** `kibana_sample_data_ecommerce`
**Generated:** 2025-07-02 16:32:36
**Total Questions:** 2

| Question | Category | Answer |
|----------|----------|--------|
| Using the available data, how would you find out the average base price of products in each category? | AGGREGATIONS | `{"size":0,"aggs":{"average_price_per_category":{"terms":{"field":"products.category.keyword"},"aggs":{"average_base_price":{"avg":{"field":"products.base_price"}}}}}}` |
| How would you determine the total taxful price for all orders made in each continent using the available data? | AGGREGATIONS | `{"size":0,"aggs":{"total_taxful_price_by_continent":{"terms":{"field":"geoip.continent_name"},"aggs":{"total_taxful_price":{"sum":{"field":"taxful_total_price"}}}}}}` |
