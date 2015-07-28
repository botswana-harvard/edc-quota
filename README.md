[![Build Status](https://travis-ci.org/botswana-harvard/edc-tracker.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-tracker)

[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-tracker/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-tracker?branch=develop)

# edc-value-tracker
Track values for enrollment caps, etc

This monitors number of instances of model created, and makes sure a certain limit is not reached.
There is a master monitor that keeps record or all site being monitored.
There is a site monitor that monitors models created at the site.

Example:


A shop that has a central distribution and also has many other distributions in other places.
The central shop would want to keep track of a certain item being soled.
Every time an item is sold a record is created that the item is sold. At the central distribution all the records of item sold at
the distributions all over a country are monitored.

This means the distribution center can keep track of how other distributions are doing and can know which distribution needs more items or
its items are not being sold well.

