[![Build Status](https://travis-ci.org/botswana-harvard/edc-tracker.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-tracker)

[![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-tracker/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-tracker?branch=develop)

# edc-value-tracker

Keep track of the number of instances created for a specified model on one or more offline clients managed by a central controller.

Clients are disconnected from the central controller when collecting data. Go online at the end of each shift or day.

- sets an overall quota for a model managed by a central controller
- sets a quota per client model to be managed by the client
- central controller can change the quota per registered client over REST API
- central controller can update itself on progress of all clients toward reaching the over overall quota
- central controller can approve for a client to override it's quota.
 