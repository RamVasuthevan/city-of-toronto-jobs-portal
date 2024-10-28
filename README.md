# City of Toronto Jobs Portal

The goal of this project to to download the job posting at the this City of Toronto Jobs Portal ([Jobs at the City](https://jobs.toronto.ca/jobsatcity/search/) and [Recreation](https://jobs.toronto.ca/recreation/search/)), save this in Git repo (i.e. [git scraping](https://ramvasuthevan.ca/git-scraping)) and to load those job posting into a sqlite db and allow these to anazlyzed with Datasette.

We'll get this working the quick and dirty way, and then will think more about architecture.

Our goal is only to get the job posts at jobs.toronto.ca not all jobs posting of the City of Toronto.

Based on an HTML comment:

```html
<!-- Jobs2Web, Inc. Site Scope Monitoring Comment - PLO -->
```

It looks like the job portal is managed by Jobs2Web, which was acquired by SuccessFactors in [2011](https://www.inc.com/courtney-rubin/jobs2web-acquired-for-$110-million.html), which was in turn acquired by SAP in [2014](https://www.forrester.com/blogs/11-12-05-sap_acquires_successfactors_a_look_at_the_deal/).


Todo:
- [ ] Move to pyproject.toml ?
- [ ] Add black, isort, autoflake, flake8 to pyproject.toml ?
- [ ] Add tests
- [ ] Add logging
- [ ] Git scraping job posts


Job Post parsing is a mess. I think the correct approach is a test driven approach to parsing the job posts, get all of the date for job post 1, then see if that code work for job post 2, etc.

Main module is too big we need to break it up.