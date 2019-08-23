.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
MRP WIP Labor/Material Variance
===============================

This module add journal entries for standard labor and overhead absorption,
variances in material, labor and overhead. It handles journal entries for
cost method = FIFO or Standard.


Configuration
=============

* Go to Inventory > Configuration > Products > Product Categories
* Create/edit product category with accounts for Variance and Absorption.
* Go to Manufacturing > Master Data > Work Centers
* Create/edit work centers with 'General Information', 'Costing Information',
  and 'Labor and Overhead'
* Go to Manufacturing > Master Data > Routings
* Create/edit routing with each work center operation lines 'Std No. of Cycles'
  and 'Std No. of Hours'.
* Check routing in Bills of Materials to verify details.

Usage
=====

* Go to Manufacturing > Manufacturing Orders
* Create a new manufacture order and plan it.
* It will create work orders based on routing's work center operations.
* Go to work orders and switch tab to 'Time Tracking'.
* Verify above configured data will be set.
* Process work order and complete it.
* It will create journal entries. If analytic account found at work center,
  it will create analytic entries as well.

Credits
=======

* Open Source Integrators <contact@opensourceintegrators.com>

Contributors
------------

* Balaji Kannan < bkannan@opensourceintegrators.com>
* Bhavesh Odedra <bodedra@opensourceintegrators.com>
