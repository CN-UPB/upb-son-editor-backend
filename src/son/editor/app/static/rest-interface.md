#Login
/login
* use github oauth process and redirect urls

#Workspace
/workspaces

| HTTP Method | description                | example request data     | example response                       |
|-------------|----------------------------|---------------------|----------------------------------------|
| GET         | lists all workspaces |                     | [ {"name": "workspace1", "id": 1234}, ... ]  |
| POST        | create a new Workspace       | {"name: "workspace1"} | {"name":"workspace1", "id": 1234}          |

/workspaces/{wsID}

| HTTP Method | description               | example request data    | example response           |
|-------------|---------------------------|--------------------|----------------------------|
| PUT         | update workspace definition | {"name":"newName"} | {"name":"newName"}  200 OK |
| DELETE      | delete workspace            |                    | 200 OK                     |

##Service Platforms
/workspaces/{wsID}/platforms

| HTTP Method | description                             | example request data                                                                                         | example response                                      |
|-------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| GET         | list configured platforms               |                                                                                                         | [{"name":"OpenBarista1","id":4321},...] |
| POST        | create new configuration for a platform | {"name":"Openbarista2", "gateKeeperURL":"http://path/to/gatekeeper/API", "credentials": "accessToken" } | {"name":"Openbarista2", "id":5432} <br/> 201 Created        |


/workspaces/{wsID}/platforms/{platformID}

| HTTP Method | description          | example request data                                                                                             | example response    |
|-------------|----------------------|-------------------------------------------------------------------------------------------------------------|---------------------|
| PUT         | update configuration | {"name":"Openbarista2"} <br> {"gateKeeperURL":"http://path/to/gatekeeper/API"}<br/> { "credentials": "accessToken" } | mirror input <br> 200 OK |
| DELETE      | delete configuration |                                                                                                             | 200 OK              |


##Catalogues (Work in Progress)
/workspaces/{wsID}/catalogues

| HTTP Method | description                              | example request data                                                                            | example response                                    |
|-------------|------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------|
| GET         | list configured catalogues               |                                                                                            | [{"name":"catalogue1", "id":42},...] |
| POST        | create new configuration for a catalogue | {"name":"Catalogue2", "url":"http://path/to/catalogue/API",<br> "credentials": "accessToken" } | 200 OK                                              |


/workspaces/{wsID}/catalogues/{catID}

| HTTP Method | description          | example request data                                                                                             | example response    |
|-------------|----------------------|-------------------------------------------------------------------------------------------------------------|---------------------|
| PUT         | update configuration | {"name":"Catalogue2"} <br> {"url":"http://path/to/catalogue/API"}<br/> { "credentials": "accessToken" } | mirror input <br> 200 OK |
| DELETE      | delete configuration |                                                                                                             | 200 OK              |


###Services
/workspaces/{wsID}/catalogues/{catID}/services

| HTTP Method | description                      | example request data | example response                                 |
|-------------|----------------------------------|-----------------|--------------------------------------------------|
| GET         | list services for this catalogue |                 |[{"name":"service1","id":1337},...] |
| POST        | publish service to catalogue     | {"id":1338}     | 200 OK                                           |


/workspaces/{wsID}/catalogues/{catID}/services/{nsID}

| HTTP Method  | description                  | example request data | example response |
|--------------|------------------------------|-----------------|------------------|
| PUT          | update service in catalogue  | {"id":1335}     | 200 OK           |
| DELTE        | publish service to catalogue |                 | 200 OK           |


###VNFs
/workspaces/{wsID}/catalogues/{catID}/functions

| HTTP Method  | description                  | example request data | example response |
|--------------|------------------------------|-----------------|------------------|
| PUT          | update vnf in catalogue  | {"id":1335}     | 200 OK           |
| DELTE        | publish vnf to catalogue |                 | 200 OK           |



/workspaces/{wsID}/catalogues/{catID}/functions/{vnfID}

| HTTP Method  | description                  | example request data | example response |
|--------------|------------------------------|-----------------|------------------|
| PUT          | update vnf in catalogue  | {"id":1335}     | 200 OK           |
| DELTE        | publish vnf to catalogue |                 | 200 OK           |


##Projects
/workspaces/{wsID}/projects/

| HTTP Method | description                | example request data     | example response                       |
|-------------|----------------------------|---------------------|----------------------------------------|
| GET         | list projects in workspace |                     | [{"name":"Project1"},...] |
| POST        | create a new Project       | {"name":"Project2"} | {"name":"Project2", "id":987}          |


/workspaces/{wsID}/projects/{projID}

| HTTP Method | description               | example request data    | example response           |
|-------------|---------------------------|--------------------|----------------------------|
| PUT         | update project definition | {"name":"newName"} | {"name":"newName"}  200 OK |
| DELETE      | delete project            |                    | 200 OK                     |


###Services
/workspaces/{wsID}/projects/{projID}/services


| HTTP Method | description                      | example request data | example response                                 |
|-------------|----------------------------------|-----------------|--------------------------------------------------|
| GET         | list services for this project |                 | [{"name":"service1","id":1337},...] |
| POST        | create new service     | {"vendor":"de.upb.cs.cn.pgsandman", <br>"name":"Service Name",<br> "version": "0.0.1"}     | {"name":"Service Name", "id":5687}                                 |


/workspaces/{wsID}/projects/{projID}/services/{nsID}

| HTTP Method | description                      | example request data | example response                                 |
|-------------|----------------------------------|-----------------|--------------------------------------------------|
|GET		  |get descriptor for network service|				   |{descriptor_version: "1.0",<br> vendor: "eu.sonata-nfv.service-descriptor",<br>name: "simplest-example",<br>version: "0.2"}|
| PUT         | modify the network service 		| {"network_functions: <br>{"vnf_id": <br>"vnf_firewall",<br> "vnf_vendor": "eu.sonata-nfv", <br>"vnf_name": "firewall-vnf", <br>"vnf_version": "0.2"}}	| 200 OK			|
| DELETE        | delete the network service    |   			  |    200 OK      |


###VNFs
/workspaces/{wsID}/projects/{projID}/functions/

| HTTP Method | description                      | example request data | example response                                 |
|-------------|----------------------------------|-----------------|--------------------------------------------------|
| GET         | list vnfs for this project |                 | [{"name":"vnf1","id":1337},...] |
| POST        | create new service     | {"vendor":"de.upb.cs.cn.pgsandman", <br>"name":"VNF Name",<br> "version": "0.0.1"}     | {"name":"VNF Name", "id":5687}                                 |



/workspaces/{wsID}/projects/{projID}/functions/{vnfID}

| HTTP Method | description                      | example request data | example response                                 |
|-------------|----------------------------------|-----------------|--------------------------------------------------|
|GET		  |get descriptor for network service|				   |{descriptor_version: "vnfd-schema-01",<br> vendor: "eu.sonata-nfv",<br>name: "simplest-example",<br>version: "0.2"}|
| PUT         | modify the vnf 		| {"virtual_links":<br> {"id: "mgmt",<br> "connectivity_type": "E-LAN", <br>"connection_points_reference":<br>{"vdu01:eth0",<br>"mgmt"} <br>"dhcp": True}}	| 200 OK			|
| DELETE        | delete the vnf    |   			  |    200 OK      |
