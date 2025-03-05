# README #

This library makes it easy to set up a Netsuite authorization without needing a frontend client using CLI utilities.

### Docs ###
[Netsuite API Documentation](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_158022624537.html)

## What do I need to get set up? ##
* Run `pip install netsuite-python`
* Activate your python VENV
* If using virtual environment 
  * Activate your virtual environment
  * `netsuite = python venv/bin/keap`

* #### Notes ####
  * Requirements
    * Sandbox requires the same setup as Prod, it DOES NOT copy over
    * An administrator for the Netsuite app to follow the steps [here](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771281570.html)
      * A user with the correct role
      * A role with the correct permissions
      * An Integration Record with the correct permissions (ensure default form is set correctly)
        * Client ID and Secret comes from this step, ensure they provide these
      * Certificate ID
        * A Certificate can be generated once you register the package with CLI with 'netsuite generate-certificate' 
        * Cert ID is available under Setup -> Integration -> OAuth 2.0 Client Credentials once the certificate is uploaded.

## Generating x509 certificate for Netsuite ###
 * Run `netsuite generate-certificate`
   * Domain: theapiguys.com
   * Organization: TAG 
   * Department: DEV
   * City: BOSTON
   * State: MA
   * Country: US
   * Email: will@theapiguys.com
 
 * It will ask for the file name that you wish to save the key to. This will be used when entering the creds.

## Uploading x509 certificate to Netsuite ##
* On Client's Netsuite top ribbon go to `Setup -> Integration -> OAuth 2.0 Client Credentials`
* Click `Create-New` button
    * Entity: The User created for TAG
    * ROLE: Role created for this integration
    * Application: Application Created for this integration
    * Certificate: Click "Choose A File" and upload the PUBLIC Cert (NOT PRIVATE KEY)
* Copy the Certificate ID
## Setting up Netsuite SDK in a project ##
* Run `netsuite generate-client-config`
    * It will ask you for information obtained above: You can use all the defaults
        * Client ID
        * Netsuite Certificate ID
        * Netsuite Key File
        * Netsuite Application Name
        * Allow None
        * Use Datetime
        * Storage Class
      
    * If you want to save to file
        * Provide a valid path for netsuite-credentials.json
        * else the credentials will be echoed out
    * To confirm, check the netsuite credentials path you entered, or the default, and there should be a json file with all
      the info you entered. Verify the details.

## Getting The Access Token ##
* Run `$netsuite get-access-token`
    * Use the defaults or repeat the info used above for
        * Path to Netsuite Credentials
    * Confirm the app name to be refreshed, if single app, just use default
* That's it! You should now have a valid token to use with the Netsuite API.


## Usage ##


It is pretty simple to get started using the SDK once you have a valid token.

### Setup Netsuite ###
```
import pathlib
from netsuite import Netsuite

#Include config file, config dict, or leave empty to use default setup

# w/ config file 
# netsuite = Netsuite(config_file=pathlib.Path('./netsuite-credentials.json'))

# using default 
netsuite = Netsuite()

#initialize apis
ns_contact_api = netsuite.REST_CLIENT.contact_api
ns_customer_api = netsuite.REST_CLIENT.customer_api
```

## Example Usage ##
 ```
 print(ns_contact_api.contact_id_get(id=1413220))
 ```


## Documentation for API Endpoints

All URIs are relative to *https://{App_Name}.suitetalk.api.netsuite.com/services/rest/record/v1*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ContactApi* | [**contact_get**](netsuite/swagger_client/docs/ContactApi.md#**contact_get****) | **GET** /contact | Get list of records.
*ContactApi* | [**contact_id_delete**](netsuite/swagger_client/docs/ContactApi.md#**contact_id_delete****) | **DELETE** /contact/{id} | Remove record.
*ContactApi* | [**contact_id_get**](netsuite/swagger_client/docs/ContactApi.md#**contact_id_get**) | **GET** /contact/{id} | Get record.
*ContactApi* | [**contact_id_patch**](netsuite/swagger_client/docs/ContactApi.md#**contact_id_patch**) | **PATCH** /contact/{id} | Update record.
*ContactApi* | [**contact_id_put**](netsuite/swagger_client/docs/ContactApi.md#**contact_id_put**) | **PUT** /contact/{id} | Insert or update record.
*ContactApi* | [**contact_post**](netsuite/swagger_client/docs/ContactApi.md#**contact_post**) | **POST** /contact | Insert record.
*CustomerApi* | [**customer_get**](netsuite/swagger_client/docs/CustomerApi.md#**customer_get**) | **GET** /customer | Get list of records.
*CustomerApi* | [**customer_id_delete**](netsuite/swagger_client/docs/CustomerApi.md#**customer_id_delete**) | **DELETE** /customer/{id} | Remove record.
*CustomerApi* | [**customer_id_get**](netsuite/swagger_client/docs/CustomerApi.md#**customer_id_get**) | **GET** /customer/{id} | Get record.
*CustomerApi* | [**customer_id_patch**](netsuite/swagger_client/docs/CustomerApi.md#**customer_id_patch**) | **PATCH** /customer/{id} | Update record.
*CustomerApi* | [**customer_id_put**](netsuite/swagger_client/docs/CustomerApi.md#**customer_id_put**) | **PUT** /customer/{id} | Insert or update record.
*CustomerApi* | [**customer_idtransform_cash_sale_post**](netsuite/swagger_client/docs/CustomerApi.md#**customer_idtransform_cash_sale_post**) | **POST** /customer/{id}/!transform/cashSale | Transform to cashSale.
*CustomerApi* | [**customer_idtransform_invoice_post**](netsuite/swagger_client/docs/CustomerApi.md#**customer_idtransform_invoice_post**) | **POST** /customer/{id}/!transform/invoice | Transform to invoice.
*CustomerApi* | [**customer_idtransform_sales_order_post**](netsuite/swagger_client/docs/CustomerApi.md#**customer_idtransform_sales_order_post**) | **POST** /customer/{id}/!transform/salesOrder | Transform to salesOrder.
*CustomerApi* | [**customer_idtransform_vendor_post**](netsuite/swagger_client/docs/CustomerApi.md#**customer_idtransform_vendor_post**) | **POST** /customer/{id}/!transform/vendor | Transform to vendor.
*CustomerApi* | [**customer_post**](netsuite/swagger_client/docs/CustomerApi.md#**customer_post**) | **POST** /customer | Insert record.

## Documentation For Models

 - [Contact](netsuite/swagger_client/docs/Contact.md)
 - [ContactCollection](netsuite/swagger_client/docs/ContactCollection.md)
 - [ContactCustomForm](netsuite/swagger_client/docs/ContactCustomForm.md)
 - [Customer](netsuite/swagger_client/docs/Customer.md)
 - [CustomerAddressBookAddressBookAddress](netsuite/swagger_client/docs/CustomerAddressBookAddressBookAddress.md)
 - [CustomerAddressBookCollection](netsuite/swagger_client/docs/CustomerAddressBookCollection.md)
 - [CustomerAddressBookElement](netsuite/swagger_client/docs/CustomerAddressBookElement.md)
 - [CustomerAlcoholRecipientType](netsuite/swagger_client/docs/CustomerAlcoholRecipientType.md)
 - [CustomerCampaignsCollection](netsuite/swagger_client/docs/CustomerCampaignsCollection.md)
 - [CustomerCampaignsElement](netsuite/swagger_client/docs/CustomerCampaignsElement.md)
 - [CustomerCollection](netsuite/swagger_client/docs/CustomerCollection.md)
 - [CustomerContactRolesCollection](netsuite/swagger_client/docs/CustomerContactRolesCollection.md)
 - [CustomerContactRolesElement](netsuite/swagger_client/docs/CustomerContactRolesElement.md)
 - [CustomerCustomForm](netsuite/swagger_client/docs/CustomerCustomForm.md)
 - [CustomerEmailPreference](netsuite/swagger_client/docs/CustomerEmailPreference.md)
 - [CustomerGlobalSubscriptionStatus](netsuite/swagger_client/docs/CustomerGlobalSubscriptionStatus.md)
 - [CustomerGroupPricingCollection](netsuite/swagger_client/docs/CustomerGroupPricingCollection.md)
 - [CustomerGroupPricingElement](netsuite/swagger_client/docs/CustomerGroupPricingElement.md)
 - [CustomerItemPricingCollection](netsuite/swagger_client/docs/CustomerItemPricingCollection.md)
 - [CustomerItemPricingElement](netsuite/swagger_client/docs/CustomerItemPricingElement.md)
 - [CustomerLanguage](netsuite/swagger_client/docs/CustomerLanguage.md)
 - [CustomerNegativeNumberFormat](netsuite/swagger_client/docs/CustomerNegativeNumberFormat.md)
 - [CustomerNumberFormat](netsuite/swagger_client/docs/CustomerNumberFormat.md)
 - [CustomerShippingCarrier](netsuite/swagger_client/docs/CustomerShippingCarrier.md)
 - [CustomerSymbolPlacement](netsuite/swagger_client/docs/CustomerSymbolPlacement.md)
 - [CustomerThirdPartyCarrier](netsuite/swagger_client/docs/CustomerThirdPartyCarrier.md)
 - [CustomeraddressBookaddressBookAddressCountry](netsuite/swagger_client/docs/CustomeraddressBookaddressBookAddressCountry.md)
 - [NsError](netsuite/swagger_client/docs/NsError.md)
 - [NsErrorOerrorDetails](netsuite/swagger_client/docs/NsErrorOerrorDetails.md)
 - [NsLink](netsuite/swagger_client/docs/NsLink.md)
 - [NsResource](netsuite/swagger_client/docs/NsResource.md)
 - [NsResourceCollection](netsuite/swagger_client/docs/NsResourceCollection.md)
 - [OneOfcontactCompany](netsuite/swagger_client/docs/OneOfcontactCompany.md)
 - [OneOfcontactCustentityCourseAttended](netsuite/swagger_client/docs/OneOfcontactCustentityCourseAttended.md)
 - [OneOfcontactCustentityEnergyEffAttended](netsuite/swagger_client/docs/OneOfcontactCustentityEnergyEffAttended.md)
 - [OneOfcontactCustentityHitachiCourseAttended](netsuite/swagger_client/docs/OneOfcontactCustentityHitachiCourseAttended.md)
 - [OneOfcontactCustentityHpCourseAttended](netsuite/swagger_client/docs/OneOfcontactCustentityHpCourseAttended.md)
 - [OneOfcontactCustentityPvCourseAtteneded](netsuite/swagger_client/docs/OneOfcontactCustentityPvCourseAtteneded.md)
 - [OneOfcontactCustentitySolCourseAttended](netsuite/swagger_client/docs/OneOfcontactCustentitySolCourseAttended.md)
 - [OneOfcontactCustentityUnventHotWaterG3](netsuite/swagger_client/docs/OneOfcontactCustentityUnventHotWaterG3.md)
 - [OneOfcontactCustentityWaterRegulations1999](netsuite/swagger_client/docs/OneOfcontactCustentityWaterRegulations1999.md)
 - [OneOfcustomerCustentityCourseAttended](netsuite/swagger_client/docs/OneOfcustomerCustentityCourseAttended.md)
 - [OneOfcustomerCustentityEnergyEffAttended](netsuite/swagger_client/docs/OneOfcustomerCustentityEnergyEffAttended.md)
 - [OneOfcustomerCustentityHitachiCourseAttended](netsuite/swagger_client/docs/OneOfcustomerCustentityHitachiCourseAttended.md)
 - [OneOfcustomerCustentityHpCourseAttended](netsuite/swagger_client/docs/OneOfcustomerCustentityHpCourseAttended.md)
 - [OneOfcustomerCustentityPvCourseAtteneded](netsuite/swagger_client/docs/OneOfcustomerCustentityPvCourseAtteneded.md)
 - [OneOfcustomerCustentitySolCourseAttended](netsuite/swagger_client/docs/OneOfcustomerCustentitySolCourseAttended.md)
 - [OneOfcustomerCustentityUnventHotWaterG3](netsuite/swagger_client/docs/OneOfcustomerCustentityUnventHotWaterG3.md)
 - [OneOfcustomerCustentityWaterRegulations1999](netsuite/swagger_client/docs/OneOfcustomerCustentityWaterRegulations1999.md)
 - [OneOfcustomerItemPricingElementItem](netsuite/swagger_client/docs/OneOfcustomerItemPricingElementItem.md)