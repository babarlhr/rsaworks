.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Job Costing in Manufacturing
===============================

This module add journal entries for labor and overhead for workorders
on jobs. Associates workcenter and job id to journal entries.
Associates workcenter to analytic entries.
Accumulates actual cost by workcenter per day and creates entries.
It handles journal entries for cost method = FIFO or Standard.


Configuration
=============

* Go to Inventory > Configuration > Products > Product Categories
* Create/edit product category with accounts for labor and overhead or burden.
* Go to Manufacturing > Master Data > Work Centers
* Create/edit work centers with labor rate, overhead rate

Usage
=====

* Go to Manufacturing > Manufacturing Orders
* Assign Job ID to manufacturing
* Create a new manufacture order and plan it.
* It will create work orders based on routing's work center operations.
* Go to work orders and switch tab to 'Time Tracking'.
* Verify above configured data will be set.
* Process work order for the unprocessed time entries
* It will create journal entries. If analytic account found at work center,
  it will create analytic entries as well.
* It will create Job costing scheduler to calculate workorder costing on daily basis.

Credits
=======

* Open Source Integrators <contact@opensourceintegrators.com>

Contributors
------------

* Balaji Kannan < bkannan@opensourceintegrators.com>
* Sandip Mangukiya < smangukiya@opensourceintegrators.com>

