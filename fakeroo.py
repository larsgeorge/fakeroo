import io
import os
import sys
import functools

import configargparse
import yaml

from faker import Faker
from faker.utils import distribution as fakedist


def parse_commandline() -> None:
    """Parses the command line arguments, which can override some YAML settings"""
    parser = configargparse.ArgParser()
    parser.add('-f', '--file', dest='filename', 
        help='name of the output file, defaults to stdout')
    parser.add('-n', '--rows', dest='rows', default=1, type=int,
        help='number of rows to generate')
    parser.add('-q', '--quiet', dest='quiet', action='store_true',
        help='suppress all normal messages')
    parser.add('-v', '--verbose', dest='verbose', action='store_true',
        help='increases number of messages')
    parser.add('yaml_files', nargs='+', help='YAML file(s)')
    global options
    options = parser.parse_args()

    is_verbose = options.verbose
    is_quiet = options.quiet
    if not is_verbose:
        sys.tracebacklimit = 0


def convert_tuple_to_str(data: tuple, delim=',', trim=True) -> str:
    """Converts tuples containing arbitrary types (not just str) into a string"""
    def stradd(x1, x2):
        if not x2:
            x2 = ""
        elif type(x2) == tuple:
            x2 = convert_tuple_to_str(x2, delim=", ")
        else:
            x2 = str(x2)
        if trim: 
            x2 = x2.strip()
        if not x1:
            return str(x2)
        else:
            return str(x1) + delim + str(x2)
    return functools.reduce(stradd, data, None)


def getStartEnd(field: dict) -> tuple:
    """Helper to get start and end values as a tuple"""
    start = field['start'] if 'start' in field else None
    end = field['end'] if 'end' in field else None
    return start, end
    

def get_header_row(data: dict, delim: str = ',') -> str:
    """Returns the header row, consisting of all column names"""
    fields = data['fields']
    header = ""
    col_count = 0
    for field in fields:
        if (len(header) > 0):
            header += delim
        col_count += 1
        header += field['name'].strip() if 'name' in field else "col_" + str(col_count)
    header += "\n"
    return header


def process_row(fields: list, fake: Faker) -> tuple:
    """Process a single row and return it as a tuple"""
    # get a row wide faker instance, else it changes from column to column
    if fake.weights:
        row_faker = fakedist.choices_distribution(fake.factories, fake.weights, length=1)[0]
    else:
        row_faker = fake
    # reset variables that are modified while the row is build
    row = ()
    row_country = None
    # iterate over the columns 
    for field in fields:
        row_len = len(row)
        # if no type is given then match the name to the type
        fld_type = field['type'] if 'type' in field else None 
        if not fld_type:
            fld_type = field['name']
        # determine the specifc locale of the field, default to row locale
        fld_faker = row_faker
        fld_locale = field['locale'] if 'locale' in field else None 
        if fld_locale:
            fld_faker = fake[fld_locale]
        # person provider
        if fld_type == 'full_name':
            row += (" ".join((fld_faker.first_name(), fld_faker.last_name())), )
        if fld_type == 'first_name':
            row += (fld_faker.first_name(), )
        if fld_type == 'last_name':
            row += (fld_faker.last_name(), )
        
        # address provider
        if fld_type == 'address':
            row += (fld_faker.address(), )
        if fld_type == 'zipcode':
            row += (fld_faker.postcode(), )
        if fld_type == 'city':
            row += (fld_faker.city(), )
        if fld_type == 'street_address':
            row += (fld_faker.street_address(), )
        if fld_type == 'street_name':
            row += (fld_faker.street_name(), )
        if fld_type == 'country':
            row += (fld_faker.country(), )
        if fld_type == 'country_code':
            if not row_country:
                row_country = fld_faker.country_code()
            row += (row_country, )
        if fld_type == 'street_address':
            row += (fld_faker.street_address(), )
        
        # phone_number provider
        if fld_type == 'phone_number':
            row += (fld_faker.phone_number(), )

        # ssn provider
        if fld_type == 'ssn':
            row += (fld_faker.ssn(), )

        # geo provider
        if fld_type == 'latitude':
            row += (fld_faker.latitude(), )
        if fld_type == 'longitude':
            row += (fld_faker.longitude(), )
        if fld_type == 'latlong':
            row += (fld_faker.latlng(), )
        if fld_type == 'local_latlong':
            if not row_country:
                row_country = fld_faker.country_code()
            row += (fld_faker.local_latlng(country_code=row_country), )
        if fld_type == 'local_latitude':
            if not row_country:
                row_country = fld_faker.country_code()
            row += (str(fld_faker.local_latlng(country_code=row_country, coords_only=True)[0]), )
        if fld_type == 'local_longitude':
            if not row_country:
                row_country = fld_faker.country_code()
            row += (str(fld_faker.local_latlng(country_code=row_country, coords_only=True)[1]), )
        
        # credit_card provider
        if fld_type == 'ccn':
            row += (fld_faker.credit_card_number(), )
        
        # internet provider
        if fld_type == 'email_address':
            fixed_domain = field['domain'] if 'domain' in field else None
            if fixed_domain:
                row += (fld_faker.email(fixed_domain), )
            else:
                domains = field['domains'] if 'domains' in field else None
                if 'format' in field and field['format'] == 'ascii':
                    if domains == 'company':
                        row += (fld_faker.ascii_company_email(), )
                    if domains == 'free':
                        row += (fld_faker.ascii_free_email(), )
                    if domains == 'safe':
                        row += (fld_faker.ascii_safe_email(), )
                    if not domains:
                        row += (fld_faker.ascii_email(), )
                else:
                    if domains == 'company':
                        row += (fld_faker.company_email(), )
                    if domains == 'free':
                        row += (fld_faker.free_email(), )
                    if domains == 'safe':
                        row += (fld_faker.safe_email(), )
                    if not domains:
                        row += (fld_faker.email(), )
        if fld_type == 'domain_name':
            level = field['level'] if 'level' in field else 1
            row += (fld_faker.domain_name(level), )
        if fld_type == 'hostname':
            level = field['level'] if 'level' in field else 1
            row += (fld_faker.hostname(level), )
        if fld_type == 'ipv4_address':
            addr_class = field['class'] if 'class' in field else None
            network = field['network'] if 'network' in field else None
            scope = field['scope'] if 'scope' in field else None
            private = True if scope == 'private' else False if scope == 'public' else None
            row += (fld_faker.ipv4(network=network, address_class=addr_class, private=private), )
        if fld_type == 'ipv6_address':
            network = field['network'] if 'network' in field else None
            row += (fld_faker.ipv6(network=network), )
        if fld_type == 'user_name':
            row += (fld_faker.user_name(), )

        # date_time provider
        if fld_type in ('date', 'time', 'date_time'):
            pattern = field['pattern'] if 'pattern' in field else None
            start, end = getStartEnd(field)
            if fld_type == 'date':
                d = fld_faker.date_between(start, end)
            if fld_type == 'time':
                d = fld_faker.time_between(start, end)
            if fld_type == 'date_time':
                d = fld_faker.date_time_between(start, end)
            if pattern:
                d = d.strftime(pattern)
            row += (d, )
        if fld_type == 'unix_time':
            start, end = getStartEnd(field)
            row += (fld_faker.unix_time(end, start), )

        # misc provider
        if fld_type == 'password':
            length = field['length'] if 'length' in field else 10
            row += (fld_faker.password(length=length), )
        if fld_type == 'uuid4':
            row += (fld_faker.uuid4(), )

        # check if anything was added, otherwise add None
        if (len(row) == row_len): 
            row += (None, )

    return row    


def process_yaml_data(data: dict) -> None:
    # get various fields from the YAML file
    format = data['format'] if 'format' in data else 'csv'
    header = data['header'] if 'header' in data else False
    filename = data['filename'] if 'filename' in data else None
    locale = data['locale'] if 'locale' in data else 'en_US'
    rows = int(data['rows']) if 'rows' in data else 1
    fields = data['fields']
    field_delim = data['field_delimiter'] if 'field_delimiter' in data else ","

    # create a faker instance with the locale(s)
    if locale is dict:
        fake = Faker(OrderedDict(locale))
    else:
        fake = Faker(locale)

    # open file to write to and emit (optional) header row
    out = open(target, 'w') if filename else sys.stdout
    if header:
        out.write(get_header_row(data, field_delim))
    # emit as many rows as are asked for
    for r in range(1, rows):
        row = process_row(fields, fake)
        out.write(convert_tuple_to_str(row, delim=field_delim))
        out.write('\n')
    # only close files
    if out is not sys.stdout:
        out.close()


def process_yaml_files() -> None:
    for f in options.yaml_files:
        with open(f) as yaml_data:
            data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    process_yaml_data(data)


def main():
    parse_commandline()
    process_yaml_files()

if __name__ == "__main__":
    main()
        