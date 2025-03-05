import json
import os

import click as click
from click import prompt

from netsuite.Netsuite import Netsuite
from netsuite.settings import api_settings, IN_MEMORY_STORAGE, JSON_STORAGE
import click
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
# from OpenSSL.SSL import FILETYPE_PEM
# from OpenSSL.crypto import (dump_certificate, X509, X509Name, PKey, TYPE_RSA, X509Req, dump_privatekey, X509Extension)


@click.group()
def cli():
    """
    Simple CLI for managing Netsuite API Access
    """
    pass


# @cli.command()
# def generate_certificate():
#     CN = prompt("Domain", hide_input=False)
#     ORG = prompt("Organization", hide_input=False)
#     ORG_UNIT = prompt("Department", hide_input=False)
#     L = prompt("City", hide_input=False)
#     ST = prompt("State", hide_input=False)
#     C = prompt("Country", hide_input=False)
#     EMAIL = prompt("Email", hide_input=False)
#
#     NETSUITE_KEY_FILE = prompt("Netsuite Key FIle Name['./netsuite-key']: ", default=api_settings.NETSUITE_KEY_FILE)
#     CERTIFICATE_FILE = './netsuite-certificate.pem'
#
#     key = PKey()
#     key.generate_key(TYPE_RSA, 4096)
#
#     cert = X509()
#
#     subject = cert.get_subject()
#     subject.CN = CN
#     subject.O = ORG
#     subject.OU = ORG_UNIT
#     subject.L = L
#     subject.ST = ST
#     subject.C = C
#     subject.emailAddress = EMAIL
#
#     cert.set_version(2)
#     cert.set_issuer(subject)
#     cert.set_subject(subject)
#     cert.set_serial_number(int.from_bytes(os.urandom(16), byteorder="big"))
#     # cert.set_serial_number(int(rand.bytes(16).encode('hex'), 16))
#     cert.gmtime_adj_notBefore(0)
#     cert.gmtime_adj_notAfter(31536000)
#     cert.set_pubkey(key)
#     cert.sign(key, 'sha256')
#
#     with open(CERTIFICATE_FILE, 'wb+') as f:
#         f.write(dump_certificate(FILETYPE_PEM, cert))
#     with open(NETSUITE_KEY_FILE, 'wb+') as f:
#         f.write(dump_privatekey(FILETYPE_PEM, key))

@cli.command()
def generate_certificate():
    generate_netsuite_certificate()

def generate_netsuite_certificate():
    # Prompt for certificate attributes
    CN = click.prompt("Domain", hide_input=False)
    ORG = click.prompt("Organization", hide_input=False)
    ORG_UNIT = click.prompt("Department", hide_input=False)
    L = click.prompt("City", hide_input=False)
    ST = click.prompt("State", hide_input=False)
    C = click.prompt("Country", hide_input=False)
    EMAIL = click.prompt("Email", hide_input=False)

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # Generate self-signed certificate using the prompted attributes
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, C),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, ST),
        x509.NameAttribute(NameOID.LOCALITY_NAME, L),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, ORG),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, ORG_UNIT),
        x509.NameAttribute(NameOID.COMMON_NAME, CN),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, EMAIL),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=730)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(CN)]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    NETSUITE_PRIVATE_KEY_FILE = prompt("Netsuite Key File Name['./netsuite_key']: ", default=api_settings.NETSUITE_KEY_FILE)
    CERTIFICATE_FILE = './netsuite_certificate.pem'

    # Write private key to file
    with open(NETSUITE_PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate to file
    with open(CERTIFICATE_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

@cli.command()
def generate_client_config():
    client_id = prompt("What is your client id?", hide_input=False)
    cert_id = prompt("What is your Netsuite certificate id?", hide_input=False)
    cert_file = prompt("Name of Netsuite Key File['netsuite-key.pem']?", hide_input=False, default='netsuite-key.pem')

    # client_secret = prompt("What is your client secret?", hide_input=True)
    # redirect_url = prompt("Redirect URL", default=api_settings.REDIRECT_URL)
    netsuite_app_name = prompt("What is the netsuite application name?", hide_input=False)
    app_name = prompt("App Name", default=api_settings.APP_NAME)
    allow_none = prompt("Allow None", default=api_settings.ALLOW_NONE)
    use_datetime = prompt("Use Datetime", default=api_settings.USE_DATETIME)
    storage_class = prompt("Storage Class", default=api_settings.defaults.get('STORAGE_CLASS'),
                           type=click.Choice(api_settings.defaults.get('DEFAULT_STORAGE_CLASSES')),
                           show_choices=True)

    creds = {
        'CLIENT_ID': client_id,
        'NETSUITE_KEY_FILE': cert_file,
        'CERT_ID': cert_id,
        # 'CLIENT_SECRET': client_secret,
        # 'REDIRECT_URL': redirect_url,
        'NETSUITE_APP_NAME': netsuite_app_name,
        'APP_NAME': app_name,
        'ALLOW_NONE': allow_none,
        'USE_DATETIME': use_datetime,
        'STORAGE_CLASS': storage_class,
    }

    if storage_class == JSON_STORAGE:
        creds['JSON_STORAGE_PATH'] = prompt("Token Storage File", default=api_settings.JSON_STORAGE_PATH,
                                            type=click.Path(readable=True, writable=True))

    save_to_file = prompt("Save settings to file?", default='y', type=click.BOOL, show_choices=True)

    if save_to_file:
        file = prompt("Save settings to file?", default=api_settings.CREDENTIALS_PATH, type=click.File("w", ))
        file.write(json.dumps(creds, indent=4))
    else:
        click.echo(creds)

    return creds

@cli.command()
def generate_netsuite_client_config():
    try:
        netsuite = Netsuite()
        if netsuite.api_settings.CLIENT_ID is not None:
            from pprint import pprint
            print("Netsuite Credentials Found.")
            print("     CURRENT CONFIG")
            print("-------------------------")
            pprint(netsuite.api_settings.__dict__.get('_user_settings'), indent=4)
            print("\n")
            if prompt("Keep settings?", type=click.BOOL, default=True):
                return
    except Exception:
        print("")
    print("****************************")
    print("  GENERATE NETSUITE CONFIG")
    print("****************************")
    steps_completed = False
    while not steps_completed:
        steps_completed = prompt(f"Have you created the integration record by following the steps in the README?", default='y', type=click.BOOL, show_choices=True)
        if steps_completed:
            client_id = prompt("Client Id", hide_input=False)
        else:
            print('Read it and do the steps hoe https://bitbucket.org/theapiguys/netsuite_python/src/master/')

    print("\n --- Certificate Configuration --- \n ")
    certificate_uploaded = False
    while not certificate_uploaded:
        certificate_uploaded = prompt(f"Have you generated a certificate and uploaded it to Netsuite?", default='n', type=click.BOOL, show_choices=True)
        if certificate_uploaded:
            cert_id = prompt("Certificate ID: ", hide_input=False)
        else:
            generate_netsuite_certificate()

    print("\n --- Certificate has been Configured --- \n ")
    # client_secret = prompt("What is your client secret?", hide_input=True)
    # redirect_url = prompt("Redirect URL", default=api_settings.REDIRECT_URL)
    netsuite_app_name = prompt("What is the netsuite application name (Portion before app.netsuite.com)?", hide_input=False)
    app_name = prompt("App Name (for token storage)", default=api_settings.APP_NAME)
    # storage_class = prompt("Storage Class", default=api_settings.defaults.get('STORAGE_CLASS'),
    #                        type=click.Choice(api_settings.defaults.get('DEFAULT_STORAGE_CLASSES')),
    #                        show_choices=True)
    storage_class = api_settings.defaults.get('STORAGE_CLASS')

    creds = {
        'CLIENT_ID': client_id,
        'CERT_ID': cert_id,
        # 'CLIENT_SECRET': client_secret,
        # 'REDIRECT_URL': redirect_url,
        'NETSUITE_APP_NAME': netsuite_app_name,
        'APP_NAME': app_name,
        'ALLOW_NONE': api_settings.ALLOW_NONE,
        'USE_DATETIME': api_settings.USE_DATETIME,
        'STORAGE_CLASS': storage_class,
    }

    if storage_class == JSON_STORAGE:
        creds['JSON_STORAGE_PATH'] = prompt("Token Storage File", default=api_settings.JSON_STORAGE_PATH,
                                            type=click.Path(readable=True, writable=True))


    with open(api_settings.CREDENTIALS_PATH, 'w') as f:
        creds_json = json.dumps(creds, indent=4)
        f.write(creds_json)
        print(f"Netsuite Credentials path: {api_settings.CREDENTIALS_PATH} ")
    print("\n ----- Configuration Generated -----")



    return creds


@cli.command()
@click.option('--credentials-file', '--f', type=click.File('r'), default=api_settings.CREDENTIALS_PATH,
              prompt="Path to Credentials File")
@click.pass_context
def get_access_token(ctx, credentials_file):
    """OAuth flow for Netsuite to obtain an access and refresh token"""
    try:
        creds = json.load(credentials_file)
    except Exception as e:
        return

    creds['APP_NAME'] = prompt("What app is being used?", type=click.STRING, default=creds['APP_NAME'])

    netsuite = Netsuite(
        config=creds
    )
    netsuite.request_access_token()
    # auth_url = netsuite.get_authorization_url()
    # click.echo(f"Visit {auth_url}")
    # response_url = prompt("Paste the return url here")
    # query_string = dict(parse.parse_qsl(parse.urlsplit(response_url).query))
    # code = query_string.get('code')
    # if code:
    #     netsuite.request_access_token(code)

    if netsuite.token.access_token:
        if creds.get('STORAGE_CLASS') == IN_MEMORY_STORAGE:
            if prompt("You have chosen memory storage so nothing is saved here. Echo results?", default="y",
                      type=click.BOOL):
                click.echo(netsuite.token.__dict__)
            else:
                click.echo(f"Saved to {credentials_file}")

@cli.command()
def generate_rest_client():
    generate_netsuite_rest_client()

def generate_netsuite_rest_client():
    ns_records_to_include = []
    print (" ----- Rest Client Generator -----")
    netsuite = Netsuite()
    use_record_wizard = prompt("Use Record Wizard?", type=click.BOOL, default=True)
    if use_record_wizard:
        needs_other_recordtypes = prompt("Will you be using record types other than customer?", type=click.BOOL, default=True)


        if needs_other_recordtypes:

            display_ns_classes = prompt("List available Netsuite Records?", type=click.BOOL, default=True)
            print("")
            print(" Getting Record Types... May take a minute...")
            records = netsuite.get_netsuite_recordtypes()
            if display_ns_classes:
                display_custom = prompt("Display Custom records (probably not)?", type=click.BOOL, default=False)
                print("\n   RECORDS")
                print("-------------------")
                if display_custom:
                    for record in records:
                        print(record)
                else:
                    for record in records:
                        if "customrecord" not in record and "customlist" not in record:
                            print(record)

            print("\n")
            add_more_records = True
            while add_more_records:
                next_record = prompt("Which records do you need?", default='')
                if next_record == '':
                    if prompt("Skip this step and use default (customer)?", type=click.BOOL, default=False):
                        break
                else:
                    if next_record not in records:
                        print("That record is not available.")
                    elif next_record in ns_records_to_include:
                        print("record already included.")
                    else:
                         ns_records_to_include.append(next_record)
                         print(f"Record Added: {next_record}")
                add_more_records = prompt("Add another?", type=click.BOOL, default='yes', show_choices=True)


        if len(ns_records_to_include) >> 0:
            record_str = ''
            index = 0
            for record in ns_records_to_include:
                print(len(ns_records_to_include))
                if index == 0:
                    print('index was 0')
                    record_str += f'{record}'
                    index += 1
                else:
                    record_str += f',{record}'
        else:
            record_str = 'customer'
    else:
        record_str = prompt("Enter Record Types (comma separated)", default='customer')
    print(f"Record STR: record_str")
    netsuite.generate_rest_client(record_types=record_str)


if __name__ == "__main__":
    cli()
