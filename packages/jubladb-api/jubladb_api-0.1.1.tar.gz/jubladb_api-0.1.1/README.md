# JublaDB Python API
A package with generated code to access the [Jubla DB](https://db.jubla.ch) API with Python code.

For more information, please visit [the project page](https://github.com/Jungwacht-Herisau/jubladb_python_api)

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/Jungwacht-Herisau/jubladb_python_api.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/Jungwacht-Herisau/jubladb_python_api.git`)

Then import the package:
```python
import jubladb_api
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import jubladb_api
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import jubladb_api
from jubladb_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = jubladb_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ServiceTokenAuthHeader
configuration.api_key['ServiceTokenAuthHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ServiceTokenAuthHeader'] = 'Bearer'

# Configure API key authorization: ServiceTokenAuthParam
configuration.api_key['ServiceTokenAuthParam'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ServiceTokenAuthParam'] = 'Bearer'


# Enter a context with an instance of the API client
with jubladb_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = jubladb_api.EventKindCategoriesApi(api_client)
    id = 'id_example' # str | ID of the resource
    sort = ['sort_example'] # List[str] | [Sort event_kind_categories according to one or more criteria](https://jsonapi.org/format/#fetching-sorting)  You should not include both ascending `id` and descending `-id` fields the same time   (optional)
    fields_event_kind_categories = [jubladb_api.EventKindCategoriesReadableAttribute()] # List[EventKindCategoriesReadableAttribute] | [Include only specified fields of Kind category in response](https://jsonapi.org/format/#fetching-sparse-fieldsets) (optional)
    filter_id_eq = [56] # List[int] | [Filter Kind category by id using eq operator](https://jsonapi.org/format/#fetching-filtering) (optional)
    filter_id_not_eq = [56] # List[int] | [Filter Kind category by id using not_eq operator](https://jsonapi.org/format/#fetching-filtering) (optional)
    filter_id_gt = [56] # List[int] | [Filter Kind category by id using gt operator](https://jsonapi.org/format/#fetching-filtering) (optional)
    filter_id_gte = [56] # List[int] | [Filter Kind category by id using gte operator](https://jsonapi.org/format/#fetching-filtering) (optional)
    filter_id_lt = [56] # List[int] | [Filter Kind category by id using lt operator](https://jsonapi.org/format/#fetching-filtering) (optional)
    filter_id_lte = [56] # List[int] | [Filter Kind category by id using lte operator](https://jsonapi.org/format/#fetching-filtering) (optional)

    try:
        # Fetch Event kind category
        api_response = api_instance.get_event_kind_category(id, sort=sort, fields_event_kind_categories=fields_event_kind_categories, filter_id_eq=filter_id_eq, filter_id_not_eq=filter_id_not_eq, filter_id_gt=filter_id_gt, filter_id_gte=filter_id_gte, filter_id_lt=filter_id_lt, filter_id_lte=filter_id_lte)
        print("The response of EventKindCategoriesApi->get_event_kind_category:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling EventKindCategoriesApi->get_event_kind_category: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*EventKindCategoriesApi* | [**get_event_kind_category**](docs/EventKindCategoriesApi.md#get_event_kind_category) | **GET** /api/event_kind_categories/{id} | Fetch Event kind category
*EventKindCategoriesApi* | [**list_event_kind_categories**](docs/EventKindCategoriesApi.md#list_event_kind_categories) | **GET** /api/event_kind_categories | List Event kind categories
*EventKindsApi* | [**get_event_kind**](docs/EventKindsApi.md#get_event_kind) | **GET** /api/event_kinds/{id} | Fetch Event kind
*EventKindsApi* | [**list_event_kinds**](docs/EventKindsApi.md#list_event_kinds) | **GET** /api/event_kinds | List Event kinds
*EventsApi* | [**get_event**](docs/EventsApi.md#get_event) | **GET** /api/events/{id} | Fetch Event
*EventsApi* | [**list_events**](docs/EventsApi.md#list_events) | **GET** /api/events | List Events
*GroupsApi* | [**get_group**](docs/GroupsApi.md#get_group) | **GET** /api/groups/{id} | Fetch Group
*GroupsApi* | [**list_groups**](docs/GroupsApi.md#list_groups) | **GET** /api/groups | List Groups
*InvoicesApi* | [**get_invoice**](docs/InvoicesApi.md#get_invoice) | **GET** /api/invoices/{id} | Fetch Invoice
*InvoicesApi* | [**list_invoices**](docs/InvoicesApi.md#list_invoices) | **GET** /api/invoices | List Invoices
*InvoicesApi* | [**update_invoice**](docs/InvoicesApi.md#update_invoice) | **PUT** /api/invoices/{id} | Update Invoice
*PeopleApi* | [**get_person**](docs/PeopleApi.md#get_person) | **GET** /api/people/{id} | Fetch Person
*PeopleApi* | [**list_people**](docs/PeopleApi.md#list_people) | **GET** /api/people | List People
*PeopleApi* | [**update_person**](docs/PeopleApi.md#update_person) | **PUT** /api/people/{id} | Update Person
*RolesApi* | [**create_role**](docs/RolesApi.md#create_role) | **POST** /api/roles | Create Role
*RolesApi* | [**delete_role**](docs/RolesApi.md#delete_role) | **DELETE** /api/roles/{id} | Destroy Role
*RolesApi* | [**get_role**](docs/RolesApi.md#get_role) | **GET** /api/roles/{id} | Fetch Role
*RolesApi* | [**list_roles**](docs/RolesApi.md#list_roles) | **GET** /api/roles | List Roles
*RolesApi* | [**update_role**](docs/RolesApi.md#update_role) | **PUT** /api/roles/{id} | Update Role


## Documentation For Models

 - [AdditionalEmails](docs/AdditionalEmails.md)
 - [AdditionalEmailsCollection](docs/AdditionalEmailsCollection.md)
 - [AdditionalEmailsReadableAttribute](docs/AdditionalEmailsReadableAttribute.md)
 - [AdditionalEmailsRequest](docs/AdditionalEmailsRequest.md)
 - [AdditionalEmailsResource](docs/AdditionalEmailsResource.md)
 - [AdditionalEmailsSingle](docs/AdditionalEmailsSingle.md)
 - [AdditionalEmailsSingleLinks](docs/AdditionalEmailsSingleLinks.md)
 - [Courses](docs/Courses.md)
 - [CoursesCollection](docs/CoursesCollection.md)
 - [CoursesReadableAttribute](docs/CoursesReadableAttribute.md)
 - [CoursesRelationships](docs/CoursesRelationships.md)
 - [CoursesRelationshipsContact](docs/CoursesRelationshipsContact.md)
 - [CoursesRelationshipsDates](docs/CoursesRelationshipsDates.md)
 - [CoursesRequest](docs/CoursesRequest.md)
 - [CoursesResource](docs/CoursesResource.md)
 - [CoursesSingle](docs/CoursesSingle.md)
 - [Dates](docs/Dates.md)
 - [DatesCollection](docs/DatesCollection.md)
 - [DatesReadableAttribute](docs/DatesReadableAttribute.md)
 - [DatesRelationships](docs/DatesRelationships.md)
 - [DatesRequest](docs/DatesRequest.md)
 - [DatesResource](docs/DatesResource.md)
 - [DatesSingle](docs/DatesSingle.md)
 - [EventKindCategories](docs/EventKindCategories.md)
 - [EventKindCategoriesCollection](docs/EventKindCategoriesCollection.md)
 - [EventKindCategoriesReadableAttribute](docs/EventKindCategoriesReadableAttribute.md)
 - [EventKindCategoriesRequest](docs/EventKindCategoriesRequest.md)
 - [EventKindCategoriesResource](docs/EventKindCategoriesResource.md)
 - [EventKindCategoriesSingle](docs/EventKindCategoriesSingle.md)
 - [EventKinds](docs/EventKinds.md)
 - [EventKindsCollection](docs/EventKindsCollection.md)
 - [EventKindsReadableAttribute](docs/EventKindsReadableAttribute.md)
 - [EventKindsRelationships](docs/EventKindsRelationships.md)
 - [EventKindsRequest](docs/EventKindsRequest.md)
 - [EventKindsResource](docs/EventKindsResource.md)
 - [EventKindsSingle](docs/EventKindsSingle.md)
 - [Events](docs/Events.md)
 - [EventsCollection](docs/EventsCollection.md)
 - [EventsReadableAttribute](docs/EventsReadableAttribute.md)
 - [EventsRelationships](docs/EventsRelationships.md)
 - [EventsRequest](docs/EventsRequest.md)
 - [EventsResource](docs/EventsResource.md)
 - [EventsSingle](docs/EventsSingle.md)
 - [Groups](docs/Groups.md)
 - [GroupsCollection](docs/GroupsCollection.md)
 - [GroupsExtraAttribute](docs/GroupsExtraAttribute.md)
 - [GroupsReadableAttribute](docs/GroupsReadableAttribute.md)
 - [GroupsRelationships](docs/GroupsRelationships.md)
 - [GroupsRequest](docs/GroupsRequest.md)
 - [GroupsResource](docs/GroupsResource.md)
 - [GroupsSingle](docs/GroupsSingle.md)
 - [InvoiceItems](docs/InvoiceItems.md)
 - [InvoiceItemsCollection](docs/InvoiceItemsCollection.md)
 - [InvoiceItemsReadableAttribute](docs/InvoiceItemsReadableAttribute.md)
 - [InvoiceItemsRelationships](docs/InvoiceItemsRelationships.md)
 - [InvoiceItemsRequest](docs/InvoiceItemsRequest.md)
 - [InvoiceItemsResource](docs/InvoiceItemsResource.md)
 - [InvoiceItemsSingle](docs/InvoiceItemsSingle.md)
 - [Invoices](docs/Invoices.md)
 - [InvoicesCollection](docs/InvoicesCollection.md)
 - [InvoicesReadableAttribute](docs/InvoicesReadableAttribute.md)
 - [InvoicesRelationships](docs/InvoicesRelationships.md)
 - [InvoicesRequest](docs/InvoicesRequest.md)
 - [InvoicesResource](docs/InvoicesResource.md)
 - [InvoicesSingle](docs/InvoicesSingle.md)
 - [JsonapiData](docs/JsonapiData.md)
 - [JsonapiError](docs/JsonapiError.md)
 - [JsonapiErrorSource](docs/JsonapiErrorSource.md)
 - [JsonapiFailure](docs/JsonapiFailure.md)
 - [JsonapiInfo](docs/JsonapiInfo.md)
 - [JsonapiJsonapi](docs/JsonapiJsonapi.md)
 - [JsonapiLink](docs/JsonapiLink.md)
 - [JsonapiLinkOneOf](docs/JsonapiLinkOneOf.md)
 - [JsonapiLinkage](docs/JsonapiLinkage.md)
 - [JsonapiPagination](docs/JsonapiPagination.md)
 - [JsonapiRelationshipLinks](docs/JsonapiRelationshipLinks.md)
 - [JsonapiResource](docs/JsonapiResource.md)
 - [JsonapiSuccess](docs/JsonapiSuccess.md)
 - [People](docs/People.md)
 - [PeopleCollection](docs/PeopleCollection.md)
 - [PeopleReadableAttribute](docs/PeopleReadableAttribute.md)
 - [PeopleRelationships](docs/PeopleRelationships.md)
 - [PeopleRequest](docs/PeopleRequest.md)
 - [PeopleResource](docs/PeopleResource.md)
 - [PeopleSingle](docs/PeopleSingle.md)
 - [PersonName](docs/PersonName.md)
 - [PersonNameCollection](docs/PersonNameCollection.md)
 - [PersonNameReadableAttribute](docs/PersonNameReadableAttribute.md)
 - [PersonNameRequest](docs/PersonNameRequest.md)
 - [PersonNameResource](docs/PersonNameResource.md)
 - [PersonNameSingle](docs/PersonNameSingle.md)
 - [PhoneNumbers](docs/PhoneNumbers.md)
 - [PhoneNumbersCollection](docs/PhoneNumbersCollection.md)
 - [PhoneNumbersReadableAttribute](docs/PhoneNumbersReadableAttribute.md)
 - [PhoneNumbersRequest](docs/PhoneNumbersRequest.md)
 - [PhoneNumbersResource](docs/PhoneNumbersResource.md)
 - [PhoneNumbersSingle](docs/PhoneNumbersSingle.md)
 - [Roles](docs/Roles.md)
 - [RolesCollection](docs/RolesCollection.md)
 - [RolesReadableAttribute](docs/RolesReadableAttribute.md)
 - [RolesRelationships](docs/RolesRelationships.md)
 - [RolesRequest](docs/RolesRequest.md)
 - [RolesResource](docs/RolesResource.md)
 - [RolesSingle](docs/RolesSingle.md)
 - [SocialAccounts](docs/SocialAccounts.md)
 - [SocialAccountsCollection](docs/SocialAccountsCollection.md)
 - [SocialAccountsReadableAttribute](docs/SocialAccountsReadableAttribute.md)
 - [SocialAccountsRequest](docs/SocialAccountsRequest.md)
 - [SocialAccountsResource](docs/SocialAccountsResource.md)
 - [SocialAccountsSingle](docs/SocialAccountsSingle.md)
 - [Types](docs/Types.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="ServiceTokenAuthHeader"></a>
### ServiceTokenAuthHeader

- **Type**: API key
- **API key parameter name**: X-TOKEN
- **Location**: HTTP header

<a id="ServiceTokenAuthParam"></a>
### ServiceTokenAuthParam

- **Type**: API key
- **API key parameter name**: token
- **Location**: URL query string

<a id="SessionAuth"></a>
### SessionAuth

- **Type**: API key
- **API key parameter name**: _session_id
- **Location**: 


## Author

oss@basilbader.com



## How this package is generated
This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: v1
- Package version: 0.1.1
- Generator version: 7.12.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

### Mustache templates
A few templates needed modifications to make it work. The original files can be found in the [OpenAPI-Generator GitHub Repo](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/python).
Updates from there should be merged into the templates here from time to time. There's no automated workflow for that yet.