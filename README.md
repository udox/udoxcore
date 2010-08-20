Ah, documentation
=================

wouldn't that be nice
---------------------

This contains useful stuff used for Sp...TV, and will soon merge in the extended set that were used on CT.

I found them useful, can see myself importing for every project. Would be keen to discuss ways we could improve this and to merge in any similar work from other projects.

It has dependancies on 3rd party apps noted in comments in the code.

### models.py

This is the most important part: a set of abstract base Models (and accompanying Managers) covering common uses such as a 'StatusModel' with configurable statuses (eg 'draft','live' etc).

Also classes for CommentableModel (for django.contrib.comments) and TaggableModel (django-tagging 3rd party app)

### admin.py

ModelAdmin base classes for the above.

### templatetags/

Useful filters and templatetags (the querystring tag [borrowed from here](http://andre.liquidmm.com/blog/2009/apr/20/flexible-query-string-building-template-tag/) is particularly good.

### utils/

Some of these might be better as tiny apps, eg ustream.py and stats.py (Google Analytics api query)
