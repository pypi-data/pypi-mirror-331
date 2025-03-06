# Tableau Toolkit


## Development Process

### Prerequisites

* Git - https://git-scm.com/
* Poetry - https://python-poetry.org/
* Python (3.13) - https://www.python.org/

### Get Project
`git clone <this repository>`

### Install Dependencies
`poetry install`

### Black to Standardize Code Formatting
`poetry run black tableau_toolkit`

### Pylint to Improve Code Readability
`poetry run pylint tableau_toolkit`

### Run unit tests
`poetry run test`

### Run cli commands
`poetry run tt`


### Build 
`poetry build`

### Publish
`poetry config pypi-token.pypi <your-api-token> # do this only your first time`

`poetry publish --skip-existing`

### Installer

`poetry run postbuild`

installer.iss - Load it into 'Inno Setup' application to create Windows installer, then remove/install as needed

* install: double click on installer in output directory
* remove: use add or remove programs from start menu and search for Tableau Toolkit

create_pkg.sh - Run it to create installer for MacOS, then remove/install as needed

* install: double click on pkg file in output directory
* remove: rm /usr/local/bin/tt

create_deb.sh - create deb installer, then remove/install as needed

* install: sudo dpkg -i *./output/filename.deb*
* remove: sudo dpkg -r *packagename*

create_rpm.sh - create rpm installer, then remove/install as needed

* install: sudo rpm -i *./output/filename.rpm*
* remove: sudo rpm -e *packagename*

## Usage

Once published, users can install and use

### Install
`pip install tableau-toolkit`

### Usage

#### First Time
If this is the first time using the tableau toolkit, 
execute the following command to create a config file. 
This only needs to be done once.

`tt init`

A file will appear at `.tableau_toolkit/.tableau.yaml`
in your home directory. 

Next, Fill in the information in the generated config file. 
For any field with the comment `# provide encoded string`, 
use `tt encode <string>` to generate the encoded string for the config file

```
api:
  version: '3.21'
authentication:
  type: personal_access_token
personal_access_token:
  name: api
  secret: # provide encoded string
postgres:
  database: workgroup
  host: localhost
  password: 
  port: 8060
  user: readonly
site:
  content_url: ''
tableau_auth:
  password: # provide encoded string
  username: 
tableau_server:
  url: # url for api access
  public_url: # url for end user access
```

#### Ready to Use
Next, execute `tt` to get a list of commands. Some example commands are listed below

```

tt get data-alerts --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get extract-refreshes --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get subscriptions --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get workbooks --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get datasources --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get views --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at" 

tt get users --no-headers --limit 10000000 --columns "object_type,object_name,object_luid,object_owner_username,object_location,object_size,site_name,site_luid,days_since_last_event,snapshot_at"

```

