# Sample Queries

## Musicians Entity IDs

```sql
SELECT ?item
WHERE
{
    ?item wdt:P31 wd:Q5 ;
            wdt:P106 wd:Q15981151.
}
```

## Albums Entity IDs

```sql
SELECT ?item
WHERE {
    ?item wdt:P31 wd:Q482994;
            wdt:P136 wd:Q8341 .
}
```
