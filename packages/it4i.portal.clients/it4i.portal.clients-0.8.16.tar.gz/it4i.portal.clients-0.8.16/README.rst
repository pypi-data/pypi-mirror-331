Retirement Notice
=================

| ``it4i-portal-clients`` was retired in favor of a complete rewrite.
| This documentation and package are obsolete and no longer available on
  IT4I login nodes.

--------------

it4i-portal-clients
===================

it4i-portal-clients provides simple user-friendly shell interface to
call `IT4I API <https://docs.it4i.cz/apiv1/>`__ requests and display
their respond.

Python 2.7 is required.

Limits are placed on the number of requests you may make to `IT4I
API <https://docs.it4i.cz/apiv1/>`__. Rate limit can be changed without
any warning at any time, but the default is 6 requests per minute.
Exceeding the limit will lead to your ip address being temporarily
blocked from making further requests. The block will automatically be
lifted by waiting an hour.

List of available utilities
---------------------------

-  `it4icheckaccess <#it4icheckaccess>`__ - Shows if IT4I account and/or
   related project has the access to specified cluster and queue.
-  `it4idedicatedtime <#it4idedicatedtime>`__ - Shows IT4I dedicated
   time.
-  `it4ifree <#it4ifree>`__ - Shows some basic information from IT4I PBS
   accounting.
-  `it4ifsusage <#it4ifsusage>`__ - Shows filesystem usage of IT4I
   cluster storage systems.
-  `it4iuserfsusage <#it4iuserfsusage>`__ - Shows user filesystem usage
   of IT4I cluster storage systems.
-  `it4projectifsusage <#it4iprojectfsusage>`__ - Shows project
   filesystem usage of IT4I cluster storage systems.
-  `it4imotd <#it4imotd>`__ - Shows IT4I messages of the day into
   formatted text or HTML page (using TAL / Zope Page Template).

Installation / upgrading
------------------------

.. code:: bash

   pip install --upgrade it4i.portal.clients

Sample config file main.cfg
---------------------------

.. code:: bash

   [main]

   # IT4I API
   api_url = https://scs.it4i.cz/api/v1/
   it4ifreetoken = <your_token>

Username is taken from OS, therefore the script has to be run under the
same user login name as you use to log into clusters.

-  System-wide config file path:
   ``/usr/local/etc/it4i-portal-clients/main.cfg``
-  Local user’s config file path: ``~/.it4ifree``

it4icheckaccess
---------------

Help of IT4ICHECKACCESS
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4icheckaccess -h
   usage: it4icheckaccess [-h] -l LOGIN -c CLUSTER -q QUEUE [-p PROJECT]

   The command shows if an IT4I account and/or related project has the access to
   specified cluster and queue. Return exit code 99 if access is not granted.

   optional arguments:
     -h, --help            show this help message and exit
     -l LOGIN, --login LOGIN
                           user login
     -c CLUSTER, --cluster CLUSTER
                           cluster name
     -q QUEUE, --queue QUEUE
                           queue
     -p PROJECT, --project PROJECT
                           project id, not required if querying projectless queue

Example of IT4ICHECKACCESS
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4icheckaccess -l XXX -c barbora -q qexp
   OK Access granted for projectless queue.

it4idedicatedtime
-----------------

Help of IT4IDEDICATEDTIME
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4idedicatedtime -h
   usage: it4idedicatedtime [-h] [-m {active,planned}]
                            [-c {anselm,salomon,barbora}]

   The command shows IT4I dedicated time. By default all planned and active
   outages of all clusters are displayed. Return exit code 99 if there is no
   outage, otherwise return 0.

   optional arguments:
     -h, --help            show this help message and exit
     -m {active,planned}, --message {active,planned}
                           select type of dedicated time. Planned contains also
                           active
     -c {anselm,salomon,barbora}, --cluster {anselm,salomon,barbora}
                           select cluster

Example of IT4IDEDICATEDTIME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4idedicatedtime
   Cluster    Start                End                  Last update
   ---------  -------------------  -------------------  -------------------
   anselm     2019-03-19 08:00:00  2019-03-19 09:30:00  2019-03-08 08:24:33
   salomon    2019-03-19 08:00:00  2019-03-19 09:30:00  2019-03-08 08:23:40

it4ifree
--------

Help of IT4IFREE
~~~~~~~~~~~~~~~~

.. code:: console

   $ it4ifree -h
   usage: it4ifree [-h] [-p] [-a]

   The command shows some basic information from IT4I PBS accounting. The
   data is related to the current user and to all projects in which user
   participates.

   optional arguments:
     -h, --help            show this help message and exit
     -p, --percent
                           show values in percentage. Projects with unlimited resources are not displayed
     -a, --all             Show all resources include inactive and future ones.


   Columns of "Projects I am participating in":
            PID: Project ID/account string.
           Type: Standard or multiyear project.
      Days left: Days till the given project expires.
          Total: Core-hours allocated to the given project.
           Used: Sum of core-hours used by all project members.
             My: Core-hours used by the current user only.
           Free: Core-hours that haven't yet been utilized.

   Columns of "Projects I am Primarily Investigating" (if present):
            PID: Project ID/account string.
           Type: Standard or multiyear project.
          Login: Project member's login name.
           Used: Project member's used core-hours.

Example of IT4IFREE
~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4ifree

   Projects I am participating in
   ==============================
   PID         Resource type    Days left      Total     Used      By me     Free
   ----------  ---------------  -------------  --------  --------  --------  --------
   OPEN-XX-XX  Karolina GPU      249                42         0         0        42
               Barbora CPU       249                42         5         5        37
               Legacy NCH        249               100         0         0       100


   Projects I am Primarily Investigating
   =====================================
   PID         Resource type    Login      Usage
   ----------  --------------   -------  --------
   OPEN-XX-XX  Barbora CPU      user1          3
               Barbora CPU      user2          2
               Karolina GPU     N/A            0
               Legacy NCH       N/A            0


   Legend
   ======
   N/A   =    No one used this resource yet
   Legacy Normalized core hours are in NCH
   Everything else is in Node Hours

it4ifsusage
-----------

Help of IT4IFSUSAGE
~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4ifsusage -h
   usage: it4ifsusage [-h]

   The command shows filesystem usage of IT4I cluster storage systems

   optional arguments:
     -h, --help            show this help message and exit

Example of IT4IFSUSAGE
~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4ifsusage
   Quota Type     Cluster / PID    File System    Space used    Space limit      Entries used  Entries limit    Last update
   -------------  ---------------  -------------  ------------  -------------  --------------  ---------------  -------------------
   User           barbora          /home          69.6 kB       25.0 GB                    17  500,000          2021-03-22 16:50:10
   User           salomon          /home          278.5 kB      250.0 GB                   94  500,000          2021-03-22 17:00:07
   User           barbora          /scratch       0 Bytes       10.0 TB                     0  10,000,000       2021-03-22 16:50:28
   User           salomon          /scratch       0 Bytes       100.0 TB                    0  10,000,000       2021-03-22 17:00:43
   User           salomon          /scratch/temp  0 Bytes       N/A                         0                   2021-03-22 17:00:57
   User           salomon          /scratch/work  0 Bytes       N/A                         0                   2021-03-22 17:00:50
   Project        service          proj3          3.1 GB        1.0 TB                      5  100,000          2021-03-22 17:00:02

it4iuserfsusage
---------------

Help of IT4IUSERFSUSAGE
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4iuserfsusage -h
   usage: it4iuserfsusage [-h] [-c {all,barbora, karolina}]

   The command shows user filesystem usage of IT4I cluster storage systems

   optional arguments:
     -h, --help            show this help message and exit

Example of IT4IUSERFSUSAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4iuserfsusage
   Cluster          File System    Space used    Space limit      Entries used  Entries limit    Last update
   ---------------  -------------  ------------  -------------  --------------  ---------------  -------------------
   barbora          /home          69.6 kB       25.0 GB                    17  500,000          2021-03-22 16:50:10
   salomon          /home          278.5 kB      250.0 GB                   94  500,000          2021-03-22 17:00:07
   barbora          /scratch       0 Bytes       10.0 TB                     0  10,000,000       2021-03-22 16:50:28
   salomon          /scratch       0 Bytes       100.0 TB                    0  10,000,000       2021-03-22 17:00:43
   salomon          /scratch/temp  0 Bytes       N/A                         0                   2021-03-22 17:00:57
   salomon          /scratch/work  0 Bytes       N/A                         0                   2021-03-22 17:00:50

it4iprojectfsusage
------------------

Help of IT4IPROJECTFSUSAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4iprojectfsusage -h
   usage: it4iprojectfsusage [-h] [-p {PID, all}]

   The command shows project filesystem usage of IT4I cluster storage systems

   optional arguments:
     -h, --help            show this help message and exit

Example of IT4IPROJECTFSUSAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4iprojectfsusage
   PID              File System    Space used    Space limit      Entries used  Entries limit    Last update
   ---------------  -------------  ------------  -------------  --------------  ---------------  -------------------
   service          proj3          3.1 GB        1.0 TB                      5  100,000          2021-03-22 17:00:02
   it4i-x-y         proj1          3.1 TB        2.0 TB                      5  100,000          2021-03-22 17:00:02
   dd-13-5          proj3          2 GB          3.0 TB                      5  100,000          2021-03-22 17:00:02
   projectx         proj2          150 TB        4.0 TB                      5  100,000          2021-03-22 17:00:02

it4imotd
--------

Help of IT4IMOTD
~~~~~~~~~~~~~~~~

.. code:: console

   $ it4imotd -h
   usage: it4imotd [-h] [-t TEMPLATE] [-w WIDTH] [-c]

   The command shows IT4I messages of the day into formatted text or HTML page.

   optional arguments:
     -h, --help            show this help message and exit
     -t TEMPLATE, --template TEMPLATE
                           path to TAL / Zope Page Template, output will be
                           formatted into HTML page
     -w WIDTH, --width WIDTH
                           maximum line width (intended for text rendering,
                           default of 78 columns)
     -c, --cron            sleep from 10 up to 60 seconds prior to any actions
     -m {TYPE}, --message {TYPE}
                           select type of messages
                           supported types:
                               all,
                               public-service-announcement,
                               service-recovered-up,
                               critical-service-down,
                               service-hard-down,
                               auxiliary-service-down,
                               planned-outage,
                               service-degraded,
                               important,
                               notice.

Example of IT4IMOTD
~~~~~~~~~~~~~~~~~~~

.. code:: console

   $ it4imotd

                          Message of the Day (DD/MM/YYYY)
                               (YYYY-MM-DD hh:mm:ss)

   More on https://...


Changelog
=========


0.8.16 (2025-03-06)
-------------------
- Add retirement notice. [Stanislav Rosický]


0.8.15 (2024-12-17)
-------------------
- Handled NoneType in it4imotd. [Ondřej Kavan]


0.8.14 (2023-02-01)
-------------------
- Minor motd bugfix. [Stanislav Rosický]


0.8.13 (2022-10-24)
-------------------
- Template updated. [Jindrich Kvita]


0.8.12 (2022-10-04)
-------------------
- README updated. [Jindrich Kvita]

- Legacy Normalised Core Hours shorten to Legacy NCH. [Jindrich Kvita]

- Major changes for better readability and affected systems. [Jindrich Kvita]


0.8.11 (2022-05-26)
-------------------
- MOTD supports new categories. [Jindrich Kvita]

- Readme updated. [Jindrich Kvita]

- Anselm and salomon choises removed, karolina added. [Jindrich Kvita]


0.8.10 (2022-05-04)
-------------------
- Updated pkg info. [Jindrich Kvita]

- Percentage representation improved for specific situations. [Jindrich Kvita]


0.8.9 (2022-04-28)
------------------
- Tests updated. [Jindrich Kvita]

- Bugfix and updated readme 2. [Jindrich Kvita]

- Bugfix and updated readme. [Jindrich Kvita]


0.8.8 (2022-04-27)
------------------
- It4ifree added -a and minor changes. [Jindrich Kvita]


0.8.7 (2022-04-19)
------------------
- Updated it4ifree. [Jindrich Kvita]


0.8.6 (2021-10-14)
------------------
- Add cluster parameter to it4icheckaccess. [Stanislav Rosický]


0.8.5 (2021-03-23)
------------------
- Install user and project filesystem usage tools. [Jan Krupa]

- Display project filesystem usage. [Jan Krupa]

- Display user filesystem usage. [Jan Krupa]

- Adds readme of project and user fs usage methods. [Jan Krupa]

- Remove cluster option from fs-usage. [Jan Krupa]


0.8.4 (2021-03-16)
------------------
- Add project storage quota to fs-usage command. [Jan Krupa]

- Update PKG-INFO Version. [Roman Slíva]

- Update it4ifsusage.py - use decimal units. [Roman Slíva]


0.8.3 (2020-10-29)
------------------
- Fix multiyear periods. [Marek Chrastina]


0.8.2 (2020-05-06)
------------------
- Add multiyear into it4ifree. [Marek Chrastina]

- Update CI. [Marek Chrastina]


0.8.1 (2020-03-25)
------------------
- Add python safety to CI. [Marek Chrastina]


0.8.0 (2020-02-18)
------------------
- Add Barbora cluster and IT4I API url. [Marek Chrastina]


0.7.8 (2019-03-22)
------------------
- Add it4ifsusage command. [Marek Chrastina]


0.7.7 (2019-03-11)
------------------
- Add it4icheckaccess command. [Marek Chrastina]

- Add it4idedicatedtime command. [Marek Chrastina]


0.7.6 (2019-03-06)
------------------
- Add options to select type of motd messages. [Marek Chrastina]


0.7.5 (2019-03-06)
------------------
- Extract json related code to separated library. [Marek Chrastina]

- It4ifreetoken configuration option will be mandatory just for it4ifree command. [Marek Chrastina]

- Remove functionaless options. [Marek Chrastina]

- Rename motd_rss to it4imotd. [Marek Chrastina]


0.7.4 (2019-03-05)
------------------
- Add option to show values in percentage for it4ifree. [Marek Chrastina]

- Replace argument parser library in it4ifree. [Marek Chrastina]

- New api url in config. [Marek Chrastina]


0.7.3 (2019-03-04)
------------------
- Update documentation. [Marek Chrastina]

- Fix help bug. [Marek Chrastina]


0.7.2 (2019-03-01)
------------------
- Update documentation. [Marek Chrastina]

- Do not allow CI failure. [Marek Chrastina]

- Fix pylint complaints. [Marek Chrastina]

- Install required pip packages before run pylint. [Marek Chrastina]

- Fix pylint complaints. [Marek Chrastina]

- Fix shellcheck complaints. [Marek Chrastina]

- Change automatic upload to manual. [Marek Chrastina]


0.7.1 (2019-02-28)
------------------
- Exclude merge commits from changelog. [Marek Chrastina]

- Add CI deploy. [Marek Chrastina]

- Add CI pylint. [Marek Chrastina]

- Add CI shellcheck. [Marek Chrastina]

- Fix mdl complaints. [Marek Chrastina]

- Add CI mdcheck. [Marek Chrastina]


0.6.7 (2017-09-08)
------------------
- Core hour => core-hour. [David Hrbáč]

- Standard CH => Normalized CH. [David Hrbáč]


0.6.6 (2017-09-08)
------------------
- Code lint. [David Hrbáč]

- Clean-up unused imports. [David Hrbáč]


0.6.5 (2017-09-05)
------------------
- Core Hours to Wall-clock Core Hours; Fixes it4i-admins/it4i-portal-clients#4. [David Hrbáč]


0.6.4 (2017-09-05)
------------------
- Core Hours to Wall-clock Core Hours; Fixes it4i-admins/it4i-portal-clients#4. [David Hrbáč]


0.6.3 (2017-08-08)
------------------
- Beutify format. [Jan Krupa]

- Fixed Standart -> Standard. [Jan Krupa]

- Fixed labels. [kru0096]

- Display normalized core hours. [kru0096]


0.6.2 (2017-07-25)
------------------
- Use the JSON for HTML render. [David Hrbáč]


0.6.1 (2017-07-25)
------------------
- Use the JSON. [David Hrbáč]


0.5.12 (2017-07-25)
-------------------
- Require dateutil. [David Hrbáč]


0.5.11 (2017-07-25)
-------------------
- Use 24 hours. [David Hrbáč]


0.5.10 (2017-07-25)
-------------------
- Use the JSON. [David Hrbáč]


0.5.9 (2017-07-21)
------------------
- Release 0.5.9. [David Hrbáč]

- Typo. [David Hrbáč]


0.5.8 (2017-07-21)
------------------
- Move to HTTPS channel. [David Hrbáč]

- Convert it4ifree to SCS, motd deprecated. [David Hrbáč]


0.5.7 (2017-02-06)
------------------
- Handle long titles. [David Hrbáč]


0.5.6 (2017-02-03)
------------------
- Corrections to README. [David Hrbáč]

- Test commit. [Jan Krupa]


0.5.5 (2017-02-02)
------------------
- Enable to display timerange for events. [David Hrbáč]


0.5.2 (2016-10-10)
------------------
- Format text. [Jan Krupa]


0.5.1 (2016-10-10)
------------------
- Pypandoc version pinned. [Filip Valder]


0.5 (2016-10-10)
----------------
- License changed. [Jan Krupa]


0.4.9 (2016-06-24)
------------------
- A helpful script for testing installs. [Filip Valder]


0.4.8 (2016-06-24)
------------------
- A more advanced solution for setup.py. [Filip Valder]

- Without the dot. [Filip Valder]

- A more advanced solution for setup.py. [Filip Valder]


0.4.7 (2016-06-24)
------------------
- Handle KeyError: 'IT4I_FACTORY_PREBUILD' [Filip Valder]


0.4.6 (2016-06-24)
------------------
- Setup_requires depends on the evironment: IT4I factory versus end-user. [Filip Valder]


0.4.5 (2016-06-24)
------------------
- Get python interpreter from the environment. [Filip Valder]


0.4.4 (2016-06-24)
------------------
- Setup deps. [Filip Valder]


0.4.3 (2016-06-24)
------------------
- Some ignores added. [Filip Valder]


0.4.2 (2016-06-23)
------------------
- The other way round. [Filip Valder]

- Exclude git-related stuff from MANIFEST.in. [Filip Valder]

- Additional requirements for setup. [Filip Valder]

- Some gitchangelog rc file. [Filip Valder]

- Mising comma. [Filip Valder]

- Auto-versioning accto git tags. [Filip Valder]

- See the hint in it4ifree.py. [Filip Valder]

- White space. [Filip Valder]

- Instructions re-ordered. [Filip Valder]


0.4.1 (2016-06-01)
------------------
- Keywords added. [Filip Valder]

- Important functional improvements & introduced README. [Filip Valder]


0.4 (2016-06-01)
----------------
- Config module introduced. [Filip Valder]

- Sample config file. [Filip Valder]

- README.txt -> README.md due to GL (the change will also appear in setup.py) [Filip Valder]

- Init & use module name ; not filename. [Filip Valder]

- Get ready for 0.4 release. [Filip Valder]

- Use module name ; not filename. [Filip Valder]

- Bug fixes. [Filip Valder]

- Support for sorting. [Filip Valder]

- Support for published date/time. [Filip Valder]

- CStringIO for full module usage support. [Filip Valder]


0.3.4 (2016-05-19)
------------------
- Support for stdin and various feed sources. [Filip Valder]

- Logging goes to separate file. [Filip Valder]

- Write to stderr instead of stdout. [Filip Valder]

- Egg-info for 0.3.3.post2. [Filip Valder]

- Repository moved, project IT4I-ized... [Filip Valder]

- 0.3.3.post1 released: setuptools is already dep of PIP, it may mess things up during install. [Filip Valder]


0.3.3 (2016-02-25)
------------------
- Egg-info files for 0.3.3. [Filip Valder]

- 0.3.3 released. [Filip Valder]

- Support for verbose and width opts; short opt for cron changed. [Filip Valder]

- Default template fixes. [Filip Valder]

- Sync with MANIFEST.in. [Filip Valder]

- Remove dist from repository. [Filip Valder]

- 0.3.2 stable with unicode encoding fixed. [Filip Valder]

- Add README. [Filip Valder]


Changelog
=========


%%version%% (unreleased)
------------------------
- Add retirement notice. [Stanislav Rosický]


0.8.16 (2025-03-06)
-------------------
- Add retirement notice. [Stanislav Rosický]


0.8.15 (2024-12-17)
-------------------
- Handled NoneType in it4imotd. [Ondřej Kavan]


0.8.14 (2023-02-01)
-------------------
- Minor motd bugfix. [Stanislav Rosický]


0.8.13 (2022-10-24)
-------------------
- Template updated. [Jindrich Kvita]


0.8.12 (2022-10-04)
-------------------
- README updated. [Jindrich Kvita]

- Legacy Normalised Core Hours shorten to Legacy NCH. [Jindrich Kvita]

- Major changes for better readability and affected systems. [Jindrich Kvita]


0.8.11 (2022-05-26)
-------------------
- MOTD supports new categories. [Jindrich Kvita]

- Readme updated. [Jindrich Kvita]

- Anselm and salomon choises removed, karolina added. [Jindrich Kvita]


0.8.10 (2022-05-04)
-------------------
- Updated pkg info. [Jindrich Kvita]

- Percentage representation improved for specific situations. [Jindrich Kvita]


0.8.9 (2022-04-28)
------------------
- Tests updated. [Jindrich Kvita]

- Bugfix and updated readme 2. [Jindrich Kvita]

- Bugfix and updated readme. [Jindrich Kvita]


0.8.8 (2022-04-27)
------------------
- It4ifree added -a and minor changes. [Jindrich Kvita]


0.8.7 (2022-04-19)
------------------
- Updated it4ifree. [Jindrich Kvita]


0.8.6 (2021-10-14)
------------------
- Add cluster parameter to it4icheckaccess. [Stanislav Rosický]


0.8.5 (2021-03-23)
------------------
- Install user and project filesystem usage tools. [Jan Krupa]

- Display project filesystem usage. [Jan Krupa]

- Display user filesystem usage. [Jan Krupa]

- Adds readme of project and user fs usage methods. [Jan Krupa]

- Remove cluster option from fs-usage. [Jan Krupa]


0.8.4 (2021-03-16)
------------------
- Add project storage quota to fs-usage command. [Jan Krupa]

- Update PKG-INFO Version. [Roman Slíva]

- Update it4ifsusage.py - use decimal units. [Roman Slíva]


0.8.3 (2020-10-29)
------------------
- Fix multiyear periods. [Marek Chrastina]


0.8.2 (2020-05-06)
------------------
- Add multiyear into it4ifree. [Marek Chrastina]

- Update CI. [Marek Chrastina]


0.8.1 (2020-03-25)
------------------
- Add python safety to CI. [Marek Chrastina]


0.8.0 (2020-02-18)
------------------
- Add Barbora cluster and IT4I API url. [Marek Chrastina]


0.7.8 (2019-03-22)
------------------
- Add it4ifsusage command. [Marek Chrastina]


0.7.7 (2019-03-11)
------------------
- Add it4icheckaccess command. [Marek Chrastina]

- Add it4idedicatedtime command. [Marek Chrastina]


0.7.6 (2019-03-06)
------------------
- Add options to select type of motd messages. [Marek Chrastina]


0.7.5 (2019-03-06)
------------------
- Extract json related code to separated library. [Marek Chrastina]

- It4ifreetoken configuration option will be mandatory just for it4ifree command. [Marek Chrastina]

- Remove functionaless options. [Marek Chrastina]

- Rename motd_rss to it4imotd. [Marek Chrastina]


0.7.4 (2019-03-05)
------------------
- Add option to show values in percentage for it4ifree. [Marek Chrastina]

- Replace argument parser library in it4ifree. [Marek Chrastina]

- New api url in config. [Marek Chrastina]


0.7.3 (2019-03-04)
------------------
- Update documentation. [Marek Chrastina]

- Fix help bug. [Marek Chrastina]


0.7.2 (2019-03-01)
------------------
- Update documentation. [Marek Chrastina]

- Do not allow CI failure. [Marek Chrastina]

- Fix pylint complaints. [Marek Chrastina]

- Install required pip packages before run pylint. [Marek Chrastina]

- Fix pylint complaints. [Marek Chrastina]

- Fix shellcheck complaints. [Marek Chrastina]

- Change automatic upload to manual. [Marek Chrastina]


0.7.1 (2019-02-28)
------------------
- Exclude merge commits from changelog. [Marek Chrastina]

- Add CI deploy. [Marek Chrastina]

- Add CI pylint. [Marek Chrastina]

- Add CI shellcheck. [Marek Chrastina]

- Fix mdl complaints. [Marek Chrastina]

- Add CI mdcheck. [Marek Chrastina]


0.6.7 (2017-09-08)
------------------
- Core hour => core-hour. [David Hrbáč]

- Standard CH => Normalized CH. [David Hrbáč]


0.6.6 (2017-09-08)
------------------
- Code lint. [David Hrbáč]

- Clean-up unused imports. [David Hrbáč]


0.6.5 (2017-09-05)
------------------
- Core Hours to Wall-clock Core Hours; Fixes it4i-admins/it4i-portal-clients#4. [David Hrbáč]


0.6.4 (2017-09-05)
------------------
- Core Hours to Wall-clock Core Hours; Fixes it4i-admins/it4i-portal-clients#4. [David Hrbáč]


0.6.3 (2017-08-08)
------------------
- Beutify format. [Jan Krupa]

- Fixed Standart -> Standard. [Jan Krupa]

- Fixed labels. [kru0096]

- Display normalized core hours. [kru0096]


0.6.2 (2017-07-25)
------------------
- Use the JSON for HTML render. [David Hrbáč]


0.6.1 (2017-07-25)
------------------
- Use the JSON. [David Hrbáč]


0.5.12 (2017-07-25)
-------------------
- Require dateutil. [David Hrbáč]


0.5.11 (2017-07-25)
-------------------
- Use 24 hours. [David Hrbáč]


0.5.10 (2017-07-25)
-------------------
- Use the JSON. [David Hrbáč]


0.5.9 (2017-07-21)
------------------
- Release 0.5.9. [David Hrbáč]

- Typo. [David Hrbáč]


0.5.8 (2017-07-21)
------------------
- Move to HTTPS channel. [David Hrbáč]

- Convert it4ifree to SCS, motd deprecated. [David Hrbáč]


0.5.7 (2017-02-06)
------------------
- Handle long titles. [David Hrbáč]


0.5.6 (2017-02-03)
------------------
- Corrections to README. [David Hrbáč]

- Test commit. [Jan Krupa]


0.5.5 (2017-02-02)
------------------
- Enable to display timerange for events. [David Hrbáč]


0.5.2 (2016-10-10)
------------------
- Format text. [Jan Krupa]


0.5.1 (2016-10-10)
------------------
- Pypandoc version pinned. [Filip Valder]


0.5 (2016-10-10)
----------------
- License changed. [Jan Krupa]


0.4.9 (2016-06-24)
------------------
- A helpful script for testing installs. [Filip Valder]


0.4.8 (2016-06-24)
------------------
- A more advanced solution for setup.py. [Filip Valder]

- Without the dot. [Filip Valder]

- A more advanced solution for setup.py. [Filip Valder]


0.4.7 (2016-06-24)
------------------
- Handle KeyError: 'IT4I_FACTORY_PREBUILD' [Filip Valder]


0.4.6 (2016-06-24)
------------------
- Setup_requires depends on the evironment: IT4I factory versus end-user. [Filip Valder]


0.4.5 (2016-06-24)
------------------
- Get python interpreter from the environment. [Filip Valder]


0.4.4 (2016-06-24)
------------------
- Setup deps. [Filip Valder]


0.4.3 (2016-06-24)
------------------
- Some ignores added. [Filip Valder]


0.4.2 (2016-06-23)
------------------
- The other way round. [Filip Valder]

- Exclude git-related stuff from MANIFEST.in. [Filip Valder]

- Additional requirements for setup. [Filip Valder]

- Some gitchangelog rc file. [Filip Valder]

- Mising comma. [Filip Valder]

- Auto-versioning accto git tags. [Filip Valder]

- See the hint in it4ifree.py. [Filip Valder]

- White space. [Filip Valder]

- Instructions re-ordered. [Filip Valder]


0.4.1 (2016-06-01)
------------------
- Keywords added. [Filip Valder]

- Important functional improvements & introduced README. [Filip Valder]


0.4 (2016-06-01)
----------------
- Config module introduced. [Filip Valder]

- Sample config file. [Filip Valder]

- README.txt -> README.md due to GL (the change will also appear in setup.py) [Filip Valder]

- Init & use module name ; not filename. [Filip Valder]

- Get ready for 0.4 release. [Filip Valder]

- Use module name ; not filename. [Filip Valder]

- Bug fixes. [Filip Valder]

- Support for sorting. [Filip Valder]

- Support for published date/time. [Filip Valder]

- CStringIO for full module usage support. [Filip Valder]


0.3.4 (2016-05-19)
------------------
- Support for stdin and various feed sources. [Filip Valder]

- Logging goes to separate file. [Filip Valder]

- Write to stderr instead of stdout. [Filip Valder]

- Egg-info for 0.3.3.post2. [Filip Valder]

- Repository moved, project IT4I-ized... [Filip Valder]

- 0.3.3.post1 released: setuptools is already dep of PIP, it may mess things up during install. [Filip Valder]


0.3.3 (2016-02-25)
------------------
- Egg-info files for 0.3.3. [Filip Valder]

- 0.3.3 released. [Filip Valder]

- Support for verbose and width opts; short opt for cron changed. [Filip Valder]

- Default template fixes. [Filip Valder]

- Sync with MANIFEST.in. [Filip Valder]

- Remove dist from repository. [Filip Valder]

- 0.3.2 stable with unicode encoding fixed. [Filip Valder]

- Add README. [Filip Valder]


