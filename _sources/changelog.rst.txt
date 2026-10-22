Changelog
=========

Unreleased
----------

Detection listing is paginated: ``Client.fetch_detections(limit=100, offset=0)``
returns up to 100 detections by default, with a maximum page size of 500. Advance
``offset`` by the number of rows returned until a page is empty to retrieve the
full list. Alert and sequence date-list endpoints accept page sizes from 1 to
100 and nonnegative offsets.

v0.1.2 (2022-07-01)
-------------------
Release note: `v0.1.2 <https://github.com/pyronear/pyro-api/releases/tag/v0.1.2>`_

v0.1.1 (2020-12-24)
-------------------
Release note: `v0.1.1 <https://github.com/pyronear/pyro-api/releases/tag/v0.1.1>`_


v0.1.0 (2020-11-26)
-------------------
Release note: `v0.1.0 <https://github.com/pyronear/pyro-api/releases/tag/v0.1.0>`_
