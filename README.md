babel-usage
===========

This repo contains a script to find out how many projects on Github
depend on [Babel] without an upper limit pin to a specific version.

The source data (.json.gz) was gathered from the [public GitHub dataset on Google BigQuery][ghbq]
using the enclosed BigQuery SQL scripts.

Usage
-----

After you've acquired `contents-with-babel.json.gz` (a copy is enclosed), run

```
python3 babel_usage_pickle.py
```

to generate `processed.pickle`, which contains dict "rows" of Babel version specs found.

Then use one of the other scripts to dump some sort of analysis out :)


[Babel]: https://github.com/python-babel/babel
[ghbq]: https://medium.com/google-cloud/github-on-bigquery-analyze-all-the-code-b3576fd2b150
